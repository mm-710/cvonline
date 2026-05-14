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
publish_skill.py - 将本地 Skill 发布到 MyFlicker Skill 市场（草稿态）

流程：
  1. 权限检查：查询管理员列表，判断当前用户是否有权发布
  2. 打包：将 skill 目录打包为 zip
  3. 静态扫描：调用 scan-zip 接口，最多重试 3 次
  4. 草稿发布：调用 basic-info 接口，创建草稿态

Usage:
    uv run <skill_directory>/scripts/publish_skill.py \\
        --skill-dir /path/to/skill-dir \\
        --display-name "中文名称" \\
        --summary "一句话描述" \\
        --username lixinjian
"""

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

from ks_aimate.sso_login_client.session import SmartSSOSession

ADMINS_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/author/skills/{slug}/admins"
SKILL_INFO_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/author/skills/{slug}"
SCAN_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/author/skills/scan-zip"
BASIC_INFO_CREATE_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/author/skills/basic-info"
BASIC_INFO_UPDATE_URL = "https://myflicker.corp.kuaishou.com/api/v1/fe/author/skills/{slug}/basic-info"
CREATOR_PAGE = "https://myflicker.corp.kuaishou.com/flicker/creator/skills"

EXCLUDE_PATTERNS = {".git", "__pycache__", ".DS_Store", "evals", "node_modules", "workspace"}


def should_exclude(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_PATTERNS or part.endswith(".pyc") or part.startswith(".version-") or (part.startswith(".") and part not in {".", ".."}):
            return True
    return False


def build_zip(skill_dir: Path, slug: str | None = None) -> bytes:
    """打包 skill 目录，解压后顶层是同名文件夹。slug 可覆盖目录名作为 zip 内顶层目录名。"""
    skill_name = slug or skill_dir.name
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(skill_dir)
            if should_exclude(rel):
                continue
            arcname = f"{skill_name}/{rel}"
            zf.write(file_path, arcname)
    return buf.getvalue()


def check_permission(session: SmartSSOSession, skill_name: str, username: str) -> tuple[bool, bool, str]:
    """
    检查发布权限。
    返回 (allowed, skill_exists, reason)
    - allowed=True, skill_exists=False : 市场无此 Skill，允许首次发布
    - allowed=True, skill_exists=True  : Skill 已存在，用户在管理员列表中，允许更新
    - allowed=False                    : 禁止发布
    """
    url = ADMINS_URL.format(slug=skill_name)
    try:
        resp = session.request("GET", url)
        body = resp.json()
    except Exception as e:
        return False, False, f"查询管理员列表失败：{e}"

    # Skill not found -> 新 Skill，可以发布
    message = body.get("message", body.get("errorMsg", ""))
    if "not found" in str(message).lower() or "skill not found" in str(message).lower():
        return True, False, "市场上尚无此 Skill，允许首次发布"

    # 拿管理员列表：优先 data 字段，result 仅当它是 dict 时才用作兜底
    data = body.get("data")
    if data is None and isinstance(body.get("result"), dict):
        data = body["result"]
    if isinstance(data, dict):
        admins = data.get("admins") or data.get("adminList") or []
    elif isinstance(data, list):
        admins = data
    else:
        # 解析失败时打印原始结构，便于排查
        print(f"  ⚠️  无法解析管理员列表，原始返回体（脱敏）：{json.dumps(body, ensure_ascii=False)[:500]}")
        admins = []

    # 兼容字符串列表和对象列表（含嵌套 user.username 格式）
    admin_names = set()
    for a in admins:
        if isinstance(a, str):
            admin_names.add(a)
        elif isinstance(a, dict):
            # 嵌套格式：{ "user": { "username": "xxx" }, "role": "admin" }
            nested_user = a.get("user")
            if isinstance(nested_user, dict):
                admin_names.add(nested_user.get("username") or nested_user.get("name") or nested_user.get("userId") or "")
            # 平铺格式：{ "username": "xxx" }
            else:
                admin_names.add(a.get("username") or a.get("name") or a.get("userId") or "")

    if username in admin_names:
        return True, True, f"用户 {username} 在管理员列表中，允许发布"
    else:
        return False, True, (
            f"❌ 发布被拒绝：Skill `{skill_name}` 已存在于市场，"
            f"但用户 `{username}` 不在其管理员列表中。\n"
            f"当前管理员：{', '.join(sorted(admin_names)) or '（无）'}"
        )


def scan_zip(session: SmartSSOSession, skill_name: str, zip_bytes: bytes, max_retries: int = 3) -> bool:
    """
    调用静态扫描接口，最多重试 max_retries 次。
    返回 True 表示扫描通过，False 表示最终失败。
    """
    for attempt in range(1, max_retries + 1):
        print(f"  [扫描 {attempt}/{max_retries}] 调用 scan-zip 接口...")
        files = {
            "file": (f"{skill_name}.zip", zip_bytes, "application/zip"),
        }
        data = {"slug": skill_name}
        try:
            resp = session.request("POST", SCAN_URL, files=files, data=data)
            body = resp.json()
        except Exception as e:
            print(f"  ⚠️  请求失败：{e}")
            if attempt < max_retries:
                print("  重试中...")
            continue

        # 判断是否通过
        success = (
            body.get("result") is True
            or body.get("code") == 0
            or body.get("code") == 1
        )
        if success:
            print(f"  ✅ 静态扫描通过")
            return True

        msg = body.get("message") or body.get("errorMsg") or json.dumps(body, ensure_ascii=False)
        print(f"  ❌ 扫描未通过（第 {attempt} 次）：{msg}")

        if attempt < max_retries:
            print(f"\n  ⚠️  扫描失败，建议用 skill-creator 检查并修复 SKILL 内容后重试。")
            print(f"  还剩 {max_retries - attempt} 次重试机会，请修复后重新运行发布命令。")
            # 每次失败后退出，让 AI 有机会修复
            return False

    print(f"\n❌ 静态扫描连续失败 {max_retries} 次，已达最大重试次数，终止发布。")
    return False


def publish_draft(session: SmartSSOSession, skill_name: str, display_name: str, summary: str, zip_bytes: bytes, skill_exists: bool) -> bool:
    """调用 basic-info 接口，创建或更新草稿态。"""
    if skill_exists:
        url = BASIC_INFO_UPDATE_URL.format(slug=skill_name)
        print(f"[4/4] 更新已有 Skill 草稿到市场（POST {url}）...")
    else:
        url = BASIC_INFO_CREATE_URL
        print(f"[4/4] 提交新 Skill 草稿到市场（POST {url}）...")
    method = "POST"
    files = {
        "file": (f"{skill_name}.zip", zip_bytes, "application/zip"),
    }
    data = {
        "slug": skill_name,
        "displayName": display_name,
        "summary": summary,
        "cover": "",
    }
    try:
        resp = session.request(method, url, files=files, data=data)
        body = resp.json()
    except Exception as e:
        print(f"❌ 草稿提交失败：{e}", file=sys.stderr)
        return False

    success = (
        body.get("result") is True
        or body.get("code") == 0
        or body.get("code") == 1
    )
    if not success:
        msg = body.get("message") or body.get("errorMsg") or json.dumps(body, ensure_ascii=False)
        print(f"❌ 草稿提交失败：{msg}", file=sys.stderr)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="发布 Skill 到 MyFlicker 市场（草稿态）")
    parser.add_argument("--skill-dir", required=True, help="Skill 目录路径")
    parser.add_argument("--slug", default=None, help="发布时使用的 slug（默认取目录名；换名发布时需指定）")
    parser.add_argument("--display-name", required=True, help="Skill 展示名称（中文）")
    parser.add_argument("--summary", required=True, help="Skill 一句话描述")
    parser.add_argument("--username", required=True, help="当前操作用户名（用于权限校验）")
    parser.add_argument("--max-scan-retries", type=int, default=3, help="静态扫描最大重试次数（默认 3）")
    parser.add_argument("--dry-run", action="store_true", help="仅执行权限检查和 Slug 冲突检测，不打包/扫描/提交草稿")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"Error: 目录不存在: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    if not (skill_dir / "SKILL.md").exists():
        print(f"Error: 目录中未找到 SKILL.md，不是有效的 skill 目录", file=sys.stderr)
        sys.exit(1)

    skill_name = args.slug or skill_dir.name
    session = SmartSSOSession()

    # Step 1: 权限检查
    print(f"[1/4] 检查发布权限（slug={skill_name}, user={args.username}）...")
    allowed, skill_exists, reason = check_permission(session, skill_name, args.username)
    print(f"      {reason}")
    if not allowed:
        sys.exit(1)

    # dry-run: 仅做权限检查，到此结束
    if args.dry_run:
        print()
        print("=" * 60)
        print("📌 dry-run 模式：仅执行权限检查，不继续打包/扫描/提交。")
        print("=" * 60)
        print(f"  Slug:         {skill_name}")
        print(f"  Skill 已存在: {skill_exists}")
        print(f"  权限:         {reason}")
        if skill_exists:
            print(f"  市场链接:     https://myflicker.corp.kuaishou.com/skillhub/skills/{skill_name}")
        print("=" * 60)
        return

    # Step 2: 打包
    print(f"[2/4] 打包 skill: {skill_name}...")
    zip_bytes = build_zip(skill_dir, slug=args.slug)
    print(f"      压缩完成，大小: {len(zip_bytes) // 1024} KB")

    # Step 3: 静态扫描
    print(f"[3/4] 静态安全扫描...")
    scan_ok = scan_zip(session, skill_name, zip_bytes, max_retries=args.max_scan_retries)
    if not scan_ok:
        sys.exit(1)

    # Step 4: 草稿发布
    ok = publish_draft(session, skill_name, args.display_name, args.summary, zip_bytes, skill_exists)
    if not ok:
        sys.exit(1)

    print()
    print("=" * 60)
    print("✅ Skill 已成功提交草稿！")
    print("=" * 60)
    print(f"  Slug:         {skill_name}")
    print(f"  展示名称:     {args.display_name}")
    print(f"  描述摘要:     {args.summary}")
    print()
    print("  请前往以下页面查看并完善草稿：")
    print(f"  {CREATOR_PAGE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
