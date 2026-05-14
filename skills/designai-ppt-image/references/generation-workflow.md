# Stage 2: 幻灯片图像生成

## Prompt 构建原则

**目标**：每张图是一整页完整的幻灯片，包含该页所有内容（标题、正文、数据、图形），AI 自主决定视觉风格和构图。

📎 执行前查阅：`reference/prompt-builder.md` 了解 prompt 构建公式。

**核心思路**：
1. 根据幻灯片标题语义，描述视觉场景（中英文均可）
2. 用结构化标签标注要显示的内容（`Slide title:` / `Key points:` / `Key metric:`）
3. 内容完整写入，不省略要点和数据
4. 遵循用户指定的风格偏好（如有）
5. 避免俗气的科技蓝等配色，使用现代高级配色

## Prompt 公式

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
, sophisticated modern color palette, avoid generic tech blue colors, 
high-end visual design, ultra high resolution, cinematic color grading, sharp typography
```

**slides.yml 中的 prompt 字段必须在 Stage 1 就完整写好**，不能留占位符。

## 两阶段生图策略（风格一致性保障）

### 情况 A：用户提供了参考图

直接用参考图对所有幻灯片图生图，天然风格一致，**全部并发生成**：

```bash
uv run <skill_directory>/scripts/batch_generate.py --manifest output/ppt-gen/image_manifest.json --input-dir output/ppt-gen --ref-image '<参考图路径>' --workers 4
```

> 注意：`<skill_directory>` 在 skill 加载时由系统上下文自动提供。

### 情况 B：无参考图（两阶段执行）

**Phase 1 — 串行生成封面（第 1 张）**：

```bash
uv run <skill_directory>/scripts/generate_image.py --prompt '{slide-01的prompt}' --output 'output/ppt-gen/images/slide-01.jpg' --aspect '16:9'
```

**Phase 2 — 以封面为参考图，并发生成剩余所有页**：

封面生成完成后，从 manifest 中去掉第 1 条，将剩余 N-1 条作为新 manifest 执行图生图批量任务。

**风格继承规则（自动注入）**：`batch_generate.py` 检测到 `--ref-image` 时，会在每张图的 prompt 前自动加入：
```
Use the reference image ONLY for visual style (color palette, lighting, typography). 
Do NOT copy its layout or content.
```

模型只参考封面的视觉风格，不会复制封面的排版和文字内容。

```bash
uv run <skill_directory>/scripts/batch_generate.py --manifest output/ppt-gen/image_manifest_rest.json --input-dir output/ppt-gen --ref-image 'output/ppt-gen/images/slide-01.jpg' --workers 4
```

> `image_manifest_rest.json` = image_manifest.json 去掉 index=1 的条目后另存

**耗时估算**：Phase 1 约 45s + Phase 2（N-1 张并发）约 50s = **总约 1.5 分钟**

## 关键前置步骤：从 slides.yml 生成 image_manifest.json

**必须在执行批量生图前先运行此步骤**：

```python
# 将此代码保存为 output/ppt-gen/gen_manifest.py 并执行
import yaml, json

with open('output/ppt-gen/slides.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

manifest = []
for slide in data['presentation']['slides']:
    manifest.append({
        'index': slide['index'],
        'output': slide['image']['output'],
        'aspect': slide['image']['aspect'],
        'prompt': slide['image']['prompt']
    })

with open('output/ppt-gen/image_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# 生成 rest manifest（去掉第1张，供 Phase 2 使用）
manifest_rest = [m for m in manifest if m['index'] != 1]
with open('output/ppt-gen/image_manifest_rest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest_rest, f, ensure_ascii=False, indent=2)

print(f'Written {len(manifest)} entries ({len(manifest_rest)} in rest manifest)')
```

执行命令：
```bash
python output/ppt-gen/gen_manifest.py
```
