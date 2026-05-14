#!/usr/bin/env -S uv run
from __future__ import annotations
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "beautifulsoup4",
#     "requests",
# ]
# ///
"""
读取微信公众号文章
用法: uv run read.py "微信文章URL" [--mode MODE] [--screenshot PATH]
或: ./read.py "微信文章URL" [--mode MODE] [--screenshot PATH]
模式: simple|browser|auto (默认auto)
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="读取微信公众号文章")
    parser.add_argument("url", help="微信文章URL")
    parser.add_argument("--mode", "-m", default="auto",
                        choices=["simple", "browser", "tavily", "auto"],
                        help="读取模式 (默认: auto)")
    parser.add_argument("--screenshot", "-s", help="browser 模式下截图保存路径")
    parser.add_argument("--tavily-api-key", help="Tavily API Key（tavily/auto 模式使用，也可通过环境变量 TAVILY_API_KEY 设置）")
    parser.add_argument("--max-paragraphs", "-n", type=int, default=50,
                        help="显示的最大段落数 (默认: 50)")
    
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    try:
        from wechat_articles import read_article, print_article_content
    except ModuleNotFoundError as e:
        print(f"错误: 缺少运行依赖 {e.name}。请确认平台 Python 环境已预装本技能依赖。")
        sys.exit(1)
    
    print(f"正在读取文章...")
    print(f"URL: {args.url[:80]}...")
    print(f"模式: {args.mode}")
    if args.screenshot:
        print(f"截图: {args.screenshot}")
    print()
    
    try:
        content = read_article(args.url, mode=args.mode, screenshot_path=args.screenshot, tavily_api_key=args.tavily_api_key)
        print_article_content(content, max_paragraphs=args.max_paragraphs)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
