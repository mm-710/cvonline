#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate>=1.0.30",
#   "markdownify>=0.12.0",
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
docs-shuttle: Pull Docs 文档到本地 MD

功能:
    - 拉取 Docs 文档到本地 Markdown 文件
    - 自动下载文档中的图片到同名目录下的 images/ 子目录
    - 自动替换 Markdown 中的图片引用为本地相对路径

用法:
    uv run --refresh-package ks_aimate pull.py <docs-url> [--output <path>] [--no-images]

示例:
    uv run --refresh-package ks_aimate pull.py https://docs.corp.kuaishou.com/d/home/fcACE4bpNmjRfz1Nal8EQYBDo
    uv run --refresh-package ks_aimate pull.py https://docs.corp.kuaishou.com/d/home/fcACE4bpNmjRfz1Nal8EQYBDo -o ./design.md
    uv run --refresh-package ks_aimate pull.py https://docs.corp.kuaishou.com/d/home/fcACE4bpNmjRfz1Nal8EQYBDo --no-images
"""

import sys
import os
import re
import argparse
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import urllib.request
import urllib.parse
import urllib.error
import ssl
from ks_aimate.sso_login_client import SmartSSOSession
from markdownify import markdownify as md_convert

# 配置
BASE_URL = "https://docs.corp.kuaishou.com"
# docs-open-skill API 配置（用于 Markdown 读取）
OPEN_SKILL_API_HOST = "https://docs.qingque.cn"
OPEN_SKILL_API_BASE = f"{OPEN_SKILL_API_HOST}/merlot/e/api/skills"

# 创建不验证 SSL 的上下文
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def get_sso_client():
    """获取 SSO 客户端"""
    return SmartSSOSession()


def get_obo_token() -> Optional[str]:
    """从 SmartSSOSession 获取 OBO Token"""
    try:
        client = get_sso_client()
        # 优先使用自动选择方法，失败则尝试 codeflicker 方法
        token = client.get_ap_claw_token() or client._get_token_codeflicker()
        return token if token else None
    except Exception:
        return None


def get_doc_markdown_via_api(doc_id: str, token: str) -> Tuple[Optional[str], Optional[str]]:
    """
    使用 docs-open-skill 的 read-doc 接口获取 Markdown
    返回: (markdown_content, error_message)
    """
    url = f"{OPEN_SKILL_API_BASE}/docs/md-content?docId={urllib.parse.quote(doc_id)}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if isinstance(result, dict) and result.get("code") not in (None, 0, 200):
            return None, f"API error: {result.get('message', 'unknown')}"

        return result.get("result", ""), None

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return None, "Token unauthorized"
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)


def extract_images_from_markdown(content: str) -> List[Dict[str, str]]:
    """从 Markdown 内容中提取图片 URL"""
    images = []
    # 匹配 ![alt](url) 格式的图片
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    seen_urls = set()

    for match in re.finditer(pattern, content):
        alt = match.group(1) or "image"
        url = match.group(2).strip()
        if url and url not in seen_urls:
            seen_urls.add(url)
            images.append({
                "alt": alt,
                "url": url,
                "original": url
            })

    return images


def parse_doc_id(url: str) -> Optional[str]:
    """从 URL 解析 docId"""
    patterns = [
        r"/d/home/(fc[A-Za-z0-9_-]+)",
        r"/k/home/[^/]+/(fc[A-Za-z0-9_-]+)",
        r"/s/home/(fc[A-Za-z0-9_-]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_doc_meta(client, doc_id: str) -> Optional[Dict]:
    """获取文档元数据"""
    resp = client.request("POST", f"{BASE_URL}/merlot/api/docs/cosmo/meta/{doc_id}?um=false", json={})
    result = resp.json()
    if result.get("code") == 0:
        return result.get("result")
    return None


def get_doc_snapshot(client, doc_id: str, rev: int) -> Optional[list]:
    """获取文档快照内容"""
    url = f"{BASE_URL}/word/api/snapshot/{doc_id}/{rev}?supportChunkSnapshot=true"
    resp = client.request("GET", url)
    result = resp.json()
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and result.get("code") == 0:
        return result.get("result")
    return None


def extract_text_from_snapshot(snapshot: list) -> Tuple[str, List[Dict[str, str]]]:
    """从快照数据中提取文本内容和图片引用"""
    if not snapshot:
        return "", []

    text_parts = []
    images = []
    image_url_patterns = [
        r'https://docs\.corp\.kuaishou\.com/image/api/external/load/out\?[^)]+',
        r'https://docs\.corp\.kuaishou\.com/image/api/convert/loadimage\?[^)]+',
        r'https://[^\s")]+?\.(?:png|jpg|jpeg|gif|webp|svg|bmp)[^\s")]*',
    ]

    def extract_from_pk9(pk9_data):
        if isinstance(pk9_data, dict):
            if 'pk12' in pk9_data:
                text = str(pk9_data['pk12'])
                text_parts.append(text)
                for pattern in image_url_patterns:
                    for match in re.finditer(pattern, text):
                        images.append({
                            "alt": "image",
                            "url": match.group(0),
                            "original": match.group(0)
                        })
            for key, value in pk9_data.items():
                if key != 'pk12':
                    extract_from_pk9(value)
        elif isinstance(pk9_data, list):
            for item in pk9_data:
                extract_from_pk9(item)

    for elem in snapshot:
        if isinstance(elem, dict):
            extract_from_pk9(elem.get('pk9', []))

    # 去重图片
    seen_urls = set()
    unique_images = []
    for img in images:
        if img["url"] not in seen_urls:
            seen_urls.add(img["url"])
            unique_images.append(img)

    return '\n'.join(text_parts), unique_images


def get_doc_text(client, doc_id: str) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """获取文档文本内容和图片列表"""
    resp = client.request("GET", f"{BASE_URL}/word/api/load/{doc_id}?um=false")
    load_info = resp.json()
    
    if not load_info or load_info.get("code") != 0:
        return None, []

    result = load_info.get('result', {})
    rev = result.get('rev') or result.get('snapshotRev')
    if not rev:
        return None, []

    snapshot = get_doc_snapshot(client, doc_id, rev)
    if not snapshot:
        return None, []

    return extract_text_from_snapshot(snapshot)


def download_image(image_url: str, save_path: Path, client) -> Optional[str]:
    """下载图片并保存到本地"""
    try:
        resp = client.request("GET", image_url)
        content = resp.content
        
        content_type = resp.headers.get("Content-Type", "")
        ext_map = {
            "image/jpeg": ".jpg", "image/jpg": ".jpg",
            "image/png": ".png", "image/gif": ".gif",
            "image/webp": ".webp", "image/svg+xml": ".svg",
            "image/bmp": ".bmp"
        }
        ext = ext_map.get(content_type, ".jpg")
        
        if save_path.suffix.lower() != ext:
            save_path = save_path.with_suffix(ext)
        
        save_path.write_bytes(content)
        return str(save_path)
    except Exception:
        return None


def sanitize_filename(filename: str) -> str:
    """清理文件名中的非法字符"""
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    return filename[:100].strip() if len(filename) > 100 else filename.strip()


def get_image_filename(image_url: str, alt: str) -> str:
    """生成图片文件名"""
    url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
    if alt and alt != "image":
        safe_alt = sanitize_filename(alt)
        if safe_alt:
            return f"{safe_alt}-{url_hash}"
    return f"image-{url_hash}"


def download_images(images: List[Dict[str, str]], output_dir: Path, client) -> Dict[str, str]:
    """批量下载图片"""
    url_to_local = {}
    if not images:
        return url_to_local

    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"🖼️  发现 {len(images)} 张图片，开始下载...")

    for i, img in enumerate(images, 1):
        url = img.get("url", "")
        alt = img.get("alt", "image")
        if not url:
            continue

        filename = get_image_filename(url, alt)
        save_path = images_dir / filename

        print(f"  📥 [{i}/{len(images)}] {filename}...", end=" ")

        local_path = download_image(url, save_path, client)
        if local_path:
            rel_path = Path(local_path).relative_to(output_dir)
            url_to_local[url] = str(rel_path)
            print("✅")
        else:
            print("❌")

    return url_to_local


def replace_image_urls(content: str, url_mapping: Dict[str, str]) -> str:
    """替换 Markdown 中的图片 URL 为本地路径"""
    for url, local_path in url_mapping.items():
        content = content.replace(url, local_path)
    return content


def html_to_markdown(content: str) -> str:
    """
    把内容中混入的 HTML 标签（尤其是表格）转成标准 Markdown。
    纯 Markdown 段落不受影响，markdownify 只处理检测到的 HTML 标签。
    """
    import re
    # 判断是否含有 HTML 标签，若无则直接返回，避免不必要的处理
    if not re.search(r'<[a-zA-Z][^>]*>', content):
        return content

    # 用 markdownify 转换整段内容
    # heading_style=ATX 保持 # 风格标题，strip=['script','style'] 去除无用标签
    converted = md_convert(
        content,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    return converted


def main():
    parser = argparse.ArgumentParser(description='Pull Docs 文档到本地 Markdown')
    parser.add_argument('url', help='Docs 文档 URL')
    parser.add_argument('-o', '--output', help='输出文件路径（默认使用文档标题）')
    parser.add_argument('--no-images', action='store_true', help='跳过图片下载')

    args = parser.parse_args()

    # 获取 SSO 客户端
    client = get_sso_client()
    if not client:
        print("❌ 无法获取 SSO 客户端", file=sys.stderr)
        sys.exit(1)

    # 解析 docId
    doc_id = parse_doc_id(args.url)
    if not doc_id:
        print(f"❌ 无法从 URL 解析 docId: {args.url}", file=sys.stderr)
        sys.exit(1)

    print(f"📄 文档ID: {doc_id}")

    # 获取文档元数据
    meta = get_doc_meta(client, doc_id)
    if not meta:
        print("❌ 无法获取文档元数据", file=sys.stderr)
        sys.exit(1)

    doc_title = meta.get('name', 'untitled')
    print(f"📝 标题: {doc_title}")

    # 获取文档内容（优先尝试 Markdown API，失败降级到 snapshot）
    print("🔄 获取文档内容...")

    text = None
    images = []
    use_markdown_api = False

    # 尝试通过 Markdown API 获取
    token = get_obo_token()
    if token:
        print("  📡 尝试 Markdown API...")
        md_content, error = get_doc_markdown_via_api(doc_id, token)
        if md_content:
            print("  ✅ Markdown API 成功")
            text = md_content
            images = extract_images_from_markdown(text)
            use_markdown_api = True
        else:
            print(f"  ⚠️ Markdown API 失败 ({error})，降级到 snapshot 方式...")

    # 降级到原有 snapshot 方式
    if text is None:
        text, images = get_doc_text(client, doc_id)
        if not text:
            print("❌ 无法获取文档内容", file=sys.stderr)
            sys.exit(1)

    # 确定输出路径
    if args.output:
        output_file = Path(args.output)
    else:
        safe_title = sanitize_filename(doc_title)
        output_file = Path(f"{safe_title}.md")

    # 下载图片
    url_mapping = {}
    if not args.no_images and images:
        output_dir = output_file.parent / output_file.stem
        url_mapping = download_images(images, output_dir, client)

    # 替换图片 URL
    if url_mapping:
        text = replace_image_urls(text, url_mapping)

    # HTML → Markdown 转换（处理文档中混入的 HTML 表格等标签）
    text = html_to_markdown(text)

    # 保存文件
    output_file.write_text(text, encoding='utf-8')
    print(f"\n✅ 文档已保存: {output_file}")

    if url_mapping:
        print(f"📁 图片已保存到: {output_file.stem}/images/")


if __name__ == "__main__":
    main()
