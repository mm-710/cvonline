#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31.0,<3",
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
"""万擎信息图生成脚本 v4.0 - 支持文生图和图生图（图片编辑），集成 SmartSSOSession 自动处理认证

Usage:
    # 文生图
    uv run generate_image.py --prompt "Your prompt here" --output output.jpg
    uv run generate_image.py --prompt-file prompt.md --output output.jpg --resolution 2K --aspect-ratio 9:16

    # 图生图（传入本地图片文件）
    uv run generate_image.py --prompt "保留主体，换成科技暗黑风" --image-file input.jpg --output output.jpg

    # 图生图（传入 base64 字符串）
    uv run generate_image.py --prompt "把背景改成深色" --image-base64 "data:image/png;base64,..." --output output.jpg
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path

from ks_aimate.sso_login_client import SmartSSOSession
from ks_aimate.wanqing_token_username import get_username

API_URL = "https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate"
MODEL = "Gemini-3.1-Flash-Image-Preview"

# Default creator: 从环境动态获取当前用户名
try:
    DEFAULT_CREATOR = get_username()
except Exception:
    DEFAULT_CREATOR = "xuekelindun"

# Default output format
DEFAULT_OUTPUT_FORMAT = "jpg"

# Resolution mapping: skill uses "2K"/"4K"/"1080p", API uses "512"/"1K"/"2K"/"4K"
RESOLUTION_MAP = {
    "2K": "2K",
    "4K": "4K",
    "1080p": "1K",
}

# v4.0: 扩展宽高比列表，与 API 枚举对齐
ASPECT_RATIO_OPTIONS = [
    # 横向
    "16:9", "4:3", "3:2", "21:9",
    # 方形
    "1:1",
    # 竖向
    "4:5", "2:3", "3:4", "9:16",
]


class ImageGenerator:
    """万擎图片生成工具 v4.0 - 同时支持文生图和图生图，使用 SmartSSOSession 自动处理认证"""

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
        response = self.client.request("POST", API_URL, json=payload, headers=headers)
        # Cookie 过期时服务端返回 401/403，重建 SSO 会话后重试一次
        if response.status_code in (401, 403):
            print("[SSO] 检测到认证失效（HTTP {}），正在重新建立 SSO 会话...".format(response.status_code),
                  file=sys.stderr)
            self.client = SmartSSOSession()
            response = self.client.request("POST", API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def generate(
        self,
        prompt: str,
        image_size: str = "2K",
        aspect_ratio: str = "16:9",
        images: list[dict] | None = None,
    ) -> dict:
        """
        生成图片。

        Args:
            prompt: 生成/编辑指令。
            image_size: 分辨率档位（"512"/"1K"/"2K"/"4K"），图生图时被忽略。
            aspect_ratio: 宽高比，如 "16:9"、"9:16"，图生图时被忽略（autoSize=True）。
            images: 参考图列表，格式为 [{"mimeType": "image/png", "data": "data:image/png;base64,..."}]。
                    传入时自动进入图生图（IMAGE_TO_IMAGE）模式；为 None 时为文生图（TEXT_TO_IMAGE）。
        """
        is_img2img = bool(images)

        request_id = f"img-req-{uuid.uuid4().hex[:8]}"
        payload: dict = {
            "chatId": f"img-chat-{uuid.uuid4().hex[:8]}",
            "sessionId": f"img-session-{uuid.uuid4().hex[:8]}",
            "requestId": request_id,
            "model": MODEL,
            "prompt": prompt,
            "timeout": 120,
        }

        if is_img2img:
            # 图生图：传入参考图，使用 autoSize 让服务端自动决定尺寸
            payload["images"] = images
            payload["autoSize"] = True
        else:
            # 文生图：使用自定义尺寸和宽高比
            payload["autoSize"] = False
            payload["generationConfig"] = {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size,
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

        api_images = result.get("images", [])
        if not api_images:
            return {
                "success": False,
                "message": "API 返回成功但无图片数据",
                "建议操作": "请尝试修改提示词后重试。",
            }

        img_data = api_images[0].get("data", "")
        mime_type = api_images[0].get("mimeType", "image/png")

        # 提取 base64 数据
        if img_data.startswith("data:"):
            b64 = img_data.split(",", 1)[1] if "," in img_data else img_data
        else:
            b64 = img_data

        # 上传到内网 CDN，获取可渲染的 URL
        import tempfile
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

        mode = result.get("usageInfo", {}).get("mode", "IMAGE_TO_IMAGE" if is_img2img else "TEXT_TO_IMAGE")

        if cdn_url:
            return {
                "success": True,
                "image_url": cdn_url,
                "mode": mode,
                "usageInfo": result.get("usageInfo", {}),
                "message": result.get("message", ""),
            }

        # CDN 上传失败时降级为 data URL
        return {
            "success": True,
            "data_url": f"data:{mime_type};base64,{b64}",
            "mime_type": mime_type,
            "mode": mode,
            "usageInfo": result.get("usageInfo", {}),
            "message": result.get("message", ""),
        }

    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        resolution: str = "2K",
        aspect_ratio: str = "16:9",
        creator: str = DEFAULT_CREATOR,
        quality: int = 95,
        image_file: str | None = None,
        image_base64: str | None = None,
    ) -> str | None:
        """
        生成图片并保存到文件。

        Args:
            prompt: 生成/编辑指令。
            output_path: 输出文件路径（.jpg/.png/.webp）。
            resolution: 分辨率档位（"2K"/"4K"/"1080p"），仅文生图有效。
            aspect_ratio: 宽高比，仅文生图有效。
            creator: 创作者标识（保留接口兼容性）。
            quality: JPEG/WEBP 质量 1-100。
            image_file: 参考图本地路径，传入时自动进入图生图模式。
            image_base64: 参考图 base64 字符串（data URL 或纯 base64），与 image_file 互斥。

        Returns:
            保存的文件路径，失败时返回 None。
        """
        # 构造 images 参数
        images: list[dict] | None = None

        if image_file:
            try:
                with open(image_file, "rb") as f:
                    raw = f.read()
                mime = mimetypes.guess_type(image_file)[0] or "image/png"
                b64 = base64.b64encode(raw).decode()
                images = [{"mimeType": mime, "data": f"data:{mime};base64,{b64}"}]
                print(f"[图生图] 已读取参考图: {image_file} ({len(raw) / 1024:.1f} KB, {mime})")
            except Exception as e:
                print(json.dumps({"success": False, "message": f"读取参考图失败: {e}"}, ensure_ascii=False))
                return None

        elif image_base64:
            # 支持纯 base64 或 data URL 两种格式
            if not image_base64.startswith("data:"):
                image_base64 = f"data:image/png;base64,{image_base64}"
            images = [{"data": image_base64}]
            print("[图生图] 已接收 base64 参考图")

        image_size = RESOLUTION_MAP.get(resolution, "2K")
        result = self.generate(
            prompt,
            image_size=image_size,
            aspect_ratio=aspect_ratio,
            images=images,
        )

        if not result.get("success"):
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return None

        mode = result.get("mode", "")
        print(f"[模式] {mode}")

        # 获取图片字节
        if "image_url" in result:
            try:
                import requests as _req
                resp = _req.get(result["image_url"], timeout=60)
                resp.raise_for_status()
                image_bytes = resp.content
            except Exception as e:
                print(json.dumps({
                    "success": False,
                    "message": f"CDN 图片下载失败: {e}",
                }, ensure_ascii=False, indent=2))
                return None
        else:
            data_url = result.get("data_url", "")
            if "," in data_url:
                b64 = data_url.split(",", 1)[1]
            else:
                b64 = data_url
            image_bytes = base64.b64decode(b64)

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 确定扩展名
        ext = Path(output_path).suffix.lower()
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            output_path = str(Path(output_path).with_suffix(f'.{DEFAULT_OUTPUT_FORMAT}'))
            ext = f'.{DEFAULT_OUTPUT_FORMAT}'

        # 使用 Pillow 保存（如不可用则直接写入原始字节）
        try:
            from PIL import Image
            from io import BytesIO
            image = Image.open(BytesIO(image_bytes))
            if ext in ['.jpg', '.jpeg']:
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                image.save(output_path, 'JPEG', quality=quality)
            elif ext == '.png':
                if image.mode == 'P':
                    image = image.convert('RGBA')
                image.save(output_path, 'PNG')
            elif ext == '.webp':
                image.save(output_path, 'WEBP', quality=quality)
            else:
                output_path = str(Path(output_path).with_suffix(f'.{DEFAULT_OUTPUT_FORMAT}'))
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                image.save(output_path, 'JPEG', quality=quality)
            print(f"[保存] {output_path} ({image.width}x{image.height})", file=sys.stderr)
        except ImportError:
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            print(f"[保存] {output_path} ({len(image_bytes) / 1024:.1f} KB)", file=sys.stderr)

        # 最终输出 JSON 到 stdout，供 Agent 捕获 image_url / data_url
        output_result = {
            "success": True,
            "output_path": output_path,
            "mode": result.get("mode", ""),
            "usageInfo": result.get("usageInfo", {}),
        }
        if "image_url" in result:
            output_result["image_url"] = result["image_url"]
        elif "data_url" in result:
            output_result["data_url"] = result["data_url"]
            output_result["mime_type"] = result.get("mime_type", "")
        print(json.dumps(output_result, ensure_ascii=False))

        return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="万擎信息图生成 v4.0（文生图 + 图生图）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 文生图
  uv run generate_image.py --prompt "咖啡因作用机制信息图" --output out.jpg
  uv run generate_image.py --prompt-file prompt.md --output out.jpg --resolution 2K --aspect-ratio 9:16

  # 图生图（按已有图修改风格）
  uv run generate_image.py --prompt "保留内容，换成赛博朋克风格" --image-file route-A.jpg --output edited.jpg

  # 图生图（base64 输入）
  uv run generate_image.py --prompt "把背景改成深色" --image-base64 "data:image/png;base64,..." --output edited.jpg
""",
    )

    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", "-p", help="图片描述/编辑提示词")
    prompt_group.add_argument("--prompt-file", "-f", help="提示词文件路径")

    parser.add_argument("--output", "-o", required=True,
                        help="输出文件路径（.jpg/.png/.webp，默认 .jpg）")
    parser.add_argument("--format", choices=["jpg", "png", "webp"], default=None,
                        help="强制输出格式（默认从扩展名检测，fallback 为 jpg）")
    parser.add_argument("--resolution", "-r", choices=["2K", "4K", "1080p"], default="2K",
                        help="分辨率档位（默认 2K，仅文生图有效）")
    parser.add_argument("--aspect-ratio", "-a", choices=ASPECT_RATIO_OPTIONS, default="16:9",
                        help="宽高比（默认 16:9，仅文生图有效）")
    parser.add_argument("--quality", "-q", type=int, choices=range(1, 101), metavar="1-100",
                        default=95, help="JPEG/WEBP 质量 1-100（默认 95）")
    parser.add_argument("--creator", "-c", default=DEFAULT_CREATOR,
                        help=f"创作者用户名（默认 {DEFAULT_CREATOR}）")

    # v4.0 新增：图生图参数（二选一）
    image_group = parser.add_mutually_exclusive_group()
    image_group.add_argument("--image-file", "-i",
                             help="参考图本地路径（传入后自动进入图生图模式）")
    image_group.add_argument("--image-base64",
                             help="参考图 base64 字符串或 data URL（与 --image-file 互斥）")

    args = parser.parse_args()

    # 读取提示词
    if args.prompt:
        prompt = args.prompt
    else:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read().strip()

    if not prompt:
        print(json.dumps({"success": False, "message": "提示词为空"}, ensure_ascii=False))
        return 1

    # 处理输出路径扩展名
    output_path = args.output
    output_ext = Path(output_path).suffix.lower()
    if args.format:
        output_path = str(Path(output_path).with_suffix(f'.{args.format}'))
    elif not output_ext or output_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        output_path = str(Path(output_path).with_suffix(f'.{DEFAULT_OUTPUT_FORMAT}'))

    gen = ImageGenerator()
    result = gen.generate_and_save(
        prompt=prompt,
        output_path=output_path,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        creator=args.creator,
        quality=args.quality,
        image_file=args.image_file,
        image_base64=args.image_base64,
    )

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
