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
搜索微信公众号文章
用法: uv run search.py "关键词" [数量]
或: ./search.py "关键词" [数量]
"""

import sys
import os

def main():
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        print("用法: uv run <skill_directory>/scripts/search.py \"关键词\" [数量]")
        print("示例: uv run <skill_directory>/scripts/search.py \"绿电直连政策\" 10")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("用法: uv run <skill_directory>/scripts/search.py \"关键词\" [数量]")
        print("示例: uv run <skill_directory>/scripts/search.py \"绿电直连政策\" 10")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    try:
        from wechat_articles import search_articles, print_article_summary
    except ModuleNotFoundError as e:
        print(f"错误: 缺少运行依赖 {e.name}。请确认平台 Python 环境已预装本技能依赖。")
        sys.exit(1)
    
    query = sys.argv[1]
    try:
        top_num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    except ValueError:
        print("错误: 数量参数必须是整数")
        sys.exit(1)
    
    print(f"正在搜索: {query}")
    print("=" * 60)
    
    try:
        articles = search_articles(query, top_num)
    except Exception as e:
        print(f"搜索失败: {e}")
        sys.exit(1)
    
    if not articles:
        print("未找到相关文章")
        return
    
    print(f"找到 {len(articles)} 篇文章:\n")
    
    for i, article in enumerate(articles, 1):
        print(f"【{i}】")
        print_article_summary(article)


if __name__ == "__main__":
    main()
