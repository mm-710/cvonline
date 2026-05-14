from __future__ import annotations

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests",
# ]
# ///
"""
微信公众号文章读取模块 - Tavily API 版本
使用 Tavily Extract API 通过住宅 IP 池提取微信文章内容，绕过微信反爬。

依赖：需要 Tavily API Key（免费额度 1000次/月，注册 https://tavily.com/）
"""

import os
import json
import requests


TAVILY_EXTRACT_URL = "https://api.tavily.com/extract"


def read_article_tavily(url, api_key=None):
    """
    使用 Tavily Extract API 读取微信公众号文章内容。

    Tavily 使用住宅 IP 池，模拟真实用户访问，可绕过微信对数据中心 IP 的反爬限制。

    Args:
        url (str): 微信文章URL
        api_key (str, optional): Tavily API Key。不传则从环境变量 TAVILY_API_KEY 读取

    Returns:
        dict: 包含 title, author, paragraphs, mode 的字典
    """
    api_key = api_key or os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        raise Exception(
            "未提供 Tavily API Key。\n"
            "  方式一: 传入 --tavily-api-key 参数\n"
            "  方式二: 设置环境变量 TAVILY_API_KEY\n"
            "  免费注册: https://tavily.com/"
        )

    payload = {
        "urls": [url],
        "include_images": False,
        "extract_depth": "basic",
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = requests.post(TAVILY_EXTRACT_URL, json=payload, headers=headers, timeout=30)

        if resp.status_code == 401:
            raise Exception("Tavily API Key 无效或已过期，请检查后重试。")
        if resp.status_code == 429:
            raise Exception("Tavily API 本月免费额度已用完（1000次/月），请等下月或升级付费计划。")
        if resp.status_code != 200:
            raise Exception(f"Tavily API 返回错误，状态码: {resp.status_code}")

        try:
            data = resp.json()
        except (ValueError, json.decoder.JSONDecodeError) as e:
            raise Exception(f"Tavily API 返回数据格式异常，无法解析 JSON: {e}")

        results = data.get("results", [])
        failed = data.get("failed_results", [])

        if failed and not results:
            raise Exception(f"Tavily 无法提取此文章: {failed[0].get('error', '未知错误')}")

        if not results:
            raise Exception("Tavily API 未返回任何内容。")

        article = results[0]
        raw_content = article.get("raw_content", "")
        title = article.get("title", "N/A")

        # 将原始内容按换行拆分为段落，过滤空行
        paragraphs = []
        for line in raw_content.split("\n"):
            stripped = line.strip()
            if len(stripped) > 5:
                paragraphs.append(stripped)

        if not paragraphs:
            raise Exception("Tavily 返回的内容为空，文章可能已被删除或需要特殊权限。")

        return {
            "title": title,
            "author": "通过 Tavily 提取（无公众号信息）",
            "paragraphs": paragraphs,
            "mode": "tavily",
        }

    except requests.exceptions.Timeout:
        raise Exception("Tavily API 请求超时，请稍后重试。")
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接 Tavily API，请检查网络。")