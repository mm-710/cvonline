#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml>=6.0",
#   "pillow>=10.0.0",
#   "reportlab>=4.0.0",
# ]
# ///
"""
export_pdf.py — 将 slides.yml + images/ 导出为 .pdf 文件

每张幻灯片图片作为一页 PDF（16:9 比例），适合线上预览和分享。

Usage:
  uv run scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml
  uv run scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml --output output/ppt-gen/pdf/presentation.pdf
  uv run scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml --output deck.pdf --title "我的演示文稿"
"""

import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def load_slides_yml(yml_path: str) -> dict:
    path = Path(yml_path)
    if not path.exists():
        print(f"Error: slides.yml not found at {yml_path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    presentation = data.get("presentation", data)
    return presentation


def build_pdf(slides_yml_path: str, output_path: str, override_title: str = None) -> str:
    """
    Build a .pdf from slides.yml + images/.
    Returns the output path.
    """
    base_dir = Path(slides_yml_path).parent
    data = load_slides_yml(slides_yml_path)

    title = override_title or data.get("title", "Presentation")
    slides = data.get("slides", [])
    slides = sorted(slides, key=lambda s: s.get("index", 9999))

    if not slides:
        print("Warning: No slides found in slides.yml")

    # Create output directory
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 16:9 page size (landscape orientation)
    page_width = 13.333 * inch
    page_height = 7.5 * inch

    c = canvas.Canvas(str(out), pagesize=(page_width, page_height))
    c.setTitle(title)

    success = 0
    skipped = 0

    for slide_data in slides:
        idx = slide_data.get("index", success + skipped + 1)
        nn = str(idx).zfill(2)
        slide_title = slide_data.get("title", f"Slide {idx}")

        # Resolve image path
        image_output = slide_data.get("image", {}).get("output", f"images/slide-{nn}.jpg")
        # 如果 image_output 已是绝对路径，直接用；否则相对 slides.yml 所在目录拼接
        image_path = Path(image_output) if Path(image_output).is_absolute() else base_dir / image_output

        # Fallback: try common extensions
        if not image_path.exists():
            for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                candidate = image_path.with_suffix(ext)
                if candidate.exists():
                    image_path = candidate
                    break

        if image_path.exists():
            try:
                # Open image to get dimensions
                img = Image.open(image_path)
                img_width, img_height = img.size

                # Calculate aspect ratio and fit to page
                img_aspect = img_width / img_height
                page_aspect = page_width / page_height

                if img_aspect > page_aspect:
                    # Image is wider than page
                    draw_width = page_width
                    draw_height = page_width / img_aspect
                    x_offset = 0
                    y_offset = (page_height - draw_height) / 2
                else:
                    # Image is taller than page
                    draw_height = page_height
                    draw_width = page_height * img_aspect
                    x_offset = (page_width - draw_width) / 2
                    y_offset = 0

                # Draw image on PDF page
                c.drawImage(
                    str(image_path),
                    x_offset,
                    y_offset,
                    width=draw_width,
                    height=draw_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                
                success += 1
                print(f"  ✅ [{idx:02d}] {slide_title} — {image_path.name}")
            except Exception as e:
                print(f"  ⚠️  [{idx:02d}] {slide_title} — error processing image: {e}")
                skipped += 1
        else:
            # No image found: add a placeholder page with title
            c.setFillColorRGB(0.1, 0.1, 0.18)  # Dark background
            c.rect(0, 0, page_width, page_height, fill=True, stroke=False)
            
            c.setFillColorRGB(1, 1, 1)  # White text
            c.setFont("Helvetica-Bold", 36)
            text_width = c.stringWidth(slide_title, "Helvetica-Bold", 36)
            c.drawString((page_width - text_width) / 2, page_height / 2, slide_title)
            
            skipped += 1
            print(f"  ⚠️  [{idx:02d}] {slide_title} — image not found ({image_output}), using text placeholder")

        c.showPage()  # Next page

    c.save()

    print(f"\n✅ PDF saved: {out}")
    print(f"   Title  : {title}")
    print(f"   Pages  : {success + skipped} total ({success} with images, {skipped} placeholders)")
    return str(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 slides.yml + images/ 导出为 .pdf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml
  python scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml --output deck.pdf
  python scripts/export_pdf.py --slides-yml output/ppt-gen/slides.yml --output deck.pdf --title "Q2 Brand Launch"

Notes:
  - Each slide image is placed as a full-page 16:9 PDF page.
  - If an image file is missing, a dark text-placeholder page is inserted instead.
  - Requires: pip install pillow pyyaml reportlab
""",
    )
    parser.add_argument("--slides-yml", required=True, help="Path to slides.yml")
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output .pdf path (default: same directory as slides.yml, named after presentation title)"
    )
    parser.add_argument("--title", default=None, help="Override presentation title")

    args = parser.parse_args()

    # Default output path: same dir as slides.yml
    if args.output is None:
        yml_path = Path(args.slides_yml)
        data = load_slides_yml(args.slides_yml)
        pdf_title = args.title or data.get("title", "presentation")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in pdf_title).strip()
        args.output = str(yml_path.parent / f"{safe_title}.pdf")

    build_pdf(args.slides_yml, args.output, args.title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
