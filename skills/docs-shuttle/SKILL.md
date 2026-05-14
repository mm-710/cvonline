---
name: docs-shuttle
description: 快手内网在线文档平台（docs.corp.kuaishou.com）与本地双向同步工具。用户说「上传文档到 Docs」「发布到 Docs」「从 Docs 拉取」「同步文档」「把这个 MD 上传到文档系统」「上传 Excel 到 Docs」「拉取表格」「拉取多维表格」「下载表格为 CSV」「上传 CSV 到表格」「更新表格数据」「批量拉取我的文档」「备份我的 Docs」「Kim Doc」「kim文档」「内网文档」「公司文档」「企业文档」，或提供 docs.corp.kuaishou.com 链接时，使用本技能。支持导入 MD/Excel/CSV 文件、拉取文档和表格（含电子表格和多维表格）内容、批量备份用户文档、按项目组织文件夹、文档搜索、权限申请、评论管理。注意：本技能仅处理在线 Docs 平台操作，不处理本地 .docx Word 文件的读写编辑。
---

# docs-shuttle: Docs 文档同步工具

## 执行步骤

**Step 1：从用户输入中获取 URL**
- 用户提供的 URL 形如 `https://docs.corp.kuaishou.com/...`
- 如果用户没有提供 URL，主动询问

**Step 2：检查 URL 路径前缀，确定文档类型**

| URL 路径前缀 | 文档类型 | 说明 |
|------------|---------|------|
| `/d/home/` | 普通文档 | 独立文档 |
| `/k/home/` | 普通文档 | 知识库内文档 |
| `/s/home/` | 普通表格 | 独立表格 |
| `/t/home/` | 普通表格 | 知识库内表格 |
| `/m/home/` | 万维表格 | 独立万维表格 |
| `/b/home/` | 万维表格 | 知识库内万维表格 |

**Step 3：根据文档类型选择合法操作**

| 文档类型 | 可用操作 |
|---------|---------|
| 普通文档 | `pull` `push` `comment` |
| 普通表格 | `read` `write` `append` `create` `mentions` |
| 万维表格 | `meta` `content` `add-record` `update-record` `delete-record` |
| 全部类型 | `download` `request_permission` `search` |

> ⚠️ 传错类型 `docs.py` 会自动报错，例如对表格 URL 执行 `pull` 会提示类型不匹配。

**Step 4：确定保存路径（仅 pull / download 需要）**
- 根据 `KS_AGENT_PLATFORM` 选择路径（见强制规则二）
- 通过 `-o` 参数显式指定，不依赖默认路径

**Step 5：执行命令（⚠️ 必须使用 uv run）**

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py <operation> <url> [args...]
```

**⚠️ 强制要求：所有命令必须以 `uv run --refresh-package ks_aimate` 开头执行！**
- ✅ 正确：`uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url>`
- ❌ 错误：`uv run <skill_directory>/scripts/docs.py read <url>`（缺少 --refresh-package 参数）
- ❌ 错误：`python docs.py read <url>`（缺少依赖）
- ❌ 错误：`python3 docs.py read <url>`（缺少依赖）
- ❌ 错误：`<skill_directory>/scripts/docs.py read <url>`（直接执行）

---

## 🚨 强制规则

### 规则一：类型判断唯一依据是 URL 路径前缀，任何其他信息均无效

禁止根据以下信息判断类型：
- ❌ 用户说的"文档"、"表格"、"万维表格"等词语
- ❌ 文件名或标题
- ❌ 用户的主观描述

**无论用户怎么描述，执行任何操作前必须先看 URL。**

| 用户说的 | URL 实际是 | 应该判断为 |
|---------|-----------|---------|
| "帮我拉取这个文档" | `/s<skill_directory>` | ⛔ 不能用 pull，应用 read（普通表格）|
| "读取这个表格" | `/d<skill_directory>` | ⛔ 不能用 read，应用 pull（普通文档）|
| "这是个万维表格" | `/s<skill_directory>` | ⛔ 不能用 meta/content，应用 read（普通表格）|

### 规则二：pull / download 必须指定 -o 路径，根据平台选择保存目录

读取 `KS_AGENT_PLATFORM` 环境变量判断平台，选择对应路径：

| 平台（`$KS_AGENT_PLATFORM`） | 保存路径 |
|-----------------------------|---------|
| `myflicker` | `/data/aime/${SANDBOX_UUID}/workspace/文件名` |
| `codeflicker` | `~/tmp/文件名` |

```bash
# myflicker 环境
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> \
  -o /data/aime/${SANDBOX_UUID}/workspace/文档名.md

### 规则四：APPEND 操作禁止把原文件整体推送回去

执行 `APPEND_TAIL` / `APPEND_HEAD` 时，**只能 push 新增内容**，绝对不能把原文件（含已有内容）整体推送。

**禁止的做法：**
```bash
# ❌ 错误：把总结追加到本地文件后整体推送，会导致原文重复出现
echo "总结内容" >> 原文.md
push 原文.md --mode edit --doc-id xxx --position APPEND_TAIL
```

**正确的做法：**
```bash
# ✅ 只创建仅含新增内容的临时文件，push 这个文件
echo "总结内容" > /tmp/append_only.md
push /tmp/append_only.md --mode edit --doc-id xxx --position APPEND_TAIL
# 或者直接把新增内容写到一个独立文件，不动原文件
```

**原文件保持不变**，push 的文件只包含本次新增的段落。
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> \
  -o /data/aime/${SANDBOX_UUID}/workspace/文件名.docx

# codeflicker 环境
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> -o ~/tmp/文档名.md
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> -o ~/tmp/文件名.docx
```

---

### 规则三：普通表格读取/分析场景必须 best-effort 补提 @mention 用户名当 URL 为 `/s/home/` 或 `/t/home/` 的普通表格时：

**何时需要额外执行 `mentions`：**
- 用户明确要求提取/查找/统计人员信息（如"列出所有负责人"、"找出被 @ 的人"、"统计参与者"）
- 用户要求分析人员相关的维度（如"按负责人分组"、"查看审批人列表"）
- 用户提到"username"、"@某人"、"mention"等关键词

**何时不需要额外执行 `mentions`：**
- 仅读取数据内容（如"读取前 10 行"、"查看表格数据"）
- 分析非人员维度（如"统计数量"、"查看进度"）
- 用户没有提到任何人员相关需求

**提取方式：**
- **提取 username / userId / displayName 时，必须走 snapshot 富文本链路**：先获取 `snapshotRevision`，再调用 `/excel/api/latest/snapshot/{docId}`，从 `<a class="cell-mention">` 的属性中提取 `data-login-id`、`data-cn-name`、`data-en-name`、`data-id`
- 如果 snapshot 链路无法获取 revision、无法获取数据、或未提取到结构化 mention，**应自动使用 SSR HTML 方式兜底一次**：调用 `/excel-ssr/api/html/{docId}` 再解析 `<a class="cell-mention">` 属性
- SSR 仅作为兜底，因为它受首屏限制，可能无法覆盖整张表；**只要 snapshot 能提取，就优先使用 snapshot 结果**
- **禁止把 `read` 读到的可见文本、`@张三` 显示内容、或肉眼分析结果，视为 username 提取成功**；`read` 只能辅助定位内容，不能替代 `mentions`
- 如果 `mentions` 深挖后仍未提取到 username，只能说明“未能从 snapshot 中提取出结构化 mention 信息”，不能说“已经从表格内容看到了 @mention，所以可以代替 username”
- mention 提取失败、无权限、API 变更、或确实不存在 mention 时，**不得阻塞主流程**；继续返回主操作结果，并说明 mention 为 best-effort 增强
- `write` / `append` / `create` 这类写操作默认不额外执行 `mentions`，除非用户明确要求校验或分析写入后的内容

推荐执行方式：

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url> [--range "0!A1:D10"]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> --best-effort
```

---

## 统一入口

**所有操作都通过 `uv run --refresh-package ks_aimate` 执行 `docs.py`：**

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py <operation> [url] [args...]
```

**⚠️ 禁止使用 `python`/`python3` 直接执行！** 必须使用 `uv run --refresh-package ks_aimate` 来管理依赖并确保使用最新版本。

---

## 命令速查

### 普通文档

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py pull <url> -o <path>
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push file.md
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py push file.md --mode edit --doc-id <id> [--position APPEND_TAIL]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment list <url> [--solved]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py comment add <url> "评论内容"
```

### 普通表格（`/s/` `/t/`）

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py create --name "表格名" [--sheet-data '[["列1","列2"]]']
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py read <url> [--range "0!A1:D10"]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py write <url> '[["数据"]]' [--cell-index B3]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py append <url> '[["数据"]]'

# 提取表格中的 @mention 用户信息（username / userId / displayName）
# 适用场景：需要提取被 @ 的人员列表、分析人员相关维度时使用
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py mentions <url> [--format text] [--best-effort]
```

### 万维表格（`/m/` `/b/`）

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py meta <url>
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py content <url> [sheet-id]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py add-record <url>#sheetId=<id> '{"title":"新记录"}'
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py update-record <url>#sheetId=<id> <record-id> '{"field1":"新值"}'
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py delete-record <url>#sheetId=<id> <record-id>
```

### 通用（全部类型）

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py search "关键词" [--page 1] [--size 20] [--json]
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py download <url> [--format pdf] -o <path>
uv run --refresh-package ks_aimate <skill_directory>/scripts/docs.py request_permission <url> [--permission-type edit] [--reason "原因"]
```

---

## 补充说明

**万维表格字段值格式**：
- 文本：`{"title": "文本"}`
- 单选：`{"field1": "选项名"}`
- 多选：`{"field1": ["选项A", "选项B"]}`
- 数字：`{"field1": 90}`
- 日期：`{"field1": "2026-04-15"}`（自动转时间戳）
- 人员：`{"field1": ["username"]}`

**下载格式**：普通文档 → docx/pdf，普通表格/万维表格 → xlsx

**认证**：通过 `SmartSSOSession` 自动处理 SSO，无需手动维护 Cookie。

**详细文档**：`reference/reference.md`
