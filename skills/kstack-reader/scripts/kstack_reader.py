#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "ks-aimate",
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

"""
KStack Article Reader - Fetch and search articles from KStack via OpenAPI
"""

import json
import os
import re
import sys
import argparse
from html.parser import HTMLParser
from ks_aimate.wanqing_token_username import get_username
from ks_aimate.sso_login_client.session import SmartSSOSession


class APIError(Exception):
    """API request error with friendly message."""
    pass

class MinimalArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

DEFAULT_APP_KEY = "a6711747-3f23-4099-912f-787a9e62bcbb"
BASE_URL = "https://myflicker.corp.kuaishou.com"
PROXY_PATH = "/api/v1/skills/exec/proxy"

GENERIC_ERROR_MESSAGE = "出了点问题，拿不到数据"

def get_openapi_host() -> str:
    """获取 OpenAPI 网关地址。"""
    return os.environ.get("OPENAPI_HOST", "openapi-gateway.internal")

def use_https() -> bool:
    """判断是否使用 HTTPS。"""
    host = get_openapi_host()
    return not host.endswith(".internal")

def get_base_url() -> str:
    """获取 API 基础 URL。"""
    protocol = "https" if use_https() else "http"
    return f"{protocol}://{get_openapi_host()}"

def get_article_content(article_id: str, username: str) -> dict:
    """获取文章详情。"""
    proxy_payload = {
        "url": f"{get_base_url()}/tech/open/api/article/detail?articleId={article_id}&username={username}",
        "method": "GET",
        "headers": {"Content-Type": "application/json", "ks-skill-proxy-apikey": DEFAULT_APP_KEY},
    }

    client = SmartSSOSession()
    try:
        resp = client.request("POST", f"{BASE_URL}{PROXY_PATH}", json=proxy_payload)
    except Exception as e:
        raise APIError(f"请求文章详情接口出错: {e}")

    try:
        data = resp.json()
    except Exception as e:
        raise APIError(f"解析文章详情接口响应失败: {e}")

    if data.get("code") in (0, "0"):
        return data.get("result", {})
    raise APIError(GENERIC_ERROR_MESSAGE)

def search_articles(keyword: str, username: str, page_size: int = 10) -> list:
    """搜索文章并过滤结果。"""
    proxy_payload = {
        "url": f"{get_base_url()}/tech/open/api/search/article/info?pageSize={page_size}&keyWord={keyword}&username={username}",
        "method": "GET",
        "headers": {"Content-Type": "application/json", "ks-skill-proxy-apikey": DEFAULT_APP_KEY},
    }

    client = SmartSSOSession()
    try:
        resp = client.request("POST", f"{BASE_URL}{PROXY_PATH}", json=proxy_payload)
    except Exception as e:
        raise APIError(f"请求搜索接口出错: {e}")

    try:
        data = resp.json()
    except Exception as e:
        raise APIError(f"解析搜索接口响应失败: {e}")

    if data.get("code") in (0, "0"):
        articles = data.get("result", {}).get("list", [])
        filtered_list = []
        for art in articles:
            filtered_list.append({
                "id": art.get("id"),
                "title": art.get("title"),
                "username": art.get("username"),
                "createTime": art.get("createTime"),
                "lastUpdateTime": art.get("lastUpdateTime"),
                "subTitle": art.get("subTitle"),
                "subContent": art.get("subContent"),
                "thumbUp": art.get("thumbUp"),
                "comment": art.get("comment"),
                "viewAmount": art.get("viewAmount")
            })
        return filtered_list
    raise APIError(GENERIC_ERROR_MESSAGE)


class HTMLToMarkdownParser(HTMLParser):
    """简单的 HTML 转 Markdown 转换器。"""
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_code = False
        self.in_pre = False
        self.in_list = False
        self.list_type = None
        self.list_count = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.result.append('\n' + '#' * level + ' ')
        elif tag == 'p':
            if self.result and not self.result[-1].endswith('\n'):
                self.result.append('\n\n')
        elif tag in ('br',):
            self.result.append('\n')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            self.in_code = True
            if not self.in_pre:
                self.result.append('`')
        elif tag == 'pre':
            self.in_pre = True
            self.result.append('\n```\n')
        elif tag == 'a':
            self.result.append('[')
            self.current_link = attrs_dict.get('href', '')
        elif tag == 'img':
            self.result.append(f"![{attrs_dict.get('alt', '')}]({attrs_dict.get('src', '')})")
        elif tag in ('ul', 'ol'):
            self.in_list = True
            self.list_type = tag
            self.list_count = 0
        elif tag == 'li':
            self.list_count += 1
            prefix = '\n- ' if self.list_type == 'ul' else f'\n{self.list_count}. '
            self.result.append(prefix)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'):
            self.result.append('\n')
        elif tag in ('strong', 'b'):
            self.result.append('**')
        elif tag in ('em', 'i'):
            self.result.append('*')
        elif tag == 'code':
            self.in_code = False
            if not self.in_pre: self.result.append('`')
        elif tag == 'pre':
            self.in_pre = False
            self.result.append('\n```\n')
        elif tag == 'a' and hasattr(self, 'current_link'):
            self.result.append(f']({self.current_link})')
            delattr(self, 'current_link')
        elif tag in ('ul', 'ol'):
            self.in_list = False
            self.result.append('\n')

    def handle_data(self, data):
        self.result.append(data if (self.in_pre or self.in_code) else data.replace('\r', ''))

    def get_markdown(self):
        text = ''.join(self.result)
        return re.sub(r'\n{3,}', '\n\n', text).strip()

def html_to_markdown(html: str) -> str:
    parser = HTMLToMarkdownParser()
    parser.feed(html)
    return parser.get_markdown() or html

def parse_kstack_url(url: str) -> str:
    if url.isdigit(): return url
    match = re.match(r"https?://kstack\.corp\.kuaishou\.com/article/(\d+)", url)
    if match: return match.group(1)
    raise APIError(GENERIC_ERROR_MESSAGE)

def format_article(article: dict) -> str:
    title = article.get("title", "Untitled")
    content = article.get("content", "")
    author = article.get("author", "Unknown")
    update_time = article.get("updateTime", "")
    if content and ("<" in content and ">" in content):
        content = html_to_markdown(content)
    result = [f"# {title}", "", f"**Author**: {author}"]
    if update_time: result.append(f"**Updated**: {update_time}")
    result.extend(["", "---", "", content])
    return "\n".join(result)

def main():
    parser = MinimalArgumentParser(add_help=False)
    parser.add_argument("article", nargs="?", help="KStack 文章 URL 或 ID")
    parser.add_argument("-s", "--search", help="搜索关键词")
    parser.add_argument("--page-size", type=int, default=10, help="搜索分页大小")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-u", "--username", help="用户名")

    try:
        args = parser.parse_args()
    except ValueError as exc:
        print(f"参数错误: {exc}", file=sys.stderr); sys.exit(1)

    username = args.username or get_username()
    if not username:
        print(GENERIC_ERROR_MESSAGE, file=sys.stderr); sys.exit(1)

    try:
        if args.search:
            results = search_articles(args.search, username, args.page_size)
            output = json.dumps(results, indent=2, ensure_ascii=False)
        elif args.article:
            article_id = parse_kstack_url(args.article)
            article = get_article_content(article_id, username)
            output = format_article(article)
        else:
            print("参数错误: 请提供文章 ID/URL 或使用 -s 搜索", file=sys.stderr); sys.exit(1)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(output)
        else:
            print(output)
    except APIError as e:
        print(f"错误: {e}", file=sys.stderr); sys.exit(1)
    except Exception as e:
        print(f"系统错误: {e}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()
