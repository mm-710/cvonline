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
"""万擎图生图脚本 - 支持1~14张参考图 + 文本提示词生成新图片

支持从本地图片文件（或 workspace/local-file-in-chat 附件目录）加载参考图，
结合 prompt 生成新图片，输出到指定路径（JPG/PNG/WEBP）。

Usage:
    uv run scripts/generate_image_ref.py --prompt "把背景换成雪山" --image ref.jpg --output result.jpg
    uv run scripts/generate_image_ref.py --prompt "风格融合" --images img1.jpg img2.jpg --output result.jpg
    uv run scripts/generate_image_ref.py --prompt-file prompt.txt --image ref.jpg --output result.jpg
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional

import requests
from ks_aimate.sso_login_client import SmartSSOSession

# SANDBOX_UUID 仅用于沙箱环境的附件目录路径，非必需
_sandbox_uuid = os.environ.get("SANDBOX_UUID")
ATTACHMENT_DIR = f"/data/aime/{_sandbox_uuid}/workspace/local-file-in-chat" if _sandbox_uuid else None

API_URL = "https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate"
MODEL = "Gemini-3.1-Flash-Image-Preview"

HEADERS = {
    "Content-Type": "application/json",
    "kwaipilot-platform": "myflicker",
    "kwaipilot-version": "1.0.0",
}

SIZE_OPTIONS = ["512", "1K", "2K", "4K"]
ASPECT_RATIO_OPTIONS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

DEFAULT_SIZE = "2K"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_OUTPUT_FORMAT = "jpg"


def load_image_as_base64(image_path: str) -> tuple[str, str]:
    """读取图片文件，返回 (data_url, mime_type)"""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}", mime_type


def list_attachment_images() -> list[str]:
    """列出 workspace/local-file-in-chat 目录下的所有图片文件，按修改时间排序（最新在前）"""
    if not ATTACHMENT_DIR or not os.path.isdir(ATTACHMENT_DIR):
        return []
    exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    files = [
        os.path.join(ATTACHMENT_DIR, f)
        for f in os.listdir(ATTACHMENT_DIR)
        if os.path.splitext(f)[1].lower() in exts
    ]
    return sorted(files, key=os.path.getmtime, reverse=True)


def image_to_image(
    prompt: str,
    image_paths: list[str] | None = None,
    image_size: str = DEFAULT_SIZE,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
) -> dict:
    """
    image_paths: 参考图片路径列表（1~14张）；
                 若为空则 fallback 扫描 workspace/local-file-in-chat 目录（按修改时间倒序取最新图片）
    """
    if not image_paths:
        image_paths = list_attachment_images()
        if not image_paths:
            return {
                "success": False,
                "message": f"附件目录 {ATTACHMENT_DIR} 中未找到图片。建议操作：请先在对话框上传图片附件后重试。",
            }

    if len(image_paths) > 14:
        return {
            "success": False,
            "message": f"参考图最多14张，当前传入 {len(image_paths)} 张。建议操作：请减少图片数量后重试。",
        }

    images = []
    for path in image_paths:
        if not os.path.isfile(path):
            return {
                "success": False,
                "message": f"图片文件不存在: {path}。建议操作：请确认图片路径是否正确后重试。",
            }
        data_url, mime = load_image_as_base64(path)
        images.append({"data": data_url, "mimeType": mime})

    request_id = f"i2i-req-{uuid.uuid4().hex[:8]}"
    session_id = f"i2i-session-{uuid.uuid4().hex[:8]}"
    chat_id = f"i2i-chat-{uuid.uuid4().hex[:8]}"

    payload = {
        "chatId": chat_id,
        "sessionId": session_id,
        "requestId": request_id,
        "model": MODEL,
        "prompt": prompt,
        "images": images,
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
        client = SmartSSOSession()
        resp = None
        for attempt in range(2):
            resp = client.request("POST", API_URL, json=payload, headers=HEADERS, timeout=130)
            if resp.status_code in (401, 403) and attempt == 0:
                # Cookie/凭证过期，重新初始化 SmartSSOSession 触发 SSO 登录后重试
                print(f"  ⚠ 检测到认证失败（HTTP {resp.status_code}），重新触发 SSO 登录后重试...")
                client = SmartSSOSession()
                continue
            break
        resp.raise_for_status()
        result = resp.json()
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "message": f"HTTP错误 {e.response.status_code}: {e.response.text}。建议操作：检查网络连接或联系管理员。",
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "请求超时（>130秒）。建议操作：图片较大时可尝试降低分辨率后重试。",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"请求异常: {e}。建议操作：检查网络连接后重试。",
        }

    if not result.get("success"):
        return {
            "success": False,
            "message": result.get("message", "未知错误") + "。建议操作：检查提示词内容是否合规。",
            "raw": result,
        }

    images_resp = result.get("images", [])
    if not images_resp:
        return {
            "success": False,
            "message": "API 返回成功但无图片数据。建议操作：重新尝试或调整提示词。",
            "raw": result,
        }

    img_data = images_resp[0].get("data", "")
    mime_type = images_resp[0].get("mimeType", "image/png")

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
            upload_resp = SmartSSOSession().request(
                "POST",
                "https://design-out.staging.kuaishou.com/private-api/common/upload-file",
                files={"file": (f"image.{ext}", f, mime_type)},
                data={"uploadType": "2"},
                timeout=(5, 15),
            )
        upload_data = upload_resp.json()
        if upload_data.get("code") == 1:
            cdn_url = upload_data.get("data")
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
    image_paths: list[str],
    image_size: str = DEFAULT_SIZE,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    quality: int = 95,
) -> Optional[str]:
    """Generate an image with reference images and save to disk. Returns saved path or None."""
    result = image_to_image(
        prompt=prompt,
        image_paths=image_paths,
        image_size=image_size,
        aspect_ratio=aspect_ratio,
    )

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
        description="万擎图生图（1~14张参考图）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 单张参考图
  uv run scripts/generate_image_ref.py --prompt "把背景换成雪山" --image ref.jpg --output result.jpg

  # 多张参考图（1~14张）
  uv run scripts/generate_image_ref.py --prompt "风格融合" --images img1.jpg img2.jpg --output result.jpg

  # 从 prompt 文件读取
  uv run scripts/generate_image_ref.py --prompt-file prompt.txt --image ref.jpg --output result.jpg

  # 自定义分辨率和宽高比
  uv run scripts/generate_image_ref.py --prompt "风格迁移" --image ref.jpg --output result.jpg --size 4K --aspect-ratio 16:9

API: https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate
Auth: SmartSSOSession (ks_aimate via internal PyPI)
最多支持 14 张参考图
""",
    )

    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", "-p", help="编辑/合成指令")
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

    # Reference image inputs
    ref_group = parser.add_mutually_exclusive_group(required=True)
    ref_group.add_argument("--image", "-i", metavar="IMAGE_PATH",
                           help="单张参考图路径")
    ref_group.add_argument("--images", nargs="+", metavar="IMAGE_PATH",
                           help="1~14张参考图路径")

    # Legacy aliases (ignored)
    parser.add_argument("--resolution", "-r", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--creator", "-c", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--image-url", default=None, help=argparse.SUPPRESS)

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

    # Warn about deprecated --image-url
    if args.image_url:
        print("Warning: --image-url 已不再支持，请将图片下载到本地后使用 --image 参数。")
        return 1

    # Collect reference image paths
    image_paths = [args.image] if args.image else args.images

    # Validate paths exist
    for p in image_paths:
        if not os.path.isfile(p):
            print(f"Error: 图片文件不存在: {p}")
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
        image_paths=image_paths,
        image_size=image_size,
        aspect_ratio=aspect_ratio,
        quality=args.quality,
    )

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
