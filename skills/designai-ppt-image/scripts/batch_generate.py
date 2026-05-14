#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# ]
# ///
"""
Batch parallel image generation for PPT slides.

Supports two modes:

1. Manifest mode (recommended for professional mode with mixed aspect ratios):
   uv run scripts/batch_generate.py --manifest output/ppt-gen/image_manifest.json
   uv run scripts/batch_generate.py --manifest output/ppt-gen/image_manifest.json --workers 4

   Manifest JSON format:
   [
     {"prompt": "...", "output": "images/slide-01-bg.jpg", "aspect": "16:9"},
     {"prompt": "...", "output": "images/slide-01-content.jpg", "aspect": "3:4"},
     {"prompt_file": "slide-02-prompt.md", "output": "images/slide-02-bg.jpg", "aspect": "16:9"}
   ]
   Each entry must have "output" and "aspect". Prompt can be inline "prompt" or file path "prompt_file".

2. Legacy prompt-file mode (all slides same aspect ratio):
   uv run scripts/batch_generate.py --input-dir output/ppt-gen --count 12
   uv run scripts/batch_generate.py --input-dir output/ppt-gen --count 12 --workers 6 --aspect-ratio 16:9

Auth: SmartSSOSession (ks_aimate.sso_login_client via internal PyPI) — handled automatically by generate_image.py subprocess.
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]


def _ratio_to_float(ratio_str: str) -> float:
    """Convert ratio string like '16:9' to float. Returns 0 on parse error."""
    try:
        w, h = ratio_str.split(":")
        return float(w) / float(h)
    except Exception:
        return 0.0


def nearest_valid_ratio(ratio_str: str) -> str:
    """
    Find the closest supported aspect ratio to the given string.
    If ratio_str is already valid, return it unchanged.
    Otherwise find the supported ratio whose float value is nearest.
    """
    if ratio_str in VALID_ASPECT_RATIOS:
        return ratio_str

    target = _ratio_to_float(ratio_str)
    if target == 0.0:
        print(f"  ⚠ Cannot parse aspect ratio '{ratio_str}', using 16:9")
        return "16:9"

    best = min(VALID_ASPECT_RATIOS, key=lambda r: abs(_ratio_to_float(r) - target))
    print(f"  ℹ Aspect '{ratio_str}' not supported → using nearest '{best}' (CSS background-size:cover will crop)")
    return best


def find_generate_script(ref_image: str = None) -> str:
    """Locate generate_image.py or generate_image_ref.py depending on ref_image."""
    script_name = "generate_image_ref.py" if ref_image else "generate_image.py"
    candidates = [
        Path("scripts") / script_name,
        Path(__file__).parent / script_name,
        Path(__file__).parent.parent.parent.parent / "scripts" / script_name,
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())
    print(f"ERROR: {script_name} not found. Tried: {[str(c) for c in candidates]}")
    sys.exit(1)


def generate_single(
    script_path: str,
    prompt: str,
    output_file: str,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    is_prompt_file: bool = False,
    ref_image: str = None,
) -> dict:
    """Generate a single image by calling generate_image.py or generate_image_ref.py as subprocess."""
    slide_name = Path(output_file).stem
    start = time.time()

    # Resolve to nearest valid ratio (never errors out, CSS cover handles cropping)
    resolved_ratio = nearest_valid_ratio(aspect_ratio)
    if resolved_ratio != aspect_ratio:
        aspect_ratio = resolved_ratio

    prompt_arg = "--prompt-file" if is_prompt_file else "--prompt"

    # When using a reference image, prepend a style-only instruction so the model
    # inherits the visual style (color palette, lighting, typography mood) of the
    # reference without copying its layout or content.
    actual_prompt = prompt
    if ref_image and not is_prompt_file:
        actual_prompt = (
            "Use the reference image ONLY for visual style reference "
            "(color palette, lighting mood, typography style, overall aesthetic). "
            "Do NOT copy the layout, text, or content from the reference image. "
            "Generate a completely new slide with the following content:\n\n"
            + prompt
        )

    try:
        import shutil
        uv_exe = shutil.which("uv") or "uv"
        cmd = [
            uv_exe, "run", script_path,
            prompt_arg, actual_prompt,
            "--output", output_file,
            "--aspect-ratio", aspect_ratio,
            "--size", resolution,
        ]
        if ref_image:
            cmd += ["--image", ref_image]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.time() - start

        output_path = Path(output_file)
        if output_path.exists() and output_path.stat().st_size > 10240:
            return {
                "slide": slide_name,
                "status": "success",
                "time": elapsed,
                "output": output_file,
                "size_kb": output_path.stat().st_size / 1024,
                "aspect": aspect_ratio,
            }
        else:
            return {
                "slide": slide_name,
                "status": "failed",
                "time": elapsed,
                "error": f"Output too small or missing ({output_path.stat().st_size if output_path.exists() else 0} bytes)",
                "stderr": result.stderr[-500:] if result.stderr else "",
                "aspect": aspect_ratio,
            }

    except subprocess.TimeoutExpired:
        return {
            "slide": slide_name,
            "status": "timeout",
            "time": 300,
            "error": "Process timed out after 300s",
            "aspect": aspect_ratio,
        }
    except Exception as e:
        return {
            "slide": slide_name,
            "status": "error",
            "time": time.time() - start,
            "error": str(e),
            "aspect": aspect_ratio,
        }


def batch_from_manifest(
    manifest_path: str,
    input_dir: str,
    workers: int = 4,
    retry: int = 2,
    resolution: str = "2K",
    ref_image: str = None,
) -> list:
    """
    Generate images from a manifest JSON file.
    Supports mixed aspect ratios — each entry specifies its own aspect.

    Manifest format (list of objects):
      [
        {"prompt": "...", "output": "images/slide-01-bg.jpg", "aspect": "16:9"},
        {"prompt_file": "slide-02-prompt.md", "output": "images/slide-02-bg.jpg", "aspect": "16:9"},
        {"prompt": "...", "output": "images/slide-02-content.jpg", "aspect": "3:4"}
      ]
    """
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}")
        sys.exit(1)

    with open(manifest_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    if not isinstance(entries, list) or not entries:
        print("ERROR: Manifest must be a non-empty JSON array")
        sys.exit(1)

    input_path = Path(input_dir)
    images_dir = input_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    script_path = find_generate_script(ref_image=ref_image)

    # Build task list
    tasks = []
    for idx, entry in enumerate(entries):
        output = entry.get("output")
        aspect = entry.get("aspect", "16:9")
        prompt = entry.get("prompt")
        prompt_file = entry.get("prompt_file")

        if not output:
            print(f"  ⚠ Entry {idx} missing 'output', skipping")
            continue
        if not prompt and not prompt_file:
            print(f"  ⚠ Entry {idx} ({output}) missing 'prompt' or 'prompt_file', skipping")
            continue
        if aspect not in VALID_ASPECT_RATIOS:
            aspect = nearest_valid_ratio(aspect)

        # 如果 output 已经是绝对路径，直接用；否则才拼接 input_path 前缀
        output_path = str(output) if Path(output).is_absolute() else str(input_path / output)

        if prompt_file:
            pf = str(input_path / prompt_file)
            tasks.append({
                "prompt": pf,
                "output": output_path,
                "aspect": aspect,
                "is_prompt_file": True,
                "label": Path(output).stem,
            })
        else:
            tasks.append({
                "prompt": prompt,
                "output": output_path,
                "aspect": aspect,
                "is_prompt_file": False,
                "label": Path(output).stem,
            })

    return _run_batch(tasks, script_path, workers, retry, resolution, ref_image=ref_image)


def batch_generate(
    input_dir: str,
    count: int,
    workers: int = 6,
    retry: int = 2,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
) -> list:
    """
    Legacy mode: generate images from slide-NN-prompt.md files (all same aspect ratio).
    For professional mode with mixed aspect ratios, use batch_from_manifest() instead.
    """
    input_path = Path(input_dir)
    images_dir = input_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    script_path = find_generate_script()

    tasks = []
    for i in range(1, count + 1):
        nn = f"{i:02d}"
        prompt_file = str(input_path / f"slide-{nn}-prompt.md")
        output_file = str(images_dir / f"slide-{nn}.jpg")

        if not Path(prompt_file).exists():
            print(f"  ⚠ Prompt file not found: {prompt_file}, skipping")
            continue

        tasks.append({
            "prompt": prompt_file,
            "output": output_file,
            "aspect": aspect_ratio,
            "is_prompt_file": True,
            "label": f"slide-{nn}",
        })

    return _run_batch(tasks, script_path, workers, retry, resolution)


def _run_batch(
    tasks: list,
    script_path: str,
    workers: int,
    retry: int,
    resolution: str,
    ref_image: str = None,
) -> list:
    """Core batch execution with parallel workers and retry logic."""
    if not tasks:
        print("ERROR: No tasks to process")
        return []

    total = len(tasks)
    print(f"{'=' * 60}")
    print(f"  Batch Image Generation")
    print(f"  Tasks: {total} | Workers: {workers} | Retry: {retry}")
    print(f"  Script: {script_path}")
    from collections import Counter
    aspect_counts = Counter(t["aspect"] for t in tasks)
    print(f"  Aspect ratios: {dict(aspect_counts)}")
    print(f"{'=' * 60}")
    print()

    all_results = []
    remaining_tasks = list(tasks)

    for attempt in range(1, retry + 1):
        if attempt > 1:
            failed_labels = {r["slide"] for r in all_results if r["status"] != "success"}
            remaining_tasks = [t for t in tasks if t["label"] in failed_labels]
            if not remaining_tasks:
                break
            print(f"\n--- Retry {attempt}/{retry}: {len(remaining_tasks)} failed tasks ---\n")

        pending = len(remaining_tasks)
        completed = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for task in remaining_tasks:
                future = executor.submit(
                    generate_single,
                    script_path,
                    task["prompt"],
                    task["output"],
                    task["aspect"],
                    resolution,
                    task["is_prompt_file"],
                    ref_image,
                )
                futures[future] = task["label"]

            for future in as_completed(futures):
                label = futures[future]
                result = future.result()
                completed += 1

                aspect_info = f" [{result.get('aspect', '?')}]"
                if result["status"] == "success":
                    print(f"  ✅ [{completed}/{pending}] {label}{aspect_info} ({result['time']:.1f}s, {result['size_kb']:.0f}KB)")
                else:
                    print(f"  ❌ [{completed}/{pending}] {label}{aspect_info} {result['status']}: {result.get('error', '')[:80]}")

                all_results = [r for r in all_results if r["slide"] != result["slide"]]
                all_results.append(result)

    success = sum(1 for r in all_results if r["status"] == "success")
    failed = sum(1 for r in all_results if r["status"] != "success")
    total_time = sum(r.get("time", 0) for r in all_results)

    print(f"\n{'=' * 60}")
    print(f"  Results: {success}/{success + failed} success")
    if failed:
        print(f"  Failed: {', '.join(r['slide'] for r in all_results if r['status'] != 'success')}")
    print(f"  Total API time: {total_time:.0f}s (wall time less due to parallelism)")
    print(f"{'=' * 60}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Batch parallel slide image generation (supports mixed aspect ratios via manifest)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manifest mode — recommended for professional mode (mixed aspect ratios)
  uv run scripts/batch_generate.py --manifest output/ppt-gen/image_manifest.json

  # Legacy mode — all slides same aspect ratio (creative mode / simple cases)
  uv run scripts/batch_generate.py --input-dir output/ppt-gen --count 12
  uv run scripts/batch_generate.py --input-dir output/ppt-gen --count 12 --aspect-ratio 16:9 --workers 4

Manifest JSON format:
  [
    {"prompt": "futuristic AI scene...", "output": "images/slide-01-bg.jpg", "aspect": "16:9"},
    {"prompt": "vertical portrait...",  "output": "images/slide-01-content.jpg", "aspect": "3:4"},
    {"prompt_file": "slide-02-prompt.md", "output": "images/slide-02-bg.jpg", "aspect": "16:9"}
  ]

Auth: SmartSSOSession (ks_aimate.sso_login_client) — handled automatically by generate_image.py subprocess.
"""
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--manifest", "-m",
        help="Path to image manifest JSON (supports mixed aspect ratios per image)",
    )
    mode_group.add_argument(
        "--count", "-n",
        type=int,
        help="Number of slides (legacy mode: reads slide-NN-prompt.md files, all same aspect ratio)",
    )

    # Common options
    parser.add_argument("--input-dir", "-i", default=".", help="Base directory for prompts and output (default: current dir)")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--retry", "-r", type=int, default=2, help="Retry failed images N times (default: 2)")
    parser.add_argument("--resolution", default="2K", choices=["512", "1K", "2K", "4K"], help="Image size (default: 2K)")

    # Legacy-only option
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="16:9",
        help="Aspect ratio for all slides — legacy mode only (default: 16:9). Use manifest mode for mixed ratios.",
    )

    # Image-to-image reference
    parser.add_argument("--ref-image", default=None, help="Reference image path for image-to-image generation (style consistency)")

    # Legacy --creator (ignored, auth handled by SSO automatically)
    parser.add_argument("--creator", "-c", default=None, help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.manifest:
        results = batch_from_manifest(
            manifest_path=args.manifest,
            input_dir=args.input_dir,
            workers=args.workers,
            retry=args.retry,
            resolution=args.resolution,
            ref_image=args.ref_image,
        )
    else:
        if not args.input_dir or args.input_dir == ".":
            print("ERROR: --input-dir is required in legacy mode")
            return 1
        results = batch_generate(
            input_dir=args.input_dir,
            count=args.count,
            workers=args.workers,
            retry=args.retry,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
        )

    failed = [r for r in results if r["status"] != "success"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
