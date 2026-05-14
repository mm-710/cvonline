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
docs-shuttle 统一入口 — 通过 URL 路径前缀判断文档类型并调用对应脚本

URL 类型判断规则:
  /d/home/{docId}          普通文档（非知识库）
  /k/home/{viewId}/{docId} 普通文档（知识库）
  /s/home/{docId}          普通表格（非知识库）
  /t/home/{viewId}/{docId} 普通表格（知识库）
  /m/home/{docId}          万维表格
  /b<skill_directory>              万维表格（知识库）

操作与类型对应:
  pull / push / comment          → 仅普通文档
  read / write / append / create / mentions → 仅普通表格
  meta / content / add-record
    / update-record / delete-record → 仅万维表格
  download / request_permission / search → 全部类型

用法:
  uv run --refresh-package ks_aimate docs.py <operation> [url] [additional_args...]

示例:
  uv run --refresh-package ks_aimate docs.py pull "https://docs.corp.kuaishou.com/d<skill_directory>"
  uv run --refresh-package ks_aimate docs.py pull "https://docs.corp.kuaishou.com/k<skill_directory>"
  uv run --refresh-package ks_aimate docs.py push ./readme.md
  uv run --refresh-package ks_aimate docs.py comment list "https://docs.corp.kuaishou.com/d<skill_directory>"
  uv run --refresh-package ks_aimate docs.py read "https://docs.corp.kuaishou.com/s<skill_directory>"
  uv run --refresh-package ks_aimate docs.py read "https://docs.corp.kuaishou.com/t<skill_directory>"
  uv run --refresh-package ks_aimate docs.py mentions "https://docs.corp.kuaishou.com/t<skill_directory>?section=397576121" --best-effort
  uv run --refresh-package ks_aimate docs.py meta "https://docs.corp.kuaishou.com/m<skill_directory>"
  uv run --refresh-package ks_aimate docs.py download "https://docs.corp.kuaishou.com/t<skill_directory>"
  uv run --refresh-package ks_aimate docs.py search "关键词"
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent

# 操作 → { doc_types: 允许的类型集合(None=全部), script: 目标脚本 }
OPERATION_MAP = {
    # 仅普通文档
    "pull":    {"doc_types": {"doc"},       "script": "pull.py"},
    "push":    {"doc_types": {"doc"},       "script": "push.py"},
    "comment": {"doc_types": {"doc"},       "script": "comment.py"},

    # 仅普通表格
    "create":  {"doc_types": {"sheet"},     "script": "sheet.py"},
    "read":    {"doc_types": {"sheet"},     "script": "sheet.py"},
    "write":   {"doc_types": {"sheet"},     "script": "sheet.py"},
    "append":  {"doc_types": {"sheet"},     "script": "sheet.py"},
    "mentions": {"doc_types": {"sheet"},    "script": "mention_extract.py"},

    # 仅万维表格
    "meta":          {"doc_types": {"metasheet"}, "script": "metasheet.py"},
    "content":       {"doc_types": {"metasheet"}, "script": "metasheet.py"},
    "add-record":    {"doc_types": {"metasheet"}, "script": "metasheet.py"},
    "update-record": {"doc_types": {"metasheet"}, "script": "metasheet.py"},
    "delete-record": {"doc_types": {"metasheet"}, "script": "metasheet.py"},

    # 全部类型
    "download":           {"doc_types": None, "script": "download.py"},
    "request_permission": {"doc_types": None, "script": "request_permission.py"},
    "search":             {"doc_types": None, "script": "search.py"},
}

# URL 路径前缀 → 文档类型（直接判断，无需 API 查询）
URL_TYPE_PATTERNS = [
    (r"/d/home/",  "doc"),
    (r"/k/home/",  "doc"),
    (r"/s/home/",  "sheet"),
    (r"/t/home/",  "sheet"),
    (r"/m/home/",  "metasheet"),
    (r"/b/home/",  "metasheet"),
]

DOC_TYPE_LABEL = {
    "doc":       "普通文档（/d/ 或 /k/）",
    "sheet":     "普通表格（/s/ 或 /t/）",
    "metasheet": "万维表格（/m/ 或 /b/）",
}

# 不需要 URL 参数的操作
NO_URL_OPS = {"create", "push", "search"}
# 第一个非选项参数是子命令而非 URL 的操作
SUBCOMMAND_OPS = {"comment", "request_permission"}


def detect_doc_type(url: str) -> Optional[str]:
    """通过 URL 路径前缀判断文档类型，无法判断则返回 None"""
    for pattern, doc_type in URL_TYPE_PATTERNS:
        if re.search(pattern, url):
            return doc_type
    return None


def find_url_arg(operation: str, args: list) -> Optional[str]:
    """从参数列表中找到 URL 参数"""
    if operation in NO_URL_OPS:
        return None
    non_option_count = 0
    skip_next = False
    for arg in args:
        if skip_next:
            # 前一个是带值选项（如 --format pdf），跳过其值
            skip_next = False
            continue
        if arg.startswith("-"):
            # 带值的长选项（如 --format pdf），下一个参数是其值
            if "=" not in arg:
                skip_next = True
            continue
        non_option_count += 1
        # subcommand 操作：第一个非选项参数是子命令，第二个才是 URL
        if operation in SUBCOMMAND_OPS and non_option_count == 1:
            continue
        return arg
    return None


def build_command(script_name: str, operation: str, args: list) -> list:
    """构建要执行的命令"""
    script_path = SCRIPT_DIR / script_name

    if script_name in ("download.py", "pull.py", "push.py", "search.py"):
        # 这些脚本不使用子命令
        return ["uv", "run", str(script_path)] + args
    elif script_name in ("comment.py", "request_permission.py"):
        # 子命令已包含在 args 中
        return ["uv", "run", str(script_path)] + args
    elif script_name in ("sheet.py", "metasheet.py"):
        # 表格脚本需要子命令
        return ["uv", "run", str(script_path), operation] + args
    else:
        return ["uv", "run", str(script_path)] + args


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print(f"\n支持的操作: {', '.join(OPERATION_MAP.keys())}")
        sys.exit(1)

    operation = sys.argv[1]
    remaining_args = sys.argv[2:]

    if operation in ("help", "--help", "-h"):
        print(__doc__)
        print(f"\n支持的操作: {', '.join(OPERATION_MAP.keys())}")
        sys.exit(0)

    if operation not in OPERATION_MAP:
        print(f"❌ 未知操作: {operation}", file=sys.stderr)
        print(f"\n支持的操作: {', '.join(OPERATION_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    op_info = OPERATION_MAP[operation]
    script_name = op_info["script"]
    allowed_types = op_info["doc_types"]  # None 表示全部类型均支持

    # 有类型限制的操作：从 URL 判断类型并校验
    if allowed_types is not None:
        url_arg = find_url_arg(operation, remaining_args)
        if url_arg:
            detected = detect_doc_type(url_arg)
            if detected is None:
                print(f"⚠️  无法从 URL 判断文档类型，将按"
                      f" '{DOC_TYPE_LABEL[list(allowed_types)[0]]}' 处理",
                      file=sys.stderr)
            elif detected not in allowed_types:
                expected = " / ".join(DOC_TYPE_LABEL[t] for t in allowed_types)
                actual = DOC_TYPE_LABEL.get(detected, detected)
                print(f"❌ 操作 '{operation}' 仅支持{expected}，"
                      f"但提供的 URL 是{actual}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"🔍 文档类型: {DOC_TYPE_LABEL[detected]}")
        elif operation not in NO_URL_OPS:
            print(f"❌ 操作 '{operation}' 需要提供文档 URL", file=sys.stderr)
            sys.exit(1)
    else:
        # 通用操作：打印检测到的类型（仅供参考）
        url_arg = find_url_arg(operation, remaining_args)
        if url_arg:
            detected = detect_doc_type(url_arg)
            if detected:
                print(f"🔍 文档类型: {DOC_TYPE_LABEL[detected]}")

    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"❌ 脚本文件不存在: {script_path}", file=sys.stderr)
        sys.exit(1)

    cmd = build_command(script_name, operation, remaining_args)
    print(f"🚀 执行: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
