#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate>=1.0.30",
# ]
#
# [tool.uv.sources]
# "ks_aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///
"""
docs-shuttle: Push MD 文件到 Docs

支持两种模式:
  1. 导入模式 (import): 创建新文档
  2. 编辑模式 (edit): 修改已有文档，支持追加/替换

用法:
    # 导入模式
    uv run --refresh-package ks_aimate push.py <file.md>
    
    # 编辑模式
    uv run --refresh-package ks_aimate push.py <file.md> --mode edit --doc-id <docId或URL> [--position <位置>]

参数:
    file.md             要上传的 Markdown 文件
    --mode              操作模式: import (默认) 或 edit
    --doc-id            文档 ID 或完整 URL（edit 模式必需）
    --position          编辑位置: REPLACE_ALL (默认) / APPEND_TAIL / APPEND_HEAD

示例:
    # 导入新文档
    uv run --refresh-package ks_aimate push.py ./design.md
    
    # 编辑已有文档（全文替换）
    uv run --refresh-package ks_aimate push.py ./design.md --mode edit --doc-id fcABxxx
    uv run --refresh-package ks_aimate push.py ./design.md --mode edit --doc-id https://docs.corp.kuaishou.com/d<skill_directory>
    
    # 编辑已有文档（追加到末尾）
    uv run --refresh-package ks_aimate push.py ./changelog.md --mode edit --doc-id fcABxxx --position APPEND_TAIL
"""

import sys
import os
import argparse
import re
from pathlib import Path
from typing import Optional, Dict
import json
from ks_aimate.sso_login_client import SmartSSOSession
# 配置
BASE_URL = "https://docs.corp.kuaishou.com"


def get_sso_client():
    """获取 SSO 客户端"""
    return SmartSSOSession()


def _check_resp(resp, step: str) -> Optional[Dict]:
    """检查响应是否有效，返回解析后的 JSON；失败时打印原因并返回 None"""
    if resp.status_code != 200:
        print(f"❌ {step} 失败 (HTTP {resp.status_code})，请检查 SSO 登录状态")
        print(f"   响应体: {repr(resp.text[:200])}")
        return None
    if not resp.text.strip():
        print(f"❌ {step} 失败：服务器返回空响应 (HTTP {resp.status_code})，SSO Cookie 可能已过期")
        print("   建议：尝试清理 Cookie 后重新运行（参见 SmartSSOSession 错误提示）")
        return None
    try:
        return resp.json()
    except Exception as e:
        print(f"❌ {step} 失败：响应非 JSON 格式 — {e}")
        print(f"   响应体: {repr(resp.text[:200])}")
        return None


def get_upload_token(client, filename: str, filesize: int) -> Optional[Dict]:
    """获取上传凭证"""
    url = f"{BASE_URL}/merlot/api/docs/yfile/v2/upload?um=false"
    data = {
        "fileName": filename,
        "fileType": "text/markdown",
        "fileSize": filesize,
        "uploadType": "upload"
    }
    resp = client.request("POST", url, json=data)
    result = _check_resp(resp, "获取上传凭证")
    if result is None:
        return None
    
    if result.get("code") == 0 and result.get("result"):
        res = result["result"]
        token_vo = res.get("tokenVo", {})
        upload_token = token_vo.get("token") or res.get("uploadToken")
        cosmo_yid = res.get("id") or res.get("cosmoYId")
        if upload_token and cosmo_yid:
            return {"uploadToken": upload_token, "cosmoYId": cosmo_yid}
    return None


def upload_file(upload_token: str, content: bytes) -> bool:
    """上传文件内容"""
    import urllib.request
    import ssl
    
    url = f"https://upload.kuaishouzt.com/api/upload?upload_token={upload_token}"
    headers = {
        "Content-Type": "text/markdown",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/"
    }
    
    req = urllib.request.Request(url, data=content, headers=headers, method="POST")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            return resp.status == 200
    except Exception:
        return False


def confirm_upload(client, filename: str, cosmo_yid: int) -> Optional[Dict]:
    """确认导入"""
    url = f"{BASE_URL}/convert/api/v3/uploadFeedback?um=true"
    data = {
        "parentId": "",  # 空字符串表示「我的空间」根目录
        "parentShortcutId": "",
        "fileName": filename,
        "docTypeEn": "doc",
        "cosmoYId": cosmo_yid
    }
    
    resp = client.request("POST", url, json=data)
    result = _check_resp(resp, "确认导入")
    if result is None:
        return None

    if result.get("code") == 0 and result.get("result"):
        r = result["result"]
        doc_id = r.get("cosmoId") or r.get("docId")
        return {
            "docId": doc_id,
            "url": r.get("cosmoUrl") or r.get("openDocUrl") or f"{BASE_URL}/d/home/{doc_id}"
        }
    return None


def import_document(client, file_path: Path) -> Optional[Dict]:
    """导入模式：创建新文档"""
    content = file_path.read_bytes()
    filename = file_path.name
    filesize = len(content)

    print(f"📤 上传: {filename}")
    
    # 1. 获取上传凭证
    token_info = get_upload_token(client, filename, filesize)
    if not token_info:
        print("❌ 获取上传凭证失败")
        return None
    
    # 2. 上传文件
    if not upload_file(token_info["uploadToken"], content):
        print("❌ 上传文件失败")
        return None
    
    # 3. 确认导入
    result = confirm_upload(client, filename, token_info["cosmoYId"])
    if not result:
        print("❌ 确认导入失败")
        return None
    
    print("✅ 上传成功!")
    return result


def parse_doc_id(url_or_id: str) -> str:
    """从 URL 或直接 docId 中提取 docId"""
    patterns = [
        r'/d/home/(fc[A-Za-z0-9_-]+)',
        r'/k/home/[^/]+/(fc[A-Za-z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id if not url_or_id.startswith('http') else url_or_id


def edit_document(client, file_path: Path, doc_id: str, position: str = "REPLACE_ALL") -> bool:
    """编辑模式：修改已有文档"""
    content = file_path.read_text(encoding='utf-8')
    
    print(f"✏️  编辑文档: {doc_id}")
    print(f"📝 位置: {position}")
    
    # 正确的 API 路径和参数
    url = f"{BASE_URL}/merlot/e/api/skills/docs/word-simple-edit?um=false"
    data = {
        "docId": doc_id,
        "mdContent": content,  # 参数名是 mdContent，不是 content
        "inputPosition": position  # 参数名是 inputPosition，不是 position
    }
    
    resp = client.request("POST", url, json=data)
    result = _check_resp(resp, "编辑文档")
    if result is None:
        return False

    if result.get("code") == 0:
        version = result.get("result", "")
        print(f"✅ 编辑成功! (版本号: {version})")
        return True
    else:
        print(f"❌ 编辑失败: {result.get('message', 'Unknown error')}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Push Markdown 文件到 Docs',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("file", type=Path, help="要上传的 Markdown 文件")
    parser.add_argument("--mode", choices=["import", "edit"], default="import",
                       help="操作模式（默认：import）")
    parser.add_argument("--doc-id", help="文档 ID 或 URL（edit 模式必需）")
    parser.add_argument("--position", choices=["REPLACE_ALL", "APPEND_TAIL", "APPEND_HEAD"],
                       default="REPLACE_ALL", help="编辑位置（edit 模式）")
    
    args = parser.parse_args()
    
    # 检查文件
    if not args.file.exists():
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)
    
    if not args.file.is_file():
        print(f"❌ 不是文件: {args.file}")
        sys.exit(1)
    
    # 检查 edit 模式参数
    if args.mode == "edit" and not args.doc_id:
        print("❌ edit 模式需要提供 --doc-id 参数")
        sys.exit(1)
    
    # 获取 SSO 客户端
    client = get_sso_client()
    if not client:
        print("❌ 无法获取 SSO 客户端")
        sys.exit(1)
    
    # 执行操作
    if args.mode == "import":
        result = import_document(client, args.file)
        if result:
            print(f"📄 文档ID: {result['docId']}")
            print(f"<a href=\"{result['url']}\" target=\"_blank\">🔗 点击这里访问</a>")
        else:
            sys.exit(1)
    else:  # edit mode
        doc_id = parse_doc_id(args.doc_id)
        if edit_document(client, args.file, doc_id, args.position):
            print(f"📄 文档ID: {doc_id}")
            print(f"<a href=\"{BASE_URL}/d/home/{doc_id}\" target=\"_blank\">🔗 点击这里访问</a>")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
