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
万维表格（MetaSheet）操作 — 读取结构 / 读取数据 / 写入数据

子命令:
  create          创建新万维表格
  meta            获取万维表格结构（Sheet 列表、列定义）
  content         读取记录数据（返回所有记录）
  add-record      新增一条记录
  update-record   更新指定记录的字段
  delete-record   删除指定记录

用法:
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py create        [--parent-id <父目录ID>]
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py meta          <docs-url>
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py content       <docs-url> [sheet-id]
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py add-record    <docs-url> [sheet-id] <values-json>
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py update-record <docs-url> [sheet-id] <record-id> <values-json>
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py delete-record <docs-url> [sheet-id] <record-id>

参数说明:
  <docs-url>      万维表格链接（/m/home/ 或 /b/home/）或 docId
                  若链接包含 #sheetId=shdXXX，则 [sheet-id] 参数可省略
  [sheet-id]      Sheet ID（shd 开头，从 meta 命令获取；可从 URL hash 自动解析）
  <record-id>     记录 ID（rc 开头，从 content 命令获取）
  <values-json>   字段值 JSON 对象，key 为字段 ID（如 title/field1），value 为字段值

字段值格式（values-json）:
  文本(text):          {"title": "示例文本"}
  单选(single_select): {"field1": "选项名称"}
  多选(multi_select):  {"field1": ["选项A", "选项B"]}
  数字(number):        {"field1": 90}
  日期(date):          {"field1": "2026-04-15"}  → 自动转为毫秒时间戳
  人员(person):        {"field1": ["username1"]}

示例:
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py create
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py create --parent-id "mine"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py meta "https://docs.corp.kuaishou.com/m<skill_directory>"
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py content "https://docs.corp.kuaishou.com/m<skill_directory>" "shdc77c..."
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py add-record "https://docs.corp.kuaishou.com/m<skill_directory>" "shdXXX" '{"title":"新记录","field1":"选项A"}'
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py update-record "https://docs.corp.kuaishou.com/m<skill_directory>" "shdXXX" "rc9717..." '{"title":"更新后的值"}'
  uv run --refresh-package ks_aimate <skill_directory>/scripts/metasheet.py delete-record "https://docs.corp.kuaishou.com/m<skill_directory>" "shdXXX" "rc9717..."
"""

import sys
import re
import json
import datetime
import uuid
import time
from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://docs.corp.kuaishou.com"

DOC_URL_PATTERNS = [
    r"/m/home/([^/?#]+)",
    r"/b/home/[^/]+/([^/?#]+)",
    r"/d/home/([^/?#]+)",
    r"/k/home/[^/]+/([^/?#]+)",
]


def get_sso_client():
    return SmartSSOSession()


def extract_doc_id(url_or_id: str) -> str:
    """从 URL 中提取 docId"""
    for pattern in DOC_URL_PATTERNS:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    if not url_or_id.startswith("http"):
        return url_or_id
    raise ValueError(f"无法从 URL 中提取 docId: {url_or_id}")


def extract_sheet_and_view_id(url: str) -> tuple[str | None, str | None]:
    """从万维表格 URL 的 hash 片段中提取 sheetId 和 viewId（可选）

    URL 格式示例:
      https://docs.corp.kuaishou.com/m<skill_directory>#sheetId=shdXXX&viewId=vwXXX
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    fragment = parsed.fragment
    if not fragment:
        return None, None
    params = {}
    for part in fragment.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            params[k] = v
    return params.get("sheetId"), params.get("viewId")


def api_get(client, url: str) -> dict:
    """GET 请求，失败时报错退出"""
    resp = client.request("GET", url)
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {url}")
        print(resp.text[:300])
        sys.exit(1)
    result = resp.json()
    code = result.get("code", 0)
    if code != 0:
        print(f"❌ 接口失败 (code={code}): {result.get('message', '未知错误')}")
        sys.exit(1)
    return result


def api_post(client, url: str, payload: dict) -> dict:
    """POST 请求，失败时报错退出"""
    resp = client.request("POST", url, json=payload)
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {url}")
        print(resp.text[:300])
        sys.exit(1)
    result = resp.json()
    code = result.get("code", 0)
    if code != 0:
        msg = result.get("message", "未知错误")
        if code == 40014:
            print(f"❌ 权限不足：当前账号对该文档没有编辑权限 (code={code}): {msg}")
        else:
            print(f"❌ 接口失败 (code={code}): {msg}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    return result


# ─────────────────────────────────────────────
# 内部 API
# ─────────────────────────────────────────────

def load_doc(client, doc_id: str) -> dict:
    """获取文档版本信息"""
    result = api_get(client, f"{BASE_URL}/metasheet/api/load/{doc_id}?um=false")
    return result.get("result", {})


def get_sheet_snapshot(client, doc_id: str, sheet_id: str) -> list:
    """获取指定 Sheet 的快照（含列定义）"""
    resp = client.request(
        "GET",
        f"{BASE_URL}/metasheet/api/{doc_id}/snapshot/sheets/{sheet_id}/last?um=false"
    )
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}")
        sys.exit(1)
    return resp.json()


def get_record_order_block(client, doc_id: str, sheet_id: str) -> dict:
    """获取 sheet 对应的 record-order block（包含 recordOrder 列表和 block id）"""
    resp = client.request(
        "GET",
        f"{BASE_URL}/metasheet/api/{doc_id}/sheets/{sheet_id}/blocks/?um=false&cursor=0"
    )
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}")
        sys.exit(1)
    blocks = resp.json().get("result", [])
    for b in blocks:
        if b.get("content", {}).get("type") == "record-order":
            return b
    return {}


def get_all_blocks_by_id(client, doc_id: str, sheet_id: str) -> dict:
    """返回 {record_id: block} 的 dict，cursor=0 获取全量"""
    resp = client.request(
        "GET",
        f"{BASE_URL}/metasheet/api/{doc_id}/sheets/{sheet_id}/blocks/?um=false&cursor=0"
    )
    if resp.status_code != 200:
        sys.exit(1)
    blocks = resp.json().get("result", [])
    return {b.get("id"): b for b in blocks if b.get("id")}


def parse_sheet_schema(snapshot: list) -> tuple:
    """从快照中提取列定义，返回 (schema, sheet_name)"""
    for item in snapshot:
        if isinstance(item, dict) and item.get("type") == 2:
            content = item.get("content", {})
            return content.get("schema", {}), content.get("name", "N/A")
    return {}, "N/A"


def build_option_id_map(schema: dict) -> dict:
    """为 single_select/multi_select 构建 {field_id: {option_name: option_id}} 映射"""
    result = {}
    for field_id, cfg in schema.items():
        if cfg and cfg.get("type") in ("single_select", "multi_select"):
            options = cfg.get("property", {}).get("options", [])
            result[field_id] = {opt["name"]: opt["id"] for opt in options if "id" in opt and "name" in opt}
    return result


def build_option_name_map(schema: dict) -> dict:
    """为 single_select/multi_select 构建 {field_id: {option_id: option_name}} 映射"""
    result = {}
    for field_id, cfg in schema.items():
        if cfg and cfg.get("type") in ("single_select", "multi_select"):
            options = cfg.get("property", {}).get("options", [])
            result[field_id] = {opt["id"]: opt["name"] for opt in options if "id" in opt and "name" in opt}
    return result


def convert_date_value(raw_value) -> str:
    """将 date 字段的时间戳转为 YYYY-MM-DD（UTC），空值返回 None"""
    if isinstance(raw_value, dict):
        dates = raw_value.get("dates") or raw_value.get("value") or []
        if dates:
            try:
                ts_ms = int(dates[0])
                dt = datetime.datetime.fromtimestamp(ts_ms / 1000, tz=datetime.timezone.utc)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass
        return None
    elif isinstance(raw_value, list) and raw_value:
        try:
            ts_ms = int(raw_value[0])
            dt = datetime.datetime.fromtimestamp(ts_ms / 1000, tz=datetime.timezone.utc)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    return None


def date_str_to_ms(date_str: str) -> int:
    """将 YYYY-MM-DD 字符串转为 UTC 零点毫秒时间戳"""
    import calendar
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return calendar.timegm(dt.timetuple()) * 1000


def build_field_value(field_id: str, raw_val, schema: dict) -> dict:
    """根据列类型构建写入格式的字段 value"""
    col_type = (schema.get(field_id) or {}).get("type", "text")
    if col_type == "date" and isinstance(raw_val, str):
        try:
            ms = date_str_to_ms(raw_val)
            return {"type": col_type, "value": {"dates": [ms]}}
        except ValueError:
            pass
    if col_type in ("multi_select", "person") and isinstance(raw_val, str):
        raw_val = [raw_val]
    # 单选/多选：将选项名称转为选项 ID
    if col_type in ("single_select", "multi_select"):
        id_map = build_option_id_map(schema).get(field_id, {})
        if id_map:
            if col_type == "single_select" and isinstance(raw_val, str):
                raw_val = id_map.get(raw_val, raw_val)
            elif col_type == "multi_select" and isinstance(raw_val, list):
                raw_val = [id_map.get(v, v) for v in raw_val]
    return {"type": col_type, "value": raw_val}


def save_blocks(client, doc_id: str, operations: list) -> dict:
    """提交 block 操作到服务端"""
    payload = {
        "sid": str(uuid.uuid4()),
        "transactions": [{
            "id": str(uuid.uuid4()),
            "operations": operations,
        }]
    }
    return api_post(client, f"{BASE_URL}/metasheet/api/save/block/{doc_id}?um=false", payload)


# ─────────────────────────────────────────────
# 子命令实现
# ─────────────────────────────────────────────

def cmd_create(parent_id: str = "mine"):
    """创建新万维表格"""
    client = get_sso_client()
    payload = {"docTypeEn": "metaSheet", "parentId": parent_id}
    result = api_post(client, f"{BASE_URL}/metasheet/api/create?um=false", payload)
    data = result.get("result", {})
    doc_id = data.get("docId", "")
    open_url = data.get("openDocUrl", "")
    sheet_id = data.get("defaultSheetId", "")
    view_id = data.get("defaultViewId", "")
    title = data.get("title", "未命名万维表格")

    print(f"✅ 万维表格已创建")
    print(f"   标题: {title}")
    print(f"   docId: {doc_id}")
    print(f"   链接: {open_url}#sheetId={sheet_id}&viewId={view_id}")
    print(f"   defaultSheetId: {sheet_id}")
    print(f"   defaultViewId:  {view_id}")


def cmd_meta(doc_id: str):
    """获取万维表格结构（Sheet 列表、列定义）"""
    client = get_sso_client()

    # 获取文档名称
    meta_resp = client.request("POST", f"{BASE_URL}/merlot/api/docs/cosmo/meta/{doc_id}?um=false", json={})
    meta_json = meta_resp.json()
    doc_name = meta_json.get("result", {}).get("docName", "N/A") if meta_json.get("code") == 0 else "N/A"

    load_data = load_doc(client, doc_id)
    sheet_versions = load_data.get("sheetSnapshotVersions", {})

    # 从 load 数据获取 Sheet 顺序
    sheet_order = []
    for s in load_data.get("sheets", []):
        if isinstance(s, dict) and s.get("content", {}).get("type") == "data-base":
            sheet_order = s["content"].get("sheetOrder", [])
            break
    if not sheet_order:
        sheet_order = list(sheet_versions.keys())

    print(f"📊 万维表格名称: {doc_name}")
    print(f"   docId: {doc_id}")
    print(f"   版本: {load_data.get('version', 'N/A')}")
    print(f"\n共有 {len(sheet_order)} 个 Sheet:\n")

    for idx, sheet_id in enumerate(sheet_order):
        cursor = sheet_versions.get(sheet_id, 0)
        snapshot = get_sheet_snapshot(client, doc_id, sheet_id)
        schema, sheet_name = parse_sheet_schema(snapshot)

        # 从 record-order block 统计存活记录数（实时）
        roc_block = get_record_order_block(client, doc_id, sheet_id)
        record_count = len(roc_block.get("content", {}).get("recordOrder", []))

        print(f"  {idx + 1}. 【{sheet_name}】  sheetId: {sheet_id}")
        print(f"     记录数: {record_count}  列数: {len(schema)}")
        if schema:
            col_info = "  ".join(
                f"{fid}({cfg.get('name', '?')}/{cfg.get('type', '?')})" if cfg else f"{fid}(?/?)"
                for fid, cfg in list(schema.items())[:8]
            )
            if len(schema) > 8:
                col_info += f"  ...共 {len(schema)} 列"
            print(f"     列: {col_info}")
        print()


def cmd_content(doc_id: str, sheet_id: str):
    """读取万维表格记录数据（基于 record-order 列表，保证实时一致）"""
    client = get_sso_client()

    snapshot = get_sheet_snapshot(client, doc_id, sheet_id)
    schema, sheet_name = parse_sheet_schema(snapshot)

    # 用 record-order block 的 recordOrder 列表作为存活记录的权威来源（实时）
    roc_block = get_record_order_block(client, doc_id, sheet_id)
    alive_ids = roc_block.get("content", {}).get("recordOrder", [])

    # 获取所有 block 数据
    all_blocks = get_all_blocks_by_id(client, doc_id, sheet_id)

    print(f"📑 Sheet: {sheet_name}  (sheetId: {sheet_id})")
    print(f"📝 共 {len(alive_ids)} 条记录\n")

    option_name_map = build_option_name_map(schema)

    output = []
    for rec_id in alive_ids:
        rec = all_blocks.get(rec_id, {})
        fields = rec.get("content", {}).get("fields", {})
        readable = {"recordId": rec_id}
        for field_id, field_data in fields.items():
            col_name = schema.get(field_id, {}).get("name", field_id) if schema else field_id
            col_type = field_data.get("type", "")
            val = field_data.get("value")
            if col_type == "date" and val is not None:
                val = convert_date_value(val)
            elif col_type == "single_select" and isinstance(val, str) and val:
                val = option_name_map.get(field_id, {}).get(val, val)
            elif col_type == "multi_select" and isinstance(val, list):
                opt_map = option_name_map.get(field_id, {})
                val = [opt_map.get(v, v) for v in val]
            readable[col_name] = val
        output.append(readable)

    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_add_record(doc_id: str, sheet_id: str, values: dict):
    """新增一条记录"""
    client = get_sso_client()

    # 获取列定义用于类型转换
    snapshot = get_sheet_snapshot(client, doc_id, sheet_id)
    schema, sheet_name = parse_sheet_schema(snapshot)

    # 获取 record-order block 用于更新排序列表
    roc_block = get_record_order_block(client, doc_id, sheet_id)
    roc_id = roc_block.get("id", "")
    record_order = roc_block.get("content", {}).get("recordOrder", [])
    # 插入到列表末尾（作为 reference 用最后一条，placement=after）
    last_ref = record_order[-1] if record_order else None

    # 生成新 record ID
    record_id = "rc" + uuid.uuid4().hex

    # 构建 fields
    fields = {}
    for field_id, raw_val in values.items():
        fields[field_id] = build_field_value(field_id, raw_val, schema)

    t = int(time.time() * 1000)
    operations = [
        {
            "command": "update",
            "blockId": record_id,
            "path": [],
            "content": {"type": "record", "fields": fields},
            "meta": {"isAlive": True, "parentId": sheet_id, "childrenIds": []},
            "applyTime": t,
        },
    ]
    if roc_id:
        list_add_op = {
            "command": "listAdd",
            "blockId": roc_id,
            "path": ["recordOrder"],
            "item": record_id,
            "applyTime": t + 1,
        }
        if last_ref:
            list_add_op["placement"] = "after"
            list_add_op["reference"] = last_ref
        operations.append(list_add_op)

    result = save_blocks(client, doc_id, operations)
    print(f"✅ 记录已新增")
    print(f"   recordId: {record_id}")
    print(f"   Sheet: {sheet_name}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_update_record(doc_id: str, sheet_id: str, record_id: str, values: dict):
    """更新指定记录的字段"""
    client = get_sso_client()

    # 获取列定义
    snapshot = get_sheet_snapshot(client, doc_id, sheet_id)
    schema, sheet_name = parse_sheet_schema(snapshot)

    # 构建 fields（只传需要修改的列）
    fields = {}
    for field_id, raw_val in values.items():
        fields[field_id] = build_field_value(field_id, raw_val, schema)

    operation = {
        "blockId": record_id,
        "path": ["fields"],
        "content": fields,
        "command": "update",
        "applyTime": int(time.time() * 1000),
    }

    result = save_blocks(client, doc_id, [operation])
    print(f"✅ 记录已更新")
    print(f"   recordId: {record_id}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_delete_record(doc_id: str, sheet_id: str, record_id: str):
    """删除指定记录（从 recordOrder 中移除）"""
    client = get_sso_client()

    roc_block = get_record_order_block(client, doc_id, sheet_id)
    roc_id = roc_block.get("id", "")
    if not roc_id:
        print("❌ 找不到 record-order block")
        sys.exit(1)

    # 用 listRemove 从 recordOrder 中移除
    operation = {
        "command": "listRemove",
        "blockId": roc_id,
        "path": ["recordOrder"],
        "item": record_id,
        "applyTime": int(time.time() * 1000),
    }

    result = save_blocks(client, doc_id, [operation])
    print(f"✅ 记录已删除: {record_id}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    # create 子命令不需要 docs-url 参数
    if cmd == "create":
        parent_id = "mine"
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--parent-id" and i + 1 < len(args):
                parent_id = args[i + 1]
                i += 2
            else:
                i += 1
        cmd_create(parent_id=parent_id)
        return

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    url_or_id = sys.argv[2]
    try:
        doc_id = extract_doc_id(url_or_id)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 尝试从 URL hash 中预提取 sheetId（可被命令行显式参数覆盖）
    url_sheet_id, _ = extract_sheet_and_view_id(url_or_id)

    if cmd == "meta":
        cmd_meta(doc_id)

    elif cmd == "content":
        # sheet-id 可由命令行显式提供，也可从 URL hash 中自动解析
        # 正确处理参数：跳过选项参数（如 --limit 3）
        sheet_id = None
        
        # 查找 sheet_id：寻找以 sh 或 shd 开头的参数（sheet ID 格式）
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            # 跳过选项参数及其值
            if arg.startswith("--"):
                i += 2  # 跳过选项和它的值
                continue
            elif arg.startswith("-"):
                i += 1
                continue
            # 检查是否为 sheet_id 格式 (sh 或 shd 开头)
            if arg.startswith("sh"):
                sheet_id = arg
                break
            i += 1
        
        # 如果命令行没有提供，使用从 URL hash 解析的
        if not sheet_id and url_sheet_id:
            sheet_id = url_sheet_id
        
        if not sheet_id:
            print("用法: metasheet.py content <docs-url> <sheet-id>")
            print("  提示: 也可将 sheetId 写在链接 hash 中，如 <docs-url>#sheetId=shdXXX")
            sys.exit(1)
        
        cmd_content(doc_id, sheet_id)

    elif cmd == "add-record":
        if len(sys.argv) >= 5:
            sheet_id = sys.argv[3]
            values = json.loads(sys.argv[4])
        elif url_sheet_id and len(sys.argv) >= 4:
            sheet_id = url_sheet_id
            values = json.loads(sys.argv[3])
        else:
            print("用法: metasheet.py add-record <docs-url> <sheet-id> <values-json>")
            print("  示例: '{\"title\":\"新记录\",\"field1\":\"选项A\"}'")
            print("  提示: 若链接中含 sheetId，可省略 <sheet-id> 参数")
            sys.exit(1)
        cmd_add_record(doc_id, sheet_id, values)

    elif cmd == "update-record":
        if len(sys.argv) >= 6:
            sheet_id = sys.argv[3]
            record_id = sys.argv[4]
            values = json.loads(sys.argv[5])
        elif url_sheet_id and len(sys.argv) >= 5:
            sheet_id = url_sheet_id
            record_id = sys.argv[3]
            values = json.loads(sys.argv[4])
        else:
            print("用法: metasheet.py update-record <docs-url> <sheet-id> <record-id> <values-json>")
            print("  示例: '{\"title\":\"更新后的值\"}'")
            print("  提示: 若链接中含 sheetId，可省略 <sheet-id> 参数")
            sys.exit(1)
        cmd_update_record(doc_id, sheet_id, record_id, values)

    elif cmd == "delete-record":
        if len(sys.argv) >= 5:
            sheet_id = sys.argv[3]
            record_id = sys.argv[4]
        elif url_sheet_id and len(sys.argv) >= 4:
            sheet_id = url_sheet_id
            record_id = sys.argv[3]
        else:
            print("用法: metasheet.py delete-record <docs-url> <sheet-id> <record-id>")
            print("  提示: 若链接中含 sheetId，可省略 <sheet-id> 参数")
            sys.exit(1)
        cmd_delete_record(doc_id, sheet_id, record_id)

    else:
        print(f"❌ 未知子命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
