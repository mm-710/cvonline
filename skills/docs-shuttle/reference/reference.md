# docs-shuttle 详细参考文档

完整的使用说明、API 参考、故障排查指南。

---

## 📋 目录

- [统一入口 docs.py](#统一入口-docspy)
- [所有操作详解](#所有操作详解)
  - [搜索文档](#搜索文档-search)
  - [上传/编辑文档](#上传编辑文档-push)
  - [拉取文档](#拉取文档-pull)
  - [下载文档](#下载文档-download)
  - [评论管理](#评论管理-comment)
  - [权限申请](#权限申请-request_permission)
  - [普通表格操作](#普通表格操作-sheet)
  - [普通表格 Mention 提取](#普通表格-mention-提取-mentions)
  - [万维表格操作](#万维表格操作-metasheet)
- [常见问题](#常见问题)
- [故障排查](#故障排查)

---

## 统一入口 docs.py

### URL 判断规则

`docs.py` 通过 URL **路径前缀直接判断文档类型**，零延迟，无 API 查询。

| URL 前缀 | 类型 |
|---------|------|
| `/d/home/` `/k/home/` | 普通文档 |
| `/s/home/` `/t/home/` | 普通表格 |
| `/m/home/` `/b/home/` | 万维表格 |

传入不匹配的 URL 类型会直接报错。

### 基本用法

```bash
# 通用语法
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py <operation> [url] [args...]

# 查看所有操作
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py help
```

### 支持的操作

| 操作 | 说明 | 适用类型 | 路由到 |
|------|------|---------|-------|
| `search` | 搜索文档 | 全部类型 | search.py |
| `push` | 上传/编辑 | 仅普通文档 | push.py |
| `pull` | 拉取文档 | 仅普通文档 | pull.py |
| `comment` | 评论管理 | 仅普通文档 | comment.py |
| `download` | 下载导出 | 全部类型 | download.py |
| `request_permission` | 申请权限 | 全部类型 | request_permission.py |
| `read` | 读取普通表格 | 仅普通表格 | sheet.py |
| `write` | 写入普通表格 | 仅普通表格 | sheet.py |
| `append` | 追加普通表格 | 仅普通表格 | sheet.py |
| `create` | 创建普通表格 | 仅普通表格 | sheet.py |
| `mentions` | 提取普通表格中的 @mention 用户 | 仅普通表格 | mention_extract.py |
| `meta` | 万维表格结构 | 仅万维表格 | metasheet.py |
| `content` | 读取万维表格记录 | 仅万维表格 | metasheet.py |
| `add-record` | 新增记录 | 仅万维表格 | metasheet.py |
| `update-record` | 更新记录 | 仅万维表格 | metasheet.py |
| `delete-record` | 删除记录 | 仅万维表格 | metasheet.py |

---

## 所有操作详解

### 搜索文档 (search)

搜索内部文档系统。

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search <keyword> [--page N] [--size N] [--json]
```

**示例**：
```bash
# 基本搜索
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search "API 设计"

# 分页
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search "test" --page 2 --size 50

# JSON 输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search "文档" --json
```

---

### 上传/编辑文档 (push)

上传新文档或编辑已有文档。

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push <file> [--mode edit] [--doc-id <id>] [--position <pos>]
```

**模式**：
- `import`（默认）：创建新文档
- `edit`：编辑已有文档（需要 --doc-id）

**编辑位置**：
- `REPLACE_ALL`（默认）：全文替换
- `APPEND_TAIL`：追加到末尾
- `APPEND_HEAD`：追加到开头

**示例**：
```bash
# 创建新文档
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push design.md

# 全文替换
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push design.md --mode edit --doc-id fcABxxx

# 追加到末尾
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push changelog.md --mode edit --doc-id fcABxxx --position APPEND_TAIL
```

**为什么用编辑模式？**

| 对比项 | 编辑模式 | 创建新文档 |
|-------|---------|-----------|
| 文档 ID | ✅ 保留 | ❌ 生成新 ID |
| URL | ✅ 不变 | ❌ 新 URL |
| 权限/分享 | ✅ 保留 | ❌ 需重新设置 |
| 评论 | ✅ 保留 | ❌ 丢失 |

---

### 拉取文档 (pull)

从 Docs 下载文档到本地 Markdown，自动下载图片。

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> [-o <file>] [--no-images]
```

**示例**：
```bash
# 自动命名
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url>

# 指定输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> -o design.md

# 不下载图片
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> --no-images
```

**文件结构**：
```
文档名.md              # 主文档
文档名/images/         # 图片目录
  ├── image-xxx.png
  └── image-yyy.jpg
```

---

### 下载文档 (download)

导出文档/表格为本地文件，自动识别类型。

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> [--format <fmt>] [-o <file>]
```

**支持格式**：

| 类型 | 默认格式 | 可选格式 |
|------|---------|---------|
| 普通文档 | docx | pdf |
| 普通表格 | xlsx | - |
| 万维表格 | xlsx | - |

**示例**：
```bash
# 自动检测并下载（包括团队 URL）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url>

# 指定格式
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> --format pdf

# 指定输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> -o output.docx
```

**流程**：
1. 检测文档类型
2. 检查下载权限
3. 触发导出任务
4. 轮询任务状态
5. 下载文件

---

### 评论管理 (comment)

查看或添加文档评论。

⚠️ **重要限制**：评论功能**仅支持普通文档**（`/d/home/` 或 `/k/home/`）  
- ❌ 不支持普通表格（`/s/home/`）
- ❌ 不支持万维表格（`/m/home/`）

**子命令**：
- `list` - 查看评论列表
- `add` - 添加新评论

**参数**：
```bash
# 查看未解决评论（默认）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment list <url> [--count N]

# ⭐ 查看已解决评论（需要 --solved 参数）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment list <url> --solved [--count N]

# 添加评论
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment add <url> <text>
```

**示例**：
```bash
# 查看未解决评论
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment list <doc-url>

# ⭐ 查看已解决评论（记得加 --solved）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment list <doc-url> --solved

# 添加评论
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment add <doc-url> "这是一条评论"
```

**💡 提示**：默认只显示未解决评论。要查看已解决评论，必须加 `--solved` 参数。

---

### 权限申请 (request_permission)

通过 API 直接申请文档权限。

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py request_permission <url> \
  [--permission-type <type>] \
  [--reason <text>]
```

**权限类型**：

| 类型 | 说明 | 推荐场景 |
|------|------|---------|
| `read` | 只读 | 查看文档 |
| `comment` | 可评论（默认） | 提供反馈 |
| `edit` | 可编辑 | 协作编辑 |
| `manage` | 可管理 | 管理协作者 |

**示例**：
```bash
# 申请评论权限（默认）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py request_permission <url>

# 申请编辑权限
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py request_permission <url> \
  --permission-type edit \
  --reason "需要协作编辑"
```

---

### 普通表格 Mention 提取 (mentions)

从普通表格 `/s/home/` 或 `/t/home/` 中提取 `@mention` 用户信息，返回：

- `username`
- `displayName`
- `enName`
- `userId`

⚠️ 这个能力和 `read` 不同：
- `read` 读取的是表格可见值
- `mentions` 优先读取 snapshot 富文本中的 mention 元信息
- 如果 snapshot 无法获取 revision、数据不可用、或未提取到结构化 mention，会自动尝试 SSR HTML 兜底
- 当用户在分析普通表格内容时，即使没有明确要求 username，也建议额外 best-effort 执行一次 `mentions`
- 提取 `username` / `userId` 时必须以 snapshot 里的 `<a class="cell-mention">` 属性为准，不能把 `read` 中看到的 `@名字` 当作提取成功
- 如果深挖后仍未提取到结构化 mention 信息，应该如实说明“snapshot 未提取成功”或“未发现结构化 mention”，而不是用可见文本替代 username
- SSR 兜底仅覆盖首屏可见区域，所以如果返回结果带有相关提示，应视为“可能不完整”

**参数**：
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> \
  [--format json|csv|text] [--revision <rev>] [--best-effort]
```

**示例**：
```bash
# 默认 JSON 输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url>

# 文本输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> --format text

# 作为读取增强，失败也不中断主流程
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> --best-effort
```

**输出示例**：
```json
{
  "doc_id": "fcAAxZM3iLK-CS42OHRCKqd-Q",
  "sheet_id": "397576121",
  "snapshot_revision": "3095",
  "total": 2,
  "users": [
    {
      "username": "wangxu14",
      "displayName": "王诩",
      "enName": "Xu Wang",
      "userId": "919223987059773748"
    }
  ]
}
```

**推荐编排**：
```bash
# 先读表格内容
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url>

# 再 best-effort 补提 username
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> --best-effort
```

---

### 普通表格操作 (sheet)

适用于 `/s/home/` 和 `/t/home/` 的普通表格。

**操作**：
- `create` - 创建普通表格
- `read` - 读取内容
- `write` - 写入数据
- `append` - 追加数据

**示例**：
```bash
# 创建表格
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py create --name "表格名" \
  --sheet-data '[["列1","列2"],["数据1","数据2"]]'

# 读取表格
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url>

# 读取指定范围
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url> --range "0!A1:D10"

# 写入数据（从 A1 开始）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py write <url> '[["数据"]]'

# 写入到指定位置
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py write <url> '[["数据"]]' --cell-index B3

# 追加到末尾
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py append <url> '[["数据"]]'
```

**数据格式**：二维数组 JSON
```json
[
  ["列1", "列2", "列3"],
  ["数据1", "数据2", "数据3"],
  ["数据4", "数据5", "数据6"]
]
```

---

### 万维表格操作 (metasheet)

适用于 `/m/home/` 和 `/b/home/` 的万维表格（结构化数据库）。

**操作**：
- `meta` - 获取表格结构
- `content` - 读取记录
- `add-record` - 新增记录
- `update-record` - 更新记录
- `delete-record` - 删除记录

**示例**：
```bash
# 获取结构（Sheet 列表、列定义）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py meta <url>

# 读取记录（sheetId 从 URL hash 自动解析）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url>#sheetId=<id>

# 显式指定 sheetId
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url> <sheet-id>

# 新增记录
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py add-record <url>#sheetId=<id> \
  '{"title":"新任务","field1":"选项A"}'

# 更新记录
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py update-record <url>#sheetId=<id> \
  <record-id> '{"title":"已完成"}'

# 删除记录
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py delete-record <url>#sheetId=<id> <record-id>
```

**字段值格式**：

| 字段类型 | 格式示例 | 说明 |
|---------|---------|------|
| 文本 `text` | `{"title": "文本"}` | 直接字符串 |
| 单选 `single_select` | `{"field1": "选项名"}` | 传选项名称 |
| 多选 `multi_select` | `{"field1": ["A", "B"]}` | 数组 |
| 数字 `number` | `{"field1": 90}` | 数值 |
| 日期 `date` | `{"field1": "2026-04-15"}` | YYYY-MM-DD，自动转时间戳 |
| 人员 `person` | `{"field1": ["username"]}` | 用户名数组 |

**ID 说明**：
- `docId`: `fc` 开头，从 URL 提取
- `sheetId`: `shd` 开头，从 meta 命令获取或 URL hash
- `recordId`: `rc` 开头，从 content 命令获取

---

## 常见问题

### Q: 统一入口 vs 独立脚本？

**统一入口 `docs.py`**：
- ✅ 统一命令格式，易记
- ✅ 自动验证 URL 类型与操作是否匹配，传错类型会立即报错提示

**独立脚本**（可选）：
- ✅ 明确类型时性能更好（无外包层）
- ✅ 批量处理同类型文档

### Q: 类型检测会很慢吗？

所有六种 URL 格式均通过路径前缀直接判断，零延迟，无 API 查询。

### Q: 如何获取 sheetId？

```bash
# 方法 1：从 meta 命令输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py meta <url>

# 方法 2：从浏览器 URL hash
# https://docs.corp.kuaishou.com/m/home/fcXXX#sheetId=shdYYY
```

### Q: 如何获取 recordId？

```bash
# 从 content 命令输出
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url> <sheet-id>
# 输出包含每条记录的 recordId
```

### Q: 普通表格 vs 万维表格？

| 对比项 | 普通表格 | 万维表格 |
|-------|---------|---------|
| URL | `/s/home/` | `/m/home/` |
| 数据模型 | 二维数组 | 结构化记录 |
| 写入方式 | 按单元格坐标 | 按记录 ID |
| 字段类型 | 文本/数字 | 文本/单选/多选/日期/人员 |
| 适合场景 | 简单数据表 | 项目管理/数据库 |

---

## 故障排查

### 问题: 401 Unauthorized

**原因**：Cookie 过期或未登录

**解决**：
```bash
# SmartSSOSession 会自动处理
# 按提示重新登录即可
```

### 问题: 403 Forbidden（下载文档）

**原因**：无下载权限

**解决**：
```bash
# 1. 申请权限
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py request_permission <url>

# 2. 等待审批
# 3. 重试下载
```

### 问题: CHECK_NO_DOWNLOAD_AUTH

**原因**：文档所有者禁用了下载功能

**解决**：联系文档所有者在安全设置中开启下载权限

### 问题: 表格拉取失败

**原因**：`pull` 命令对表格支持有限

**解决**：
```bash
# 改用 download 命令导出为 xlsx
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url>
```

### 问题: 万维表格找不到记录

**原因**：可能在不同的 Sheet 中

**解决**：
```bash
# 1. 先查看所有 Sheet
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py meta <url>

# 2. 指定正确的 sheetId
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url> <correct-sheet-id>
```

---

## 使用场景示例

### 场景 1: 普通表格操作（知识库 URL `/t/`）

```bash
# /t/home/ 直接路由到 sheet.py
# 不需要 API 查询，无延迟
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read \
  "https://docs.corp.kuaishou.com/t<skill_directory>"
# 输出: 🔍 文档类型: 普通表格（/s/ 或 /t/）
```

### 场景 2: 文档协作流程

```bash
# 1. 搜索文档
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search "API 规范"

# 2. 拉取到本地
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull fcABxxx -o api.md

# 3. 本地编辑
vim api.md

# 4. 上传更新（保留 ID 和权限）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push api.md --mode edit --doc-id fcABxxx
```

### 场景 3: 表格数据处理

```bash
# 1. 读取表格数据
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url> > data.json

# 2. 处理数据（示例：可以用任何方式处理 JSON）
# 方式 1: 手动编辑 data.json 文件
# 方式 2: 用 Python 脚本处理
# 方式 3: 用 jq 命令行工具处理
#   例如：jq '.rows += [{"name": "新行", "value": 100}]' data.json > new_data.json


# 3. 追加新数据
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py append <url> "$(cat new_data.json)"
```

### 场景 4: 万维表格批量操作

```bash
# 1. 获取结构
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py meta <url>

# 2. 读取所有记录
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url> <sheet-id> > records.json

# 3. 批量更新（循环）
while read record_id; do
  uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py update-record <url> <sheet-id> \
    "$record_id" '{"status":"已完成"}'
done < record_ids.txt
```

---

## 环境要求

### uv 运行环境（推荐）

所有脚本使用 PEP 723 格式，支持 uv 自包含运行：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 Homebrew
brew install uv

# 运行脚本（自动管理依赖）
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py <operation>
```

**优势**：
- ✅ 自动依赖管理
- ✅ 隔离环境，无冲突
- ✅ 快速启动，有缓存
- ✅ 不污染系统环境

---

## API 参考

### 主要 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/merlot/api/docs/cosmo/meta/{docId}` | POST | 获取文档元数据 |
| `/merlot/api/docs/search` | POST | 搜索文档 |
| `/d/export/{docId}` | GET | 触发文档导出 |
| `/s/export/{docId}` | GET | 触发表格导出 |
| `/metasheet/api/export/{docId}` | GET | 触发万维表格导出 |
| `/word/api/pending/{docId}` | GET | 轮询导出状态 |
| `/merlot/api/share-apply/role` | POST | 申请权限 |
| `/react/api/doc-discussion/discussions` | GET | 查询评论 |

完整 API 列表请查看各脚本源码。

---

**最后更新**：2026-04-16  
**维护者**：yukeyou
