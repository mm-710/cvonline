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
docs-shuttle: 导出 Docs 文档 / 普通表格 / 万维表格

支持的文档类型及导出格式:
  doc       (普通文档 /d/home/ /k/home/)  → docx（默认）或 pdf
  sheet     (普通表格 /s/home/ /t/home/)  → xlsx（固定）
  metasheet (万维表格 /m/home/ /b/home/)  → xlsx（固定）

用法:
    uv run --refresh-package ks_aimate download.py <doc_id_or_url> [--format docx|pdf|xlsx] [-o output_path]

示例:
    uv run --refresh-package ks_aimate download.py https://docs.corp.kuaishou.com/d<skill_directory>
    uv run --refresh-package ks_aimate download.py https://docs.corp.kuaishou.com/s<skill_directory>
    uv run --refresh-package ks_aimate download.py https://docs.corp.kuaishou.com/m<skill_directory>
    uv run --refresh-package ks_aimate download.py fcABxxx --format pdf
    uv run --refresh-package ks_aimate download.py https://docs.corp.kuaishou.com/d<skill_directory> -o ./output.docx
"""

import sys
import re
import time
import argparse
from pathlib import Path
from typing import Optional, Union
from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://docs.corp.kuaishou.com"

# 各类型对应的权限检查 scene 参数
DOC_TYPE_SCENE = {
    "doc": "doc",
    "sheet": "sheet",
    "metasheet": "metasheet",
}


def get_sso_client():
    return SmartSSOSession()


def parse_doc_id(url_or_id: str) -> Optional[str]:
    """从 URL 或直接 ID 解析 docId"""
    if re.match(r'^fc[A-Za-z0-9_-]+$', url_or_id):
        return url_or_id
    patterns = [
        r"/d/home/(fc[A-Za-z0-9_-]+)",
        r"/d/export/(fc[A-Za-z0-9_-]+)",
        r"/k/home/[^/]+/(fc[A-Za-z0-9_-]+)",
        r"/s/home/(fc[A-Za-z0-9_-]+)",
        r"/t/home/[^/]+/(fc[A-Za-z0-9_-]+)",
        r"/m/home/(fc[A-Za-z0-9_-]+)",
        r"/b/home/[^/]+/(fc[A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return None


def detect_doc_type(url_or_id: str, client) -> str:
    """检测文档类型：doc / sheet / metasheet
    先从 URL 路径推断，无法判断时查 meta 接口。
    """
    if re.search(r"/m/home/|/b/home/", url_or_id):
        return "metasheet"
    if re.search(r"/s/home/|/t/home/", url_or_id):
        return "sheet"
    if re.search(r"/d/home/|/k/home/", url_or_id):
        return "doc"

    doc_id = parse_doc_id(url_or_id)
    if doc_id:
        resp = client.request("POST", f"{BASE_URL}/merlot/api/docs/cosmo/meta/{doc_id}?um=false", json={})
        result = resp.json()
        if result.get("code") == 0:
            doc_type_en = result.get("result", {}).get("docTypeEn", "").lower()
            if "metasheet" in doc_type_en or "meta_sheet" in doc_type_en:
                return "metasheet"
            if "sheet" in doc_type_en:
                return "sheet"
    return "doc"


def get_doc_title(client, doc_id: str) -> Optional[str]:
    """获取文档标题"""
    resp = client.request("POST", f"{BASE_URL}/merlot/api/docs/cosmo/meta/{doc_id}?um=false", json={})
    result = resp.json()
    if result.get("code") == 0:
        meta = result.get("result", {})
        return meta.get("docName") or meta.get("name") or meta.get("title")
    return None


def sanitize_filename(name: str) -> str:
    """去除文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()


def check_download_permission(client, doc_id: str, scene: str = "doc") -> bool:
    """检查文档下载权限"""
    url = f"{BASE_URL}/merlot/api/share-apply/download/check"
    params = {"cosmoId": doc_id, "func": "download_all", "scene": scene}
    print(f"🔐 检查下载权限...")
    resp = client.request("GET", url, params=params)
    result = resp.json()
    if result.get("code") != 0:
        print(f"❌ 权限检查失败: {result.get('message', '未知错误')}")
        return False
    need_apply = result.get("result", {}).get("needApply", True)
    if need_apply:
        print("❌ 无下载权限，需要申请")
        return False
    print("✅ 权限检查通过")
    return True


def trigger_export(client, doc_id: str, fmt: str, doc_type: str = "doc") -> Optional[str]:
    """触发导出任务，返回 task_id"""
    if doc_type == "metasheet":
        url = f"{BASE_URL}/metasheet/api/export/{doc_id}"
    elif doc_type == "sheet":
        url = f"{BASE_URL}/s/export/{doc_id}"
    else:
        url = f"{BASE_URL}/d/export/{doc_id}"

    print(f"📤 触发导出任务 (type={doc_type}, format={fmt})...")
    resp = client.request("GET", url, params={"format": fmt})
    result = resp.json()
    if result.get("code") == 0:
        task_id = result.get("result")
        print(f"✅ 任务ID: {task_id}")
        return task_id
    print(f"❌ 触发导出失败: {result.get('message', '未知错误')}")
    return None


def poll_pending(client, doc_id: str, task_id: str, doc_type: str = "doc",
                 max_retries: int = 15) -> Optional[Union[str, bytes]]:
    """轮询导出任务状态。
    - doc/sheet: 返回下载 URL（str）
    - metasheet: downloadFile 直接返回文件流（bytes）
    """
    print(f"⏳ 等待导出任务完成...")

    if doc_type == "metasheet":
        url = f"{BASE_URL}/metasheet/api/downloadFile/{doc_id}"
        params = {"key": task_id, "filePath": "null"}
        for attempt in range(1, max_retries + 1):
            resp = client.request("GET", url, params=params)
            ct = resp.headers.get("Content-Type", "")
            if resp.status_code == 200 and "spreadsheet" in ct and len(resp.content) > 100:
                print(f"✅ 文件已就绪")
                return resp.content  # bytes
            print(f"   [{attempt}/{max_retries}] 任务处理中，3秒后重试...")
            if attempt < max_retries:
                time.sleep(3)
    else:
        url = f"{BASE_URL}/word/api/pending/{doc_id}"
        params = {"um": "false", "key": task_id}
        for attempt in range(1, max_retries + 1):
            resp = client.request("GET", url, params=params)
            try:
                result = resp.json()
            except Exception:
                result = {}
            dl_url = result.get("result")
            if result.get("code") == 0 and dl_url and isinstance(dl_url, str) and dl_url.startswith("http"):
                print(f"✅ 文件已就绪")
                return dl_url  # str URL
            print(f"   [{attempt}/{max_retries}] 任务处理中，3秒后重试...")
            if attempt < max_retries:
                time.sleep(3)

    print(f"❌ 等待超时（重试 {max_retries} 次）")
    return None


def download_file(client, download_url: str, output_path: Path) -> bool:
    """从指定 URL 下载文件"""
    print(f"⬇️  下载文件...")
    resp = client.request("GET", download_url)
    content = resp.content
    ct = resp.headers.get("Content-Type", "")

    if content and "html" not in ct and "json" not in ct:
        output_path.write_bytes(content)
        print(f"✅ 文档已保存: {output_path} ({len(content):,} bytes)")
        return True

    if "json" in ct:
        try:
            j = resp.json()
            print(f"❌ 下载失败: {j.get('message', '未知错误')}")
        except Exception:
            print(f"❌ 下载失败: 未知响应")
    else:
        print(f"❌ 下载失败 (Content-Type={ct})")
    return False


def main():
    parser = argparse.ArgumentParser(description="导出 Docs 文档/普通表格/万维表格")
    parser.add_argument("doc", help="文档 ID 或完整 URL")
    parser.add_argument(
        "--format", dest="fmt", choices=["docx", "pdf", "xlsx"], default=None,
        help="导出格式（文档默认 docx，表格默认 xlsx）",
    )
    parser.add_argument("-o", "--output", help="输出文件路径（默认使用文档标题作为文件名）")
    args = parser.parse_args()

    doc_id = parse_doc_id(args.doc)
    if not doc_id:
        print(f"❌ 无法解析 docId: {args.doc}", file=sys.stderr)
        sys.exit(1)

    print(f"📄 文档ID: {doc_id}")

    client = get_sso_client()

    # 检测文档类型
    doc_type = detect_doc_type(args.doc, client)
    print(f"📋 文档类型: {doc_type}")

    # 根据类型确定默认格式
    is_table = doc_type in ("sheet", "metasheet")
    fmt = args.fmt or ("xlsx" if is_table else "docx")

    if args.output:
        output_path = Path(args.output)
    else:
        title = get_doc_title(client, doc_id)
        if title:
            safe_title = sanitize_filename(title)
            print(f"📝 文档标题: {title}")
            output_path = Path(f"{safe_title}.{fmt}")
        else:
            output_path = Path(f"{doc_id}.{fmt}")

    scene = DOC_TYPE_SCENE.get(doc_type, "doc")

    # 1. 权限检查
    if not check_download_permission(client, doc_id, scene=scene):
        print("\n💡 可使用 request_permission.py 申请文档权限")
        sys.exit(1)

    # 2. 触发导出
    task_id = trigger_export(client, doc_id, fmt, doc_type=doc_type)
    if not task_id:
        sys.exit(1)

    # 3. 轮询任务状态，获取下载 URL 或文件内容
    pending_result = poll_pending(client, doc_id, task_id, doc_type=doc_type)
    if pending_result is None:
        sys.exit(1)

    # 4. 保存文件
    if isinstance(pending_result, bytes):
        # metasheet 直接返回文件流
        output_path.write_bytes(pending_result)
        print(f"✅ 文档已保存: {output_path} ({len(pending_result):,} bytes)")
    else:
        if not download_file(client, pending_result, output_path):
            sys.exit(1)


if __name__ == "__main__":
    main()
