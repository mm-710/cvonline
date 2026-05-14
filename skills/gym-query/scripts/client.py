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
Kwai Gym API Client
快手健身房 API 客户端 - 使用 SmartSSOSession 自动处理认证
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL_XZ = "https://xz.corp.kuaishou.com"
BASE_URL_SAAS = "https://saas.qingchengfit.cn"


class KwaiGymClient:
    """快手健身房 API 客户端 - 使用 SmartSSOSession 自动处理认证"""
    
    def __init__(self):
        # 初始化 SSO 会话客户端
        self.client = SmartSSOSession()
    
    def get_gym_list(self) -> List[Dict[str, Any]]:
        """获取健身房列表"""
        url = f"{BASE_URL_XZ}/xz-gym/api/user/gym/query"
        response = self.client.request("POST", url, json={})
        data = response.json()
        
        if data.get("code") == 0:
            return data.get("result", [])
        raise Exception(f"获取健身房列表失败: {data.get('message')}")
    
    def get_gym_detail(self, shop_id: int) -> Dict[str, Any]:
        """获取健身房详细信息"""
        url = f"{BASE_URL_SAAS}/api/shops/{shop_id}/detail/"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", {}).get("shop", {})
        raise Exception(f"获取健身房详情失败: {data}")
    
    def get_teachers(self, shop_id: int) -> List[Dict[str, Any]]:
        """获取教练列表"""
        url = f"{BASE_URL_SAAS}/api/v2/shops/{shop_id}/teachers/?show_all=1"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", {}).get("teachers", [])
        raise Exception(f"获取教练列表失败: {data}")
    
    def get_group_lessons(self, shop_id: int, date: str) -> List[Dict[str, Any]]:
        """获取团课预约列表（date: YYYY-MM-DD）"""
        url = f"{BASE_URL_SAAS}/api/mobile/schedules/group/?shop_id={shop_id}&date={date}"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", {}).get("schedules", [])
        raise Exception(f"获取团课列表失败: {data}")
    
    def get_setting_detail(self, setting_id: int) -> Dict[str, Any]:
        """获取健身房设置信息"""
        url = f"{BASE_URL_SAAS}/api/v2/setting/{setting_id}/detail/"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", {})
        raise Exception(f"获取设置详情失败: {data}")
    
    def get_user_notices(self, shop_id: int, timestamp: int = None) -> Dict[str, Any]:
        """获取用户通知"""
        import time
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        url = f"{BASE_URL_SAAS}/api/user/notices/no/?shop_id={shop_id}&timestamp={timestamp}"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", {})
        raise Exception(f"获取用户通知失败: {data}")
    
    def get_activities(self, shop_id: int) -> List[Dict[str, Any]]:
        """获取活动列表"""
        url = f"{BASE_URL_SAAS}/api/v2/shops/{shop_id}/homepage/grant-activites/"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", [])
        raise Exception(f"获取活动列表失败: {data}")
    
    def get_course_tags(self, shop_id: int, date: str) -> List[Dict[str, Any]]:
        """获取课程标签"""
        url = f"{BASE_URL_SAAS}/api/mobile/schedules/tags/?shop_id={shop_id}&date={date}"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get("status") == 200:
            return data.get("data", [])
        raise Exception(f"获取课程标签失败: {data}")


def main():
    """命令行入口"""
    client = KwaiGymClient()

    if len(sys.argv) < 2:
        print("用法: uv run scripts/client.py <command> [args...]")
        print("命令:")
        print("  list                    - 获取健身房列表")
        print("  detail <shop_id>        - 获取健身房详情")
        print("  teachers <shop_id>      - 获取教练列表")
        print("  lessons <shop_id> <date> - 获取团课列表 (date: YYYY-MM-DD)")
        print("  activities <shop_id>    - 获取活动列表")
        print("  tags <shop_id> <date>   - 获取课程标签")
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "list":
            result = client.get_gym_list()
        elif cmd == "detail" and len(sys.argv) >= 3:
            result = client.get_gym_detail(int(sys.argv[2]))
        elif cmd == "teachers" and len(sys.argv) >= 3:
            result = client.get_teachers(int(sys.argv[2]))
        elif cmd == "lessons" and len(sys.argv) >= 4:
            result = client.get_group_lessons(int(sys.argv[2]), sys.argv[3])
        elif cmd == "activities" and len(sys.argv) >= 3:
            result = client.get_activities(int(sys.argv[2]))
        elif cmd == "tags" and len(sys.argv) >= 4:
            result = client.get_course_tags(int(sys.argv[2]), sys.argv[3])
        else:
            print(f"未知命令或参数不足：{cmd}")
            sys.exit(1)

        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
