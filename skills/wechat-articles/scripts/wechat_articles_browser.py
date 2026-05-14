from __future__ import annotations

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "beautifulsoup4",
# ]
# ///
"""
微信公众号文章读取模块 - agent-browser 版本
使用 agent-browser CLI 通过子进程调用实现浏览器渲染读取。
依赖：运行环境需要提供 agent-browser 命令。
"""

import subprocess
import json
import time
import sys
from bs4 import BeautifulSoup


def _run_agent_browser(*args, timeout=30):
    """
    执行 agent-browser CLI 命令并返回输出
    
    Args:
        *args: agent-browser 子命令和参数
        timeout (int): 超时秒数
    
    Returns:
        str: 命令标准输出
    
    Raises:
        Exception: 命令执行失败时
    """
    cmd = ["agent-browser"] + list(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0:
            raise Exception(f"agent-browser 命令失败: {' '.join(cmd)}\nstderr: {result.stderr}")
        return result.stdout
    except FileNotFoundError:
        raise Exception("未找到 agent-browser 命令。请确认运行环境已启用该浏览器工具。")
    except subprocess.TimeoutExpired:
        raise Exception(f"agent-browser 命令超时 ({timeout}s): {' '.join(cmd)}")
    except OSError as e:
        raise Exception(f"agent-browser 执行异常（系统错误）: {e}")


def _parse_eval_output(raw_output):
    """
    解析 agent-browser eval 命令的输出。
    eval 返回的是 JSON 格式字符串（带引号），需要 json.loads 还原。
    """
    raw_output = raw_output.strip()
    if raw_output.startswith('"') and raw_output.endswith('"'):
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return raw_output[1:-1]
    return raw_output


def _diagnose_page(soup):
    """
    诊断页面状态，区分风控、链接过期、JS未渲染等情况。
    
    Returns:
        str: 诊断消息，None 表示页面正常
    """
    page_text = soup.get_text()
    
    # 检查常见的微信风控/错误页面
    if "请在微信客户端打开链接" in page_text:
        return "微信要求在客户端打开此链接，浏览器可能被风控。"
    
    if "链接已过期" in page_text or "该内容已被发布者删除" in page_text:
        return "文章链接已过期或已被删除。"
    
    if "此内容因违规无法查看" in page_text:
        return "文章因违规已被微信屏蔽。"
    
    if "环境异常" in page_text or "操作频繁" in page_text:
        return "微信检测到环境异常或操作频繁，触发了反爬机制。"
    
    if "验证" in page_text and len(page_text) < 500:
        return "页面可能是验证码/安全验证页面，非文章内容。"
    
    # 检查是否是空白页面
    body = soup.find('body')
    if body and len(body.get_text().strip()) < 50:
        return "页面内容几乎为空，可能 JS 未渲染完成或被拦截。"
    
    return None


def read_article_browser(url, screenshot_path=None):
    """
    使用 agent-browser CLI 读取微信公众号文章内容
    
    流程：
    1. agent-browser open <url> —— 打开页面（模拟移动端 UA）
    2. agent-browser wait "#js_content" —— 显式等待正文元素出现
    3. agent-browser eval <js> —— 获取渲染后的完整 HTML
    4. BeautifulSoup 解析提取结构化内容
    5. agent-browser close —— 关闭浏览器
    
    Args:
        url (str): 微信文章URL
        screenshot_path (str, optional): 截图保存路径
    
    Returns:
        dict: 包含 title, author, paragraphs, mode 的字典
    """
    # 简化URL
    simple_url = url.split("&new=1")[0] if "&new=1" in url else url
    
    # 设置移动端 UA 模拟
    iphone_ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.0 Mobile/15E148 Safari/604.1"
    )
    
    try:
        # 1. 打开页面（设置 UA 模拟移动端）
        _run_agent_browser(
            "--user-agent", iphone_ua,
            "open", simple_url,
            timeout=60
        )
        
        # 2. 等待正文区域出现（最关键的改进：不仅等 networkidle，还要显式等待 #js_content）
        #    先等 DOM 基本加载
        _run_agent_browser("wait", "--load", "domcontentloaded", timeout=30)
        
        #    再显式等待微信正文容器出现（最多等 15 秒）
        try:
            _run_agent_browser("wait", "#js_content", timeout=15)
        except Exception:
            # #js_content 未出现，尝试额外等一下 networkidle 后再检查
            print("⏳ #js_content 未立即出现，等待 networkidle...", file=sys.stderr)
            try:
                _run_agent_browser("wait", "--load", "networkidle", timeout=15)
            except Exception:
                pass
            # 再等 2 秒给 JS 渲染缓冲时间
            time.sleep(2)
        
        # 3. 如果需要截图
        if screenshot_path:
            _run_agent_browser("screenshot", "--full", screenshot_path, timeout=15)
        
        # 4. 获取渲染后的完整 HTML
        html_content = _run_agent_browser(
            "eval", "document.documentElement.outerHTML",
            timeout=15
        )
        html_content = _parse_eval_output(html_content)
        
        # 5. 用 BeautifulSoup 解析
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题
        title_elem = soup.find('h1', {'class': 'rich_media_title'})
        title = title_elem.get_text().strip() if title_elem else "N/A"
        
        # 提取公众号
        author_elem = soup.find('a', {'id': 'js_name'})
        author = author_elem.get_text().strip() if author_elem else "N/A"
        
        # 提取正文
        content_div = soup.find('div', {'id': 'js_content'})
        if not content_div:
            # 正文不存在 —— 诊断原因
            diagnosis = _diagnose_page(soup)
            if diagnosis:
                raise Exception(f"未找到正文内容。诊断: {diagnosis}")
            else:
                # 获取页面标题和部分文本帮助调试
                page_title = soup.find('title')
                page_title_text = page_title.get_text().strip() if page_title else "无标题"
                page_text_preview = soup.get_text()[:200].strip()
                raise Exception(
                    f"未找到正文内容（#js_content 不存在）。\n"
                    f"  页面标题: {page_title_text}\n"
                    f"  页面内容预览: {page_text_preview}"
                )
        
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
        
        # 如果段落为空但正文 div 存在，尝试直接提取文本
        if not valid_paragraphs:
            raw_text = content_div.get_text().strip()
            if raw_text:
                # 按换行分段
                valid_paragraphs = [
                    line.strip() for line in raw_text.split('\n')
                    if len(line.strip()) > 5
                ]
        
        if not valid_paragraphs:
            raise Exception("正文区域存在但内容为空，可能 JS 渲染未完成或文章内容为纯图片。")
        
        return {
            "title": title,
            "author": author,
            "paragraphs": valid_paragraphs,
            "mode": "browser"
        }
        
    finally:
        # 6. 确保关闭浏览器（即使出错也要清理）
        try:
            _run_agent_browser("close", timeout=10)
        except Exception:
            pass


def print_article_content(content, max_paragraphs=50):
    """
    打印文章内容
    """
    print("=" * 80)
    print(f"标题: {content['title']}")
    print(f"公众号: {content['author']}")
    print(f"模式: {content.get('mode', 'unknown')}")
    print("=" * 80)
    print()
    
    for i, p in enumerate(content['paragraphs'][:max_paragraphs]):
        print(p)
        print()
    
    if len(content['paragraphs']) > max_paragraphs:
        print(f"... (还有 {len(content['paragraphs']) - max_paragraphs} 段)")
