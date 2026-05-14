# Stage 3: 导出前产物校验

在执行 export_pptx.py / export_pdf.py 之前，必须运行以下校验脚本，确保所有幻灯片图片都是本次生成的最新产物。

## 校验脚本

```python
import yaml, sys
from pathlib import Path

slides_yml = Path('output/ppt-gen/slides.yml')
with open(slides_yml) as f:
    data = yaml.safe_load(f)

# 以 slides.yml 的修改时间作为本次生成开始时间基准
baseline_mtime = slides_yml.stat().st_mtime
base_dir = slides_yml.parent

missing, stale = [], []
slides = sorted(data['presentation']['slides'], key=lambda s: s.get('index', 9999))
for slide in slides:
    img_rel = slide.get('image', {}).get('output', '')
    img_path = base_dir / img_rel
    if not img_path.exists():
        missing.append(f"  ❌ 缺失: {img_rel}")
    elif img_path.stat().st_mtime < baseline_mtime:
        stale.append(f"  ⚠️  过期: {img_rel} (图片早于 slides.yml，可能是上次生成的旧文件)")

if missing or stale:
    print('图片校验失败，请先补全生成：')
    for m in missing: print(m)
    for s in stale: print(s)
    sys.exit(1)
else:
    print(f'✅ 全部 {len(slides)} 张幻灯片图片已就绪，顺序按 index 排列')
```

## 校验规则说明

| 情况 | 处理方式 |
|------|---------|
| 图片文件不存在 | ❌ 阻断导出，必须重新生成该页 |
| 图片文件早于 slides.yml | ⚠️ 阻断导出，图片是旧产物（可能是上次会话遗留），必须重新生成 |
| 图片文件晚于 slides.yml | ✅ 通过，是本次生成的新产物 |

## 校验失败后的修复流程

1. 对每个缺失/过期的图片，单独重新生成：
   ```bash
   uv run <skill_directory>/scripts/generate_image.py --prompt '{该页prompt}' --output 'output/ppt-gen/{img_rel}' --aspect '16:9'
   ```
2. 重新运行校验脚本，直到全部通过
3. 再执行 export_pptx.py 和 export_pdf.py
