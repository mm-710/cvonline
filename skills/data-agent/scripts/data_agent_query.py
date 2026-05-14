#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "ks-aimate>=1.0.29",
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

import json
import os
import sys
import time

from ks_aimate.sso_login_client import SmartSSOSession
from ks_aimate.wanqing_token_usage_id import generate_wanqing_token_usage_id
from ks_aimate.wanqing_token_username import get_username
from ks_aimate.myflicker_sdk.client import send_standard_thinking, send_standard_md, EventType


if len(sys.argv) != 4:
    print("Usage: uv run scripts/data_agent_query.py <chat_session_id> <question> <agent_id>")
    sys.exit(1)

# 环境变量配置
KS_AGENT_PLATFORM = os.environ.get("KS_AGENT_PLATFORM", "UNKNOWN")

CHAT_SESSION_ID = sys.argv[1]
QUESTION = sys.argv[2]
AGENT_ID = sys.argv[3]
MODULE = "TG_DATA_PRODUCT_AGENT"
CHAT_API_URL = "https://tc.corp.kuaishou.com/rest/flow/api/v1/llm/agent/open/chat/completions/v2"
SESSION_TTL_SECONDS = 3 * 3600  # 3 小时未使用则过期（秒）

# 根据平台动态构建 session 存储路径
platform_dir = f".{KS_AGENT_PLATFORM}" if KS_AGENT_PLATFORM != "UNKNOWN" else ".default"
SESSION_MAP_FILE = os.path.expanduser(f"~/{platform_dir}/data-agent-sessions.json")
CHAT_TIMEOUT = int(os.environ.get("DATA_AGENT_CHAT_TIMEOUT", "900"))


def load_session_state():
    if not os.path.exists(SESSION_MAP_FILE) or not CHAT_SESSION_ID:
        return "", None

    try:
        with open(SESSION_MAP_FILE, "r") as f:
            session_map = json.load(f)
        session_state = session_map.get(CHAT_SESSION_ID, "")
        if isinstance(session_state, dict):
            last_used_time = session_state.get("lastUsedTime")
            if last_used_time and (int(time.time()) - int(last_used_time)) > SESSION_TTL_SECONDS:
                # session 已过期，视为新 session
                return None, None
            session_id = session_state.get("sessionId", "")
            query_id = session_state.get("queryId")
            return str(session_id) if session_id else "", None
        if session_state:
            return str(session_state), None
    except Exception:
        pass

    return "", None


def save_session_state(session_id, query_id):
    if not session_id or not CHAT_SESSION_ID:
        return

    os.makedirs(os.path.dirname(SESSION_MAP_FILE), exist_ok=True)
    try:
        session_map = {}
        if os.path.exists(SESSION_MAP_FILE):
            with open(SESSION_MAP_FILE, "r") as f:
                try:
                    session_map = json.load(f)
                except Exception:
                    session_map = {}

        session_map[CHAT_SESSION_ID] = {
            "sessionId": str(session_id),
            "queryId": query_id,
            "lastUsedTime": int(time.time()),
        }
        cleanup_expired_sessions(session_map)
        with open(SESSION_MAP_FILE, "w") as f:
            json.dump(session_map, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def cleanup_expired_sessions(session_map: dict) -> None:
    """清理 session_map 中超过 SESSION_TTL_SECONDS 未使用的条目（原地修改）。"""
    now = int(time.time())
    expired_keys = [
        key for key, state in session_map.items()
        if not isinstance(state, dict)
           or not state.get("lastUsedTime")
           or (now - int(state["lastUsedTime"])) > SESSION_TTL_SECONDS
    ]
    for key in expired_keys:
        del session_map[key]


def extract_stream_text(item):
    if not isinstance(item, dict):
        return ""

    for key in ("appendStr", "content", "text", "answer", "message", "value"):
        value = item.get(key)
        if value:
            return str(value)

    return ""


def parse_optional_int(value):
    if value in (None, ""):
        return None

    try:
        return int(value)
    except Exception:
        return None

# 初始化 SmartSSOSession 客户端
client = SmartSSOSession()

# 获取用户名
USER_NAME = get_username()

# 检查用户名是否为空
if not USER_NAME:
    print("❌ 错误: 无法获取用户名，请检查 Git 配置或环境变量")
    sys.exit(1)


# 查询本地字典，获取 data-server-session-id 和 query-id
data_server_session_id, data_server_query_id = load_session_state()



# 构建请求体
payload = {
    "agentId": int(AGENT_ID),
    "module": MODULE,
    "question": QUESTION,
    "userName": USER_NAME,
    "stream": True,
}
if data_server_session_id:
    parsed_session_id = parse_optional_int(data_server_session_id)
    if parsed_session_id is not None:
        payload["sessionId"] = parsed_session_id

# 生成唯一的 request_id（只生成一次，复用）
request_id = generate_wanqing_token_usage_id("req")

headers = {
    "Content-Type": "application/json",
    "X-Ks-Wq-Traffic-Business-Source": "agent_cost_governance",
    "x-ks-wq-request-id": request_id,
    "x-ks-wq-end-user-id": USER_NAME,
    "x-ks-wq-business-extra-info": json.dumps({
        "agent_identify": "",
        "platform": KS_AGENT_PLATFORM,
        "session_id": CHAT_SESSION_ID,
    }),
}



# 状态追踪
is_thinking = False
session_id = None
query_id = None
last_status_label = None
final_output_parts = []
all_raw_lines = []

try:
    response = client.request(
        "POST",
        CHAT_API_URL,
        extra_config={ "obo_required" : True },
        json=payload,
        headers=headers,
        stream=True,
        timeout=(10, CHAT_TIMEOUT),
    )
    if not response.ok:
        print(f"\n❌ HTTP 错误 {response.status_code}: {response.text}")
        sys.exit(1)
    response.raise_for_status()

    for line in response.iter_lines(decode_unicode=True):
        try:
            if not line:
                continue

            line = line.strip()
            if not line:
                continue

            if line.startswith("data:"):
                line = line[5:].strip()

            if line == "[DONE]":
                break

            item_payload = json.loads(line)
            # print(f"[RAW] {line}", flush=True)

            if item_payload.get("result") not in (None, 1, "1"):
                error_msg = item_payload.get("error_msg") or item_payload.get("message") or json.dumps(item_payload, ensure_ascii=False)
                print(f"\n❌ 数据平台接口返回了错误信息：{error_msg}")
                break

            data_node = item_payload.get("data", {})
            if not data_node:
                continue

            if data_node.get("streamEnd") == "[DONE]":
                break

            if "sessionId" in data_node and data_node["sessionId"]:
                session_id = data_node["sessionId"]
            if "queryId" in data_node and data_node["queryId"]:
                query_id = data_node["queryId"]

            step_data = data_node.get("stepData", {})
            sub_type = step_data.get("subType")
            
            # 处理思考过程
            if sub_type == "TG_THINK_STREAMING":
                inner_data_list = step_data.get("data", [])
                if not is_thinking:
                    print("\n> 💡 思考中...", flush=True)
                    is_thinking = True
                for item in inner_data_list:
                    content = item.get("appendStr", "")
                    if content:
                        print(content, end="", flush=True)
                        send_standard_thinking(
                            session_key=CHAT_SESSION_ID,
                            delta=content,
                            event=EventType.STREAM,
                        )
            # 处理思考过程，兼容新版协议
            if sub_type == "MODEL_THINKING":
                component_info = step_data.get("componentInfo", {})
                if not is_thinking:
                    print("\n> 💡 思考中...", flush=True)
                    is_thinking = True
                content = component_info.get("props",{}).get("content")
                if content:
                    print(content, end="", flush=True)
                    send_standard_thinking(
                        session_key=CHAT_SESSION_ID,
                        delta=content,
                        event=EventType.STREAM,
                    )

            # 处理正式输出
            if sub_type == "TG_COMMON_STREAMING":
                inner_data_list = step_data.get("data", [])
                if is_thinking:
                    print("\n> ✅ 思考结束\n", flush=True)
                    is_thinking = False
                for item in inner_data_list:
                    content = item.get("appendStr", "")
                    if content:
                        print(content, end="", flush=True)
                        send_standard_thinking(
                            session_key=CHAT_SESSION_ID,
                            delta=content,
                            event=EventType.STREAM,
                        )
            # 处理正式输出，兼容新版协议
            if sub_type == "MODEL_ANSWER":
                component_info = step_data.get("componentInfo", {})
                if is_thinking:
                    print("\n> ✅ 思考结束\n", flush=True)
                    is_thinking = False
                content = component_info.get("props",{}).get("content")
                if content:
                    print(content, end="", flush=True)
                    send_standard_thinking(
                        session_key=CHAT_SESSION_ID,
                        delta=content,
                        event=EventType.STREAM,
                    )
            # 输出结束
            if sub_type == "TG_COMMON_END":
                print("\n> ✅ 回答结束\n", flush=True)

            # 输出结束，兼容新版协议
            if sub_type == "AGENT_END":
                component_info = step_data.get("componentInfo", {})
                print("\n> ✅ 回答结束\n", flush=True)
                total_costtotal_cost = component_info.get("props",{}).get("totalTimeCost")
                if total_costtotal_cost:
                    print(f"整体耗时:{total_costtotal_cost}", end="", flush=True)
                        
        except (json.JSONDecodeError, KeyError, Exception):
            # 捕获异常，防止解析单行失败导致整个脚本崩溃，静默处理以保证输出流连贯
            continue

except Exception as e:
    if is_thinking:
        print("\n> ⚠️ 思考中断")
    
    # 检查是否是 HTTP 错误
    if hasattr(e, 'response'):
        print(f"\n❌ HTTP 错误: {e}")
        try:
            print(f"响应内容: {e.response.text}")
        except Exception:
            pass
    else:
        print(f"\n❌ 请求发生异常: {e}")

# 如果结束时还在思考状态，闭合它
if is_thinking:
    print("\n> ✅ 思考结束\n", flush=True)


save_session_state(session_id, query_id)
