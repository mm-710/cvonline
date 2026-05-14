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
"""万擎图生图脚本 - 支持1~14张参考图 + 文本提示词生成新图片"""

import argparse
import base64
import json
import mimetypes
import os
import tempfile
import uuid

from ks_aimate.sso_login_client.session import SmartSSOSession

_sandbox_uuid = os.environ.get("SANDBOX_UUID", "")
_platform = os.environ.get("KS_AGENT_PLATFORM", "")

if _sandbox_uuid and _platform == "myflicker":
    WORKSPACE = f"/data/aime/{_sandbox_uuid}/workspace"
    ATTACHMENT_DIR = f"{WORKSPACE}/local-file-in-chat"
else:
    # 本地 IDE 环境：附件路径由调用方通过 --images 明确传入
    WORKSPACE = ""
    ATTACHMENT_DIR = ""

API_URL = "https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate"
MODEL = "Gemini-3.1-Flash-Image-Preview"

HEADERS = {
    "Content-Type": "application/json",
    "kwaipilot-platform": os.environ.get("KS_AGENT_PLATFORM", "myflicker"),
    "kwaipilot-version": "1.0.0",
}


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
    image_size: str = "1K",
    aspect_ratio: str = "1:1",
) -> dict:
    """
    image_paths: 当前消息附件的路径列表（均在 workspace/local-file-in-chat/ 下）；
                 若为空则 fallback 扫描 local-file-in-chat 目录（按修改时间倒序取最新图片）
    """
    if not image_paths:
        image_paths = list_attachment_images()
        if not image_paths:
            hint = f"附件目录 {ATTACHMENT_DIR}" if ATTACHMENT_DIR else "附件目录（本地环境需通过 --images 明确传入路径）"
            return {
                "success": False,
                "message": f"{hint} 中未找到图片。建议操作：请通过 --images 参数传入图片路径，或在对话框上传图片附件后重试。",
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

    client = SmartSSOSession()
    try:
        resp = client.request("POST", API_URL, json=payload, headers=HEADERS, timeout=130)
        if resp.status_code in (401, 403):
            # SSO 凭证过期，重建 Session 强制重新获取 token，重试一次
            client = SmartSSOSession()
            resp = client.request("POST", API_URL, json=payload, headers=HEADERS, timeout=130)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        text = getattr(getattr(e, "response", None), "text", "")
        if status:
            return {
                "success": False,
                "message": f"HTTP错误 {status}: {text}。建议操作：检查网络连接或联系管理员。",
            }
        if "timed out" in str(e).lower() or "timeout" in str(e).lower():
            return {
                "success": False,
                "message": "请求超时（>130秒）。建议操作：图片较大时可尝试降低分辨率后重试。",
            }
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
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
    cdn_url = None
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(base64.b64decode(b64))
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            upload_resp = client.request(
                "POST",
                "https://design-out.staging.kuaishou.com/private-api/common/upload-file",
                files={"file": (f"image_{ts}.{ext}", f, mime_type)},
                data={"uploadType": "2"},
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
            "usageInfo": result.get("usageInfo", {}),
            "message": result.get("message", ""),
        }

    # CDN 上传失败时降级为 data URL
    return {
        "success": True,
        "data_url": f"data:{mime_type};base64,{b64}",
        "mime_type": mime_type,
        "usageInfo": result.get("usageInfo", {}),
        "message": result.get("message", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="万擎图生图（1~14张参考图）")
    parser.add_argument("--prompt", required=True, help="编辑/合成指令")
    parser.add_argument(
        "--images",
        nargs="*",
        default=None,
        metavar="IMAGE_PATH",
        help="当前消息附件的图片路径（均在 workspace/local-file-in-chat/ 下），支持1~14张；省略时自动扫描该目录兜底",
    )
    parser.add_argument(
        "--size",
        default="2K",
        choices=["512", "1K", "2K", "4K"],
        help="分辨率档位（默认2K）",
    )
    parser.add_argument(
        "--ratio",
        default="1:1",
        help="宽高比，例如 1:1, 16:9, 9:16 等",
    )
    args = parser.parse_args()

    result = image_to_image(
        args.prompt,
        image_paths=args.images or [],
        image_size=args.size,
        aspect_ratio=args.ratio,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
