#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "ks_aimate",
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
快手智能卫生间查询工具 - 独立版（uv 自包含脚本）

Usage:
    # 查询万家灯火 8 层
    uv run query_wc.py --garden "万家灯火" --floor 8
    
    # 查询元中心 1号楼 3 层
    uv run query_wc.py --garden "元中心" --building "1号楼" --floor 3
    
    # 列出所有可用园区
    uv run query_wc.py --list-gardens
"""

import json
import sys
import os
from pathlib import Path
from ks_aimate.sso_login_client import SmartSSOSession

class WCQueryTool:
    """卫生间查询工具 - 使用 SmartSSOSession 自动处理认证"""
    
    BASE_URL = "https://xz.corp.kuaishou.com/is-intelligent-device"
    
    def __init__(self):
        self.client = SmartSSOSession()
    
    def get_garden_building_list(self):
        """获取园区和楼宇列表"""
        url = f"{self.BASE_URL}/api/inte-devi/garden-building-list"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get('code') != 0:
            raise Exception(f"获取园区列表失败: {data.get('message')}")
        
        return data.get('result', [])
    
    def find_garden_building(self, garden_keyword: str = None, building_keyword: str = None):
        """根据关键词查找园区和楼宇
        
        Args:
            garden_keyword: 园区关键词（如"万家灯火"）
            building_keyword: 楼宇关键词（如"B座"）
        
        Returns:
            (garden_id, building_id, garden_name, building_name) 或 None
        """
        gardens = self.get_garden_building_list()
        
        # 如果没有指定园区，使用第一个
        if not garden_keyword:
            if gardens:
                garden = gardens[0]
                building = garden.get('buildingList', [])[0] if garden.get('buildingList') else None
                if building:
                    return (
                        garden['gardenId'],
                        building['buildingId'],
                        garden['gardenName'],
                        building['buildingName']
                    )
        
        # 查找匹配的园区
        for garden in gardens:
            if garden_keyword and garden_keyword in garden['gardenName']:
                buildings = garden.get('buildingList', [])
                
                # 如果指定了楼宇关键词，查找匹配的楼宇
                if building_keyword:
                    for building in buildings:
                        if building_keyword in building['buildingName']:
                            return (
                                garden['gardenId'],
                                building['buildingId'],
                                garden['gardenName'],
                                building['buildingName']
                            )
                
                # 否则返回该园区的第一个楼宇
                if buildings:
                    building = buildings[0]
                    return (
                        garden['gardenId'],
                        building['buildingId'],
                        garden['gardenName'],
                        building['buildingName']
                    )
        
        return None
    
    def get_devices(self, garden_id: int, building_id: int):
        """获取指定园区和楼宇的设备状态"""
        url = f"{self.BASE_URL}/api/inte-devi/{garden_id}/{building_id}/devices"
        response = self.client.request("GET", url)
        data = response.json()
        
        if data.get('code') != 0:
            raise Exception(f"获取设备状态失败: {data.get('message')}")
        
        return data.get('result', [])
    
    def query_floor(self, garden_keyword: str = None, building_keyword: str = None, floor: int = None):
        """查询指定楼层的卫生间状态
        
        Args:
            garden_keyword: 园区关键词（如"万家灯火"、"五彩城"）
            building_keyword: 楼宇关键词（如"B座"）
            floor: 楼层号（如 8）
        """
        # 查找园区和楼宇
        result = self.find_garden_building(garden_keyword, building_keyword)
        if not result:
            print(f"❌ 未找到匹配的园区或楼宇")
            if garden_keyword:
                print(f"   搜索关键词：园区='{garden_keyword}', 楼宇='{building_keyword or '任意'}'")
            return
        
        garden_id, building_id, garden_name, building_name = result
        print(f"📍 查询位置：{garden_name} - {building_name}")
        
        # 获取设备状态
        floors = self.get_devices(garden_id, building_id)
        
        # 查找指定楼层
        target_floor = None
        if floor:
            floor_name = f"{floor}层"
            for floor_data in floors:
                if floor_data.get('floorName') == floor_name:
                    target_floor = floor_data
                    break
            
            if not target_floor:
                print(f"❌ 未找到 {floor_name} 的智能卫生间数据")
                return
            
            self._display_floor(target_floor)
        else:
            # 显示所有楼层
            for floor_data in floors:
                self._display_floor(floor_data)
    
    def _display_floor(self, floor_data):
        """显示楼层卫生间状态"""
        floor_name = floor_data.get('floorName', '未知楼层')
        print(f"\n{'='*50}")
        print(f"🏢 {floor_name}")
        print(f"{'='*50}\n")
        
        washrooms = floor_data.get('washroomList', [])
        if not washrooms:
            print("  (暂无智能卫生间数据)")
            return
        
        for washroom in washrooms:
            self._display_washroom(washroom)
    
    def _is_gendered_washroom(self, washroom_name: str) -> bool:
        """判断卫生间名称是否包含性别信息
        
        Args:
            washroom_name: 卫生间名称，如"男卫1"、"女卫东"、"无障碍卫生间"
        
        Returns:
            True 如果包含明确的性别标识（男/女），False 否则
        """
        gender_keywords = ['男', '女']
        return any(keyword in washroom_name for keyword in gender_keywords)
    
    def _display_washroom(self, washroom):
        """显示卫生间状态"""
        washroom_name = washroom.get('washroomName', '未知位置')
        devices = washroom.get('deviceList', [])
        
        if not devices:
            print(f"📍 {washroom_name}")
            
            # 判断是否是性别相关的卫生间（男卫/女卫）
            if self._is_gendered_washroom(washroom_name):
                print(f"   ℹ️ 无可用数据（接口限制：仅返回与您性别一致的卫生间数据）")
            else:
                print(f"   ⚠️ 此卫生间暂未接入智能设备监控系统")
            return
        
        # 统计空闲率
        free_count = sum(1 for d in devices if d.get('deviceState') == 'OPEN')
        total_count = len(devices)
        rate = (free_count / total_count * 100) if total_count > 0 else 0
        
        print(f"📍 {washroom_name}")
        print(f"   空闲率：{free_count}/{total_count} ({rate:.0f}%)\n")
        
        # 列出所有坑位
        for device in devices:
            device_name = device.get('deviceName', '')
            device_state = device.get('deviceState', '')
            device_desc = device.get('deviceDesc', '')
            
            if device_state == 'OPEN':
                status = "✅ 空闲"
            else:
                status = f"❌ 占用 ({device_desc})"
            
            print(f"   {device_name}号坑位: {status}")
        
        print()


def main():
    """主函数 - 支持命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='查询快手园区智能卫生间状态')
    parser.add_argument('--garden', '-g', help='园区关键词（如"万家灯火"、"五彩城"）')
    parser.add_argument('--building', '-b', help='楼宇关键词（如"B座"）')
    parser.add_argument('--floor', '-f', type=int, help='楼层号（如 8）')
    parser.add_argument('--list-gardens', action='store_true', help='列出所有可用园区和楼宇')
    
    args = parser.parse_args()
    
    # 初始化查询工具（自动处理 SSO 认证）
    tool = WCQueryTool()
    
    # 列出所有园区
    if args.list_gardens:
        try:
            gardens = tool.get_garden_building_list()
            print("\n📋 可用园区和楼宇：\n")
            for garden in gardens:
                print(f"🏢 {garden['gardenName']} (ID: {garden['gardenId']})")
                for building in garden.get('buildingList', []):
                    print(f"   └─ {building['buildingName']} (ID: {building['buildingId']})")
            print()
        except Exception as e:
            print(f"❌ 获取园区列表失败: {e}")
            sys.exit(1)
        return
    
    # 执行查询
    try:
        tool.query_floor(
            garden_keyword=args.garden,
            building_keyword=args.building,
            floor=args.floor
        )
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
