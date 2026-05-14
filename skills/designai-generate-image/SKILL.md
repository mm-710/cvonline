---
name: designai-generate-image
description: 全能 AI 生图 skill，凡是提到截图、风格参考、生成图片等且不要求交互功能的，优先走designai-generate-image。以下场景唤醒（不限于）：文生图（生成图片、文生图、画图、AI绘图、做一张图、generate image、image generation）；图生图（图生图、修改图片、换背景、改风格、改颜色、去水印、多图合成、图片编辑、基于参考图生成、把图片改成、风格融合、人物一致性、参考截图）。以下场景不唤醒：信息图（生成信息图、做信息图、数据可视化图、infographic）请路由到 designai-Infographic-image skill；图片下载、图片查看、图片上传 CDN 等非生图场景不唤醒。
---

# 万擎 AI 全能生图 Skill

## 核心参考文件

| 文件 | 作用 |
|------|------|
| `<skill_directory>/reference/Prompt-Workflow.md` | **文生图提示词生成完整流程**（Step 0~4，模式A必须完整执行） |
| `<skill_directory>/reference/Prompt-Reference.md` | Part 3：84种风格词库（Route B 风格句来源）；Part 4：行业色板；Part 7/8：写实摄影/游戏/食物/建筑等场景专项词库（**仅用于 Route B 风格句及模式B图生图 prompt 扩写，不影响 Route A**） |
| `<skill_directory>/reference/intent-signals.md` | 信息图信号词、修改图片信号词、图生图场景参考 |
| `<skill_directory>/reference/check-list.md` | 模式A 生成后图片质量检查清单 |
| `<skill_directory>/reference/error-handling.md` | SSO 认证机制与错误处理详情 |

---

## 入口：意图识别与自动分流

**无需询问用户，根据以下条件自动判断（按优先级从高到低）：**

| 判断条件 | 走向 |
|---|---|
| 用户意图是生成**信息图**（见信号词） | → **路由到 designai-Infographic-image skill** |
| 当前消息有附件图片（本地路径） | → **模式B（图生图）** |
| 用户消息中包含图片 CDN URL（`http://` 或 `https://` 开头的图片链接） | → **模式B（图生图，先下载）** |
| 当前消息无图片，但用户意图是**修改/编辑上一张已生成的图片**（见信号词） | → **模式B（图生图，使用对话历史中最近一张图片）** |
| 当前消息无图片，纯文字描述新内容 | → **模式A（文生图）** |

> 详细的信号词列表及路由话术见 `<skill_directory>/reference/intent-signals.md`

---

## 模式A — 文生图

### 阶段1：生成提示词（⚠️ 询问节点1）

**完整执行 `Prompt-Workflow.md` 的 Step 0 → Step 1 → Step 2 → Step 3 → Step 4：**

1. **Step 0**：读取 Workflow 判断图片类型（12种）+ 内容类型（文字型/视觉型）
2. **Step 1**：按 Workflow 推荐比例，向用户确认（**这是询问节点1**）
3. **Step 2**：生成 Route A（叙事流，无风格约束）
4. **Step 3**：生成 Route B（在 Route A 基础上加风格句，从 `Prompt-Reference.md` Part 3 匹配）
5. **Step 4**：同时输出 Route A + Route B，并附上确认提示，进入阶段2

---

### 阶段2：执行生成（⚠️ 询问节点2）

Route A + Route B 输出后，附上确认提示：

```
以上是 Route A 和 Route B 两个版本，回复「生成」将同时生成两张图片进行对比，或告诉我需要调整的地方。
```

**⚠️ 用户回复「生成」后，将两段提示词分别写入文件，并行生成两张图片：**

> ⚠️ **必须使用时间戳命名临时文件**，避免同一天多次生成时文件互相覆盖。

```bash
TS=$(date +%Y%m%d_%H%M%S)

cat > /tmp/prompt_route_a_${TS}.txt << 'EOF'
{Route A 完整提示词}
EOF

cat > /tmp/prompt_route_b_${TS}.txt << 'EOF'
{Route B 完整提示词}
EOF

uv run <skill_directory>/scripts/generate_image.py \
  --prompt "$(cat /tmp/prompt_route_a_${TS}.txt)" --size 2K --ratio {用户确认的比例} &

uv run <skill_directory>/scripts/generate_image.py \
  --prompt "$(cat /tmp/prompt_route_b_${TS}.txt)" --size 2K --ratio {用户确认的比例} &

wait
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--size` | 分辨率：`512` / `1K` / `2K` / `4K` | `2K` |
| `--ratio` | 宽高比，支持：`1:1` `9:16` `16:9` `3:4` `4:5` `21:9` 等 | `1:1` |

---

### 阶段3：检查与迭代

两张图片生成后，逐项检查并在必要时静默修正重新生成（最多迭代 3 次）。

> 检查清单及处理规则详见 `<skill_directory>/reference/check-list.md`

**输出格式（⚠️ 图片 Markdown 必须在同一行，`]` 和 `(` 之间绝对不能有换行）：**

```
**Route A — 叙事流版本**

![Route A](https://...)

**Route B — 风格锚点版本（{风格名}）**

![Route B](https://...)

| 参数 | Route A | Route B |
|------|---------|---------|
| 比例 | {aspectRatio} | {aspectRatio} |
| 分辨率 | {imageSize} | {imageSize} |
| Token | {totalTokenCount} | {totalTokenCount} |
```

---

## 模式B — 图生图

### 步骤1：图片收集

按优先级获取参考图片：

1. **当前消息附件**（最高优先级）：从当前消息的附件列表中获取路径，附件存放在 `$WORKSPACE/local-file-in-chat/` 目录下，**必须使用当前消息中用户刚上传的路径，禁止使用历史消息中的旧附件路径**
2. **CDN URL**：若用户提供了以 `http://` 或 `https://` 开头的图片链接，先调用下载脚本转为本地路径：
   ```bash
   uv run <skill_directory>/scripts/download_cdn_images.py \
     --urls "https://cdn.example.com/image0.png" "https://cdn.example.com/image1.png" \
     --skill-directory <skill_directory>
   ```
   脚本输出 JSON，成功时返回 `local_paths` 字段，将其值作为下一步 `--images` 参数。
3. **历史附件 fallback**：若当前消息无图片，脚本会自动扫描 `local-file-in-chat/` 目录中最新的图片文件作为兜底（最新修改时间优先）。如不确定使用哪张，先向用户确认图片列表。

> ⚠️ 图片数量限制：最多 14 张（Gemini 3.1 Flash Image 模型限制）

### 步骤2：一次性询问缺失参数

若以下参数用户未提供，一次性询问，不分多轮：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 编辑/合成指令（想做什么）| **必填，若为空则询问** |
| `--ratio` | 宽高比 | `1:1` |
| `--size` | 分辨率 | `2K` |

### 步骤3：静默扩写 prompt

将用户的简短指令**在内部扩写为更详细的 Gemini 图生图指令**，扩写结果**不展示给用户**，直接进入生成步骤。

扩写原则：明确描述保留什么（人物特征、主体构成等）和改变什么（背景、颜色、风格等）；若为多图合成，说明各图的参考角色。

### 步骤4：执行生成

> ⚠️ **必须使用时间戳命名临时文件**，避免多次生成互相覆盖。

```bash
TS=$(date +%Y%m%d_%H%M%S)

uv run <skill_directory>/scripts/image_to_image.py \
  --prompt "{扩写后的完整指令}" \
  --images {图片路径1} {图片路径2} ... \
  --size 2K --ratio {比例}
```

**参数枚举：**

**imageSize**：`512` | `1K` | `2K` | `4K`

**aspectRatio**：`1:1` | `1:4` | `1:8` | `2:3` | `3:2` | `3:4` | `4:1` | `4:3` | `4:5` | `5:4` | `8:1` | `9:16` | `16:9` | `21:9`

### 步骤5：输出结果

**成功时输出格式（⚠️ `]` 和 `(` 之间绝对不能有换行或空格）：**

```markdown
**图片生成成功！**

![生成图片]({image_url字段值})

| 参数 | 值 |
|------|----|
| 参考图 | {输入图片数量} 张 |
| 分辨率 | {imageSize} |
| 宽高比 | {aspectRatio} |
| Token 消耗 | {totalTokenCount} |
```

- 优先使用 `image_url` 字段（CDN URL，`https://...` 格式），浏览器可直接渲染
- 若无 `image_url` 则使用 `data_url` 字段（base64 内嵌格式）
- 若脚本返回 `success: false`，自动简化 prompt 重试一次，仍失败则直接输出 `message` 字段内容

---

## 认证与错误处理

两个脚本均集成 `SmartSSOSession` 自动认证，支持 401/403 自动重试。

> 详细的错误处理规则及兜底话术见 `<skill_directory>/reference/error-handling.md`
