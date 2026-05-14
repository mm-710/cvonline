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
docs-shuttle: 文档权限申请工具

当遇到"暂无权限访问"的文档时，使用此脚本申请权限。
通过 API 接口直接完成权限申请，无需浏览器自动化。

用法:
    uv run --refresh-package ks_aimate request_permission.py <docs-url> [--permission-type <type>] [--reason <reason>]

参数:
    docs-url              文档 URL（完整链接或 docId）
    --permission-type, -t 权限类型：read / comment / edit / manage（默认：comment）
    --reason, -r          申请理由（选填）

示例:
    uv run --refresh-package ks_aimate request_permission.py https://docs.corp.kuaishou.com/d<skill_directory>
    uv run --refresh-package ks_aimate request_permission.py fcABxxx --permission-type edit --reason "需要协作编辑"
    uv run --refresh-package ks_aimate request_permission.py fcABxxx -t comment -r "提供反馈意见"

权限类型说明:
    read    - 可阅读：只能查看文档内容
    comment - 可评论：可以查看和评论（推荐默认）
    edit    - 可编辑：可以查看、评论和编辑文档
    manage  - 可管理：最高权限，可以管理协作者和文档设置
"""

import sys
import argparse
import re
import os
from pathlib import Path
from ks_aimate.sso_login_client import SmartSSOSession

# 基础 URL
BASE_URL = "https://docs.corp.kuaishou.com"

# 权限类型映射（用户参数 -> API accessLevelEn）
PERMISSION_TYPE_MAP = {
    "read": "readOnly",
    "comment": "readComment",
    "edit": "write",
    "manage": "coAdmin",
}

# 权限类型中文描述
PERMISSION_TYPES = {
    "read": "可阅读",
    "comment": "可评论",
    "edit": "可编辑",
    "manage": "可管理",
}


def get_sso_client():
    """获取 SSO 客户端"""
    return SmartSSOSession()


def extract_doc_id(url_or_id: str) -> str:
    """从 URL 或直接 docId 中提取 docId"""
    patterns = [
        r'/d/home/([^/?#]+)',
        r'/k/home/[^/]+/([^/?#]+)',
        r'/s/home/([^/?#]+)',
        r'/t/home/[^/]+/([^/?#]+)',
        r'/m/home/([^/?#]+)',
        r'/b/home/[^/]+/([^/?#]+)',
        r'[?&]docId=([^&]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    if not url_or_id.startswith('http'):
        return url_or_id

    return url_or_id


def build_doc_url(doc_id: str) -> str:
    """构建文档 URL"""
    if doc_id.startswith('http'):
        return doc_id
    return f"{BASE_URL}/d/home/{doc_id}"


def get_co_admins(sso_client, doc_id: str) -> list:
    """
    从 admin-user-list 接口获取文档管理员的 entityId 列表，作为 coAdmins 字段。
    """
    url = f"{BASE_URL}/merlot/api/docs/admin-user-list/{doc_id}?um=false"
    print(f"� 获取文档管理员列表...")

    try:
        resp = sso_client.request("GET", url)
        if resp.status_code != 200:
            print(f"   ⚠️  获取管理员列表失败，状态码: {resp.status_code}")
            return []

        data = resp.json()
        if data.get("code") != 0:
            print(f"   ⚠️  获取管理员列表接口返回错误: {data.get('message')}")
            return []

        collaborators = data.get("result", {}).get("collaborators", [])
        entity_ids = [c["entity"]["entityId"] for c in collaborators if c.get("entity", {}).get("entityId")]
        print(f"   ✅ 获取到 {len(entity_ids)} 位管理员")
        return entity_ids

    except Exception as e:
        print(f"   ⚠️  获取管理员列表异常: {e}")
        return []


def record_no_permission_audit(sso_client, doc_id: str):
    """
    调用无权限访问审计日志接口，记录当前用户尝试访问了无权限文档。
    """
    url = f"{BASE_URL}/merlot/api/docs/audit/logs/no-permission/{doc_id}?um=false"
    print(f"📝 记录无权限访问日志...")

    try:
        resp = sso_client.request("POST", url)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            print(f"   ✅ 审计日志记录成功")
        else:
            print(f"   ⚠️  审计日志记录失败，状态码: {resp.status_code}")
    except Exception as e:
        print(f"   ⚠️  审计日志记录异常: {e}")


def apply_permission(sso_client, doc_id: str, access_level_en: str,
                     co_admins: list, content: str) -> bool:
    """
    调用权限申请接口。
    """
    url = f"{BASE_URL}/merlot/api/share-apply/role?um=false"
    payload = {
        "accessLevelEn": access_level_en,
        "coAdmins": co_admins,
        "content": content,
        "docId": doc_id,
    }
    print(f"📤 提交权限申请...")

    try:
        resp = sso_client.request("POST", url, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                print(f"   ✅ 权限申请提交成功")
                return True
            else:
                print(f"   ❌ 申请接口返回错误: {data.get('message')}")
                return False
        else:
            print(f"   ❌ 申请接口请求失败，状态码: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 申请接口异常: {e}")
        return False


def request_permission(doc_url: str, permission_type: str = "comment",
                       reason: str = "") -> dict:
    """
    申请文档权限主流程：
    1. SSO 认证
    2. 获取文档管理员列表（coAdmins）
    3. 记录无权限访问审计日志
    4. 提交权限申请
    """
    doc_id = extract_doc_id(doc_url)
    access_level_en = PERMISSION_TYPE_MAP[permission_type]
    content = reason if reason else "申请阅读并评论"

    print(f"📄 文档 ID: {doc_id}")
    print(f"🔐 申请权限：{PERMISSION_TYPES[permission_type]} ({access_level_en})")
    print(f"📝 申请理由：{content}")
    print()

    # 步骤 1: SSO 认证
    print("🔐 正在进行 SSO 认证...")
    sso_client = get_sso_client()
    if not sso_client:
        return {
            "success": False,
            "message": "SSO 客户端初始化失败，请确保已安装 kuaishou-sso-login-client skill",
        }

    # 触发一次认证，确保 session 有效
    try:
        resp = sso_client.request("GET", build_doc_url(doc_id))
        print(f"   ✅ SSO 认证完成（状态码: {resp.status_code}）")
    except Exception as e:
        print(f"   ⚠️  SSO 预热请求失败: {e}，继续尝试...")
    print()

    # 步骤 2: 获取管理员列表
    co_admins = get_co_admins(sso_client, doc_id)
    print()

    # 步骤 3: 记录无权限审计日志
    record_no_permission_audit(sso_client, doc_id)
    print()

    # 步骤 4: 提交权限申请
    success = apply_permission(sso_client, doc_id, access_level_en, co_admins, content)
    print()

    if success:
        print("=" * 60)
        print("✅ 权限申请已成功提交！")
        print("=" * 60)
        print(f"📄 文档: {build_doc_url(doc_id)}")
        print(f"🔐 权限: {PERMISSION_TYPES[permission_type]}")
        print(f"📝 理由: {content}")
        print("⏰ 请等待文档所有者审批")
        print("=" * 60)
        return {
            "success": True,
            "message": "权限申请已提交，等待审批",
            "doc_id": doc_id,
            "doc_url": build_doc_url(doc_id),
            "permission_type": permission_type,
            "permission_type_cn": PERMISSION_TYPES[permission_type],
            "access_level_en": access_level_en,
            "content": content,
        }
    else:
        return {
            "success": False,
            "message": "权限申请提交失败，请检查日志或手动申请",
        }


def main():
    parser = argparse.ArgumentParser(
        description="Docs 文档权限申请工具（通过 API 直接申请）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
权限类型说明:
  read    - 可阅读：只能查看文档内容
  comment - 可评论：可以查看和评论（推荐默认）
  edit    - 可编辑：可以查看、评论和编辑文档
  manage  - 可管理：最高权限，可以管理协作者和文档设置

使用示例:
  # 申请可评论权限（默认）
  uv run --refresh-package ks_aimate request_permission.py https://docs.corp.kuaishou.com/d<skill_directory>

  # 申请可编辑权限并说明理由
  uv run --refresh-package ks_aimate request_permission.py fcABxxx --permission-type edit --reason "需要协作编辑文档"

  # 申请可管理权限
  uv run --refresh-package ks_aimate request_permission.py fcABxxx -t manage -r "需要管理文档协作者"
        """,
    )

    parser.add_argument("doc_url", help="文档 URL 或 docId")
    parser.add_argument(
        "-t", "--permission-type",
        choices=["read", "comment", "edit", "manage"],
        default="comment",
        help="权限类型（默认：comment）",
    )
    parser.add_argument("-r", "--reason", default="", help="申请理由（选填）")

    args = parser.parse_args()

    print("=" * 60)
    print("📋 权限申请信息")
    print("=" * 60)
    print(f"文档链接：{args.doc_url}")
    print(f"申请权限：{PERMISSION_TYPES[args.permission_type]}")
    if args.reason:
        print(f"申请理由：{args.reason}")
    print("=" * 60)
    print()

    result = request_permission(args.doc_url, args.permission_type, args.reason)

    if result["success"]:
        sys.exit(0)
    else:
        print(f"❌ 失败：{result.get('message', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
