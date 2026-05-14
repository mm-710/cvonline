# /// script
# requires-python = ">=3.10"
# dependencies = [
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
from __future__ import annotations

"""
公司食堂外卖订餐脚本

功能：
  1. list    - 查询可预订外卖菜品（输出结构化菜单，供 Agent 展示给用户）
  2. floors  - 查询指定菜品的可选取餐楼层（供 Agent 展示给用户选择）
  3. order   - 精确下单（通过 dishId + floorId，由 Agent 在用户确认后调用）
  4. query   - 查询我的订单
  5. cancel  - 取消订单

设计说明（Agent 对话式订餐流程）：
  本脚本专为 Agent 对话式引导设计，典型流程：
    Step 1: Agent 问用户「订哪天？哪个区域？」
    Step 2: Agent 调 list  → 展示菜品推荐给用户
    Step 3: 用户选菜品 → Agent 调 floors → 展示可选楼层给用户
    Step 4: 用户选楼层 → Agent 展示确认单，等用户确认
    Step 5: 用户确认 → Agent 调 order --dish_id xxx --floor_id xxx 精确下单

认证方式：
  使用 `ks_aimate` 提供的 `SmartSSOSession` 自动处理 SSO 认证，无需人工干预。

用法：
  uv run scripts/meal-order.py list   --garden_name "元中心" --area_name "T3" --date "2026-04-08"
  uv run scripts/meal-order.py floors --garden_name "元中心" --area_name "T3" --date "2026-04-08" --dish_id 719680 --meal_type 2
  uv run scripts/meal-order.py order  --garden_name "元中心" --area_name "T3" --date "2026-04-08" --dish_id 719680 --floor_id 442007 --meal_type 2
  uv run scripts/meal-order.py query
  uv run scripts/meal-order.py cancel --order_id 12345678
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://xz.corp.kuaishou.com"
CANTEEN_URL = "https://xz.corp.kuaishou.com/canteen/"

GARDEN_ALIASES: Dict[str, str] = {
    "元中心": "北京·元中心",
    "北京元中心": "北京·元中心",
    "万家灯火": "北京·万家灯火大厦",
    "万家灯火大厦": "北京·万家灯火大厦",
    "百度国际": "深圳·百度国际大厦",
    "欧美金融": "杭州·欧美金融中心",
    "星耀": "杭州·星耀中心",
    "星耀中心": "杭州·星耀中心",
}

MEAL_TYPE_MAP: Dict[int, str] = {1: "早餐", 2: "午餐", 3: "晚餐"}


# ─── SmartSSOSession 调用器 ──────────────────────────────────────────────────
class SSOCaller:
    """通过 SmartSSOSession 自动处理 SSO 认证。

    工作原理：
      - 使用 SmartSSOSession.request() 发起请求，认证由脚本内部自动处理。
    """

    def __init__(self) -> None:
        self._client = SmartSSOSession()

    def fetch_json(self, method: str, path: str,
                   params: Optional[Dict] = None,
                   json_body: Optional[Any] = None) -> Dict:
        url = BASE_URL + path
        response = self._client.request(
            method, url,
            params=params,
            json=json_body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if response.status_code == 401:
            raise RuntimeError(
                "SSO 认证失败（401）。请等待 KIM 扫码完成或重新触发认证。"
            )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"接口返回格式异常：{data}")
        if data.get("code", 0) not in (0, None):
            raise RuntimeError(
                f"接口错误（code={data.get('code')}）：{data.get('message', data.get('msg', '未知'))}"
            )
        return data


def make_caller() -> Any:
    return SSOCaller()


# ─── 园区/区域解析 ────────────────────────────────────────────────────────────
def normalize_garden(name: str) -> str:
    for k, v in GARDEN_ALIASES.items():
        if k in name:
            return v
    return name.strip()


def find_garden_area(caller: Any, garden_name: str, area_name: str):
    data = caller.fetch_json("GET", "/cafeteria/api/v2/areaName/mealReservation/gardens")
    gardens = data.get("result") or []
    g_norm = normalize_garden(garden_name).lower().replace(" ", "").replace("·", "")

    best = None
    for g in gardens:
        gnorm = str(g.get("name") or "").lower().replace(" ", "").replace("·", "")
        if g_norm and (g_norm in gnorm or gnorm in g_norm):
            best = g
            break
    if not best and gardens:
        best = next((g for g in gardens if g.get("selected")), gardens[0])
    if not best:
        raise RuntimeError(f"未找到园区：{garden_name}")

    garden_id = str(best.get("id") or "")
    garden_full = str(best.get("name") or "")
    area_list_raw = best.get("areaNameList") or []
    area_list = [
        a if isinstance(a, str) else a.get("areaName", "")
        for a in area_list_raw
        if (a if isinstance(a, str) else a.get("areaName", ""))
    ]

    if area_name:
        area_q = area_name.strip().upper()
        # 优先精确匹配（大小写不敏感）
        matched = next((a for a in area_list if a.upper() == area_q), None)
        # 精确不到，尝试「输入是区域名的完整前缀且无歧义」
        if not matched:
            prefix_matches = [a for a in area_list if a.upper().startswith(area_q)]
            if len(prefix_matches) == 1:
                matched = prefix_matches[0]
            elif len(prefix_matches) > 1:
                # 有歧义，告诉 Agent 需要用户澄清
                raise RuntimeError(
                    f"区域「{area_name}」存在歧义，{garden_full} 下有多个匹配：{prefix_matches}。\n"
                    f"💡 Agent 处理：告知用户「{area_name}」对应多个区域，请用户明确选择其中一个。"
                )
        if not matched:
            raise RuntimeError(
                f"未找到区域「{area_name}」。{garden_full} 下可用区域：{area_list}。\n"
                f"💡 Agent 处理：告知用户该区域不存在，让用户从以上列表中重新选择。"
            )
    else:
        matched = None
        for a in area_list_raw:
            if isinstance(a, dict) and a.get("selected"):
                matched = a.get("areaName")
                break
        if not matched and area_list:
            matched = area_list[0]

    if not matched:
        raise RuntimeError(f"未找到区域：{area_name}（{garden_full} 下可用区域：{area_list}）")
    return garden_id, garden_full, matched


# ─── CMD: default-location ────────────────────────────────────────────────────
def cmd_default_location(args, caller) -> None:
    """查询用户上次使用的默认园区和区域。

    页面通过 gardens 接口的 selected 字段自动带出上次用户的位置：
      - 哪个园区 selected=true → 用户上次用的园区
      - 该园区下哪个 areaName selected=true → 用户上次用的区域

    Agent 应在对话开始时先调此命令（前提是用户未明确给出可直接使用的园区/区域）：
      - 有默认位置 → 先向用户确认默认位置，不要直接追问园区
      - 无默认位置（从未用过） → 再询问用户所在的园区和区域
    """
    data = caller.fetch_json("GET", "/cafeteria/api/v2/areaName/mealReservation/gardens")
    gardens = data.get("result") or []

    if not gardens:
        print("❌ 获取园区列表失败，请检查登录状态。")
        return

    # 找到 selected=true 的园区
    default_garden = next((g for g in gardens if g.get("selected")), None)
    all_garden_names = [g.get("name") for g in gardens]

    if not default_garden:
        print("📍 用户尚无默认位置（从未使用过外卖订餐）。")
        print(f"\n可用园区（共 {len(gardens)} 个）：")
        for g in gardens:
            area_list_raw = g.get("areaNameList") or []
            areas = [
                a if isinstance(a, str) else a.get("areaName", "")
                for a in area_list_raw
                if (a if isinstance(a, str) else a.get("areaName", ""))
            ]
            print(f"  • {g.get('name')}（区域：{', '.join(areas)}）")
        print(f"\n💡 Agent 处理：询问用户在哪个园区工作，以及在哪个楼/区域取餐。")
        return

    # 找到默认园区下 selected=true 的区域
    garden_name = default_garden.get("name", "")
    garden_id = str(default_garden.get("id", ""))
    area_list_raw = default_garden.get("areaNameList") or []

    default_area = None
    all_areas = []
    for a in area_list_raw:
        if isinstance(a, str):
            all_areas.append(a)
        elif isinstance(a, dict):
            aname = a.get("areaName", "")
            if aname:
                all_areas.append(aname)
            if a.get("selected"):
                default_area = aname

    if default_area:
        print(f"📍 用户上次取餐位置：{garden_name} · {default_area}")
        print(f"   gardenId: {garden_id}  |  areaName: {default_area}")
        print(f"\n💡 Agent 处理：向用户确认「检测到你上次在 {garden_name} · {default_area} 取餐，这次还是这里吗？」")
        print(f"   要求：本轮地点确认应一次确认到园区和区域两个层级，不要只确认区域。")
        print(f"   用户确认后即可直接用 list/order 等命令，无需再次询问园区和区域。")
    else:
        # 有默认园区但没有 selected 区域（第一次用该园区，未选过区域）
        print(f"📍 用户上次使用园区：{garden_name}（尚未选过具体区域）")
        print(f"   gardenId: {garden_id}")
        print(f"   该园区下可选区域：{', '.join(all_areas)}")
        print(f"\n💡 Agent 处理：告知用户园区为 {garden_name}，并在同一轮直接让用户从这些区域中选择：{', '.join(all_areas)}。")
        print(f"   要求：一次确认到完整地点，不要下一轮再补问区域。")


# ─── CMD: list ────────────────────────────────────────────────────────────────
def cmd_list(args, caller) -> None:
    """查询可预订外卖菜品。输出包含 dishId、价格、商家、楼层余量，供 Agent 展示给用户选择。"""
    garden_id, garden_full, area = find_garden_area(caller, args.garden_name, args.area_name)
    target_date = args.date or datetime.now().date().isoformat()
    meal_type_filter = args.meal_type  # None 表示不过滤

    data = caller.fetch_json("GET", "/cafeteria/api/v2/mealReservation/meals",
                             params={"gardenId": garden_id, "areaName": area, "date": target_date})
    meals = data.get("result") or []
    if not meals:
        print(f"📭 【{target_date}】{garden_full}·{area} 暂无可预订外卖。")
        print("💡 Agent 提示：先结合当前时间、用户查询日期和餐型判断原因。")
        print("   - 如果已到下周菜单发布时间，且用户查的是某个具体餐型（尤其早餐），优先提示该餐型暂无可订外卖。")
        print("   - 如果查询日期明显超出已发布范围，再提示菜单可能尚未发布。")
        print("   - 如果是当天或近期餐段，则提示该时段可能已售罄、已截止，或该餐段本身不提供外卖。")
        return

    displayed_any = False
    print(f"📋 【{target_date}】{garden_full}·{area} 可预订外卖菜品：\n")
    for meal in meals:
        meal_type_id = meal.get("mealType")  # 有些接口在 category 级别返回 mealType
        meal_name = meal.get("name", "")
        dish_list = meal.get("dishList") or []

        available    = [d for d in dish_list if str(d.get("state", "")) not in ("1", "3")]
        not_open_yet = [d for d in dish_list if str(d.get("state", "")) == "3"]
        ended        = [d for d in dish_list if str(d.get("state", "")) == "1"]

        # 按 meal_type 过滤
        if meal_type_filter is not None:
            available    = [d for d in available    if d.get("mealType") == meal_type_filter]
            not_open_yet = [d for d in not_open_yet if d.get("mealType") == meal_type_filter]
            ended        = [d for d in ended        if d.get("mealType") == meal_type_filter]

        if not available and not not_open_yet and not ended:
            continue

        displayed_any = True
        print(f"━━━ {meal_name}（可预订 {len(available)} / 共 {len(dish_list)}）")
        for d in available:
            floors_with_stock = [
                f for f in (d.get("list") or []) if f.get("remainAmount", 0) > 0
            ]
            floor_desc = "、".join(
                f"{f['floor']}（余{f['remainAmount']}）" for f in floors_with_stock
            ) if floors_with_stock else "无余量"
            meal_type_name = MEAL_TYPE_MAP.get(d.get("mealType"), "")
            print(f"  ✅ [{d.get('dishId')}] {d.get('name')}  ¥{d.get('price')}  "
                  f"{meal_type_name}  剩余:{d.get('remainAmount')}/{d.get('totalAmount')}")
            print(f"     取餐点：{floor_desc}")
        for d in not_open_yet:
            open_time = d.get("description") or "稍后"
            meal_type_name = MEAL_TYPE_MAP.get(d.get("mealType"), "")
            print(f"  ⏳ [{d.get('dishId')}] {d.get('name')}  ¥{d.get('price')}  "
                  f"{meal_type_name}  [尚未开放：{open_time}]")
        for d in ended:
            print(f"  ❌ [{d.get('dishId')}] {d.get('name')}  ¥{d.get('price')}  [已截止]")
        print()

    if not displayed_any:
        meal_type_name = MEAL_TYPE_MAP.get(meal_type_filter, "") if meal_type_filter else "该餐段"
        print(f"📭 【{target_date}】{garden_full}·{area} 暂无{meal_type_name}可展示菜品。")
        print("💡 Agent 提示：这不一定代表菜单未发布。")
        print("   - 如果已到下周菜单发布时间，优先提示该餐型暂无可订外卖。")
        print("   - 如果是早餐场景，尤其是周五 18:00 后查询下周早餐，优先提示早餐通常没有外卖菜品。")
        print("   - 如果查询日期明显超出当前已发布范围，再提示菜单可能尚未发布。")
        return

    meal_type_name = MEAL_TYPE_MAP.get(meal_type_filter, "") if meal_type_filter else ""
    print(f"💡 Agent 提示：请将以上菜品推荐给用户，询问用户想要哪道菜"
          f"{'（' + meal_type_name + '）' if meal_type_name else ''}，"
          f"再用 floors 命令查询该菜品的可选取餐楼层。")
    print(f"   注意：取餐点名称由系统决定，可能在其他楼栋（属正常情况）。"
          f"直接展示给用户，不要解释或猜测原因。")


# ─── CMD: floors ──────────────────────────────────────────────────────────────
def cmd_floors(args, caller) -> None:
    """查询指定菜品的可选取餐楼层。供 Agent 展示给用户，让用户选择送到哪层。"""
    garden_id, garden_full, area = find_garden_area(caller, args.garden_name, args.area_name)
    target_date = args.date or datetime.now().date().isoformat()
    dish_id = args.dish_id
    meal_type = args.meal_type

    data = caller.fetch_json("GET", "/cafeteria/api/v2/mealReservation/meals",
                             params={"gardenId": garden_id, "areaName": area, "date": target_date})
    meals = data.get("result") or []
    all_dishes = [d for m in meals for d in (m.get("dishList") or [])]

    dish = next((d for d in all_dishes if d.get("dishId") == dish_id), None)
    if not dish:
        print(f"❌ 未找到 dishId={dish_id} 的菜品。请先用 list 命令查看可用菜品。")
        return

    floor_list = dish.get("list") or []
    available_floors = [f for f in floor_list if f.get("remainAmount", 0) > 0]
    full_floors = [f for f in floor_list if f.get("remainAmount", 0) == 0]

    meal_type_name = MEAL_TYPE_MAP.get(dish.get("mealType"), "")
    print(f"🏢 【{dish.get('name')}】¥{dish.get('price')}  {meal_type_name}")
    print(f"   dishId: {dish_id}  |  {target_date}  |  {garden_full}·{area}\n")

    if not available_floors:
        print("❌ 该菜品所有取餐点均已无余量，无法下单。")
        return

    print(f"可选取餐楼层（有余量，共 {len(available_floors)} 个）：\n")
    for f in available_floors:
        print(f"  ✅ [{f['floorId']}] {f['floor']}  余量：{f['remainAmount']}")
    if full_floors:
        print(f"\n已满楼层（{len(full_floors)} 个）：")
        for f in full_floors:
            print(f"  ❌ [{f['floorId']}] {f['floor']}  已满")

    print(f"\n💡 Agent 提示：请将以上楼层选项展示给用户，询问「送到哪层？」，")
    print(f"   用户选择后，展示确认单并等用户确认，再调用 order 命令正式下单：")
    first_floor = available_floors[0]
    print(f"   uv run scripts/meal-order.py order "
          f"--garden_name \"{args.garden_name}\" --area_name \"{args.area_name}\" "
          f"--date \"{target_date}\" --dish_id {dish_id} "
          f"--floor_id {first_floor['floorId']} --meal_type {meal_type}")


# ─── 失败原因枚举 ──────────────────────────────────────────────────────────────
FAIL_REASON_FLOOR_SOLDOUT   = "floor_soldout"    # 指定楼层余量为 0
FAIL_REASON_DISH_SOLDOUT    = "dish_soldout"     # 菜品整体售罄（所有楼层均无余量）
FAIL_REASON_DISH_ENDED      = "dish_ended"       # 菜品已截止（state=1，过了订餐时间）
FAIL_REASON_REORDER         = "reorder"          # 当天该餐型已有订单
FAIL_REASON_DEADLINE_PASSED = "deadline_passed"  # 整体订餐截止（服务端返回 5078）
FAIL_REASON_NO_PERMISSION   = "no_permission"    # 无订餐权限（外包等）
FAIL_REASON_UNKNOWN         = "unknown"          # 其他未知错误


def _print_fallback(reason: str, dish_name: str, dish_id: int, floor_name: str,
                    floor_id: int, garden_name: str, area_name: str,
                    target_date: str, meal_type: int,
                    all_dishes: List[Dict], dish: Optional[Dict]) -> None:
    """根据失败原因打印降级建议，供 Agent 引导用户重新选择。"""
    meal_type_name = MEAL_TYPE_MAP.get(meal_type, str(meal_type))

    if reason == FAIL_REASON_REORDER:
        print(f"⚠️  下单失败：{target_date} 已有{meal_type_name}外卖订单，不能重复下单。")
        print(f"   【Agent 处理】用 query 命令查询已有订单展示给用户，询问是否需要取消后重订。")
        return

    if reason == FAIL_REASON_DEADLINE_PASSED:
        print(f"⚠️  下单失败：{target_date} {meal_type_name}外卖已截止（服务端拒绝）。")
        print(f"   【Agent 处理】告知用户订餐截止，询问是否要订其他日期。")
        return

    if reason == FAIL_REASON_NO_PERMISSION:
        print(f"⚠️  下单失败：账号无外卖订餐权限。")
        print(f"   【Agent 处理】告知用户该账号暂无订餐权限，可联系行政申请开通。")
        return

    # 余量相关失败：尝试推荐替代楼层或替代菜品
    if reason in (FAIL_REASON_FLOOR_SOLDOUT, FAIL_REASON_DISH_SOLDOUT):
        if reason == FAIL_REASON_FLOOR_SOLDOUT:
            print(f"⚠️  下单失败：取餐点「{floor_name}」余量已不足（刚刚被抢完）。")
        else:
            print(f"⚠️  下单失败：菜品「{dish_name}」已全部售罄。")

        # 先尝试推荐同一菜品的其他楼层
        if dish:
            alt_floors = [f for f in (dish.get("list") or [])
                          if f.get("remainAmount", 0) > 0 and f.get("floorId") != floor_id]
            if alt_floors:
                print(f"\n   同一菜品仍有余量的其他取餐点：")
                for f in alt_floors:
                    print(f"   ✅ [{f['floorId']}] {f['floor']}  余量：{f['remainAmount']}")
                print(f"\n   【Agent 处理】询问用户是否改到以上楼层取餐，确认后重新调用 order：")
                f0 = alt_floors[0]
                print(f"   uv run scripts/meal-order.py order "
                      f"--garden_name \"{garden_name}\" --area_name \"{area_name}\" "
                      f"--date \"{target_date}\" --dish_id {dish_id} "
                      f"--floor_id {f0['floorId']} --meal_type {meal_type}")
                return

        # 菜品整体售罄，推荐其他可订菜品
        alt_dishes = [d for d in all_dishes
                      if d.get("dishId") != dish_id
                      and str(d.get("state", "")) != "1"
                      and d.get("mealType") == meal_type
                      and d.get("remainAmount", 0) > 0]
        if alt_dishes:
            print(f"\n   其他仍可预订的{meal_type_name}菜品：")
            for d in alt_dishes[:5]:
                floors_ok = [f for f in (d.get("list") or []) if f.get("remainAmount", 0) > 0]
                floor_hint = f"取餐点：{'、'.join(f['floor'] for f in floors_ok[:2])}" if floors_ok else "取餐点余量待确认"
                print(f"   ✅ [{d.get('dishId')}] {d.get('name')}  ¥{d.get('price')}  剩余:{d.get('remainAmount')}  {floor_hint}")
            print(f"\n   【Agent 处理】展示以上菜品给用户，让用户重新选择，")
            print(f"   再用 floors 命令确认楼层余量，用户确认后重新调用 order。")
        else:
            print(f"\n   ❌ 该日期区域已无其他可预订的{meal_type_name}外卖。")
            print(f"   【Agent 处理】告知用户今日外卖已全部售罄，建议去食堂堂食。")
        return

    if reason == FAIL_REASON_DISH_ENDED:
        print(f"⚠️  下单失败：菜品「{dish_name}」的订餐已截止（state=1）。")
        alt_dishes = [d for d in all_dishes
                      if d.get("dishId") != dish_id
                      and str(d.get("state", "")) != "1"
                      and d.get("mealType") == meal_type
                      and d.get("remainAmount", 0) > 0]
        if alt_dishes:
            print(f"\n   仍可预订的其他菜品：")
            for d in alt_dishes[:5]:
                print(f"   ✅ [{d.get('dishId')}] {d.get('name')}  ¥{d.get('price')}")
            print(f"   【Agent 处理】展示以上菜品给用户重新选择。")
        else:
            print(f"   【Agent 处理】告知用户今日外卖已全部截止。")
        return

    # 未知错误
    print(f"⚠️  下单失败（原因未知）。")
    print(f"   【Agent 处理】告知用户下单遇到问题，建议稍后重试或直接前往食堂。")


# ─── CMD: order ───────────────────────────────────────────────────────────────
def cmd_order(args, caller) -> None:
    """精确下单。使用 dishId + floorId，由 Agent 在用户确认后调用。
    
    下单失败时会输出结构化的失败原因和降级建议，供 Agent 引导用户重新选择。
    失败场景及降级策略：
      - 楼层刚被抢完  → 自动推荐同菜品其他有余量楼层
      - 菜品整体售罄  → 推荐同区域其他可订菜品（从最新菜单实时获取）
      - 菜品已截止    → 推荐其他未截止菜品
      - 已有重复订单  → 提示查询/取消已有订单
      - 服务端截止    → 提示订餐已截止
      - 无权限        → 提示联系行政开通
    """
    garden_id, garden_full, area = find_garden_area(caller, args.garden_name, args.area_name)
    target_date = args.date or datetime.now().date().isoformat()
    meal_type = args.meal_type
    dish_id = args.dish_id
    floor_id = args.floor_id

    # 1. 重单检测
    try:
        reorder_check = caller.fetch_json(
            "POST", "/cafeteria/api/v2/mealReservation/isReOrder",
            json_body=[{"orderMealDate": target_date, "dishId": dish_id,
                        "mealType": meal_type, "amount": 1, "floorId": floor_id}]
        )
        if reorder_check.get("result") is True:
            _print_fallback(FAIL_REASON_REORDER, "", dish_id, "", floor_id,
                            args.garden_name, args.area_name, target_date, meal_type, [], None)
            sys.exit(2)
    except RuntimeError as e:
        print(f"⚠️  重单检测异常（{e}），继续尝试下单...")

    # 2. 实时获取最新菜品状态（下单前再确认一次余量，距展示菜单可能已过一段时间）
    dish_name = f"dishId:{dish_id}"
    floor_name = f"floorId:{floor_id}"
    price = None
    all_dishes: List[Dict] = []
    dish: Optional[Dict] = None

    try:
        data = caller.fetch_json("GET", "/cafeteria/api/v2/mealReservation/meals",
                                 params={"gardenId": garden_id, "areaName": area,
                                         "date": target_date})
        all_dishes = [d for m in (data.get("result") or [])
                      for d in (m.get("dishList") or [])]
        dish = next((d for d in all_dishes if d.get("dishId") == dish_id), None)

        if dish:
            dish_name = dish.get("name", dish_name)
            price = dish.get("price")

            # 检查菜品是否尚未开放（state=3）
            if str(dish.get("state", "")) == "3":
                open_time = dish.get("description") or "稍后"
                print(f"⏳ 下单失败：菜品「{dish_name}」尚未开放预订（{open_time}开始）。")
                print(f"   【Agent 处理】告知用户该菜品 {open_time} 开始可以预订，询问是否等待或换其他菜品。")
                sys.exit(2)

            # 检查菜品是否已截止
            if str(dish.get("state", "")) == "1":
                _print_fallback(FAIL_REASON_DISH_ENDED, dish_name, dish_id, floor_name, floor_id,
                                args.garden_name, args.area_name, target_date, meal_type,
                                all_dishes, dish)
                sys.exit(2)

            # 检查菜品整体余量
            if dish.get("remainAmount", 0) == 0:
                _print_fallback(FAIL_REASON_DISH_SOLDOUT, dish_name, dish_id, floor_name, floor_id,
                                args.garden_name, args.area_name, target_date, meal_type,
                                all_dishes, dish)
                sys.exit(2)

            # 检查指定楼层余量
            floor_obj = next((f for f in (dish.get("list") or [])
                              if f.get("floorId") == floor_id), None)
            if floor_obj:
                floor_name = floor_obj.get("floor", floor_name)
                if floor_obj.get("remainAmount", 0) == 0:
                    _print_fallback(FAIL_REASON_FLOOR_SOLDOUT, dish_name, dish_id,
                                    floor_name, floor_id,
                                    args.garden_name, args.area_name, target_date, meal_type,
                                    all_dishes, dish)
                    sys.exit(2)
    except RuntimeError as e:
        print(f"⚠️  下单前菜品状态确认失败（{e}），直接尝试下单...")

    # 3. 调用下单接口
    body = [{
        "orderMealDate": target_date,
        "dishId": dish_id,
        "mealType": meal_type,
        "amount": 1,
        "floorId": floor_id,
        "floor": floor_name,
    }]

    # 捕获接口层面的业务错误，细化为具体失败原因
    try:
        caller.fetch_json("POST", "/cafeteria/api/v2/areaName/mealReservation/order",
                          params={"garden": garden_full, "areaName": area},
                          json_body=body)
    except RuntimeError as e:
        err_msg = str(e)
        # 根据服务端返回的错误信息判断失败原因
        if "5078" in err_msg or "订餐时间" in err_msg or "截止" in err_msg:
            reason = FAIL_REASON_DEADLINE_PASSED
        elif "重复" in err_msg or ("已经" in err_msg and "订" in err_msg):
            reason = FAIL_REASON_REORDER
        elif "权限" in err_msg or "外包" in err_msg or "无权" in err_msg:
            reason = FAIL_REASON_NO_PERMISSION
        elif "余量" in err_msg or "sold" in err_msg.lower() or "库存" in err_msg:
            reason = FAIL_REASON_DISH_SOLDOUT
        else:
            reason = FAIL_REASON_UNKNOWN
            print(f"   服务端返回：{err_msg}")

        _print_fallback(reason, dish_name, dish_id, floor_name, floor_id,
                        args.garden_name, args.area_name, target_date, meal_type,
                        all_dishes, dish)
        sys.exit(2)

    # 4. 下单成功
    meal_type_name = MEAL_TYPE_MAP.get(meal_type, str(meal_type))
    price_str = f"  ¥{price}" if price is not None else ""
    print(f"✅ {meal_type_name}外卖下单成功！")
    print(f"   菜品：{dish_name}{price_str}")
    print(f"   取餐点：{floor_name}")
    print(f"   日期：{target_date}  园区：{garden_full}·{area}")
    print(f"   取餐当天凭餐柜通知自取，请留意消息提醒。")




# ─── CMD: query ───────────────────────────────────────────────────────────────
def cmd_query(args, caller) -> None:
    """查询我的外卖订单。

    策略：
    1. /order/query/undone 查询所有「预定中」的未来订单（含明天及以后）
    2. /order/query/today  查询今日订单（含已完成/已取消等历史状态）
    3. 合并去重后展示，若指定 --date 则客户端按日期过滤
    
    安全说明：
    - 两个接口均由服务端按当前用户过滤，不会返回其他用户数据
    """
    target_date = args.date  # 可能为 None

    try:
        # 接口1：预定中的未来订单（包含明天及以后）
        data_undone = caller.fetch_json("GET", "/cafeteria/api/v2/order/query/undone",
                                        params={"pageNum": 1, "pageSize": 100})
        undone_orders = (data_undone.get("result") or {}).get("list") or []

        # 接口2：今日订单（含各种状态）
        data_today = caller.fetch_json("GET", "/cafeteria/api/v2/order/query/today",
                                       params={"pageNum": 1, "pageSize": 100})
        today_orders = (data_today.get("result") or {}).get("list") or []

        # 合并去重（以 orderId 为 key，undone 优先，因为状态更准确）
        seen = set()
        all_orders = []
        for o in undone_orders + today_orders:
            oid = o.get("orderId") or o.get("id")
            if oid not in seen:
                seen.add(oid)
                all_orders.append(o)

        # 如果指定了日期，在客户端按日期过滤
        if target_date:
            all_orders = [
                o for o in all_orders
                if (o.get("date") or o.get("edibleTime") or "")[:10] == target_date
            ]
    except RuntimeError as e:
        print(f"❌ 查询订单失败：{e}")
        return

    if not all_orders:
        msg = "📭 暂无外卖订单"
        if target_date:
            msg += f"（就餐日期：{target_date}）"
        else:
            msg += "（当前有效订单）"
        print(msg)
        return

    print(f"📦 外卖订单（共 {len(all_orders)} 条）：\n")
    for o in all_orders:
        order_id  = o.get("orderId") or o.get("id")
        order_no  = o.get("orderNo") or ""
        name      = o.get("name") or o.get("dishName") or ""
        location  = o.get("location") or o.get("floor") or ""
        date_str  = (o.get("date") or o.get("edibleTime") or "")[:10]
        mt        = o.get("mealType")
        meal_desc = mt.get("desc") if isinstance(mt, dict) else MEAL_TYPE_MAP.get(mt, str(mt or ""))
        st        = o.get("orderStatus")
        status    = st.get("desc") if isinstance(st, dict) else str(o.get("status") or st or "")
        
        print(f"  [orderId:{order_id}]  订单号:{order_no}")
        print(f"  菜品:{name}  餐型:{meal_desc}  状态:{status}")
        print(f"  取餐点:{location}  就餐日期:{date_str}\n")
    
    print("💡 Agent 提示：若用户要取消某条订单，从上方结果中取 orderId 调用 cancel 命令，")
    print("   不要要求用户自己提供订单号。")


# ─── CMD: cancel ──────────────────────────────────────────────────────────────
def cmd_cancel(args, caller) -> None:
    """取消外卖订单。
    
    安全策略：
    - 直接调用取消接口，由服务端校验订单归属
    - 服务端会验证订单是否属于当前用户
    - 如果不属于会返回权限错误
    
    注意：
    - 只能取消自己预订的订单
    - 就餐当天 10:00 前均可取消
    """
    try:
        order_id = int(args.order_id)
    except (TypeError, ValueError):
        print(f"❌ order_id 必须是整数，收到：{args.order_id}")
        sys.exit(1)
    
    # 直接调用取消接口，由服务端校验权限
    try:
        caller.fetch_json("POST", "/cafeteria/api/v2/order/cancel",
                          params={"orderId": order_id})
        print(f"✅ 订单 {order_id} 已取消。")
    except RuntimeError as e:
        err_msg = str(e)
        # 根据错误信息判断具体原因
        if "权限" in err_msg or "无权" in err_msg or "不属于" in err_msg:
            print(f"❌ 无权操作：订单 {order_id} 不属于当前用户。")
            print("   只能取消自己预订的订单。")
            sys.exit(1)
        elif "5078" in err_msg or "截止" in err_msg or "已过" in err_msg or "不能取消" in err_msg:
            print(f"❌ 取消失败：订单 {order_id} 已过取消截止时间。")
            print("   就餐当天 10:00 前可取消，请检查时间。")
            sys.exit(1)
        elif "不存在" in err_msg or "已取消" in err_msg:
            print(f"❌ 订单 {order_id} 不存在或已取消。")
            sys.exit(1)
        else:
            print(f"❌ 取消失败：{err_msg}")
            sys.exit(1)


# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="快手食堂外卖订餐脚本（对话式 Agent 调用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
前置条件：脚本会通过 `SmartSSOSession` 自动处理 SSO 认证

Agent 对话式订餐流程：
  Step 0  检查时间窗口      → 不在窗口期时直接结束，不先收集其他信息
  Step 1  default-location → 用户未明确提供地址时，先查默认园区/区域
  Step 2  list             → 获取菜单，Agent 展示给用户选菜
  Step 3  floors           → 获取楼层，Agent 展示给用户选取餐点
  Step 4  order            → 用户确认后精确下单（用 dishId + floorId）

示例：
  uv run scripts/meal-order.py default-location
  uv run scripts/meal-order.py list   --garden_name "元中心" --area_name "T3" --date "2026-04-08" --meal_type 2
  uv run scripts/meal-order.py floors --garden_name "元中心" --area_name "T3" --date "2026-04-08" --dish_id 719680 --meal_type 2
  uv run scripts/meal-order.py order  --garden_name "元中心" --area_name "T3" --date "2026-04-08" --dish_id 719680 --floor_id 442007 --meal_type 2
  uv run scripts/meal-order.py query
  uv run scripts/meal-order.py cancel --order_id 12345678
""")

    sub = parser.add_subparsers(dest="cmd")

    # default-location
    sub.add_parser("default-location", help="查询用户默认园区/区域（订餐前优先确认历史取餐位置）")

    # list
    p = sub.add_parser("list", help="查询可预订菜品（展示给用户选择）")
    p.add_argument("--garden_name", required=True, help="园区，如：元中心")
    p.add_argument("--area_name", default="", help="区域，如：T3；不填取默认")
    p.add_argument("--date", default=None, help="日期 YYYY-MM-DD，默认今天")
    p.add_argument("--meal_type", type=int, default=None,
                   help="餐型筛选：1=早餐, 2=午餐, 3=晚餐；不填显示全部")

    # floors
    p = sub.add_parser("floors", help="查询指定菜品的可选取餐楼层（展示给用户选择）")
    p.add_argument("--garden_name", required=True)
    p.add_argument("--area_name", default="")
    p.add_argument("--date", default=None)
    p.add_argument("--dish_id", required=True, type=int, help="菜品ID（来自 list 命令）")
    p.add_argument("--meal_type", type=int, default=2, help="餐型：1=早餐, 2=午餐, 3=晚餐")

    # order
    p = sub.add_parser("order", help="精确下单（用户确认后调用）")
    p.add_argument("--garden_name", required=True)
    p.add_argument("--area_name", default="")
    p.add_argument("--date", default=None)
    p.add_argument("--dish_id", required=True, type=int, help="菜品ID（来自 list 命令）")
    p.add_argument("--floor_id", required=True, type=int, help="楼层ID（来自 floors 命令）")
    p.add_argument("--meal_type", type=int, default=2, help="餐型：1=早餐, 2=午餐, 3=晚餐")

    # query
    p = sub.add_parser("query", help="查询我的外卖订单")
    p.add_argument("--date", default=None)

    # cancel
    p = sub.add_parser("cancel", help="取消外卖订单")
    p.add_argument("--order_id", required=True, help="订单ID（整数）")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    caller = make_caller()

    try:
        if args.cmd == "list":
            cmd_list(args, caller)
        elif args.cmd == "floors":
            cmd_floors(args, caller)
        elif args.cmd == "order":
            cmd_order(args, caller)
        elif args.cmd == "default-location":
            cmd_default_location(args, caller)
        elif args.cmd == "query":
            cmd_query(args, caller)
        elif args.cmd == "cancel":
            cmd_cancel(args, caller)
    except RuntimeError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
