#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "ks-aimate",
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
"""
Kwai Gym MCP Tool - MCP 工具封装
用于通过 MCP 协议调用 Kwai Gym API
"""

import sys
import os
import json

# 导入当前目录的 client 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import KwaiGymClient


def get_gym_list():
    """获取健身房列表"""
    client = KwaiGymClient()
    gyms = client.get_gym_list()
    return {"result": gyms}


def get_gym_detail(shop_id: int):
    """获取健身房详细信息"""
    client = KwaiGymClient()
    detail = client.get_gym_detail(shop_id)
    return {"result": detail}


def get_teachers(shop_id: int):
    """获取教练列表"""
    client = KwaiGymClient()
    teachers = client.get_teachers(shop_id)
    return {"result": teachers}


def get_group_lessons(shop_id: int, date: str):
    """获取团课预约列表"""
    client = KwaiGymClient()
    lessons = client.get_group_lessons(shop_id, date)
    return {"result": lessons}


def get_setting_detail(setting_id: int):
    """获取健身房设置信息"""
    client = KwaiGymClient()
    setting = client.get_setting_detail(setting_id)
    return {"result": setting}


def get_user_notices(shop_id: int, timestamp: int = None):
    """获取用户通知"""
    client = KwaiGymClient()
    notices = client.get_user_notices(shop_id, timestamp)
    return {"result": notices}


def get_activities(shop_id: int):
    """获取活动列表"""
    client = KwaiGymClient()
    activities = client.get_activities(shop_id)
    return {"result": activities}


def get_course_tags(shop_id: int, date: str):
    """获取课程标签"""
    client = KwaiGymClient()
    tags = client.get_course_tags(shop_id, date)
    return {"result": tags}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: uv run scripts/mcp_tool.py <tool_name> [args...]")
        print("可用工具:")
        print("  get_gym_list")
        print("  get_gym_detail <shop_id>")
        print("  get_teachers <shop_id>")
        print("  get_group_lessons <shop_id> <date>")
        print("  get_setting_detail <setting_id>")
        print("  get_user_notices <shop_id> [timestamp]")
        print("  get_activities <shop_id>")
        print("  get_course_tags <shop_id> <date>")
        sys.exit(1)

    tool_name = sys.argv[1]

    try:
        tools = {
            "get_gym_list": lambda: get_gym_list(),
            "get_gym_detail": lambda: get_gym_detail(int(sys.argv[2])) if len(sys.argv) > 2 else {"error": "缺少 shop_id 参数"},
            "get_teachers": lambda: get_teachers(int(sys.argv[2])) if len(sys.argv) > 2 else {"error": "缺少 shop_id 参数"},
            "get_group_lessons": lambda: get_group_lessons(int(sys.argv[2]), sys.argv[3]) if len(sys.argv) > 3 else {"error": "缺少 shop_id 或 date 参数"},
            "get_setting_detail": lambda: get_setting_detail(int(sys.argv[2])) if len(sys.argv) > 2 else {"error": "缺少 setting_id 参数"},
            "get_user_notices": lambda: get_user_notices(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else None),
            "get_activities": lambda: get_activities(int(sys.argv[2])) if len(sys.argv) > 2 else {"error": "缺少 shop_id 参数"},
            "get_course_tags": lambda: get_course_tags(int(sys.argv[2]), sys.argv[3]) if len(sys.argv) > 3 else {"error": "缺少 shop_id 或 date 参数"},
        }

        if tool_name in tools:
            result = tools[tool_name]()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未知工具：{tool_name}")
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
