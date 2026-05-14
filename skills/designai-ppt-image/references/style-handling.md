# Step 2: 参考图与风格处理

大纲确认后，询问用户视觉风格设置。

## 询问模板

```
📐 视觉风格设置：

1️⃣ 是否有参考图？
   上传后 AI 会严格参考其色彩体系和视觉风格生成幻灯片。

2️⃣ 想要什么风格？
   例如：极简设计、赛博朋克、商务专业、潮流时尚、温暖人文、科技未来等
   （如不指定，AI 会根据内容主题自主决定）

请告诉我：
- 有参考图 → 直接上传
- 有风格偏好 → 描述你想要的风格
- 都没有 → 回复「没有」，AI 自主决定
```

## 处理流程

### 情况 A：用户上传了图片

**必须先下载图片到本地，再传给生图脚本。**

1. **创建参考图目录并下载**：

```python
import urllib.request, os from pathlib import Path

ref_dir = Path("output/ppt-gen/ref")
ref_dir.mkdir(parents=True, exist_ok=True)

image_url = "{从对话消息中提取的图片URL}"
ref_path = str(ref_dir / "ref-01.jpg")

# 下载图片
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(image_url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    with open(ref_path, "wb") as f:
        f.write(resp.read())
```

2. **下载成功后**：使用 `generate_image_ref.py` 图生图模式

3. **若下载失败**（CDN限制），告知用户：
```
参考图 URL 无法在本地环境访问（CodeFlicker CDN 仅限沙箱访问）。
请将图片另存为本地文件，告诉我文件的绝对路径，
或者回复「无参考图」由 AI 自主决定视觉风格。
```

### 情况 B：无参考图

#### 子情况 B1：用户指定了风格偏好

记录用户的风格描述，在生成每张幻灯片的 prompt 时融入风格关键词。

**风格 → Prompt 映射示例**：
- "极简设计" → `minimalist design, clean layout, plenty of white space`
- "赛博朋克" → `cyberpunk aesthetic, neon colors, futuristic tech`
- "温暖人文" → `warm humanistic style, soft colors, approachable design`

#### 子情况 B2：用户未指定风格

Agent 根据内容主题和调性自主决定视觉风格。

## 避免俗气配色规则

无论用户是否指定风格，都要在 prompt 中明确避免以下配色：
- 避免 `generic tech blue (科技蓝)`
- 避免 `cliché corporate color schemes`
- 使用 `sophisticated, modern color palettes`

在每张幻灯片的 prompt 末尾统一加入：
```
, sophisticated modern color palette, avoid generic tech blue colors, high-end visual design
```
