# Prompt Builder — 生图 Prompt 构建指南

> 此文件供 SKILL.md 按需加载：生成幻灯片图片时执行 `read_file("reference/prompt-builder.md")` 查阅。

---

## 核心原则

创意模式每张幻灯片 = 一整页完整的 AI 生成图像，包含该页所有内容（标题、正文、数据、图形）。

**Prompt 构建思路**：
1. 根据幻灯片标题和内容，用语义化方式描述这张幻灯片的视觉场景
2. 明确标注要显示的文字内容（标题/要点/数据）
3. 融入用户指定的风格偏好（如有）
4. 避免俗气配色，使用现代高级配色
5. 加上质量词

---

## Prompt 构建公式

```
{风格前缀（如用户指定）}, {视觉场景描述（中英文均可）},
professional presentation slide, 16:9 widescreen,
Slide title: {title}
{如有副标题}: Subtitle: {subtitle}
{如有要点}: Key points:
• {point 1}
• {point 2}
• {point 3}
{如有关键数据}: Key metric: {key_data}
, sophisticated modern color palette, avoid generic tech blue colors, high-end visual design, ultra high resolution, cinematic color grading, sharp typography
```

> 视觉场景词的写法规则见下方「视觉场景词规则（必须执行）」章节。

## ⚠️ Key points 写法强制规范（CRITICAL）

### 规则 1：每条 bullet 必须包含完整语义

格式：`「时间/编号 + 主体 + 动词 + 结果/程度」`

- ❌ 禁止：`• 萌芽期 单点试验`（只有名词堆叠）
- ✅ 要求：`• 2023-2024萌芽期 单点场景试验为主 基础算法探索`

### 规则 2：Key metrics 必须展开完整含义，禁止只写数字

- ❌ 禁止：`Key metric: 88%`（AI 不知道这是什么的 88%）
- ✅ 要求：`Key metrics: 88% companies actively using AI, 39% achieving real ROI, -19% actual efficiency`

### 规则 3：视觉场景词和内容描述必须分开

prompt 的结构是：**先写视觉构图（场景词）→ 再写内容（标题/要点/数据）**，两者不能混写。

- ✅ 好的版本：先写 `timeline visualization showing AI development phases`（构图），然后再写 `Slide title: ...` + `Key points: ...`
- ❌ 差的版本：把视觉描述和内容描述混在一起，AI 两件事都做不好

### 规则 4：每条 bullet 字数下限 15 字（中文），禁止纯名词堆叠

---

**风格前缀示例**（根据用户指定的风格）：
- 极简设计：`minimalist design, clean layout, plenty of white space` 或 `极简设计，简洁布局，大量留白`
- 赛博朋克：`cyberpunk aesthetic, neon colors, futuristic tech` 或 `赛博朋克美学，霓虹色彩，未来科技`
- 商务专业：`professional business style, corporate elegance` 或 `专业商务风格，企业优雅`
- 温暖人文：`warm humanistic style, soft colors, approachable design` 或 `温暖人文风格，柔和色彩，亲切设计`
- 潮流时尚：`trendy fashion style, bold colors, dynamic layout` 或 `潮流时尚风格，大胆色彩，动态布局`
- 科技未来：`futuristic tech style, innovative design, cutting-edge visual` 或 `科技未来风格，创新设计，前沿视觉`

---

## 视觉场景词规则（必须执行）

规划每张幻灯片的 prompt 时，**禁止直接把标题塞进视觉描述**。必须根据该页主题，提炼一个独立的「视觉场景词」——描述这张幻灯片如果是一个电影片段，场景和氛围是什么。

### 核心规则

1. **每张幻灯片必须有独立的视觉场景词**，让每页有自己的视觉性格，而不是千篇一律的"商务风"
2. **场景词描述的是视觉意象和构图方式**，不是内容本身
3. **整套 PPT 使用统一的底色和主色调**，保持视觉一致性；允许在强调色上有细微变化（如数据页亮色高亮关键数字、引用页单色条纹），但禁止不同页面使用完全不同的配色方案
4. **目录页必须建立明确的视觉语言基调**，定义整套 PPT 的底色、主色、强调色，后续所有页以此为风格锚点

### 视觉场景词示例

| 页面类型 | ❌ 错误写法 | ✅ 正确写法（场景词） |
|---|---|---|
| 时间轴/阶段页 | `slide about four stages` | `timeline visualization showing four phases, horizontal progression arrows` |
| 对比页 | `comparison of two things` | `side-by-side comparison, left side in muted grey, right side in vibrant coral and gold` |
| 安全/风险页 | `security topic slide` | `zero-trust security model visual, dark crimson and silver tones` |
| 引用/金句页 | `quote slide` | `large typographic treatment, single bold accent stripe in warm gold, minimalist layout` |
| 架构图页 | `architecture diagram` | `layered pyramid diagram, interconnected nodes with glowing edges` |
| 数据大屏页 | `data slide` | `data dashboard with multiple metric cards, bar charts and percentage rings` |
| 章节分隔页 | `chapter divider` | `full-bleed chapter divider, oversized section number, single dramatic accent color stripe` |
| 多Agent页 | `agent architecture` | `multi-agent ecosystem, routing hub at center, interconnected nodes radiating outward` |
| 结尾页 | `thank you slide` | `forward momentum visual, confident closing, warm light fading to horizon` |

### 提炼场景词的思路

写 prompt 前先问自己两个问题：
1. **「这页的核心动作是什么？」** — 对比、展示、流转、警示、总结？
2. **「如果这是一个电影镜头，摄影师会怎么构图？」** — 全景/特写/对称/斜角/俯视？

把这两个问题的答案合并，就是场景词。

---

## 配色避坑指南

**禁止使用的俗气配色**：
- ❌ 科技蓝（generic tech blue #0066CC, #3B82F6）
- ❌ 传统企业蓝灰配色（corporate blue-grey）
- ❌ 过时的渐变蓝绿（outdated blue-green gradients）

**推荐现代配色方向**：
- ✅ 高级灰 + 强调色（sophisticated grey with accent colors）
- ✅ 大地色系（earth tones）
- ✅ 莫兰迪色系（muted pastel colors）
- ✅ 深色系 + 金属质感（dark mode with metallic accents）
- ✅ 鲜明对比色（bold contrasting colors）

每张幻灯片的 prompt 末尾都要加上：
```
, sophisticated modern color palette, avoid generic tech blue colors, high-end visual design
```

---

## 质量后缀（每张图必加）

```
ultra high resolution, cinematic color grading, 16:9 widescreen, sharp typography
```
