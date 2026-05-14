# DesignAi-ppt-image

> AI 创意图片演示文稿生成 Skill（v2.5.0）——从 ks-design-slide-deck 创意模式拆分

## 📌 概述

整页 AI 图片生成 PPT，每张幻灯片都是一整页完整的 AI 图像（包含标题、内容、数据可视化等设计元素）。支持「参考视觉」模式图生图和用户自定义风格偏好。自动避免俗气配色。

**幻灯片虽为图片格式，但支持灵活的自然语言编辑**——只需说"修改第X页的XXX内容"即可重新生成该页。

## 🎯 触发场景

- 生成PPT / 做幻灯片 / 创意幻灯片 / 品牌发布 / AI图片PPT / 修改第X页
- make slides / create presentation / creative slides / image slides / edit slide
- 提供参考图片触发图生图风格迁移
- 可指定风格偏好（极简、赛博朋克、商务、人文等）

## ✨ v2.5.0 更新（Skill-Creator 质量检查修复）

1. ✅ **SKILL.md 结构优化**：从 420 行压缩到 177 行（符合 ≤200 行规范）
   - 采用 Progressive Disclosure 原则：核心流程保留在主文件
   - 详细内容拆分到 `references/` 目录（4 个参考文档）
2. ✅ **Description 格式优化**：改为第三人称动词开头（符合 skill-creator 标准）
3. ✅ **Skill-Creator 检查通过**：综合评分 95/100 ⭐⭐⭐⭐⭐

## 📁 目录结构

```
DesignAi-ppt-image/
├── SKILL.md                         # Skill 主指令文件（177 行，符合规范）
├── manifest.json                    # Skill 元数据
├── CHANGELOG.md
├── README.md
├── references/                      # 详细参考文档（Progressive Disclosure）
│   ├── outline-planning.md          # Step 1 详细说明
│   ├── style-handling.md            # Step 2 风格处理流程
│   ├── generation-workflow.md       # Stage 2 生成详细步骤
│   └── slides-yml-structure.md      # slides.yml 结构说明
├── README.md                        # 本文件
├── manifest.json
├── scripts/
│   ├── generate_image.py            # 单张文生图 CLI
│   ├── batch_generate.py            # 并行批量生图（manifest 模式，4 workers）
│   ├── generate_image_ref.py        # 图生图（参考视觉模式，1~14张参考图）
│   ├── export_pptx.py               # 导出 .pptx 文件
│   ├── export_pdf.py                # 导出 .pdf 文件（新增）
│   └── assemble_presentation.py     # 组装 Viewer（已弃用）
└── reference/
    └── prompt-builder.md            # AI 图片 prompt 关键词速查表
```

## ⚙️ 安装依赖

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🔗 依赖服务

- **Kwaipilot Image API**：`https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate`
- **模型**：`Gemini-3.1-Flash-Image-Preview`，需公司内网 / VPN

---

*Skill Owner: luzifeng | Created: 2026-04-24 | Split from ks-design-slide-deck v4.6.4*
