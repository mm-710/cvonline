# ks-design-infographic

信息图生成器 Skill — 将任意内容（文字、网页、文档、图片）自动转化为精美信息图；支持对已有信息图进行风格迁移与局部编辑。

## 版本

**v3.2.3** (v4.0)

---

## 更新日志

### v3.2.3 (2026-04-25)
- 规范性修复：统一 skill name 为 `designai-infographic-image`（全小写）
- 优化 SSO 依赖说明，符合《Skills开发指南（BETA）》规范
- 压缩 SKILL.md 至 3000 字以内，详细内容移至 `reference/workflow-details.md`
- 删除冗余的 `requirements.txt`（已使用 PEP 723 依赖声明）
- 通过规范检查，可以上线

### v4.0.0（2026-04）
- 接入图生图（图片编辑）能力，支持风格迁移、局部调整、参考图生图
- 工作流优化：风格选择和宽高比确认合并为一次交互
- 宽高比从5种扩展至9种
- `generate_image.py` 新增 `--image-file`、`--image-base64` 参数
- 新增阶段6「后续编辑引导」

### v3.2.0
- 初始版本，支持文生图和双路线并行生图

---

- 支持所有类型输入：纯文本、Markdown、URL、图片/截图、数据表格
- 16种大类视觉风格可选（手绘漫画、科技暗黑、赛博朋克等）
- 双路线并行生图（路线A叙事流 + 路线B风格矩阵），每次产出两张图供用户择优
- **v4.0 新增**：9种宽高比（16:9 / 4:3 / 3:2 / 21:9 / 1:1 / 4:5 / 2:3 / 3:4 / 9:16）
- **v4.0 新增**：图生图/图片编辑能力（风格迁移、局部调整、参考图生图）
- **v4.0 新增**：工作流优化，风格选择和宽高比确认合并为一次交互
- 自动质量检查 + 最多3次迭代优化
- 基于快手内网图像生成 API（需内网环境）

## 目录结构

```
ks-design-infographic/
├── SKILL.md                        # Skill 主指令文件（v4.0）
├── README.md                       # 本文件
├── scripts/
│   └── generate_image.py           # 图像生成脚本 v4.0（支持文生图 + 图生图）
├── reference/
│   ├── infographic-types.md        # 10种信息图类型详解与选型指南
│   ├── style-matching.md           # 22种风格详细描述
│   └── workflow-details.md         # 详细工作流程、风格矩阵、提示词模板（v3.2.3新增）
└── examples/
    ├── example-dream-prose.md      # 案例：梦境/文学输入
    └── example-ecosystem.md        # 案例：生态系统输入
```

## 功能概述

### 1. 通过 CodeFlicker Agent Skill 调用（推荐）

将本目录放置到：
```
~/.agents/skills/ks-design-infographic/
```
或项目级：
```
<project>/.agents/skills/ks-design-infographic/
```

### 2. 直接调用脚本

#### 文生图

```bash
# 从文本提示直接生成
uv run scripts/generate_image.py \
    --prompt "一张关于咖啡因作用机制的信息图" \
    --output output/caffeine.jpg \
    --resolution 2K \
    --aspect-ratio 9:16 \
    --creator yourname

# 从提示词文件生成
uv run scripts/generate_image.py \
    --prompt-file prompt.md \
    --output output/result.jpg \
    --resolution 2K \
    --aspect-ratio 16:9
```

#### 图生图（v4.0 新增）

```bash
# 按已有图修改风格（传入本地图片文件）
uv run scripts/generate_image.py \
    --prompt "保留内容，将整体风格改为赛博朋克风格，霓虹色系" \
    --image-file output/route-A.jpg \
    --output output/edited.jpg

# 按参考图风格生成新内容（传入参考图 + 新主题提示词）
uv run scripts/generate_image.py \
    --prompt "参考输入图片的视觉风格，生成关于人工智能发展历程的信息图" \
    --image-file reference-style.jpg \
    --output output/new-infographic.jpg

# 传入 base64 进行图片编辑
uv run scripts/generate_image.py \
    --prompt "把背景改成深色调" \
    --image-base64 "data:image/png;base64,iVBORw0KGgo..." \
    --output output/edited.jpg
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` / `-p` | 文本提示词 | — |
| `--prompt-file` / `-f` | 提示词文件路径 | — |
| `--output` / `-o` | 输出文件路径 | — |
| `--resolution` / `-r` | 分辨率：`2K` / `4K` / `1080p`（仅文生图有效） | `2K` |
| `--aspect-ratio` / `-a` | 宽高比（仅文生图有效，见下方列表） | `16:9` |
| `--quality` / `-q` | JPEG/WEBP 质量 1-100 | `95` |
| `--creator` / `-c` | 创作者用户名 | 自动获取当前用户 |
| `--format` | 强制输出格式：`jpg` / `png` / `webp` | 自动检测 |
| `--image-file` / `-i` | 参考图本地路径（触发图生图模式）| — |
| `--image-base64` | 参考图 base64 字符串或 data URL（与 --image-file 互斥）| — |

### 支持的宽高比（v4.0 扩展）

| 宽高比 | 方向 | 典型场景 |
|--------|------|----------|
| `16:9` | 横向宽屏 | PPT / 报告 / 网页 Banner（默认） |
| `4:3` | 横向 | 传统幻灯片 / 宽屏文档 |
| `3:2` | 横向 | 杂志版式 / 横版海报 |
| `21:9` | 超宽 | 超宽屏展示 / 横幅 Banner |
| `1:1` | 方形 | 社媒方图 / Bento 卡片 |
| `4:5` | 竖向 | Instagram 竖版 / 移动端竖图 |
| `2:3` | 竖向 | 海报竖版（接近 A4） |
| `3:4` | 竖向 | A4 竖版文档 / 宣传单 |
| `9:16` | 竖向 | 手机海报 / 小红书 / 单页信息图 |

## 网络要求

⚠️ `generate_image.py` 调用快手内网 API，**需在快手内网环境或 VPN 下使用**。

API 地址：`https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate`
模型：`Gemini-3.1-Flash-Image-Preview`

## Skill 工作流（v4.0）

### 文生图模式

1. **阶段1** — 解析输入内容（文本/URL/图片等）
2. **阶段2** — 展示「快速启动卡片」（风格菜单 + 宽高比推荐合并，一次交互完成）
3. **阶段3** — 生成双路线提示词（路线A叙事流 + 路线B风格矩阵）
4. **阶段4** — 并行调用生图脚本，产出两张图
5. **阶段5** — 自动质量检查，最多3次迭代，交付结果
6. **阶段6** — 展示后续编辑引导（换风格/局部调整/参考图）

### 图生图模式（v4.0 新增）

- **阶段E** — 检测触发条件（用户上传图片/使用「换风格」关键词）→ 构造编辑提示词 → 调用图生图脚本 → 展示结果

详细规则见 [SKILL.md](SKILL.md)。

## 参考文档

- [reference/infographic-types.md](reference/infographic-types.md) — 选型指南
- [reference/style-matching.md](reference/style-matching.md) — 风格描述库
- [examples/](examples/) — 典型案例（输入→提示词→输出）

## 更新日志

### v4.0.0（2026-04）
- 接入图生图（图片编辑）能力，支持风格迁移、局部调整、参考图生图
- 工作流优化：风格选择和宽高比确认合并为一次交互（原阶段1+3合并）
- 宽高比从5种扩展至9种，与 API 完整枚举对齐
- `generate_image.py` 新增 `--image-file`、`--image-base64` 参数
- 新增阶段6「后续编辑引导」，形成创作闭环

### v3.2.0
- 初始版本，支持文生图和双路线并行生图
