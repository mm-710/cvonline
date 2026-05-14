#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "ks-aimate>=1.0.30",
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
from __future__ import annotations

"""
check_install_dep.py - 检查并安装 MyFlicker Skill 依赖

支持两种环境：
1. CodeFlicker：检查本地目录，使用 codeflicker:// 协议安装
2. MyFlicker Work：通过 MyFlicker API 安装

Usage:
    # 检查是否已安装
    uv run <skill_directory>/scripts/check_install_dep.py check <slug>

    # 检查并自动安装（未安装时）
    uv run <skill_directory>/scripts/check_install_dep.py ensure <slug>

    # 批量 ensure（空格分隔多个 slug）
    uv run <skill_directory>/scripts/check_install_dep.py ensure <slug1> <slug2> ...

Exit codes:
    0 — 已安装（或安装成功）
    1 — 未安装（仅 check 模式）
    2 — 安装失败
"""

import argparse
import json
import os
import sys
import webbrowser
from urllib.parse import quote

from ks_aimate.sso_login_client.session import SmartSSOSession

BASE_URL = "https://myflicker.corp.kuaishou.com"


def detect_environment(session: SmartSSOSession) -> str:
    """
    检测当前运行环境。
    
    Returns:
        "codeflicker" - CodeFlicker IDE 环境（有 ap_token）
        "myflicker" - MyFlicker Work 环境（无 ap_token）
    """
    # SmartSSOSession 在 CodeFlicker 环境下会从 Debug Server 获取 ap_token
    if hasattr(session, 'ap_token') and session.ap_token:
        return "codeflicker"
    return "myflicker"


def is_installed_codeflicker(slug: str) -> bool:
    """
    CodeFlicker 环境：检查本地目录是否存在该 Skill。
    
    检查顺序：skills/、remote-personal-skills/、remote-skills/
    """
    # 获取 workspace 根目录
    # 在 CodeFlicker 中，脚本运行在沙箱环境，workspace 路径通常为 /data/aime/{uuid}/workspace
    # 或者通过环境变量获取
    workspace = os.environ.get("WORKSPACE_PATH") or os.environ.get("CODEFLICKER_WORKSPACE")
    
    if not workspace:
        # 尝试从当前脚本位置推断
        # 脚本通常在 <workspace>/.codeflicker/remote-personal-skills/<skill>/scripts/ 下
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上查找，直到找到 .codeflicker 目录
        current = script_dir
        while current != '/':
            codeflicker_dir = os.path.join(current, '.codeflicker')
            if os.path.exists(codeflicker_dir):
                workspace = current
                break
            current = os.path.dirname(current)
    
    if not workspace:
        # 最后尝试使用用户主目录下的 .codeflicker
        home = os.path.expanduser("~")
        workspace = home
    
    # 检查三个可能的目录
    check_dirs = [
        os.path.join(workspace, "skills", slug),
        os.path.join(workspace, ".codeflicker", "skills", slug),
        os.path.join(workspace, ".codeflicker", "remote-personal-skills", slug),
        os.path.join(workspace, ".codeflicker", "remote-skills", slug),
    ]
    
    for dir_path in check_dirs:
        if os.path.exists(dir_path):
            skill_md = os.path.join(dir_path, "SKILL.md")
            if os.path.exists(skill_md):
                return True
    
    return False


def is_installed_myflicker(session: SmartSSOSession, slug: str) -> bool:
    """MyFlicker Work 环境：通过 API 检查是否已安装。"""
    resp = session.request('GET', f"{BASE_URL}/api/v1/fe/skills/installed/{slug}")
    resp.raise_for_status()
    data = resp.json()
    if "result" in data:
        return bool(data["result"])
    if "data" in data and isinstance(data["data"], dict):
        return bool(data["data"].get("installed", False))
    return False


def get_skill_cdn_url(session: SmartSSOSession, slug: str) -> str | None:
    """
    获取 Skill 的 CDN 下载链接。
    
    Returns:
        CDN URL 字符串，失败返回 None
    """
    try:
        resp = session.request('GET', f"{BASE_URL}/api/v1/fe/skills/detail/{slug}")
        resp.raise_for_status()
        data = resp.json()
        
        # 提取 latestVersion.cdnUrl
        if "data" in data:
            skill_data = data["data"]
            if "latestVersion" in skill_data:
                latest = skill_data["latestVersion"]
                if isinstance(latest, dict) and "cdnUrl" in latest:
                    return latest["cdnUrl"]
        
        return None
    except Exception as e:
        print(f"❌ 获取 {slug} CDN URL 失败: {e}", file=sys.stderr)
        return None


def install_codeflicker(session: SmartSSOSession, slug: str) -> bool:
    """
    CodeFlicker 环境：通过 codeflicker:// 协议安装 Skill。
    
    Returns:
        True 表示安装链接已打开（不保证安装成功）
    """
    cdn_url = get_skill_cdn_url(session, slug)
    if not cdn_url:
        print(f"❌ 无法获取 {slug} 的下载链接", file=sys.stderr)
        return False
    
    # URL 编码 cdnUrl
    encoded_url = quote(cdn_url, safe='')
    
    # 拼接 codeflicker:// 协议链接
    install_url = f"codeflicker://kuaishou.codeflicker/skill/install?url={encoded_url}&name={slug}&preInstall=false"
    
    print(f"⏳ 正在打开安装链接: {install_url}")
    
    # 尝试打开链接
    try:
        webbrowser.open(install_url)
        print(f"✅ 安装链接已打开，请在 CodeFlicker 中确认安装")
        return True
    except Exception as e:
        print(f"❌ 打开安装链接失败: {e}", file=sys.stderr)
        print(f"请手动访问: {install_url}")
        return False


def install_myflicker(session: SmartSSOSession, slug: str) -> bool:
    """MyFlicker Work 环境：通过 API 安装。"""
    resp = session.request(
        'POST',
        f"{BASE_URL}/api/v1/fe/skills/install/{slug}",
        params={"autoDispatchUpdate": "true"},
        headers={"content-length": "0"},
        data=b"",
    )
    resp.raise_for_status()
    data = resp.json()
    if "result" in data:
        return bool(data["result"])
    if "code" in data:
        return data["code"] in (0, 1)
    return True


def cmd_check(session: SmartSSOSession, slug: str) -> int:
    """检查 Skill 是否已安装。"""
    env = detect_environment(session)
    
    if env == "codeflicker":
        installed = is_installed_codeflicker(slug)
    else:
        installed = is_installed_myflicker(session, slug)
    
    if installed:
        print(f"✅ {slug} 已安装 ({env})")
        return 0
    else:
        print(f"❌ {slug} 未安装 ({env})")
        return 1


def cmd_ensure(session: SmartSSOSession, slugs: list[str]) -> int:
    """检查并安装 Skill（如未安装）。"""
    env = detect_environment(session)
    all_ok = True
    
    for slug in slugs:
        # 检查是否已安装
        if env == "codeflicker":
            installed = is_installed_codeflicker(slug)
        else:
            installed = is_installed_myflicker(session, slug)
        
        if installed:
            print(f"✅ {slug} 已安装，跳过 ({env})")
            continue
        
        print(f"⏳ {slug} 未安装，正在安装... ({env})")
        
        try:
            if env == "codeflicker":
                ok = install_codeflicker(session, slug)
            else:
                ok = install_myflicker(session, slug)
        except Exception as e:
            print(f"❌ {slug} 安装失败: {e}", file=sys.stderr)
            all_ok = False
            continue
        
        if ok:
            # CodeFlicker 环境下，链接打开就算成功（实际安装需要用户确认）
            print(f"✅ {slug} 安装成功" if env == "myflicker" else f"⏳ {slug} 安装链接已打开，请确认安装")
        else:
            print(f"❌ {slug} 安装失败", file=sys.stderr)
            all_ok = False
    
    return 0 if all_ok else 2


def main():
    parser = argparse.ArgumentParser(description="检查并安装 MyFlicker Skill 依赖")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    check_p = subparsers.add_parser("check", help="检查单个 skill 是否已安装")
    check_p.add_argument("slug", help="Skill slug（即 skill 名称）")
    
    ensure_p = subparsers.add_parser("ensure", help="检查并自动安装（支持多个 slug）")
    ensure_p.add_argument("slugs", nargs="+", help="一个或多个 skill slug")
    
    args = parser.parse_args()
    session = SmartSSOSession()
    
    if args.cmd == "check":
        sys.exit(cmd_check(session, args.slug))
    elif args.cmd == "ensure":
        sys.exit(cmd_ensure(session, args.slugs))


if __name__ == "__main__":
    main()
