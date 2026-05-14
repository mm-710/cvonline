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
普通表格操作 — 创建 / 读取 / 写入 / 追加

子命令:
  create   创建新表格（可选同时写入初始数据）
  read     读取表格内容
  write    向表格指定位置写入数据
  append   在表格末尾追加数据

用法:
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py create --name <名称> [--sheet-data <json>] [--parent-id <id>]
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py read   <docs-url> [--sheet-index N] [--range 0!A1:Z100]
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py write  <docs-url> <sheet-data-json> [--sheet-index N] [--cell-index A1]
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py append <docs-url> <sheet-data-json> [--sheet-index N]

参数说明:
  <docs-url>         表格链接（/s/home/ 或 /t/home/）或 docId
  <sheet-data-json>  二维数组 JSON，如 '[["姓名","分数"],["张三",90]]'
  --name             新表格名称（create 子命令必填）
  --sheet-index N    页签索引，从 0 开始（默认 0）
  --cell-index       写入起始单元格（write 子命令，默认 A1）
  --range            查询范围（read 子命令，如 0!A1:D10）
  --parent-id        创建到指定文件夹 ID（create 子命令，可选）

页签选择规则（read 子命令）:
  1. URL 带 ?section=<sheetId>  → 按 sheetId 匹配对应页签
  2. 无 section，URL 带 sheetId=0 的页签 → 自动定位（文档默认页签）
  3. 显式传 --sheet-index N     → 按索引读取

示例:
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py create --name "我的表格"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py create --name "学生成绩" --sheet-data '[["姓名","分数"],["张三",90]]'
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py read   "https://docs.corp.kuaishou.com/s<skill_directory>"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py read   "https://docs.corp.kuaishou.com/s<skill_directory>?section=849588606"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py read   "https://docs.corp.kuaishou.com/s<skill_directory>" --range "0!A1:D10"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py write  "https://docs.corp.kuaishou.com/s<skill_directory>" '[["姓名","分数"],["张三",90]]'
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py write  "https://docs.corp.kuaishou.com/s<skill_directory>" '[["新值"]]' --cell-index B3
  uv run --refresh-package ks_aimate <skill_directory>/scripts/sheet.py append "https://docs.corp.kuaishou.com/s<skill_directory>" '[["李四",85]]'

注意:
  write 子命令仅用于向用户明确指定的固定位置写入，追加到末尾请用 append 子命令
"""

import sys
import re
import json
import urllib.parse
from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://docs.corp.kuaishou.com"
API_BASE = f"{BASE_URL}/merlot/e/api/skills"

DOC_URL_PATTERNS = [
    (r"/s/home/([^/?#]+)", "SHEET"),
    (r"/t/home/[^/]+/([^/?#]+)", "SHEET"),
    (r"/d/home/([^/?#]+)", "DOC"),
    (r"/k/home/[^/]+/([^/?#]+)", "DOC"),
]


def get_sso_client():
    return SmartSSOSession()


def extract_doc_id(url_or_id: str) -> str:
    """从 URL 中提取 docId"""
    for pattern, _ in DOC_URL_PATTERNS:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    if not url_or_id.startswith("http"):
        return url_or_id
    raise ValueError(f"无法从 URL 中提取 docId: {url_or_id}")


def extract_section_id(url_or_id: str) -> str | None:
    """从 URL 的 section 查询参数中提取 sheetId，如 ?section=849588606。
    无 section 参数时返回 "0"（文档默认页签的 sheetId 固定为 0）。"""
    if not url_or_id.startswith("http"):
        return "0"
    parsed = urllib.parse.urlparse(url_or_id)
    params = urllib.parse.parse_qs(parsed.query)
    return params.get("section", ["0"])[0]


def col_index_to_letter(idx: int) -> str:
    """列索引(0-based) → 列字母，如 0→A, 25→Z, 26→AA"""
    result = ""
    while idx >= 0:
        result = chr(ord("A") + idx % 26) + result
        idx = idx // 26 - 1
    return result


# ─────────────────────────────────────────────
# API 调用
# ─────────────────────────────────────────────

def get_sheet_meta(client, doc_id: str, sheet_index: int = 0, sheet_id: str = None) -> tuple:
    """获取表格元数据，返回 (meta_data, sheet_info)。
    若提供 sheet_id，优先按 sheetId 匹配页签（忽略 sheet_index）。"""
    resp = client.request(
        "GET",
        f"{API_BASE}/excel/meta?docId={urllib.parse.quote(doc_id)}",
        headers={"Referer": f"{BASE_URL}/s/home/{doc_id}"}
    )
    result = resp.json()
    if result.get("code") not in (0, 200, None):
        print(f"❌ 获取元数据失败 (code={result.get('code')}): {result.get('message', '未知错误')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    meta_data = result.get("result", {})
    sheets = meta_data.get("sheetInfoList", meta_data.get("sheetInfos", []))
    if not sheets:
        print("❌ 表格没有页签")
        sys.exit(1)
    # 优先按 sheetId 匹配
    if sheet_id is not None:
        for i, s in enumerate(sheets):
            if str(s.get("sheetId", "")) == str(sheet_id):
                print(f"🔗 section={sheet_id} → 页签 index={i} ({s.get('sheetName', '')})")
                return meta_data, s
        print(f"⚠️  未找到 sheetId={sheet_id} 对应的页签，回退到 index={sheet_index}")
    if sheet_index >= len(sheets):
        print(f"❌ 页签索引 {sheet_index} 不存在（共 {len(sheets)} 个页签）")
        sys.exit(1)
    return meta_data, sheets[sheet_index]


def get_sheet_content(client, doc_id: str, range_str: str) -> dict:
    """获取指定范围的单元格数据"""
    resp = client.request(
        "GET",
        f"{API_BASE}/excel/content"
        f"?docId={urllib.parse.quote(doc_id)}"
        f"&range={urllib.parse.quote(range_str)}",
        headers={"Referer": f"{BASE_URL}/s/home/{doc_id}"}
    )
    result = resp.json()
    if result.get("code") not in (0, 200, None):
        print(f"❌ 获取内容失败 (code={result.get('code')}): {result.get('message', '未知错误')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    return result.get("result", {})


def write_sheet_data(client, doc_id: str, cell_contents: list, sheet_index: int = 0, cell_index: str = "A1") -> str:
    """向表格写入数据，返回 version"""
    payload = {
        "docId": doc_id,
        "sheetIndex": sheet_index,
        "cellIndex": cell_index,
        "cellContents": cell_contents,
    }
    resp = client.request(
        "POST",
        f"{API_BASE}/excel/simple-edit",
        json=payload,
        headers={"Referer": f"{BASE_URL}/s/home/{doc_id}"}
    )
    result = resp.json()
    if result.get("code") not in (0, 200, None):
        print(f"❌ 写入失败 (code={result.get('code')}): {result.get('message', '未知错误')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    return result.get("result", "")


# ─────────────────────────────────────────────
# 子命令实现
# ─────────────────────────────────────────────

def cmd_create(name: str, sheet_data: list = None, parent_id: str = None):
    """创建新表格，可选同时写入初始数据"""
    client = get_sso_client()
    create_payload = {"docTypeEn": "SHEET", "docName": name}
    if parent_id:
        create_payload["parentId"] = parent_id
    resp = client.request(
        "POST",
        f"{API_BASE}/docs/create",
        json=create_payload,
        headers={"Referer": BASE_URL}
    )
    result = resp.json()
    if result.get("code") not in (0, 200, None):
        print(f"❌ 创建失败 (code={result.get('code')}): {result.get('message', '未知错误')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    data = result.get("result", {})
    doc_id = data.get("docId")
    open_url = data.get("openDocUrl", "")
    print(f"✅ 表格已创建: docId={doc_id}")
    print(f"   链接: {open_url}")

    if sheet_data and doc_id:
        version = write_sheet_data(client, doc_id, sheet_data, sheet_index=0, cell_index="A1")
        print(f"✅ 初始数据已写入 ({len(sheet_data)} 行), version={version}")

    print(f"\n打开链接: {open_url}")


def cmd_read(doc_id: str, sheet_index: int, range_str: str = None, sheet_id: str = None):
    """读取表格内容"""
    client = get_sso_client()
    meta_data, sheet_info = get_sheet_meta(client, doc_id, sheet_index, sheet_id=sheet_id)
    actual_index = sheet_info.get("sheetIndex", sheet_index)

    print(f"📊 表格名称: {meta_data.get('docName', 'N/A')}")
    print(f"📑 页签: {sheet_info.get('sheetName', 'N/A')} (index={actual_index})")
    print(f"   行数: {sheet_info.get('maxRowIndex', 'N/A')}, 列数: {sheet_info.get('maxColumnIndex', 'N/A')}")

    if range_str:
        effective_range = range_str
    else:
        max_row = min(sheet_info.get("maxRowIndex", 100), 200)
        max_col = min(sheet_info.get("maxColumnIndex", 50), 50)
        col_letter = col_index_to_letter(max_col)
        effective_range = f"{actual_index}!A1:{col_letter}{max_row}"

    print(f"📐 查询范围: {effective_range}\n")
    content = get_sheet_content(client, doc_id, effective_range)
    print(json.dumps(content, ensure_ascii=False, indent=2))


def cmd_write(doc_id: str, sheet_data: list, sheet_index: int, cell_index: str):
    """向表格指定位置写入数据"""
    client = get_sso_client()
    print(f"📊 文档 ID: {doc_id}")
    print(f"✏️  写入位置: 页签 {sheet_index}, 起始单元格 {cell_index}")
    print(f"   数据行数: {len(sheet_data)}")
    version = write_sheet_data(client, doc_id, sheet_data, sheet_index=sheet_index, cell_index=cell_index)
    print(f"✅ 写入完成, version={version}")


def cmd_append(doc_id: str, sheet_data: list, sheet_index: int):
    """在表格末尾追加数据"""
    client = get_sso_client()
    _, sheet_info = get_sheet_meta(client, doc_id, sheet_index)
    max_row = sheet_info.get("maxRowIndex", 0)
    max_col = sheet_info.get("maxColumnIndex", 0)
    print(f"📊 文档 ID: {doc_id}")
    print(f"📑 当前表格: 行数={max_row}, 列数={max_col}")

    if max_row > 0 and max_col > 0:
        col_letter = col_index_to_letter(min(max_col, 50))
        range_str = f"{sheet_index}!A1:{col_letter}{max_row}"
        content = get_sheet_content(client, doc_id, range_str)
        cells = content.get("rows") or content.get("excelShowDataCellDTOS", [])
        last_data_row = 0
        for row in cells:
            for cell in row:
                if cell and cell.get("showValue"):
                    row_idx = cell.get("rowIndex", 0)
                    if row_idx > last_data_row:
                        last_data_row = row_idx
        next_row = last_data_row + 1
    else:
        next_row = 0

    cell_index = f"A{next_row + 1}"
    print(f"➕ 追加位置: {cell_index} (第 {next_row + 1} 行)")
    version = write_sheet_data(client, doc_id, sheet_data, sheet_index=sheet_index, cell_index=cell_index)
    print(f"✅ 追加完成 ({len(sheet_data)} 行), version={version}")


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    # create 子命令不需要 <docs-url>
    if cmd == "create":
        rest = sys.argv[2:]
        name = None
        sheet_data = None
        parent_id = None
        i = 0
        while i < len(rest):
            if rest[i] == "--name" and i + 1 < len(rest):
                name = rest[i + 1]; i += 2
            elif rest[i] == "--sheet-data" and i + 1 < len(rest):
                sheet_data = json.loads(rest[i + 1]); i += 2
            elif rest[i] == "--parent-id" and i + 1 < len(rest):
                parent_id = rest[i + 1]; i += 2
            else:
                i += 1
        if not name:
            print("用法: sheet.py create --name <名称> [--sheet-data <json>] [--parent-id <id>]")
            sys.exit(1)
        cmd_create(name, sheet_data, parent_id)
        return

    # 其余子命令需要 <docs-url>
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    url_or_id = sys.argv[2]
    try:
        doc_id = extract_doc_id(url_or_id)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if cmd == "read":
        rest = sys.argv[3:]
        sheet_index = 0
        range_str = None
        sheet_id = extract_section_id(url_or_id)  # 有 section 用 section，无则默认 "0"
        i = 0
        while i < len(rest):
            if rest[i] == "--sheet-index" and i + 1 < len(rest):
                sheet_index = int(rest[i + 1]); sheet_id = None; i += 2  # 显式指定时忽略 section
            elif rest[i] == "--range" and i + 1 < len(rest):
                range_str = rest[i + 1]; i += 2
            else:
                i += 1
        cmd_read(doc_id, sheet_index, range_str, sheet_id=sheet_id)

    elif cmd == "write":
        if len(sys.argv) < 4:
            print("用法: sheet.py write <docs-url> <sheet-data-json> [--sheet-index N] [--cell-index A1]")
            sys.exit(1)
        sheet_data = json.loads(sys.argv[3])
        rest = sys.argv[4:]
        sheet_index = 0
        cell_index = "A1"
        i = 0
        while i < len(rest):
            if rest[i] == "--sheet-index" and i + 1 < len(rest):
                sheet_index = int(rest[i + 1]); i += 2
            elif rest[i] == "--cell-index" and i + 1 < len(rest):
                cell_index = rest[i + 1]; i += 2
            else:
                i += 1
        cmd_write(doc_id, sheet_data, sheet_index, cell_index)

    elif cmd == "append":
        if len(sys.argv) < 4:
            print("用法: sheet.py append <docs-url> <sheet-data-json> [--sheet-index N]")
            sys.exit(1)
        sheet_data = json.loads(sys.argv[3])
        rest = sys.argv[4:]
        sheet_index = 0
        i = 0
        while i < len(rest):
            if rest[i] == "--sheet-index" and i + 1 < len(rest):
                sheet_index = int(rest[i + 1]); i += 2
            else:
                i += 1
        cmd_append(doc_id, sheet_data, sheet_index)

    else:
        print(f"❌ 未知子命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
