---
name: designai-infographic-image
description: 将任意内容（文字、网页、文档、图片、数据表格）转化为精美信息图；支持对已有信息图进行风格迁移和局部编辑。当用户说"生成信息图"、"做信息图"、"做一张信息图"、"把这个做成信息图"、"给我做张图"、"信息可视化"、"make infographic"、"create infographic"、"visualize this data"、"turn this into an infographic"、"修改信息图"、"换风格"、"图片编辑"、"edit infographic"、"refine this image"时唤醒。不支持：纯数据分析报告（无需生图）、视频/音频内容转换、需要实时数据的动态图表。
---

# 信息图生成器 (Infographic Generator) v4.0

## 概述

信息图生成器专注于将**任何输入内容**自动转化为精美的信息图，并支持对已有图片进行**风格迁移与局部编辑**。全自动决策——接收原始资料后，自动完成整理、选型、配风格、写提示词、生成图片全流程，用户只需提供素材。

**核心特性：**
- 支持所有类型输入：文本、URL、图片、文档
- 16种视觉风格可选（手绘漫画、科技暗黑、赛博朋克等）
- 双路线并行生图：每次产出两张图供择优（路线A叙事流 + 路线B风格矩阵）
- 9种宽高比：16:9 / 4:3 / 3:2 / 21:9 / 1:1 / 4:5 / 2:3 / 3:4 / 9:16
- 自动质量检查 + 最多3次迭代优化
- **图生图/图片编辑**：支持基于已有图片进行风格迁移或局部修改

---

## ⚠️ 前置条件

**本 skill 依赖 `kuaishou-sso-login-client` skill**（已在 manifest.json 中声明，会自动安装）。

**SSO 认证：**
- 生图脚本已集成 `SmartSSOSession`（`ks_aimate.sso_login_client`），自动处理 SSO 认证
- 脚本头部已声明依赖，`uv run` 首次执行时自动从 `https://pypi.corp.kuaishou.com` 安装
- 首次访问或会话过期时，会自动静默登录或弹出 KIM 扫码
- 目标站点：`https://codeflicker.corp.kuaishou.com`

**Cookie 过期自动恢复机制（v4.1）：**
- 脚本内置双层防护：当 API 返回 HTTP 401/403 时，自动重建 `SmartSSOSession` 并重试一次（Python 脚本层）
- Agent 层同步兜底：若脚本整体返回 SSO 失效错误，Agent 主动调用 `kuaishou-sso-login-client` skill 重新登录后再重试（仅触发一次）
- 若双层恢复后仍失败，向用户报告错误并停止

**环境要求：**
- 需确保能访问内网 PyPI（公司内网/VPN）

---

## 核心工作原则

**最高原则：信任模型的视觉创造力，Skill 只做内容净化和污染防护。**

### 内容净化原则
1. **连续叙事流**：提示词必须是连续段落，禁止拆成命名区块（「XX机制：」「XX数据：」）
2. **去污染不去内容**：去除 markdown 符号但保留所有数据、说明文字、括号备注
3. **底部金句**：每张图底部包含 8-20 字情感收尾金句，融入正文
4. **全中文输出**：禁止元素中写明「所有文字必须为中文」

### 污染防护原则
5. **格式符号净化**：禁用【】《》★等（会被渲染为装饰文字）
6. **宽高比数字防泄漏**：禁止元素中必须写「禁止出现 9:16、16:9 等宽高比数字」
7. **技术单位禁入**：禁止 px/pt/rem 等
8. **结构词禁入**：禁止「区块」「面板」「主角区」等
9. **防泄漏三件套**：①禁止宽高比数字 ②禁止格式符号装饰 ③禁止孤立数字刻度

### 视觉质量原则
10. **不指定风格名称**：禁止写 `gradient-tech` 或精确 hex 色值，可用情绪词
11. **不指定图表类型**：禁止写「横向条形图」「4阶段卡片」等
12. **不拆区块**：禁止预分为「核心数字区」「对比区」等
13. **信息量控制**：核心信息点 ≤ 8个

> 详细规则见：`<skill_directory>/reference/workflow-details.md`

---

## 工作流

### 模式检测优先

- 用户上传图片 + 提出修改需求 → **图生图模式（阶段E）**
- 用户提供内容素材（文本/URL/文档）→ **文生图模式（阶段1-6）**

---

### 【文生图模式】完整流程

#### 阶段1：解析输入内容

接受所有类型输入：文本/文档、URL（fetch_web）、图片（read_file识别内容）、混合输入。

**解析目标**：主题、关键数据、说明文字、信息量 → 立即展示「快速启动卡片」

#### 阶段2：快速启动卡片

向用户展示内容解析结果表格（主题、推荐宽高比）及 16 种可选视觉风格（编号 1-17）。

用户输入示例：
- `1` → 系统自动匹配风格 + 推荐宽高比
- `10` → 科技暗黑风 + 推荐宽高比
- `9:16 + 12` → 赛博朋克风 + 9:16 竖版
- 不输入 → 默认选项1，立即开始生图

> 完整风格列表与表格格式见：`<skill_directory>/reference/step-by-step-guide.md`

#### 阶段3：生成双路线提示词

**路线A：叙事流**（不指定风格）
- 短、直接、连续叙述，不拆区块、不指定图表类型、不写风格词
- 保留所有数据，去除 markdown 符号，末尾融入金句

**路线B：风格矩阵引导**
- 与路线A相同内容 + 在开头追加视觉风格引导句
- 根据内容「领域×基调」从风格矩阵选择风格描述

> 详细风格矩阵、提示词模板见：`<skill_directory>/reference/workflow-details.md`

保存为：
- `output/{主题关键词}/route-A-prompt.md`
- `output/{主题关键词}/route-B-prompt.md`

#### 阶段4：双路线并行生图

若上次脚本调用返回 SSO/401/403 失效错误，先调用 `kuaishou-sso-login-client` skill 重新登录，再执行脚本（仅允许触发一次重登录）。

```bash
# 路线A
uv run "<skill_directory>/scripts/generate_image.py" \
    --prompt-file "output/{主题关键词}/route-A-prompt.md" \
    --output "output/{主题关键词}/route-A.jpg" \
    --resolution 2K --aspect-ratio {宽高比} --creator "{username}"

# 路线B
uv run "<skill_directory>/scripts/generate_image.py" \
    --prompt-file "output/{主题关键词}/route-B-prompt.md" \
    --output "output/{主题关键词}/route-B.jpg" \
    --resolution 2K --aspect-ratio {宽高比} --creator "{username}"
```

脚本自动完成：生成图片（调用万擎 API）→ 上传至 CDN → 获取 CDN URL → 保存本地文件。

> 脚本输出 JSON 格式及 CDN/base64 降级说明见：`<skill_directory>/reference/step-by-step-guide.md`

#### 阶段5：提取 CDN URL 并渲染（最多3次迭代）

1. 用 `read_file` 检查 P0 问题（结构词/技术单位/格式符号/宽高比数字/英文文字）
2. P0 失败 → 修改提示词重新生成（最多3次）；P0 通过 → 渲染
3. 从脚本 JSON 输出中提取 `image_url`（优先）或 `data_url`（降级）
4. 用 Markdown 渲染（`]` 和 `(` 之间绝对不能换行或空格）

> 完整渲染格式模板见：`<skill_directory>/reference/step-by-step-guide.md`

#### 阶段6：后续编辑引导

```
✅ 生成完成！

💡 还可以继续优化：
• 输入「换风格 + 编号」对选定版本进行风格迁移
• 直接上传图片并描述修改需求，进行局部调整
• 上传一张参考图，我可以按该图的视觉风格重新生成
```

---

### 【图生图模式】阶段E：图片编辑

**触发条件**：用户上传图片 + 描述修改 / 输入「换风格 + 编号」/ 上传参考图 + 新内容

**执行步骤**：

1. 用 `read_file` 读取用户上传的图片
2. 根据用户需求构造提示词（风格迁移/局部调整/参考图生图）
3. 调用图生图脚本：

```bash
uv run "<skill_directory>/scripts/generate_image.py" \
    --prompt "..." --image-file "input.jpg" \
    --output "output/edited.jpg" --creator "{username}"
```

4. 从 JSON 中提取 `image_url` 或 `data_url`，用 Markdown 渲染
5. 展示「后续编辑引导」，用户可继续迭代优化

若脚本返回 SSO 失效错误，先调用 `kuaishou-sso-login-client` skill 重新登录再重试（仅一次）。

> 详细提示词模板见：`<skill_directory>/reference/workflow-details.md`

---

## 支持的输入类型

纯文本/Markdown（直接分析）、URL/网页（fetch_web）、图片内容来源（read_file 识别）、图片参考/待编辑（read_file 转 base64）、PDF（需先提取文本）、数据表格（转为叙述）。

---

## 支持文件

- **`<skill_directory>/scripts/generate_image.py`** — 图像生成脚本 v4.0（支持文生图和图生图）
- **`<skill_directory>/reference/workflow-details.md`** — 详细工作流程、风格矩阵、提示词模板、质量检查清单
- **`<skill_directory>/reference/step-by-step-guide.md`** — 阶段2风格选择表格、脚本 JSON 输出格式、渲染模板
- **`<skill_directory>/reference/infographic-types.md`** — 10种类型详解与选型指南
- **`<skill_directory>/reference/style-matching.md`** — 22种风格详细描述
- **`<skill_directory>/examples/`** — 典型案例（输入 → 提示词 → 输出）

> 注意：`<skill_directory>` 来自 skill 加载时系统上下文中的路径信息。
