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
快手行政服务报修系统 API 脚本
版本: 6.0.0

功能:
  - 查询工单进度（query_orders: 进行中/待评价/已完成）
  - 提交报修工单（submit）
  - 查询枚举（园区/楼栋/楼层/服务类型，供 AI 填参）

认证:
  已集成 SmartSSOSession，认证由脚本内部自动处理

用法:
  uv run scripts/repair-api.py --action query_orders --type 1
  uv run scripts/repair-api.py --action submit \\
    --phone 13800138000 --parkId 58 --buildId 76 --floorId 331 \\
    --typeId 101 --description "工位附近空调温度太低，麻烦调节一下"
  uv run scripts/repair-api.py --action get_enums
"""

import json
import argparse
import re
import sys
import time
from ks_aimate.sso_login_client import SmartSSOSession

# ============================================================
# 配置
# ============================================================
BASE_URL = "https://xz.corp.kuaishou.com"

# ============================================================
# 报修 API 客户端
# ============================================================

class RepairClient:
    """快手行政服务报修系统客户端 - 使用 SmartSSOSession 自动处理认证"""
    
    BASE_URL = "https://xz.corp.kuaishou.com"
    
    def __init__(self):
        # 初始化 SSO 会话客户端
        self.client = SmartSSOSession()
        self._service_types_cache = None
    
    def get_parks(self) -> dict:
        """获取园区列表"""
        response = self.client.request("GET", f"{self.BASE_URL}/repair/api/park")
        return response.json()
    
    def get_service_types(self) -> list:
        """获取服务类型列表"""
        if self._service_types_cache is not None:
            return self._service_types_cache
        response = self.client.request("GET", f"{self.BASE_URL}/repair/api/type/get")
        data = response.json()
        result = data.get("result", {})
        if isinstance(result, dict):
            self._service_types_cache = result.get("typeVoList", [])
        else:
            self._service_types_cache = result if isinstance(result, list) else []
        return self._service_types_cache

    def get_type_names_by_id(self, type_id: int) -> tuple[str, str]:
        """根据 typeId 获取 (父类名, 子类名)"""
        for t in self.get_service_types():
            if isinstance(t, dict) and t.get("typeId") == type_id and t.get("parent"):
                parent = t.get("parent", {})
                return parent.get("typeName", ""), t.get("typeName", "")
        return "", ""

    def is_leaf_type_id(self, type_id: int) -> bool:
        """校验是否为可提交的叶子类型（必须带 parent）"""
        for t in self.get_service_types():
            if isinstance(t, dict) and t.get("typeId") == type_id and t.get("parent"):
                return True
        return False

    
    def query_orders(self, order_type: int = 1, page_num: int = 1, page_size: int = 10) -> dict:
        """查询工单
        
        Args:
            order_type: 1=进行中, 2=待评价, 3=已完成
            page_num: 页码
            page_size: 每页数量
        """
        url = f"{self.BASE_URL}/repair/api/query?pageNum={page_num}&pageSize={page_size}&type={order_type}"
        response = self.client.request("GET", url)
        return response.json()
    
    def submit_order(self, phone: str, park_id: int, build_id: int, 
                    floor_id: int, type_id: int, description: str,
                    room_id: int = None, pic_ids: str = "") -> dict:
        """提交报修工单
        
        Args:
            phone: 联系电话
            park_id: 园区 ID
            build_id: 楼栋 ID
            floor_id: 楼层 ID
            type_id: 服务类型 ID
            description: 问题描述
            room_id: 房间 ID（可选）
            pic_ids: 图片 IDs（可选）
        """
        # 自动推导 typeText（必填字段）
        parent_name, child_name = self.get_type_names_by_id(type_id)
        type_text = f"{parent_name}-{child_name}" if parent_name and child_name else ""
        
        # 构造请求体（字段映射：buildingId ← build_id, type ← type_id）
        body = {
            "phone": phone,
            "parkId": park_id,
            "buildingId": build_id,  # 注意：不是 buildId
            "floorId": floor_id,
            "roomId": room_id,
            "type": type_id,  # 注意：不是 typeId
            "typeText": type_text,
            "description": description,
            "picIds": pic_ids or "",
        }
        
        url = f"{self.BASE_URL}/repair/api/submit"
        response = self.client.request("POST", url, json=body, timeout=15)
        return response.json()

    def collect_recent_order_ids(self, page_size: int = 30) -> set[int]:
        """收集最近工单 ID（用于提交前后增量比对）"""
        baseline: set[int] = set()
        for order_type in (1, 2, 3):
            resp = self.query_orders(order_type=order_type, page_num=1, page_size=page_size)
            if resp.get("code") != 0:
                continue
            for order in resp.get("result", {}).get("list", []) or []:
                oid = order.get("id")
                if isinstance(oid, int):
                    baseline.add(oid)
        return baseline

    def find_new_order_after_submit(
        self,
        baseline_ids: set[int],
        description: str,
        type_id: int,
        page_size: int = 30,
    ) -> dict | None:
        """在提交后查找新增工单（优先按新增ID，再结合描述/类型匹配）"""
        _, child_name = self.get_type_names_by_id(type_id)
        child_name = (child_name or "").split("（", 1)[0].strip()
        desc = (description or "").strip()

        for order_type in (1, 2, 3):
            resp = self.query_orders(order_type=order_type, page_num=1, page_size=page_size)
            if resp.get("code") != 0:
                continue

            for order in resp.get("result", {}).get("list", []) or []:
                oid = order.get("id")
                if not isinstance(oid, int) or oid in baseline_ids:
                    continue

                order_desc = str(order.get("description", "")).strip()
                if desc and desc not in order_desc and order_desc not in desc:
                    continue

                if child_name:
                    order_type_text = str(order.get("type", ""))
                    if child_name not in order_type_text:
                        continue

                return order
        return None


# ============================================================
# CLI 入口
# ============================================================

def print_json(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="快手行政服务报修 API 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run scripts/repair-api.py --action query_orders --type 1
  uv run scripts/repair-api.py --action submit \\
    --phone 13800138000 --parkId 58 --buildId 76 --floorId 331 --typeId 101 \\
    --description "工位附近空调温度太低，请调节"
  uv run scripts/repair-api.py --action get_enums
        """
    )
    parser.add_argument(
        "--action", required=True,
        choices=["query_orders", "submit", "get_enums"],
        help="操作: query_orders=查询工单  submit=提交工单  get_enums=查枚举",
    )
    parser.add_argument("--type", type=int, default=1)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--size", type=int, default=10)
    parser.add_argument("--phone", type=str)
    parser.add_argument("--parkId", type=int)
    parser.add_argument("--buildId", type=int)
    parser.add_argument("--floorId", type=int)
    parser.add_argument("--roomId", type=int)
    parser.add_argument("--typeId", type=int)
    parser.add_argument("--description", type=str)
    parser.add_argument("--picIds", type=str, default="")
    args = parser.parse_args()
    
    # 初始化客户端
    client = RepairClient()
    
    if args.action == "get_enums":
        parks = client.get_parks()
        type_list = client.get_service_types()
        print("=== 园区 / 楼栋 / 楼层 ===")
        for park in parks.get("result", []):
            print(f"  园区 [{park['id']}] {park['name']}")
            for b in park.get("buildingList", []):
                print(f"    楼栋 [{b['id']}] {b['name']}")
                for f in b.get("floorList", []):
                    rooms = f.get("roomList") or []
                    suffix = ""
                    if rooms:
                        sample = "、".join(f"{r['id']}:{r['name']}" for r in rooms[:3])
                        suffix = f"  → {sample}" + (f"...（共{len(rooms)}间）" if len(rooms) > 3 else "")
                    print(f"      楼层 [{f['id']}] {f['name']}{suffix}")
        print("\n=== 服务类型（叶子节点，提交时使用 typeId）===")
        for t in type_list:
            if isinstance(t, dict) and t.get("parent"):
                print(f"  [{t['typeId']}] {t['parent']['typeName']} / {t['typeName']}")
    
    elif args.action == "query_orders":
        label = {1: "进行中", 2: "待评价", 3: "已完成"}.get(args.type, str(args.type))
        result = client.query_orders(args.type, args.page, args.size)
        if result.get("code") == 0:
            orders = result.get("result", {}).get("list", [])
            total = result.get("result", {}).get("total", 0)
            print(f"共 {total} 条")
            for i, o in enumerate(orders, 1):
                desc = o.get("description", "")
                print(f"[{i}] ID:{o['id']}  {o.get('type', '')}")
                print(f"     位置: {o.get('location', '')}")
                print(f"     描述: {desc[:60]}{'...' if len(desc) > 60 else ''}")
                print(f"     时间: {o.get('date', '')}")
                print(f"     状态: {label}")
                print()
        else:
            print_json(result)
    
    elif args.action == "submit":
        if not all([args.phone, args.parkId, args.buildId, args.floorId,
                    args.typeId, args.description]):
            print("❌ 缺少必填参数: --phone --parkId --buildId --floorId "
                  "--typeId --description", file=sys.stderr)
            sys.exit(1)
        if args.description and len(args.description) < 5:
            print("❌ 问题描述至少 5 个字", file=sys.stderr)
            sys.exit(1)

        if not client.is_leaf_type_id(args.typeId):
            print("❌ typeId 无效：必须是服务类型叶子节点", file=sys.stderr)
            sys.exit(1)

        phone = re.sub(r"\D", "", args.phone or "")
        if not re.fullmatch(r"1[3-9]\d{9}", phone):
            print("❌ 手机号格式错误，请输入 11 位大陆手机号", file=sys.stderr)
            sys.exit(1)

        baseline_ids = client.collect_recent_order_ids(page_size=30)

        result = client.submit_order(
            phone=phone,
            park_id=args.parkId,
            build_id=args.buildId,
            floor_id=args.floorId,
            type_id=args.typeId,
            description=args.description,
            room_id=args.roomId,
            pic_ids=args.picIds,
        )
        if result.get("code") == 0:
            print("ℹ️ 提交请求已受理，正在核验工单创建结果...")
            created_order = None
            max_attempts = 4
            for attempt in range(1, max_attempts + 1):
                created_order = client.find_new_order_after_submit(
                    baseline_ids=baseline_ids,
                    description=args.description,
                    type_id=args.typeId,
                    page_size=30,
                )
                if created_order:
                    result["verifyAttempts"] = attempt
                    break
                time.sleep(2)

            if created_order:
                result["verifiedCreated"] = True
                result["verifyStatus"] = "verified_success"
                result["orderId"] = created_order.get("id")
                print(f"✅ 工单提交成功（ID: {created_order.get('id')}）")
            else:
                result["verifiedCreated"] = False
                result["verifyStatus"] = "verify_failed"
                result["verifyAttempts"] = max_attempts
                result["verifyMessage"] = "提交已受理，但暂未核验到新工单，请核对手机号并稍后重试"
                print("⚠️ 提交请求已受理，但未核验到新工单，请核对手机号后重试")
        elif result.get("error"):
            print(f"❌ 提交失败: {result.get('message', '')}")
        else:
            print(f"❌ 业务失败: {result.get('message', '')}")
        print_json(result)


if __name__ == "__main__":
    main()
