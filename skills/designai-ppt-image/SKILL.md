---
name: designai-ppt-image
description: >
  Generate AI-powered PowerPoint presentations where each slide is a complete AI-generated image
  including title, content, data visualizations, and design elements.
  Use when the user wants to "生成PPT", "做幻灯片", "create presentation", "make slides",
  "将文档变成PPT", "根据物料生成PPT", or "修改第X页" (edit specific slides).
  Supports natural language editing to regenerate individual slides. Outputs dual formats:
  .pptx (downloadable) and .pdf (online preview). Supports reference image style transfer
  and style preferences (minimalist, cyberpunk, business, etc.).
  Do NOT use when: users only want text-based slides; users need fully editable text;
  users are discussing PPT concepts without wanting to create one.
---

# DesignAi-ppt-image — AI 图像生成式 PPT

根据物料规划 PPT，每张幻灯片用 AI 图像生成完整一页。支持参考图风格迁移和自定义风格偏好。

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

## 执行顺序

```
Step 0: 生成任务目录（每次新任务必须新建，避免旧图混入）
Step 1: 提取物料 → 规划大纲
Step 2: 参考图/风格处理
Stage 1: 生成 slides.yml
Stage 2: 生成幻灯片图像
Stage 3: 导出 .pptx 和 .pdf
```

---

## Step 0：创建任务目录（CRITICAL — 每次新任务必须执行）

**每次生成新 PPT 任务时，必须创建带时间戳的独立目录**，绝不复用旧目录。
旧文件物理上就不在同一个目录里，根本不可能混进来，比时间戳校验更可靠。

```bash
python3 -c "
import datetime, os
ts = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
task_dir = os.path.abspath(f'output/ppt-gen/{ts}')
os.makedirs(f'{task_dir}/images', exist_ok=True)
os.makedirs(f'{task_dir}/pptx', exist_ok=True)
os.makedirs(f'{task_dir}/pdf', exist_ok=True)
print(f'TASK_DIR={task_dir}')
"
```

执行后记录输出的 `TASK_DIR` **绝对路径**，**后续所有步骤统一使用此路径，禁止在命令前加 `cd workspace &&`**。

> ⚠️ **修改已有 PPT 某一页时，不新建目录，继续使用原 TASK_DIR**。

---

## Step 1：提取物料，规划大纲

收到用户物料后，深度分析内容，提取核心主题、章节结构、每页内容。

**详细说明**：`references/outline-planning.md`

输出大纲让用户确认后进入 Step 2。

---

## Step 2：参考图与风格处理

大纲确认后，询问用户：

```
📐 视觉风格设置：

1️⃣ 是否有参考图？上传后 AI 会参考其色彩体系和视觉风格。
2️⃣ 想要什么风格？（极简、赛博朋克、商务、人文等）

请告诉我：
- 有参考图 → 直接上传
- 有风格偏好 → 描述风格
- 都没有 → 回复「没有」，AI 自主决定
```

**CRITICAL（参考图处理）**：
- 用户上传图片时，**必须先将图片下载到本地** `{TASK_DIR}/ref/ref-01.jpg`，再传给生图脚本；不得直接使用 URL
- 若下载失败（CDN 限制），告知用户：「参考图 URL 无法在本地访问，请将图片另存为本地文件并告知绝对路径，或回复「无参考图」由 AI 自主决定风格」

**详细处理流程**：`references/style-handling.md`

---

## Stage 1: Content Planning

**CRITICAL：生成 slides.yml 前，必须先加载 `reference/prompt-builder.md` 并按其规则为每张幻灯片构建 prompt 字段。禁止跳过此步骤自行编写 prompt。**

生成 `slides.yml`，幻灯片数量由内容决定（4-20 张）。

**CRITICAL：每张幻灯片的 `content` 字段必须填写真实内容**，这是生图 prompt 的核心依据。

**CRITICAL：slides.yml 必须包含以下三类页面，缺少任何一个均不可开始生成：**
- **第 1 页**：`type: cover`（封面，包含演示文稿标题、副标题/日期/作者）
- **第 2 页**：`type: toc`（目录，列出所有章节标题）
- **最后 1 页**：`type: closing`（感谢/结束页，感谢语 + 演讲者信息）

**CRITICAL：每张幻灯片的 `image.prompt` 字段必须在 Stage 1 就完整写好**（按 `reference/prompt-builder.md` 规则），不得留占位符如「Stage 2 生成」。

生成 slides.yml 后，在向用户展示大纲时，需明确标注这三页已包含。

**结构说明**：`references/slides-yml-structure.md`

---

## Stage 2: 幻灯片图像生成

> ⚠️ **命令必须直接执行，禁止在前面加 `cd workspace &&`。所有路径使用 {TASK_DIR} 绝对路径。**

**CRITICAL（生图前必须执行）**：先从 `slides.yml` 生成 `image_manifest.json` 和 `image_manifest_rest.json`，再执行批量生图命令。详见 `references/generation-workflow.md`。

### 两阶段生图策略

**情况 A：用户提供了参考图** → 全部并发生成

```bash
uv run <skill_directory>/scripts/batch_generate.py --manifest {TASK_DIR}/image_manifest.json --input-dir {TASK_DIR} --ref-image '<参考图路径>' --workers 4
```

**情况 B：无参考图** → 两阶段执行

1. Phase 1：串行生成封面
   ```bash
   uv run <skill_directory>/scripts/generate_image.py --prompt '{slide-01 prompt}' --output '{TASK_DIR}/images/slide-01.jpg' --aspect '16:9'
   ```

2. Phase 2：以封面为参考图，并发生成剩余页
   ```bash
   uv run <skill_directory>/scripts/batch_generate.py --manifest {TASK_DIR}/image_manifest_rest.json --input-dir {TASK_DIR} --ref-image '{TASK_DIR}/images/slide-01.jpg' --workers 4
   ```

**详细流程**：`references/generation-workflow.md`

> 🔐 **SSO 自动重登**：脚本内置 cookie 过期自动重试机制——遇到 401/403 时自动重新初始化 `SmartSSOSession` 触发 SSO 登录，然后重试一次，无需手动干预。

**耗时估算**：Phase 1 约 45s + Phase 2 约 50s = **总约 1.5 分钟**

---

## Stage 3: 导出 PPTX 和 PDF

**Stage 2 完成后立即执行，无需询问用户。**

> 由于每次任务使用独立的 {TASK_DIR}，目录内只有本次生成的图片，无需时间戳校验。

### 步骤 1：导出 PPTX

```bash
uv run <skill_directory>/scripts/export_pptx.py --slides-yml {TASK_DIR}/slides.yml --output '{TASK_DIR}/pptx/{演示文稿标题}.pptx'
```

### 步骤 2：转换为 PDF

```bash
uv run <skill_directory>/scripts/export_pdf.py --slides-yml {TASK_DIR}/slides.yml --output '{TASK_DIR}/pdf/{演示文稿标题}.pdf'
```

### 完成提示（CRITICAL：必须输出以下格式，禁止只展示图片）

Stage 3 完成后，**必须向用户以文字形式输出两个文件的绝对路径**，禁止仅展示图片或省略路径。最终交付物只有 2 个：

- 📊 **PPTX**（可下载/编辑）：`{TASK_DIR 绝对路径}/pptx/{title}.pptx`
- 📄 **PDF**（线上预览/分享）：`{TASK_DIR 绝对路径}/pdf/{title}.pdf`

> ⚠️ `images/` 内的 `.jpg` 是中间产物，不得直接提供给用户。后续修改：说"修改第X页的XXX内容"。

---

## Output Structure

每次新任务建独立时间戳目录，修改任务沿用原目录：

```
output/ppt-gen/
└── 2026-04-26-163000/
    ├── slides.yml / image_manifest.json / image_manifest_rest.json
    ├── images/slide-*.jpg   ← 中间产物
    ├── pptx/{title}.pptx   ← 最终交付
    └── pdf/{title}.pdf     ← 最终交付
```

---

## 参考文档

- `references/outline-planning.md` - Step 1 详细说明
- `references/style-handling.md` - Step 2 风格处理
- `references/generation-workflow.md` - Stage 2 生成流程
- `references/slides-yml-structure.md` - slides.yml 结构（含强制三页要求）
- `reference/prompt-builder.md` - Prompt 构建公式

---

## 依赖服务

- **Kwaipilot Image API**：`https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate`
- **模型**：`Gemini-3.1-Flash-Image-Preview`
- **SSO 认证**：`ks_aimate.sso_login_client`
