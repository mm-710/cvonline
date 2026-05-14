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
微信公众号文章搜索与读取模块
提供搜索和读取微信公众号文章的功能，支持 simple 模式和 agent-browser 模式
"""

import asyncio
import requests
from bs4 import BeautifulSoup


def search_articles(query, top_num=5):
    """
    搜索微信公众号文章
    
    Args:
        query (str): 搜索关键词
        top_num (int): 返回结果数量，默认5篇
    
    Returns:
        list: 文章列表，每篇包含 title、url、source、date、snippet
        
    Raises:
        Exception: 搜索失败或返回异常时
    """
    if not query or not query.strip():
        raise ValueError("搜索关键词不能为空")
    
    try:
        import miku_ai.spider
    except ImportError:
        raise Exception("缺少 miku-ai 依赖，无法搜索公众号文章。请确认平台已预装该依赖。")
    
    try:
        articles = asyncio.run(miku_ai.spider.get_wexin_article(query, top_num))
    except Exception as e:
        raise Exception(f"搜索公众号文章失败: {e}")
    
    if articles is None:
        raise Exception("搜索接口返回为空，请稍后重试。")
    
    if not isinstance(articles, list):
        raise Exception(f"搜索接口返回格式异常（期望列表，实际 {type(articles).__name__}），请稍后重试。")
    
    # 过滤无效条目（缺少 url 的条目无法读取）
    valid_articles = []
    for a in articles:
        if isinstance(a, dict) and a.get("url"):
            valid_articles.append(a)
    
    return valid_articles


def read_article_simple(url):
    """
    使用简单模式读取微信公众号文章内容（requests + BeautifulSoup）
    
    Args:
        url (str): 微信文章URL
    
    Returns:
        dict: 包含 title, author, paragraphs 的字典
    """
    # 简化URL
    simple_url = url.split("&new=1")[0] if "&new=1" in url else url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        response = requests.get(simple_url, headers=headers, timeout=30, allow_redirects=True)
    except requests.exceptions.Timeout:
        raise Exception("请求超时，微信服务器响应过慢，请稍后重试。")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接微信服务器，请检查网络连接。")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {e}")
    
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码: {response.status_code}")
    
    # 解析HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 提取标题
    title_elem = soup.find('h1', {'class': 'rich_media_title'})
    title = title_elem.get_text().strip() if title_elem else "N/A"
    
    # 提取公众号
    author_elem = soup.find('a', {'id': 'js_name'})
    author = author_elem.get_text().strip() if author_elem else "N/A"
    
    # 提取正文
    content_div = soup.find('div', {'id': 'js_content'})
    if not content_div:
        raise Exception("未找到正文内容")
    
    # 移除脚本和样式
    for script in content_div.find_all(['script', 'style']):
        script.decompose()
    
    # 提取段落
    paragraphs = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
    valid_paragraphs = []
    
    for p in paragraphs:
        text = p.get_text().strip()
        if len(text) > 5:
            valid_paragraphs.append(text)
    
    if not valid_paragraphs:
        raise Exception("文章中未提取到有效段落（内容可能为纯图片或空文档）。")
    
    return {
        "title": title,
        "author": author,
        "paragraphs": valid_paragraphs,
        "mode": "simple"
    }


def read_article(url, mode="auto", screenshot_path=None, tavily_api_key=None):
    """
    读取微信公众号文章内容（支持多种模式）

    Args:
        url (str): 微信文章URL
        mode (str): 读取模式 - "simple" | "browser" | "tavily" | "auto"
        screenshot_path (str, optional): browser 模式下的截图保存路径
        tavily_api_key (str, optional): Tavily API Key（tavily/auto 模式使用）

    Returns:
        dict: 包含 title, author, paragraphs, mode 的字典
    """
    if mode == "simple":
        return read_article_simple(url)

    elif mode == "browser":
        from wechat_articles_browser import read_article_browser
        return read_article_browser(url, screenshot_path)

    elif mode == "tavily":
        from wechat_articles_tavily import read_article_tavily
        return read_article_tavily(url, api_key=tavily_api_key)

    elif mode == "auto":
        # 自动降级链：simple → browser → tavily → paste（提示用户粘贴）
        # 微信对数据中心 IP 有反爬保护，逐步切换更可靠的方式
        errors = []

        # 第一层：simple（最快，直接 HTTP 请求）
        try:
            return read_article_simple(url)
        except Exception as e:
            msg = f"simple 模式失败: {e}"
            errors.append(msg)
            print(msg)

        # 第二层：agent-browser（真实浏览器渲染，但仍可能被 IP 反爬拦截）
        try:
            print("降级到 agent-browser 模式...")
            from wechat_articles_browser import read_article_browser
            return read_article_browser(url, screenshot_path)
        except Exception as e:
            msg = f"browser 模式失败: {e}"
            errors.append(msg)
            print(msg)

        # 第三层：Tavily API（住宅 IP 池，绕过反爬）
        try:
            print("降级到 Tavily API 模式（住宅 IP 提取）...")
            from wechat_articles_tavily import read_article_tavily
            return read_article_tavily(url, api_key=tavily_api_key)
        except Exception as e:
            msg = f"tavily 模式失败: {e}"
            errors.append(msg)
            print(msg)

        # 全部失败 → 提示用户粘贴内容
        raise Exception(
            "所有提取方式均失败:\n  "
            + "\n  ".join(errors)
            + "\n\n💡 兜底方案: 请在微信中打开文章 → 全选复制内容 → 直接粘贴给我，我来整理成 Markdown。"
        )

    else:
        raise ValueError(f"未知模式: {mode}，可选值: simple, browser, tavily, auto")


def print_article_summary(article):
    """
    打印文章摘要（搜索结果）
    """
    print(f"标题: {article.get('title', 'N/A')}")
    print(f"来源: {article.get('source', article.get('author', 'N/A'))}")
    print(f"日期: {article.get('date', 'N/A')}")
    print(f"链接: {article.get('url', 'N/A')}")
    snippet = article.get('snippet', article.get('digest', ''))
    if snippet:
        print(f"摘要: {snippet[:100]}...")
    print("-" * 60)


def print_article_content(content, max_paragraphs=50):
    """
    打印文章内容
    """
    print("=" * 80)
    print(f"标题: {content.get('title', 'N/A')}")
    print(f"公众号: {content.get('author', 'N/A')}")
    print(f"模式: {content.get('mode', 'unknown')}")
    print("=" * 80)
    print()
    
    paragraphs = content.get('paragraphs', [])
    if not paragraphs:
        print("（无正文内容）")
        return
    
    for i, p in enumerate(paragraphs[:max_paragraphs]):
        print(p)
        if i < len(paragraphs[:max_paragraphs]) - 1:
            print()
    
    if len(paragraphs) > max_paragraphs:
        print(f"\n... (还有 {len(paragraphs) - max_paragraphs} 段)")
