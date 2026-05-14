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
Docs 评论功能 - 向指定文档添加评论 / 查看评论列表

⚠️  重要限制：评论功能仅支持普通文档（/d/home/ 或 /k/home/）
   不支持普通表格（/s/home/）和万维表格（/m/home/）

用法:
  添加评论:   uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py add <docs-url> <comment-text> [reply_id]
  查看评论:   uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py list <docs-url> [--solved] [--count N]

  兼容旧用法（直接添加评论）:
              uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py <docs-url> <comment-text> [reply_id]

示例:
  uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py add "https://docs.corp.kuaishou.com/d<skill_directory>" "这是一条评论"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py list "https://docs.corp.kuaishou.com/d<skill_directory>"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py list "https://docs.corp.kuaishou.com/d<skill_directory>" --solved
  uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py list "https://docs.corp.kuaishou.com/d<skill_directory>" --count 10
"""

import sys
import re
import json
from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://docs.corp.kuaishou.com"


def get_sso_client():
    return SmartSSOSession()


def extract_doc_id(url: str) -> str:
    """从 URL 中提取文档 ID（fc 开头）"""
    match = re.search(r'(fc[A-Za-z0-9_-]+)', url)
    if not match:
        raise ValueError(f"无法从 URL 中提取文档 ID: {url}")
    return match.group(1)


def check_doc_type(url: str) -> tuple[bool, str]:
    """
    检查URL是否为普通文档类型
    返回: (是否支持评论, 文档类型说明)
    """
    # 检查是否为表格或万维表格URL
    if re.search(r'/s/home/', url):
        return False, "普通表格（/s/home/）不支持评论功能"
    if re.search(r'/m/home/', url) or re.search(r'/b/home/', url):
        return False, "万维表格（/m/home/）不支持评论功能"
    
    # 普通文档支持评论
    if re.search(r'/d/home/', url) or re.search(r'/k/home/', url):
        return True, "普通文档"
    
    # 团队URL需要进一步检测类型
    if re.search(r'/t/home/', url):
        return True, "团队文档（需进一步验证类型）"
    
    # 默认允许，但提示可能不支持
    return True, "未知类型（可能不支持评论）"



def list_comments(client, doc_id: str, solved: bool = False, count: int = 50) -> dict:
    """查询文档评论列表"""
    if solved:
        # 已解决评论用独立接口
        url = f"{BASE_URL}/react/api/doc-discussion/solved-discussions/{doc_id}"
        params = {"asc": "false", "count": count, "cursor": ""}
    else:
        # solved=false 为必填参数
        url = f"{BASE_URL}/react/api/doc-discussion/discussions/{doc_id}"
        params = {"count": count, "solved": "false"}

    resp = client.request(
        "GET", url,
        params=params,
        headers={"Referer": f"{BASE_URL}/d/home/{doc_id}"}
    )
    return resp.json()


def add_comment(client, doc_id: str, text: str, reply_id: str = "") -> dict:
    """向指定文档添加评论"""
    url = f"{BASE_URL}/react/api/doc-discussion/add/{doc_id}"

    # 构建 payload
    json_content = json.dumps({
        "ops": [
            {"insert": text + "\n\n", "type": "text"}
        ]
    })
    html_content = f"<p>{text}</p>"

    payload = {
        "htmlContent": html_content,
        "jsonContent": json_content,
        "replyId": reply_id
    }

    resp = client.request(
        "POST", url,
        json=payload,
        headers={"Referer": f"{BASE_URL}/d/home/{doc_id}"}
    )
    return resp.json()


def print_comments(result: dict, solved: bool):
    """格式化打印评论列表"""
    disc_data = result.get("result", {}).get("discussions", {})
    discussions = disc_data.get("discussions", [])
    total_unsolved = disc_data.get("totalUnsolved", "?")
    total_solved = disc_data.get("totalSolved", "?")
    user_infos = {u["id"]: u.get("name", u.get("nickname", "")) for u in result.get("result", {}).get("userInfos", [])}

    print(f"📊 未解决: {total_unsolved} 条  已解决: {total_solved} 条")
    print(f"{'已解决' if solved else '未解决'}评论列表（共 {len(discussions)} 条）：")
    print()

    if not discussions:
        print("（暂无评论）")
        return

    for i, disc in enumerate(discussions, 1):
        disc_id = disc.get("id", "")
        solved_by = disc.get("solvedBy", "0")
        status = "✅ 已解决" if solved_by != "0" else "🟡 未解决"
        author_id = disc.get("authorId", "")
        author = user_infos.get(author_id, author_id[:8] + "...")

        # 优先从 jsonContent 提取纯文本
        content_text = ""
        json_content = disc.get("jsonContent", "")
        if json_content:
            try:
                ops = json.loads(json_content).get("ops", [])
                content_text = "".join(op.get("insert", "") for op in ops).strip()
            except Exception:
                pass
        if not content_text:
            content_text = re.sub(r'<[^>]+>', '', disc.get("content", "") or "").strip()

        print(f"[{i}] ID: {disc_id}  {status}")
        print(f"    👤 {author}")
        print(f"    💬 {content_text[:120]}")

        replies = disc.get("replies", {}).get("replies", [])
        for j, reply in enumerate(replies, 1):
            r_id = reply.get("id", "")
            r_author_id = reply.get("authorId", "")
            r_author = user_infos.get(r_author_id, r_author_id[:8] + "...")
            r_text = ""
            r_json = reply.get("jsonContent", "")
            if r_json:
                try:
                    ops = json.loads(r_json).get("ops", [])
                    r_text = "".join(op.get("insert", "") for op in ops).strip()
                except Exception:
                    pass
            if not r_text:
                r_text = re.sub(r'<[^>]+>', '', reply.get("content", "") or "").strip()
            print(f"    ↳ 回复[{j}] ID:{r_id}  👤 {r_author}  {r_text[:80]}")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # 判断是否使用子命令
    cmd = sys.argv[1]

    if cmd == "list":
        # list 子命令
        if len(sys.argv) < 3:
            print("Usage: uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py list <docs-url> [--solved] [--count N]")
            sys.exit(1)
        url_or_id = sys.argv[2]
        
        # 检查文档类型
        supported, doc_type = check_doc_type(url_or_id)
        if not supported:
            print(f"❌ 不支持的文档类型: {doc_type}")
            print(f"⚠️  评论功能仅支持普通文档（/d/home/ 或 /k/home/）")
            print(f"   不支持普通表格（/s/home/）和万维表格（/m/home/）")
            sys.exit(1)
        
        rest = sys.argv[3:]
        solved = "--solved" in rest
        count = 50
        for i, a in enumerate(rest):
            if a == "--count" and i + 1 < len(rest):
                count = int(rest[i + 1])

        doc_id = extract_doc_id(url_or_id)
        print(f"📄 文档 ID: {doc_id}")
        print(f"📝 文档类型: {doc_type}")
        print(f"🔍 查询{'已解决' if solved else '未解决'}评论（最多 {count} 条）...\n")

        client = get_sso_client()
        result = list_comments(client, doc_id, solved=solved, count=count)
        if result.get("code") == 0:
            if solved:
                # 查已解决时，补查未解决数量
                unsolved_result = list_comments(client, doc_id, solved=False, count=1)
                if unsolved_result.get("code") == 0:
                    unsolved_count = unsolved_result["result"]["discussions"].get("totalUnsolved", "?")
                    result["result"]["discussions"]["totalUnsolved"] = unsolved_count
                result["result"]["discussions"]["totalSolved"] = len(result["result"]["discussions"].get("discussions", []))
            else:
                # 查未解决时，补查已解决数量
                solved_result = list_comments(client, doc_id, solved=True, count=500)
                if solved_result.get("code") == 0:
                    solved_count = len(solved_result["result"]["discussions"].get("discussions", []))
                    result["result"]["discussions"]["totalSolved"] = solved_count
            print_comments(result, solved)
        else:
            print(f"❌ 查询失败: {result.get('message', '未知错误')}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

    elif cmd == "add":
        # add 子命令
        if len(sys.argv) < 4:
            print("Usage: uv run --refresh-package ks_aimate <skill_directory>/scripts/comment.py add <docs-url> <comment-text> [reply_id]")
            sys.exit(1)
        url_or_id = sys.argv[2]
        
        # 检查文档类型
        supported, doc_type = check_doc_type(url_or_id)
        if not supported:
            print(f"❌ 不支持的文档类型: {doc_type}")
            print(f"⚠️  评论功能仅支持普通文档（/d/home/ 或 /k/home/）")
            print(f"   不支持普通表格（/s/home/）和万维表格（/m/home/）")
            sys.exit(1)
        
        text = sys.argv[3]
        reply_id = sys.argv[4] if len(sys.argv) > 4 else ""
        doc_id = extract_doc_id(url_or_id)
        print(f"📄 文档 ID: {doc_id}")
        print(f"📝 文档类型: {doc_type}")
        print(f"💬 评论内容: {text}")
        client = get_sso_client()
        result = add_comment(client, doc_id, text, reply_id)
        if result.get("code") == 0:
            discussion = result["result"]["discussion"]
            print(f"✅ 评论添加成功!")
            print(f"   评论 ID: {discussion['id']}")
            print(f"   内容: {discussion['content']}")
            print(f"   创建时间: {discussion['createTime']}")
        else:
            print(f"❌ 评论添加失败: {result.get('message', '未知错误')}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)

    else:
        # 兼容旧用法
        if len(sys.argv) < 3:
            print(__doc__)
            sys.exit(1)
        url_or_id = sys.argv[1]
        
        # 检查文档类型
        supported, doc_type = check_doc_type(url_or_id)
        if not supported:
            print(f"❌ 不支持的文档类型: {doc_type}")
            print(f"⚠️  评论功能仅支持普通文档（/d/home/ 或 /k/home/）")
            print(f"   不支持普通表格（/s/home/）和万维表格（/m/home/）")
            sys.exit(1)
        
        text = sys.argv[2]
        reply_id = sys.argv[3] if len(sys.argv) > 3 else ""
        doc_id = extract_doc_id(url_or_id)
        print(f"📄 文档 ID: {doc_id}")
        print(f"📝 文档类型: {doc_type}")
        print(f"💬 评论内容: {text}")
        client = get_sso_client()
        result = add_comment(client, doc_id, text, reply_id)
        if result.get("code") == 0:
            discussion = result["result"]["discussion"]
            print(f"✅ 评论添加成功!")
            print(f"   评论 ID: {discussion['id']}")
            print(f"   内容: {discussion['content']}")
            print(f"   创建时间: {discussion['createTime']}")
        else:
            print(f"❌ 评论添加失败: {result.get('message', '未知错误')}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)


if __name__ == "__main__":
    main()
