# Stage 1: Content Planning (slides.yml)

幻灯片数量由内容决定，简单话题 4-6 张，详细内容最多 20 张。

## 强制结构要求（CRITICAL）

每次生成必须包含以下三页，缺一不可：

| 位置 | type | 内容要求 |
|------|------|---------|
| **第 1 页** | `cover` | 演示文稿标题、副标题/日期/作者 |
| **第 2 页** | `toc` | 列出所有章节标题，让观众预览全文结构 |
| **最后 1 页** | `closing` | 感谢语（"感谢聆听"/"Thank You"）+ 演讲者信息或联系方式 |

## slides.yml 结构

**CRITICAL：每张幻灯片的 `content` 字段必须填写真实内容**，这是生图 prompt 的核心依据。

```yaml
presentation:
  title: "演示文稿标题"
  mode: "creative"
  total_slides: 10
  palette: "F"        # 用户选定的 Palette 代号（A-Q），详见 reference/prompt-builder.md
  ref_image: null     # 参考图路径（图生图模式时填写）
  output_dir: "output/ppt-gen"  # 仅供记录，实际由 --output-dir 参数控制

  slides:
    - index: 1
      type: "cover"         # cover | toc | section | content | data | quote | closing
      title: "演示文稿主标题"
      subtitle: "副标题 / 日期 / 作者"
      content: ""            # 封面无正文内容
      image:
        prompt: "professional annual report cover, authoritative brand presence, professional presentation slide, 16:9 widescreen, Slide title: 演示文稿主标题, Subtitle: 副标题 / 日期 / 作者, ultra high resolution, cinematic color grading"
        output: "images/slide-01.jpg"
        aspect: "16:9"

    - index: 2
      type: "toc"
      title: "目录"
      content: "1. 章节一\n2. 章节二\n3. 章节三\n4. 结论"
      image:
        prompt: "（按 reference/prompt-builder.md 规则，在 Stage 1 生成 slides.yml 时完整写好）"
        output: "images/slide-02.jpg"
        aspect: "16:9"

    - index: 3
      type: "content"
      title: "核心观点标题"
      content: "观点1：{具体论述}\n观点2：{具体论述}\n数据：{关键数字}"
      key_data: "83%"        # 该页最重要的数字/数据（可选）
      image:
        prompt: "data visualization, growth metrics, business dashboard, professional presentation slide, 16:9 widescreen, Slide title: 核心观点标题, Key points: • 观点1 • 观点2, Key metric: 83%, ultra high resolution, cinematic color grading"
        output: "images/slide-03.jpg"
        aspect: "16:9"

    - index: 4
      type: "data"
      title: "数据对比标题"
      content: "A: 45% vs B: 78%，增长率：+73%"
      key_data: "+73%"
      image:
        prompt: "（按 reference/prompt-builder.md 规则，在 Stage 1 生成 slides.yml 时完整写好）"
        output: "images/slide-04.jpg"
        aspect: "16:9"

    # ... 内容页 ...

    - index: N   # 最后一页，必须是 closing
      type: "closing"
      title: "感谢聆听"
      content: "演讲者：{姓名} | 联系方式：{邮箱/部门}"
      image:
        prompt: "（按 reference/prompt-builder.md 规则，在 Stage 1 生成 slides.yml 时完整写好）"
        output: "images/slide-NN.jpg"
        aspect: "16:9"
```

## 幻灯片类型说明

- `cover`: 封面
- `toc`: 目录
- `section`: 章节分隔页
- `content`: 内容页
- `data`: 数据可视化页
- `quote`: 引用/名言页
- `closing`: 结束页
