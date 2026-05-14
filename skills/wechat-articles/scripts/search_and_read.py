#!/usr/bin/env -S uv run
from __future__ import annotations
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "beautifulsoup4",
#     "requests",
#     "miku-ai",
# ]
# ///
"""
搜索并读取微信公众号文章
用法: uv run search_and_read.py "关键词" [数量] [--mode MODE]
或: ./search_and_read.py "关键词" [数量] [--mode MODE]
模式: simple|browser|auto (默认auto)
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="搜索并读取微信公众号文章")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("num", nargs="?", type=int, default=3, 
                        help="返回文章数量 (默认: 3)")
    parser.add_argument("--mode", "-m", default="auto",
                        choices=["simple", "browser", "tavily", "auto"],
                        help="读取模式 (默认: auto)")
    parser.add_argument("--max-paragraphs", "-n", type=int, default=30,
                        help="每篇文章显示的最大段落数 (默认: 30)")
    parser.add_argument("--no-read", action="store_true",
                        help="只搜索不读取文章内容")
    parser.add_argument("--tavily-api-key", help="Tavily API Key（tavily/auto 模式使用）")
    
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    try:
        from wechat_articles import (
            search_articles,
            read_article,
            print_article_summary,
            print_article_content,
        )
    except ModuleNotFoundError as e:
        print(f"错误: 缺少运行依赖 {e.name}。请确认平台 Python 环境已预装本技能依赖。")
        sys.exit(1)
    
    print(f"正在搜索: {args.query}")
    print("=" * 80)
    
    articles = search_articles(args.query, args.num)
    
    if not articles:
        print("未找到相关文章")
        return
    
    print(f"找到 {len(articles)} 篇文章")
    
    if args.no_read:
        print("\n文章列表:")
        print("=" * 80)
        for i, article in enumerate(articles, 1):
            print(f"\n【{i}】")
            print_article_summary(article)
        return
    
    print(f"开始读取内容 (模式: {args.mode})...\n")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{'='*80}")
        print(f"【第 {i} 篇】")
        print(f"{'='*80}")
        print_article_summary(article)
        
        try:
            print(f"\n正在读取全文...")
            content = read_article(article['url'], mode=args.mode, tavily_api_key=args.tavily_api_key)
            print_article_content(content, max_paragraphs=args.max_paragraphs)
        except Exception as e:
            print(f"读取失败: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
