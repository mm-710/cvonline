---
name: wechat-articles
description: >
  提供微信公众号文章搜索与读取功能，支持关键词搜索与全文提取。以下场景唤醒此 skill：用户搜索公众号文章、按关键词查找微信内容、读取/摘要/分析/翻译 mp.weixin.qq.com 链接的内容、用户说"帮我找公众号文章"、"读这篇微信文章"、"搜索公众号"、"抓取公众号"、用户粘贴了微信文章 URL 并要求提取或处理内容、需要从微信公众号获取资讯/报告/行业信息。以下场景不唤醒：非微信公众号内容查询、纯图片或视频下载请求、与公众号文章无关的信息检索、用户仅问微信使用方法。
---

# 微信公众号文章搜索与读取 (v2.1)

搜索和读取微信公众号文章的完整工具，支持 **simple**（快速） / **browser**（渲染） / **tavily**（住宅 IP） 三模式 + **auto** 智能降级。

> **v2.1 变更**：新增 Tavily API 模式，利用住宅 IP 池绕过微信反爬；auto 模式降级链优化为 simple → browser → tavily → 提示用户粘贴。

## 快速开始

### 搜索文章
```bash
uv run <skill_directory>/scripts/search.py "关键词" [数量]
```
示例：
```bash
uv run <skill_directory>/scripts/search.py "绿电直连政策" 10
```

### 读取文章
```bash
uv run <skill_directory>/scripts/read.py "微信文章URL" [--mode MODE] [--screenshot PATH] [--tavily-api-key KEY]
```
模式选择：
- `--mode=simple` - 快速模式（requests + BeautifulSoup）
- `--mode=browser` - 渲染模式（agent-browser CLI，真实浏览器渲染）
- `--mode=tavily` - 住宅 IP 模式（Tavily API，绕过微信反爬，**推荐**）
- `--mode=auto` - 智能降级（默认，推荐）

Tavily API Key 可选通过 `--tavily-api-key` 传入或设置环境变量 `TAVILY_API_KEY`。免费额度 1000 次/月，注册 https://tavily.com/。

### 搜索+读取一体
```bash
uv run <skill_directory>/scripts/search_and_read.py "关键词" [数量] [--mode MODE]
```

## Python API 使用（推荐）

```python
import sys
sys.path.append('<skill_directory>/scripts')  # 使用实际的 skill 目录路径

from wechat_articles import search_articles, read_article

# 搜索文章
articles = search_articles("绿电直连政策", top_num=5)

# 读取文章（建议加错误处理）
try:
    content = read_article(articles[0]['url'], mode='auto', tavily_api_key='tvly-dev-xxx')
    print(f"标题: {content['title']}")
    print(f"公众号: {content['author']}")
    print(f"发布时间: {content['publish_time']}")  # 若有
    print(f"读取模式: {content['mode']}")
    for p in content['paragraphs'][:10]:
        print(p)
except Exception as e:
    print(f"读取失败: {e}")
```

### 返回数据结构说明

`read_article()` 返回一个字典，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | str | 文章标题 |
| `author` | str | 公众号名称（tavily 模式下为提示信息） |
| `publish_time` | str | 发布时间（部分文章可能为空） |
| `paragraphs` | list[str] | 正文段落列表 |
| `mode` | str | 实际使用的读取模式（`simple` / `browser` / `tavily`） |

`search_articles()` 返回列表，每项包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | str | 文章标题 |
| `url` | str | 文章链接（有时效性，建议尽快读取） |
| `author` | str | 公众号名称 |
| `digest` | str | 文章摘要 |

## 模式对比

| 模式 | 速度 | 绕过反爬 | 资源 | 适用场景 |
|------|------|----------|------|----------|
| simple | 快 (0.5-1s) | ❌ 数据中心 IP | 轻量 | 简单页面，频繁调用 |
| browser | 慢 (3-8s) | ❌ 数据中心 IP | 较重 | 复杂页面，需 JS 渲染 |
| tavily | 中 (1-3s) | ✅ 住宅 IP 池 | 轻量 | **微信反爬场景首选** |
| auto | 自适应 | ✅ 三级降级 | 自适应 | 默认推荐 |

## auto 智能降级链

微信对数据中心 IP 有反爬保护。auto 模式依次尝试：

```
simple ──失败──▶ browser ──失败──▶ tavily ──失败──▶ 提示用户粘贴内容
```

这种设计确保：即使前两种本地方式被微信拦截，Tavily 的住宅 IP 仍能成功提取。如果三层都失败，会提示用户手动复制粘贴文章内容作为最终兜底方案。

## 运行依赖

平台提供 `uv`，首次运行时会按脚本 PEP 723 声明安装 Python 依赖：
```bash
# 直接运行即可，Python 依赖自动处理
uv run <skill_directory>/scripts/search.py "关键词"
```

Browser 模式需要运行环境提供 `agent-browser` 命令。Tavily 模式需要 Tavily API Key（免费注册 https://tavily.com/）。

## 技术实现说明

### browser 模式工作流程

`wechat_articles_browser.py` 通过 subprocess 调用 agent-browser CLI 实现浏览器渲染读取：

```
1. agent-browser --user-agent <iPhone_UA> open <url>   # 打开页面（模拟移动端）
2. agent-browser wait --load domcontentloaded           # 等待 DOM 加载
3. agent-browser wait "#js_content"                     # 显式等待正文区域出现
4. agent-browser eval "document.documentElement.outerHTML"  # 获取完整 HTML
5. BeautifulSoup 解析提取：标题、作者、正文段落
6. agent-browser close                                  # 关闭浏览器
```

### tavily 模式工作流程

`wechat_articles_tavily.py` 调用 Tavily Extract API：

```
1. POST https://api.tavily.com/extract { urls: [url] }  # 通过住宅 IP 提取
2. 解析返回的 raw_content → 按换行拆分为段落
3. 返回结构化结果
```

**关键设计**：Tavily 使用住宅 IP 池，对微信呈现为真实用户访问，能稳定绕过反爬机制。获取的是**原文**，不经过任何 AI 改写。

## 注意事项

- 搜索结果 URL 有时效性，建议尽快读取
- 避免高频请求防止触发反爬
- Tavily 免费额度 1000 次/月，对个人用户完全够用
- Tavily API Key 建议通过环境变量 `TAVILY_API_KEY` 设置，避免每次传参
- auto 模式三层降级确保最高成功率，极端情况下提示用户粘贴为最终兜底
- 转载文章注意版权，最好获得原作者授权

欢迎反馈 & PR！GitHub: https://github.com/johan-oilman/wechat-articles
