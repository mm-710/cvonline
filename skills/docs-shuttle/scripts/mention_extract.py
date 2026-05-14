#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate>=1.0.30",
# ]
#
# [tool.uv.sources]
# "ks_aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///
"""
docs-shuttle: 从普通表格中提取 @mention 用户信息

用途:
  - 从 /s/home/ 或 /t/home/ 的普通表格中提取被 @ 的用户名和用户信息
  - 返回 username / displayName / enName / userId
  - 供 docs-shuttle 在读表、分析表格内容时做 best-effort 增强
  - 优先走 snapshot 富文本链路；若 snapshot 无法提取，再使用 SSR HTML 作为兜底
  - 不能用 read 可见文本代替 username 提取

用法:
  uv run mention_extract.py <docs-url> [--format json|csv|text]
  uv run mention_extract.py <docs-url> --revision 3095
  uv run mention_extract.py <docs-url> --best-effort
"""

import argparse
import csv
import io
import json
import re
import sys
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple

try:
    from ks_aimate.sso_login_client import SmartSSOSession
except ImportError:
    print("❌ 错误: 无法导入 ks_aimate 库", file=sys.stderr)
    print("💡 请使用 uv run mention_extract.py 运行此脚本", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://docs.corp.kuaishou.com"
SSR_API = f"{BASE_URL}/excel-ssr/api/html"


def parse_sheet_url(url_or_id: str) -> Tuple[Optional[str], Optional[str]]:
    """从普通表格 URL 或 docId 中提取 docId 和 sheetId。"""
    if not url_or_id.startswith("http"):
        return url_or_id, None

    doc_id = None
    patterns = [
        r"/s/home/([^/?#]+)",
        r"/t/home/[^/]+/([^/?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            doc_id = match.group(1)
            break

    sheet_id = None
    parsed = urllib.parse.urlparse(url_or_id)
    if parsed.query:
        params = urllib.parse.parse_qs(parsed.query)
        sheet_id = params.get("section", [None])[0]

    return doc_id, sheet_id


def collect_revision_candidates(obj: object, candidates: Set[str]) -> None:
    """递归收集可能的 revision 值。"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            normalized = key.lower()
            if normalized in ("snapshotrevision", "snapshotrev", "revision", "version"):
                if isinstance(value, (int, float)) and value > 0:
                    candidates.add(str(int(value)))
                elif isinstance(value, str) and value.isdigit():
                    candidates.add(value)
            collect_revision_candidates(value, candidates)
    elif isinstance(obj, list):
        for item in obj:
            collect_revision_candidates(item, candidates)


def get_meta_revision_candidates(client: SmartSSOSession, doc_id: str) -> List[str]:
    candidates: Set[str] = set()
    try:
        meta_url = f"{BASE_URL}/merlot/e/api/skills/excel/meta?docId={doc_id}"
        meta_resp = client.request("GET", meta_url)
        meta_data = meta_resp.json()
        collect_revision_candidates(meta_data, candidates)
    except Exception as exc:
        print(f"⚠️  从 meta API 获取 revision 失败: {exc}", file=sys.stderr)
    return sorted(candidates, key=int, reverse=True)


def get_top_snapshot_revision_candidates(client: SmartSSOSession, doc_id: str) -> List[str]:
    candidates: Set[str] = set()
    try:
        snapshot_url = f"{BASE_URL}/excel/api/latest/snapshot/{doc_id}?top=true"
        snapshot_resp = client.request("GET", snapshot_url)
        snapshot_data = snapshot_resp.json()
        collect_revision_candidates(snapshot_data, candidates)
    except Exception as exc:
        print(f"⚠️  从 snapshot API 获取 revision 失败: {exc}", file=sys.stderr)
    return sorted(candidates, key=int, reverse=True)


def get_page_revision_candidates(client: SmartSSOSession, url: str, doc_id: str) -> List[str]:
    """从文档页面 HTML 中提取可能的 revision。"""
    candidates: Set[str] = set()
    target_url = url if url.startswith("http") else f"{BASE_URL}/s/home/{doc_id}"
    try:
        resp = client.request("GET", target_url)
        html = resp.text
        patterns = [
            r"snapshotRevision[\"'\s:=]+(\d+)",
            r"snapshotRev[\"'\s:=]+(\d+)",
            r"revision[\"'\s:=]+(\d+)",
            r"/excel/api/latest/snapshot/[^?]+\?snapshotRevision=(\d+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                candidates.add(match.group(1))
    except Exception as exc:
        print(f"⚠️  从文档页面提取 revision 失败: {exc}", file=sys.stderr)
    return sorted(candidates, key=int, reverse=True)


def get_snapshot_revision(client: SmartSSOSession, url: str, doc_id: str) -> Optional[str]:
    """按多种来源深挖 snapshotRevision。"""
    candidate_sources = [
        ("meta API", get_meta_revision_candidates(client, doc_id)),
        ("top snapshot", get_top_snapshot_revision_candidates(client, doc_id)),
        ("doc page", get_page_revision_candidates(client, url, doc_id)),
    ]

    seen: Set[str] = set()
    ordered_candidates: List[str] = []
    for source_name, source_candidates in candidate_sources:
        if source_candidates:
            print(
                f"🔎 从 {source_name} 找到 revision 候选: {', '.join(source_candidates[:5])}",
                file=sys.stderr,
            )
        for candidate in source_candidates:
            if candidate not in seen:
                seen.add(candidate)
                ordered_candidates.append(candidate)

    if ordered_candidates:
        return ordered_candidates[0]
    return None


def fetch_snapshot_data(
    client: SmartSSOSession,
    doc_id: str,
    snapshot_revision: str,
    sheet_id: Optional[str] = None,
) -> Optional[dict]:
    """获取包含富文本 HTML 的 snapshot 数据。"""
    params = {
        "snapshotRevision": snapshot_revision,
        "top": "false",
    }
    if sheet_id:
        params["sheetId"] = sheet_id

    url = f"{BASE_URL}/excel/api/latest/snapshot/{doc_id}?{urllib.parse.urlencode(params)}"

    try:
        response = client.request("GET", url)
        if response.status_code != 200:
            print(f"❌ API 请求失败: HTTP {response.status_code}", file=sys.stderr)
            return None
        return response.json()
    except Exception as exc:
        print(f"❌ 请求 snapshot API 失败: {exc}", file=sys.stderr)
        return None


def fetch_ssr_html(client: SmartSSOSession, doc_id: str, original_url: str) -> Optional[str]:
    """获取表格 SSR HTML，作为 snapshot 失败时的兜底来源。"""
    try:
        resp = client.request(
            "GET",
            f"{SSR_API}/{urllib.parse.quote(doc_id)}?showTopToolbar=false",
            headers={"Referer": original_url},
        )
        if resp.status_code != 200:
            print(f"⚠️  SSR 接口请求失败: HTTP {resp.status_code}", file=sys.stderr)
            return None
        return resp.text
    except Exception as exc:
        print(f"⚠️  请求 SSR HTML 失败: {exc}", file=sys.stderr)
        return None


def parse_html_attrs(opening_tag: str) -> Dict[str, str]:
    """解析 HTML 开始标签上的属性，兼容单双引号及无引号值。"""
    attrs: Dict[str, str] = {}
    for match in re.finditer(
        r'([:@\w-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))',
        opening_tag,
        re.IGNORECASE,
    ):
        key = match.group(1)
        value = match.group(2) or match.group(3) or match.group(4) or ""
        attrs[key] = value
    return attrs


def strip_html_tags(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    return re.sub(r"\s+", " ", text).strip()


def extract_users_from_snapshot(data: object) -> List[Dict[str, str]]:
    """从 snapshot JSON 中递归提取 mention 用户信息。"""
    users: Dict[str, Dict[str, str]] = {}

    def extract_from_html(html_str: str) -> None:
        anchor_pattern = re.compile(
            r"(<a\b[^>]*>)(.*?)</a>",
            re.IGNORECASE | re.DOTALL,
        )
        for match in anchor_pattern.finditer(html_str):
            opening_tag = match.group(1)
            inner_html = match.group(2) or ""
            attrs = parse_html_attrs(opening_tag)
            class_name = attrs.get("class", "")
            if "cell-mention" not in class_name:
                continue

            username = (
                attrs.get("data-login-id")
                or attrs.get("data-loginId")
                or attrs.get("data-login")
                or ""
            ).strip()
            if not username or username in users:
                continue

            display_text = strip_html_tags(inner_html).lstrip("@").strip()
            display_name = (
                attrs.get("data-cn-name")
                or attrs.get("data-display-name")
                or display_text
            )
            en_name = attrs.get("data-en-name") or attrs.get("data-english-name") or ""
            user_id = attrs.get("data-id") or attrs.get("data-user-id") or attrs.get("data-userid") or ""

            users[username] = {
                "username": username,
                "displayName": display_name,
                "enName": en_name,
                "userId": user_id,
            }

    def visit(obj: object) -> None:
        if isinstance(obj, dict):
            for value in obj.values():
                if isinstance(value, str) and "cell-mention" in value:
                    extract_from_html(value)
                else:
                    visit(value)
        elif isinstance(obj, list):
            for item in obj:
                visit(item)

    visit(data)
    return sorted(users.values(), key=lambda item: (item.get("displayName", ""), item.get("username", "")))


def extract_users_from_ssr_html(html: str) -> List[Dict[str, str]]:
    """从 SSR HTML 中提取首屏 mention 用户信息。"""
    users: Dict[str, Dict[str, str]] = {}
    anchor_pattern = re.compile(r"(<a\b[^>]*>)(.*?)</a>", re.IGNORECASE | re.DOTALL)

    for match in anchor_pattern.finditer(html):
        opening_tag = match.group(1)
        inner_html = match.group(2) or ""
        attrs = parse_html_attrs(opening_tag)
        class_name = attrs.get("class", "")
        if "cell-mention" not in class_name:
            continue

        username = (
            attrs.get("data-login-id")
            or attrs.get("data-loginId")
            or attrs.get("data-login")
            or ""
        ).strip()
        if not username or username in users:
            continue

        display_text = strip_html_tags(inner_html).lstrip("@").strip()
        display_name = (
            attrs.get("data-cn-name")
            or attrs.get("data-display-name")
            or display_text
        )
        en_name = attrs.get("data-en-name") or attrs.get("data-english-name") or ""
        user_id = attrs.get("data-id") or attrs.get("data-user-id") or attrs.get("data-userid") or ""

        users[username] = {
            "username": username,
            "displayName": display_name,
            "enName": en_name,
            "userId": user_id,
        }

    return sorted(users.values(), key=lambda item: (item.get("displayName", ""), item.get("username", "")))


def build_result(
    doc_id: str,
    sheet_id: Optional[str],
    revision: Optional[str],
    users: List[Dict[str, str]],
    warning: Optional[str] = None,
) -> Dict[str, object]:
    result: Dict[str, object] = {
        "doc_id": doc_id,
        "sheet_id": sheet_id,
        "snapshot_revision": revision,
        "total": len(users),
        "users": users,
    }
    if warning:
        result["warning"] = warning
    return result


def render_json(result: Dict[str, object]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


def render_csv(result: Dict[str, object]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["username", "displayName", "enName", "userId"])
    writer.writeheader()
    writer.writerows(result["users"])
    return output.getvalue()


def render_text(result: Dict[str, object]) -> str:
    lines = [f"找到 {result['total']} 个用户:\n"]
    for user in result["users"]:
        line = f"  {user.get('username', 'N/A'):20s} - {user.get('displayName', 'N/A')}"
        if user.get("enName"):
            line += f" ({user['enName']})"
        lines.append(line)
    if result.get("warning"):
        lines.append("")
        lines.append(f"⚠️  {result['warning']}")
    return "\n".join(lines)


def emit_output(result: Dict[str, object], fmt: str, output_file: Optional[str]) -> None:
    if fmt == "json":
        content = render_json(result)
    elif fmt == "csv":
        content = render_csv(result)
    else:
        content = render_text(result)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as file_obj:
            file_obj.write(content)
        print(f"✅ 已保存到: {output_file}")
        return

    print(content)


def fail_or_warn(message: str, args: argparse.Namespace, doc_id: str, sheet_id: Optional[str]) -> None:
    if not args.best_effort:
        print(message, file=sys.stderr)
        sys.exit(1)

    print(f"⚠️  {message}", file=sys.stderr)
    emit_output(build_result(doc_id, sheet_id, None, [], warning=message), args.format, args.output)
    sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从普通表格中提取 @mention 用户信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run mention_extract.py "https://docs.corp.kuaishou.com/t<skill_directory>?section=123"
  uv run mention_extract.py "https://docs.corp.kuaishou.com/s<skill_directory>" --format text
  uv run mention_extract.py "..." --best-effort
        """,
    )
    parser.add_argument("url", help="普通表格 URL（/s/home/ 或 /t/home/）或 docId")
    parser.add_argument("--format", choices=["json", "csv", "text"], default="json", help="输出格式")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--revision", help="手动指定 snapshotRevision")
    parser.add_argument(
        "--best-effort",
        action="store_true",
        help="提取失败时返回空结果并附带 warning，不中断主流程",
    )
    args = parser.parse_args()

    print(f"📋 解析 URL: {args.url}")
    doc_id, sheet_id = parse_sheet_url(args.url)
    if not doc_id:
        fail_or_warn(f"无法从输入中提取 docId: {args.url}", args, "", sheet_id)

    print(f"  DocId: {doc_id}")
    print(f"  SheetId: {sheet_id or '(未指定)'}\n")

    print("🔐 初始化 SSO 认证...")
    client = SmartSSOSession()
    warning: Optional[str] = None

    if args.revision:
        revision = args.revision
        print(f"📌 使用指定的 revision: {revision}")
    else:
        print("📌 自动获取 snapshotRevision...")
        revision = get_snapshot_revision(client, args.url, doc_id)
        if revision:
            print(f"  Revision: {revision}\n")

    users: List[Dict[str, str]] = []
    snapshot_attempted = False
    if revision:
        print("🌐 获取 snapshot 数据...")
        snapshot_attempted = True
        snapshot_data = fetch_snapshot_data(client, doc_id, revision, sheet_id)
        if not snapshot_data and sheet_id:
            print("⚠️  使用 section 对应 sheetId 获取失败，尝试不带 sheetId 重试...", file=sys.stderr)
            snapshot_data = fetch_snapshot_data(client, doc_id, revision, None)
        if snapshot_data:
            print("🔍 从 snapshot 提取用户信息...")
            users = extract_users_from_snapshot(snapshot_data)
            if not users and sheet_id:
                print("⚠️  指定 sheetId 未提取到用户，尝试全表范围重试...", file=sys.stderr)
                fallback_snapshot = fetch_snapshot_data(client, doc_id, revision, None)
                if fallback_snapshot:
                    users = extract_users_from_snapshot(fallback_snapshot)
        else:
            print("⚠️  snapshot 数据获取失败，准备尝试 SSR 兜底...", file=sys.stderr)
    else:
        print("⚠️  未能自动获取 snapshotRevision，准备尝试 SSR 兜底...", file=sys.stderr)

    if not users:
        print("🧭 尝试使用 SSR HTML 兜底提取...")
        ssr_html = fetch_ssr_html(client, doc_id, args.url)
        if ssr_html:
            users = extract_users_from_ssr_html(ssr_html)
            if users:
                warning = "通过 SSR HTML 兜底提取成功；SSR 仅覆盖首屏可见区域，结果可能不完整"
            elif snapshot_attempted:
                warning = "snapshot 未提取到结构化 mention，且 SSR 首屏范围内也未发现可提取的 mention"
            else:
                warning = "无法获取 snapshotRevision，且 SSR 首屏范围内未发现可提取的 mention"
        elif snapshot_attempted:
            warning = "snapshot 提取失败，且 SSR 兜底也未成功"
        else:
            warning = "无法获取 snapshotRevision，且 SSR 兜底也未成功"

    if not users:
        result = build_result(doc_id, sheet_id, revision, [], warning=warning)
        emit_output(result, args.format, args.output)
        return

    print(f"  找到 {len(users)} 个唯一用户\n")
    result = build_result(doc_id, sheet_id, revision, users, warning=warning)
    emit_output(result, args.format, args.output)


if __name__ == "__main__":
    main()
