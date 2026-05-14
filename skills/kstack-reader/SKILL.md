---
name: kstack-reader
description: 读取或搜索快手内网 KStack 技术文章。当用户说「帮我看 KStack 上的某篇文章」「搜索内网技术文档」「查KStack」或提供 KStack 文章链接时触发。不负责非 KStack 内容的部分。
---

# KStack Article Reader

读取 KStack 文章并渲染成 Markdown，或根据关键词搜索文章列表。

## 接入前提

- Python 环境（推荐使用 [uv](https://github.com/astral-sh/uv) 运行）

## 基本使用

本脚本已适配 `uv` 自运行格式，包含 `requests` 依赖。

### 读取文章内容

```bash
# 读取文章（通过 ID 或链接）
uv run <skill_directory>/scripts/kstack_reader.py 13970
uv run <skill_directory>/scripts/kstack_reader.py https://kstack.corp.kuaishou.com/article/13970

# 保存到文件
uv run <skill_directory>/scripts/kstack_reader.py 13970 -o article.md
```

### 搜索文章

搜索结果将以 JSON 格式返回，已过滤掉正文等冗余字段。

```bash
# 搜索关键词
uv run "$KSTACK_READER_PY" -s "AI"

# 指定分页大小
uv run "$KSTACK_READER_PY" -s "AI" --page-size 5
```

## 错误处理

若无法获取数据，将报错：`出了点问题，拿不到数据`。
