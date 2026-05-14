#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate",
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

import argparse
import json
import sys

from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://myflicker.corp.kuaishou.com"
PROXY_PATH = "/api/v1/skills/exec/proxy"
TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, max_results: int, search_depth: str):
    body = {
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_images": False,
        "include_raw_content": False,
    }

    proxy_payload = {
        "url": TAVILY_URL,
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": body,
    }

    client = SmartSSOSession()
    try:
        resp = client.request("POST", f"{BASE_URL}{PROXY_PATH}", json=proxy_payload)
        resp_text = resp.text
    except Exception as e:
        raise SystemExit(f"❌ 请求失败: {e}\n建议操作：检查网络连通性后重试。")

    try:
        obj = json.loads(resp_text)
    except json.JSONDecodeError:
        raise SystemExit(f"Tavily returned non-JSON: {resp_text[:300]}")

    out = {
        "query": query,
        "results": [],
    }

    for r in (obj.get("results") or [])[:max_results]:
        out["results"].append(
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
            }
        )

    return out


def to_brave_like(obj: dict) -> dict:
    results = []
    for r in obj.get("results", []) or []:
        results.append(
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "snippet": r.get("content"),
            }
        )
    return {"query": obj.get("query"), "results": results}


def to_markdown(obj: dict) -> str:
    lines = []
    for i, r in enumerate(obj.get("results", []) or [], 1):
        title = (r.get("title") or "").strip() or r.get("url") or "(no title)"
        url = r.get("url") or ""
        snippet = (r.get("content") or "").strip()
        lines.append(f"{i}. {title}")
        if url:
            lines.append(f"   {url}")
        if snippet:
            lines.append(f"   - {snippet}")
    return "\n".join(lines).strip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--max-results", type=int, default=5)
    ap.add_argument(
        "--search-depth",
        default="basic",
        choices=["basic", "advanced"],
        help="Tavily search depth",
    )
    ap.add_argument(
        "--format",
        default="raw",
        choices=["raw", "brave", "md"],
        help="Output format: raw (default) | brave (title/url/snippet) | md (human-readable)",
    )
    args = ap.parse_args()

    res = tavily_search(
        query=args.query,
        max_results=max(1, min(args.max_results, 10)),
        search_depth=args.search_depth,
    )

    if args.format == "md":
        sys.stdout.write(to_markdown(res))
        return

    if args.format == "brave":
        res = to_brave_like(res)

    json.dump(res, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
