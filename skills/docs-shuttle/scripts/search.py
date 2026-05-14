#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
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
Docs 搜索工具

使用 API 搜索文档。

用法：
    uv run --refresh-package ks_aimate search.py "关键词" [--page 1] [--size 20] [--json]
"""

import argparse
import json
import sys
import os
from pathlib import Path
from ks_aimate.sso_login_client import SmartSSOSession

# 配置
BASE_URL = "https://docs.corp.kuaishou.com"


def get_sso_client():
    return SmartSSOSession()


def search_via_api(keyword: str, page: int = 1, size: int = 20) -> dict:
    """通过 API 搜索文档"""
    client = get_sso_client()
    if not client:
        return {"success": False, "error": "无法获取 SSO 客户端"}

    url = f"{BASE_URL}/merlot/api/searchs/search?um=false"
    data = {
        "pageNum": page,
        "pageSize": size,
        "keywords": keyword,
        "type": "all",
        "orderBy": "viewTime"
    }

    try:
        resp = client.request("POST", url, json=data)
        result = resp.json()

        if result.get('code') != 0:
            return {
                "success": False,
                "error": f"API 返回错误: {result.get('message', 'Unknown error')}"
            }

        search_result = result.get('result', {})
        items = search_result.get('list', [])
        total = search_result.get('total', 0)

        results = []
        for item in items:
            doc_id = item.get('docId', '')
            doc_type = item.get('docTypeEn', 'doc')

            # 构建 URL
            if doc_type == 'folder':
                url_path = f"/s<skill_directory>{doc_id}"
            elif doc_type == 'kb' or item.get('spaceShortcutId'):
                url_path = f"/k/home/{item.get('spaceShortcutId', '')}/{doc_id}"
            else:
                url_path = f"/d/home/{doc_id}"

            results.append({
                "title": item.get('docName', 'Untitled'),
                "url": f"{BASE_URL}{url_path}",
                "author": item.get('creatorName', '') or item.get('lastEditorName', ''),
                "snippet": (item.get('contentPreview', '') or '')[:200],
                "type": doc_type,
                "docId": doc_id
            })

        return {
            "success": True,
            "total": total,
            "page": page,
            "size": size,
            "results": results
        }

    except Exception as e:
        return {"success": False, "error": f"请求失败: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description='Docs 文档搜索工具')
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('--page', type=int, default=1, help='页码（默认：1）')
    parser.add_argument('--size', type=int, default=20, help='每页结果数（默认：20）')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')

    args = parser.parse_args()

    print(f"🔍 搜索: {args.keyword}", file=sys.stderr)
    print(file=sys.stderr)

    result = search_via_api(args.keyword, args.page, args.size)

    if result['success']:
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"✅ 找到 {result['total']} 条结果", file=sys.stderr)
            print(file=sys.stderr)

            for i, doc in enumerate(result['results'], 1):
                print(f"{i}. {doc['title']}")
                print(f"   🔗 {doc['url']}")
                if doc['author']:
                    print(f"   👤 {doc['author']}")
                if doc['snippet']:
                    print(f"   📝 {doc['snippet']}")
                print()
    else:
        print(f"❌ 搜索失败: {result.get('error', '未知错误')}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
