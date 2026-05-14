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
"""万擎文生图脚本 - 调用内部API生成图片，集成 SmartSSOSession 自动处理认证"""

import argparse
import base64
import json
import os
import tempfile
import uuid

from ks_aimate.sso_login_client.session import SmartSSOSession


API_URL = "https://codeflicker.corp.kuaishou.com/eapi/kwaipilot/image/generate"
CDN_UPLOAD_URL = "https://design-out.staging.kuaishou.com/private-api/common/upload-file"
MODEL = "Gemini-3.1-Flash-Image-Preview"


class ImageGenerator:
    """万擎文生图工具 - 使用 SmartSSOSession 自动处理认证"""

    def __init__(self):
        self.client = SmartSSOSession()

    def _request(self, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "kwaipilot-platform": os.environ.get("KS_AGENT_PLATFORM", "myflicker"),
            "kwaipilot-version": "1.0.0",
        }
        response = self.client.request("POST", API_URL, json=payload, headers=headers)
        if response.status_code in (401, 403):
            # SSO 凭证过期，重建 Session 强制重新获取 token，重试一次
            self.client = SmartSSOSession()
            response = self.client.request("POST", API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def _upload_to_cdn(self, b64: str, mime_type: str) -> str | None:
        """将 base64 图片上传到内网 CDN，返回可渲染的 URL，失败返回 None"""
        import datetime
        ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                tmp.write(base64.b64decode(b64))
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                resp = self.client.request(
                    "POST",
                    CDN_UPLOAD_URL,
                    files={"file": (f"image_{ts}.{ext}", f, mime_type)},
                    data={"uploadType": "2"},
                )
            data = resp.json()
            if data.get("code") == 1:
                return data.get("data")
        except Exception:
            pass
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
        return None

    def generate(self, prompt: str, image_size: str = "2K", aspect_ratio: str = "1:1") -> dict:
        payload = {
            "chatId": f"img-chat-{uuid.uuid4().hex[:8]}",
            "sessionId": f"img-session-{uuid.uuid4().hex[:8]}",
            "requestId": f"img-req-{uuid.uuid4().hex[:8]}",
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
            }

        images = result.get("images", [])
        if not images:
            return {
                "success": False,
                "message": "API 返回成功但无图片数据，请尝试修改提示词后重试。",
            }

        img_data = images[0].get("data", "")
        mime_type = images[0].get("mimeType", "image/png")

        # 提取 base64 数据
        if img_data.startswith("data:"):
            b64 = img_data.split(",", 1)[1] if "," in img_data else img_data
        else:
            b64 = img_data

        # 上传到内网 CDN
        cdn_url = self._upload_to_cdn(b64, mime_type)
        if cdn_url:
            return {
                "success": True,
                "image_url": cdn_url,
                "usageInfo": result.get("usageInfo", {}),
                "message": "图像生成成功",
            }

        # CDN 上传失败时降级为 data URL
        return {
            "success": True,
            "data_url": f"data:{mime_type};base64,{b64}",
            "mime_type": mime_type,
            "usageInfo": result.get("usageInfo", {}),
            "message": "图像生成成功",
        }


def main():
    parser = argparse.ArgumentParser(description="万擎文生图")
    parser.add_argument("--prompt", required=True, help="图片描述提示词")
    parser.add_argument("--size", default="2K", choices=["512", "1K", "2K", "4K"], help="分辨率档位")
    parser.add_argument("--ratio", default="1:1", help="宽高比，例如 1:1, 16:9, 9:16 等")
    args = parser.parse_args()

    gen = ImageGenerator()
    result = gen.generate(args.prompt, args.size, args.ratio)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
