#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "pillow>=10.0.0",
#   "ks-aimate",
# ]
#
# [tool.uv.sources]
# "ks-aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///
"""万擎文生图脚本 - 调用内部API生成图片，集成 SmartSSOSession 自动处理认证

支持从 prompt 或 prompt 文件生成图片，输出到指定路径（JPG/PNG/WEBP）。

Usage:
    uv run scripts/generate_image.py --prompt "Your prompt" --output output.jpg
    uv run scripts/generate_image.py --prompt-file prompt.txt --output output.jpg --size 2K --aspect-ratio 16:9
"""

import argparse
import base64
import json
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional

from ks_aimate.sso_login_client import SmartSSOSession

API_URL = "https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate"
MODEL = "Gemini-3.1-Flash-Image-Preview"

SIZE_OPTIONS = ["512", "1K", "2K", "4K"]
ASPECT_RATIO_OPTIONS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

DEFAULT_SIZE = "2K"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_OUTPUT_FORMAT = "jpg"

# Legacy shorthand aliases (for batch_generate.py compatibility)
_LEGACY_RATIO_MAP = {
    "bg": "16:9",
    "content": "3:4",
    "inset": "4:3",
}


class ImageGenerator:
    """万擎文生图工具 - 使用 SmartSSOSession 自动处理认证"""

    BASE_URL = "https://codeflicker.corp.kuaishou.com"

    def __init__(self):
        # 初始化 SSO 会话客户端，首次请求时自动触发认证
        self.client = SmartSSOSession()

    def _request(self, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "kwaipilot-platform": "myflicker",
            "kwaipilot-version": "1.0.0",
        }
        for attempt in range(2):
            response = self.client.request("POST", API_URL, json=payload, headers=headers)
            if response.status_code in (401, 403) and attempt == 0:
                # Cookie/凭证过期，强制重新初始化 SmartSSOSession 触发 SSO 登录后重试
                print("  ⚠ 检测到认证失败（HTTP %d），重新触发 SSO 登录后重试..." % response.status_code)
                self.client = SmartSSOSession()
                continue
            response.raise_for_status()
            return response.json()
        # 第二次仍失败
        response.raise_for_status()
        return response.json()

    def generate(self, prompt: str, image_size: str = DEFAULT_SIZE, aspect_ratio: str = DEFAULT_ASPECT_RATIO) -> dict:
        request_id = f"img-req-{uuid.uuid4().hex[:8]}"
        payload = {
            "chatId": f"img-chat-{uuid.uuid4().hex[:8]}",
            "sessionId": f"img-session-{uuid.uuid4().hex[:8]}",
            "requestId": request_id,
            "model": MODEL,
            "prompt": prompt,
            "autoSize": False,
            "timeout": 120,
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size,
                },
            },
        }

        try:
            result = self._request(payload)
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败: {e}。建议操作：检查网络连接或确认 SSO 会话是否有效。",
            }

        if not result.get("success"):
            return {
                "success": False,
                "message": result.get("message", "未知错误"),
                "建议操作": "请检查 prompt 内容是否合规，或重试一次。",
            }

        images = result.get("images", [])
        if not images:
            return {
                "success": False,
                "message": "API 返回成功但无图片数据",
                "建议操作": "请尝试修改提示词后重试。",
            }

        img_data = images[0].get("data", "")
        mime_type = images[0].get("mimeType", "image/png")

        # 提取 base64 数据
        if img_data.startswith("data:"):
            b64 = img_data.split(",", 1)[1] if "," in img_data else img_data
        else:
            b64 = img_data

        # 上传到内网 CDN，获取可渲染的 URL
        ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
        cdn_url = None
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                tmp.write(base64.b64decode(b64))
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                resp = self.client.request(
                    "POST",
                    "https://design-out.staging.kuaishou.com/private-api/common/upload-file",
                    files={"file": (f"image.{ext}", f, mime_type)},
                    data={"uploadType": "2"},
                    timeout=(5, 15),
                )
            data = resp.json()
            if data.get("code") == 1:
                cdn_url = data.get("data")
        except Exception:
            pass
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        if cdn_url:
            return {
                "success": True,
                "image_url": cdn_url,
                "b64": b64,
                "mime_type": mime_type,
                "usageInfo": result.get("usageInfo", {}),
                "message": result.get("message", ""),
            }

        # CDN 上传失败时降级为 data URL
        return {
            "success": True,
            "data_url": f"data:{mime_type};base64,{b64}",
            "b64": b64,
            "mime_type": mime_type,
            "usageInfo": result.get("usageInfo", {}),
            "message": result.get("message", ""),
        }


# =============================================================================
# Save helper (CLI only — not part of the core API)
# =============================================================================

def _nearest_valid_ratio(ratio_str: str) -> str:
    """Map any ratio string to the nearest supported value."""
    if ratio_str in _LEGACY_RATIO_MAP:
        return _LEGACY_RATIO_MAP[ratio_str]
    if ratio_str in ASPECT_RATIO_OPTIONS:
        return ratio_str

    def _f(r):
        try:
            w, h = r.split(":")
            return float(w) / float(h)
        except Exception:
            return 0.0

    target = _f(ratio_str)
    if target == 0.0:
        print(f"  ⚠ Cannot parse aspect ratio '{ratio_str}', using {DEFAULT_ASPECT_RATIO}")
        return DEFAULT_ASPECT_RATIO
    best = min(ASPECT_RATIO_OPTIONS, key=lambda r: abs(_f(r) - target))
    if best != ratio_str:
        print(f"  ℹ Aspect '{ratio_str}' not supported → using nearest '{best}'")
    return best


def _write_image_bytes(image_bytes: bytes, output_path: str, quality: int = 95) -> Optional[str]:
    """Write raw image bytes to disk, auto-converting format from extension."""
    try:
        from io import BytesIO
        from PIL import Image

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image = Image.open(BytesIO(image_bytes))
        ext = Path(output_path).suffix.lower()

        if not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            output_path = str(Path(output_path).with_suffix(f".{DEFAULT_OUTPUT_FORMAT}"))
            ext = f".{DEFAULT_OUTPUT_FORMAT}"

        if ext in [".jpg", ".jpeg"]:
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(output_path, "JPEG", quality=quality)
        elif ext == ".png":
            if image.mode == "P":
                image = image.convert("RGBA")
            image.save(output_path, "PNG")
        elif ext == ".webp":
            image.save(output_path, "WEBP", quality=quality)
        else:
            output_path = str(Path(output_path).with_suffix(f".{DEFAULT_OUTPUT_FORMAT}"))
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(output_path, "JPEG", quality=quality)

        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ Image saved: {output_path} ({image.width}x{image.height}, {file_size_kb:.1f} KB)")
        return output_path

    except Exception as e:
        print(f"❌ Failed to save image: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_and_save(
    prompt: str,
    output_path: str,
    image_size: str = DEFAULT_SIZE,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    quality: int = 95,
) -> Optional[str]:
    """Generate an image and save it to disk. Returns saved path or None."""
    gen = ImageGenerator()
    result = gen.generate(prompt=prompt, image_size=image_size, aspect_ratio=aspect_ratio)

    if not result.get("success"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return None

    b64 = result.get("b64")
    if not b64:
        data_url = result.get("data_url", "")
        if "," in data_url:
            b64 = data_url.split(",", 1)[1]
    if not b64:
        print("❌ No image data in result")
        return None

    try:
        image_bytes = base64.b64decode(b64)
    except Exception as e:
        print(f"❌ Base64 decode failed: {e}")
        return None

    return _write_image_bytes(image_bytes, output_path, quality)


# =============================================================================
# Command Line Interface
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="万擎文生图 - 调用 Kwaipilot API 生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/generate_image.py --prompt "A futuristic city skyline" --output city.jpg
  uv run scripts/generate_image.py --prompt-file prompt.txt --output result.jpg --size 2K --aspect-ratio 16:9
  uv run scripts/generate_image.py --prompt "Portrait" --output p.jpg --size 4K --aspect-ratio 9:16

API: https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate
Auth: SmartSSOSession (ks_aimate.sso_login_client via internal PyPI)
""",
    )

    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", "-p", help="图片描述提示词")
    prompt_group.add_argument("--prompt-file", "-f", help="包含提示词的文件路径")

    parser.add_argument("--output", "-o", required=True,
                        help="输出文件路径（.jpg/.png/.webp，无扩展名默认 .jpg）")
    parser.add_argument("--format", choices=["jpg", "png", "webp"], default=None,
                        help="强制输出格式（默认从扩展名自动识别，兜底 jpg）")
    parser.add_argument("--size", "-s", choices=SIZE_OPTIONS, default=DEFAULT_SIZE,
                        help=f"分辨率档位（默认 {DEFAULT_SIZE}）")
    parser.add_argument("--aspect-ratio", "-a", default=DEFAULT_ASPECT_RATIO,
                        help=f"宽高比（默认 {DEFAULT_ASPECT_RATIO}）。支持：{', '.join(ASPECT_RATIO_OPTIONS)}")
    parser.add_argument("--quality", "-q", type=int, default=95, metavar="1-100",
                        help="JPEG 质量 1-100（默认 95）")
    # Legacy aliases (ignored)
    parser.add_argument("--resolution", "-r", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--creator", "-c", default=None, help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Get prompt
    if args.prompt:
        prompt = args.prompt
    else:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read().strip()

    if not prompt:
        print("Error: Empty prompt")
        return 1

    # Resolve size (legacy --resolution alias)
    image_size = args.size
    if args.resolution and args.size == DEFAULT_SIZE:
        _legacy = {"1K": "1K", "2K": "2K", "4K": "4K", "1080p": "2K"}
        image_size = _legacy.get(args.resolution, DEFAULT_SIZE)

    # Resolve aspect ratio
    aspect_ratio = _nearest_valid_ratio(args.aspect_ratio)

    # Resolve output path
    output_path = args.output
    ext = Path(output_path).suffix.lower()
    if args.format:
        output_path = str(Path(output_path).with_suffix(f".{args.format}"))
    elif not ext or ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        output_path = str(Path(output_path).with_suffix(f".{DEFAULT_OUTPUT_FORMAT}"))

    result = generate_and_save(
        prompt=prompt,
        output_path=output_path,
        image_size=image_size,
        aspect_ratio=aspect_ratio,
        quality=args.quality,
    )

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
