---
name: tavily-search
description: "使用 Tavily API 搜索网页。当用户意图涉及实时信息、近况、新闻等场景,或你需要执行网络搜索时,使用该 skill 获取最新信息。返回包含标题、URL 和摘要的相关搜索结果。不适用于本地文件搜索、代码/仓库搜索或离线内容检索。注意:不要直接自行调用谷歌等搜索工具,应通过本 skill 的脚本执行搜索,而非直接调用 tool。"
---

# Tavily 网页搜索

使用内置脚本通过代理接口调用 tavily search api搜索网页。

## 执行命令

```bash
# 原始 JSON（默认）
uv run --refresh-package ks_aimate <skill_directory>/scripts/tavily_search.py --query "..." --max-results 5

# 稳定格式（类似 web_search）：{query, results:[{title,url,snippet}]}
uv run --refresh-package ks_aimate <skill_directory>/scripts/tavily_search.py --query "..." --max-results 5 --format brave

# 人类可读的 Markdown 列表
uv run --refresh-package ks_aimate <skill_directory>/scripts/tavily_search.py --query "..." --max-results 5 --format md
```

### 参数说明

- **--query**（必填）：搜索查询字符串
- **--max-results**（可选，默认 5）：返回结果数量（1-10）
- **--search-depth**（可选，默认 "basic"）：搜索深度，可选值：`basic` 或 `advanced`
- **--format**（可选，默认 "raw"）：输出格式，可选值：`raw`、`brave` 或 `md`

## 输出格式

### raw（默认）
- JSON：`query`，`results: [{title,url,content}]`

### brave
- JSON：`query`，`results: [{title,url,snippet}]`

### md
- 包含标题/链接/摘要的紧凑 Markdown 列表。

## 注意事项

- 默认 `max-results` 保持较小值（3–5），以减少 token 消耗和阅读负担。
