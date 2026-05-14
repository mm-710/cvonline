#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""
assemble_presentation.py — Stage 3 Assembly Script for ks-design-slide-deck

Reads slides.yml and generates viewer.html by copying viewer-shell.html and
replacing the 5 template variables:
  {{TITLE}}   — presentation title
  {{MODE}}    — "professional" | "creative"
  {{SLIDES}}  — JS array content (slide paths)
  {{TITLES}}  — JSON array of slide titles
  {{TOTAL}}   — total slide count

Usage:
  uv run scripts/assemble_presentation.py --slides-yml output/ppt-gen/slides.yml
  uv run scripts/assemble_presentation.py --slides-yml output/ppt-gen/slides.yml --output-dir output/ppt-gen
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# Path to the viewer shell template (relative to this script)
VIEWER_SHELL_PATH = Path(__file__).parent.parent / "assets" / "viewer-shell.html"


def load_slides_yml(yml_path: str) -> dict:
    """Load and parse slides.yml."""
    path = Path(yml_path)
    if not path.exists():
        print(f"Error: slides.yml not found at {yml_path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def image_to_base64(img_path: Path) -> str:
    """Convert image file to base64 data URI."""
    import base64
    import mimetypes
    mime, _ = mimetypes.guess_type(str(img_path))
    if not mime:
        mime = "image/jpeg"
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


def build_slide_entries(slides: list, mode: str, output_dir: Path) -> tuple[list, list]:
    """
    Build slide src list and titles list.
    For creative mode: embed images as base64 data URIs so viewer.html is self-contained.
    For professional mode: keep relative HTML paths (images already text-embedded).
    Returns (srcs, titles).
    """
    srcs = []
    titles = []
    for slide in slides:
        idx = slide.get("index", len(srcs) + 1)
        nn = str(idx).zfill(2)
        title = slide.get("title", f"幻灯片 {idx}").replace('"', '\\"')
        titles.append(title)

        if mode == "professional":
            srcs.append(f"slide-{nn}.html")
        else:
            img_path = output_dir / "images" / f"slide-{nn}.jpg"
            if img_path.exists():
                srcs.append(f"images/slide-{nn}.jpg")
                print(f"   [link] slide-{nn}.jpg → relative path ✅")
            else:
                srcs.append(f"images/slide-{nn}.jpg")
                print(f"   [warn]  slide-{nn}.jpg not found, using relative path")
    return srcs, titles


def build_viewer(slides_yml_path: str, output_dir: str = None) -> str:
    """
    Read slides.yml, fill viewer-shell.html template, write viewer.html.
    Images are embedded as base64 data URIs → viewer.html is fully self-contained.

    Returns the output path of viewer.html.
    """
    # Load slides.yml
    data = load_slides_yml(slides_yml_path)
    presentation = data.get("presentation", data)  # support both wrapped and flat

    title = presentation.get("title", "Presentation")
    mode = presentation.get("mode", "professional")
    slides = presentation.get("slides", [])

    if not slides:
        print("Warning: No slides found in slides.yml")

    # Determine output directory
    if output_dir is None:
        output_dir = str(Path(slides_yml_path).parent)
    output_dir_path = Path(output_dir)

    print(f"📦 Building viewer with relative image paths (fast loading)...")
    srcs, titles = build_slide_entries(slides, mode, output_dir_path)

    # Read viewer shell
    if not VIEWER_SHELL_PATH.exists():
        print(f"Error: viewer-shell.html not found at {VIEWER_SHELL_PATH}")
        sys.exit(1)

    shell = VIEWER_SHELL_PATH.read_text(encoding="utf-8")

    # Build replacement values
    slides_js = ",".join(f'"{s}"' for s in srcs)
    titles_js = json.dumps(titles, ensure_ascii=False)
    total_str = str(len(slides))

    # Replace template variables
    viewer = shell
    viewer = viewer.replace("{{TITLE}}", title)
    viewer = viewer.replace("{{MODE}}", mode)
    viewer = viewer.replace("{{SLIDES}}", slides_js)
    viewer = viewer.replace("{{TITLES}}", titles_js)
    viewer = viewer.replace("{{TOTAL}}", total_str)

    out_path = output_dir_path / "viewer.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(viewer, encoding="utf-8")

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"✅ viewer.html written → {out_path}  ({size_mb:.1f} MB, self-contained)")
    print(f"   Title  : {title}")
    print(f"   Mode   : {mode}")
    print(f"   Slides : {total_str}")

    return str(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble viewer.html from slides.yml using viewer-shell.html template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/assemble_presentation.py --slides-yml output/ppt-gen/slides.yml
  python scripts/assemble_presentation.py --slides-yml output/ppt-gen/slides.yml --output-dir output/ppt-gen
        """,
    )
    parser.add_argument(
        "--slides-yml",
        required=True,
        help="Path to slides.yml file.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write viewer.html into. Defaults to the same directory as slides.yml.",
    )
    args = parser.parse_args()

    build_viewer(args.slides_yml, args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
