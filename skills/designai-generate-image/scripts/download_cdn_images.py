#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""下载 CDN 图片到本地，根据 KS_AGENT_PLATFORM 自动选择保存目录"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def download_images(urls: list[str], skill_directory: str) -> dict:
    platform = os.environ.get("KS_AGENT_PLATFORM", "codeflicker")
    sandbox_uuid = os.environ.get("SANDBOX_UUID", "")

    if platform == "myflicker" and sandbox_uuid:
        output_dir = Path(f"/data/aime/{sandbox_uuid}/workspace/local-file-in-chat")
    else:
        output_dir = Path(skill_directory) / "tmp"

    output_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    local_paths = []
    for idx, url in enumerate(urls):
        # 从 URL 推断扩展名，fallback 到 .png
        ext = Path(url.split("?")[0]).suffix or ".png"
        filename = f"ref_{ts}_{idx}{ext}"
        save_path = output_dir / filename

        try:
            urllib.request.urlretrieve(url, save_path)
            local_paths.append(str(save_path))
        except urllib.error.URLError as e:
            return {
                "success": False,
                "message": f"下载图片失败（{url}）: {e}。建议操作：检查 URL 是否有效或网络是否可访问。",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存图片失败（{url}）: {e}。建议操作：检查目录写权限。",
            }

    return {
        "success": True,
        "local_paths": local_paths,
        "output_dir": str(output_dir),
        "platform": platform,
    }


def main():
    parser = argparse.ArgumentParser(description="下载 CDN 图片到本地")
    parser.add_argument("--urls", nargs="+", required=True, help="CDN 图片 URL 列表")
    parser.add_argument("--skill-directory", required=True, help="skill 目录路径（来自 <skill_directory>）")
    args = parser.parse_args()

    result = download_images(args.urls, args.skill_directory)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
