#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "ks-aimate>=1.0.30",
# ]
#
# [tool.uv.sources]
# "ks-aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///
"""从 MyFlicker Skill 市场拉取全量 Skill，按关键词粗排后返回 top 候选。

语义重排由调用方（AI）完成，本脚本只负责：
  1. 分页拉取市场数据
  2. 关键词 + 否定惩罚粗筛
  3. 返回 JSON 供 AI 做语义判断
"""

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict, cast

from ks_aimate.sso_login_client.session import SmartSSOSession

API_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/skills/list"
PAGE_SIZE = 100
# 粗排候选数，供 AI 做语义重排用，比最终展示数量多
COARSE_CANDIDATES = 15

# 否定前缀列表：紧跟这些前缀的词组不计入正向匹配，反而扣分
NEGATION_PREFIXES = [
    "不负责", "不支持", "不处理", "不包含", "不适用", "不用于",
    "不能", "不会", "无法", "禁止", "仅限", "不涉及",
]


class SkillItem(TypedDict):
    slug: str
    summary: str


class SearchMatch(TypedDict):
    slug: str
    summary: str
    score: float


JsonObject = dict[str, object]
JsonList = list[object]


def fetch_page(client: SmartSSOSession, page: int) -> tuple[list[SkillItem], int]:
    """返回 (items, total)，total 仅第 1 页有效，其余页返回 0。"""
    response = client.request(
        "POST",
        API_URL,
        json={
            "sort": "hottest",
            "page": page,
            "size": PAGE_SIZE,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = cast(object, response.json())
    if not isinstance(payload, dict):
        raise ValueError("skills/list 返回结构异常，根节点不是对象")

    payload_dict = cast(JsonObject, payload)
    data_value = payload_dict.get("data")
    if data_value is None:
        return [], 0
    if not isinstance(data_value, dict):
        raise ValueError("skills/list 返回结构异常，data 不是对象")

    data_dict = cast(JsonObject, data_value)

    # 从第 1 页获取 total
    total = int(data_dict.get("total") or 0)

    items_value = data_dict.get("items")
    if items_value is None:
        return [], total
    if not isinstance(items_value, list):
        raise ValueError("skills/list 返回结构异常，data.items 不是数组")

    items_list = cast(JsonList, items_value)
    normalized_items: list[SkillItem] = []
    for raw_item in items_list:
        if not isinstance(raw_item, dict):
            continue
        item = cast(JsonObject, raw_item)
        slug = str(item.get("slug") or "").strip()
        summary = str(item.get("summary") or "").strip()
        if slug and summary:
            normalized_items.append({"slug": slug, "summary": summary})

    return normalized_items, total


def build_skill_map(client: SmartSSOSession) -> dict[str, str]:
    # 先拉第 1 页，获取 total 以确定总页数
    first_items, total = fetch_page(client, 1)
    skill_map: dict[str, str] = {item["slug"]: item["summary"] for item in first_items}

    if total <= PAGE_SIZE:
        return skill_map

    import math
    total_pages = math.ceil(total / PAGE_SIZE)
    remaining_pages = range(2, total_pages + 1)

    # 并发拉取剩余页
    with ThreadPoolExecutor(max_workers=min(8, len(remaining_pages))) as executor:
        futures = {executor.submit(fetch_page, client, p): p for p in remaining_pages}
        for future in as_completed(futures):
            items, _ = future.result()
            for item in items:
                skill_map[item["slug"]] = item["summary"]

    return skill_map


def tokenize(text: str) -> list[str]:
    """将文本拆成可匹配 token。
    方案 D：中文只产出 bigram，不产出单字（消除单字噪音）；英文/数字保留整体词。
    混合段先按中英文边界拆子段再分别处理。
    """
    tokens: list[str] = []
    for segment in re.split(r"[^\w\u4e00-\u9fff]+", text.lower()):
        if not segment:
            continue
        for sub in re.split(r"(?<=[\u4e00-\u9fff])(?=[a-z0-9])|(?<=[a-z0-9])(?=[\u4e00-\u9fff])", segment):
            if not sub:
                continue
            if re.fullmatch(r"[a-z0-9]+", sub):
                # 英文/数字：保留整体
                tokens.append(sub)
            else:
                # 中文：只产出 bigram，不产出单字（方案 D）
                for i in range(len(sub) - 1):
                    tokens.append(sub[i : i + 2])
    return list(dict.fromkeys(tokens))


def _split_negation_segments(summary: str) -> tuple[str, str]:
    """将 summary 拆分为正向描述片段和否定片段。

    否定片段：紧跟否定前缀后、直到句尾（。！换行）之间的文字。
    返回 (positive_text, negative_text)。
    """
    neg_pattern = "(" + "|".join(re.escape(p) for p in NEGATION_PREFIXES) + r")[^。！\n]*"
    negative_parts: list[str] = re.findall(neg_pattern, summary)
    negative_text = " ".join(negative_parts)
    positive_text = re.sub(neg_pattern, " ", summary)
    return positive_text, negative_text


def score_summary(query: str, summary: str) -> float:
    """计算 query 与 summary 的关键词相关性分数。

    - 正向命中：+1/词
    - 否定片段命中：-2/词（避免"不负责会议室"被误算正分）
    - 完整短语命中正向区额外加分
    """
    query_terms = tokenize(query)
    if not query_terms:
        return 0.0

    positive_text, negative_text = _split_negation_segments(summary.lower())
    query_lower = query.lower()

    pos_score = sum(1 for term in query_terms if term in positive_text)
    neg_score = sum(1 for term in query_terms if term in negative_text)
    score: float = pos_score - 2.0 * neg_score

    # 完整短语命中正向区额外加分
    if query_lower in positive_text:
        score += len(query_terms) + 2

    return score


def search_coarse_candidates(query: str, skill_map: dict[str, str]) -> list[SearchMatch]:
    """关键词粗排，返回 top COARSE_CANDIDATES 条候选供 AI 做语义重排。

    方案 B：要求命中 token 占 query tokens 总数的比例（覆盖率）不低于 MIN_COVERAGE，
    过滤掉零散单词碰巧命中的低相关候选。
    """
    MIN_COVERAGE = 0.25  # 至少 25% 的 query bigram/词在 summary 中命中
    query_terms = tokenize(query)
    if not query_terms:
        return []

    candidates: list[SearchMatch] = []
    for slug, summary in skill_map.items():
        score = score_summary(query, summary)
        if score <= 0:
            continue
        # 方案 B：计算覆盖率，过滤低相关候选
        positive_text, _ = _split_negation_segments(summary.lower())
        pos_hits = sum(1 for t in query_terms if t in positive_text)
        coverage = pos_hits / len(query_terms)
        if coverage < MIN_COVERAGE:
            continue
        candidates.append({"slug": slug, "summary": summary, "score": score})

    candidates.sort(key=lambda item: (-item["score"], item["slug"]))
    return candidates[:COARSE_CANDIDATES]


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description="Search duplicated skills from MyFlicker marketplace")
        _ = parser.add_argument("--query", required=True, type=str, help="用户当前要创建的 Skill 意图")
        args = parser.parse_args()

        query = cast(str, args.query).strip()
        if not query:
            raise ValueError("query 不能为空")

        client = SmartSSOSession()
        skill_map = build_skill_map(client)
        candidates = search_coarse_candidates(query, skill_map)
        result = {
            "query": query,
            "total_skills": len(skill_map),
            "note": "以下为关键词粗排候选，请由 AI 根据语义相关性进一步筛选和重排",
            "candidates": [{"slug": item["slug"], "summary": item["summary"]} for item in candidates],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print(f"错误：{error}")
        print("指引：请检查 SSO 登录状态、内网连通性，或确认 Skill 市场接口是否可访问。")
        sys.exit(0)


if __name__ == "__main__":
    main()
