#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.28",
#   "pydantic>=2.0",
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
公司食堂菜单查询脚本

Cookie 管理：使用 SmartSSOSession 自动处理 SSO 认证，无需人工干预
- 认证成功后，自动保存会话状态供后续使用

用法：
  uv run scripts/cafeteria-recommendation.py --garden_name "元中心" --taste_preference "辣"
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field
from ks_aimate.sso_login_client import SmartSSOSession


class CafeteriaRecommendationParams(BaseModel):
    """
    Skill 标准入参（大模型只允许传这些）。

    - garden_name 为必填：缺失时不要调用本技能，应先追问用户园区。
    - taste_preference / custom_date / area_name / meal_type 为可选。
    """

    garden_name: str = Field(
        ...,
        description="用户所在园区（必填）。若不知道园区，请先询问用户在哪个园区，不要调用本技能。",
        min_length=1,
    )
    taste_preference: Optional[str] = Field(
        default="",
        description="用户喜好关键词（可选）。例如：辣、低热量、面条、牛肉、素食、不要葱等。若留空则直接返回园区菜品列表。",
    )
    custom_date: Optional[str] = Field(
        default=None,
        description="可选：YYYY-MM-DD。若传入则覆盖自动推断日期。",
    )
    area_name: Optional[str] = Field(
        default="",
        description="可选：指定档口/区域名称，如西部马华。不填则查询园区全部档口。",
    )
    meal_type: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="可选：餐型，1=早餐,2=午餐,3=晚餐,4=夜宵。不传则按文案/时间自动推断。",
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=200,
        description="最多返回多少条菜品（去重后）。",
    )

    per_store_max_dishes: int = Field(
        default=50,
        ge=1,
        le=200,
        description="每个档口在文本输出中最多展示多少道菜（不会改变真实抓取/去重结果，只影响展示截断）。",
    )


@dataclass(frozen=True)
class Dish:
    garden_name: str
    area_name: str
    store_id: int
    store_name: str
    meal_time: str
    dish_name: str
    cate_name: str
    description: str


class CafeteriaRecommendationSkill:
    """
    基于公司食堂 API 的"按喜好查菜品" Skill（OpenClaw 使用）。

    - 使用 SmartSSOSession 自动处理 SSO 认证
    - 自动推断日期与餐次（早餐/午餐/晚餐）
    - 走链路：园区/区域 -> 档口 -> 餐次 -> 菜单
    - 在本地做偏好匹配过滤，返回人类可读结果
    """

    # OpenClaw 元信息
    name: str = "cafeteria_recommendation"
    description: str = (
        "当员工询问食堂/菜谱/有什么好吃的/某园区中午吃什么/想吃辣的或低热量时调用。"
        "工具会按日期、园区、餐次拉取档口与今日菜单，并按用户偏好在本地过滤后返回推荐清单。"
    )
    parameters = CafeteriaRecommendationParams

    BASE_URL = "https://xz.corp.kuaishou.com"

    _MEAL_TYPE_ID_TO_NAME: Dict[int, str] = {
        1: "早餐",
        2: "午餐",
        3: "晚餐",
        4: "夜宵",
    }

    _TAKEOUT_INTENT_PATTERN = re.compile(
        r"(外卖|订餐|下单|预约外卖|送餐|配送|取消订单|取消外卖|查订单|订单状态|外送)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        timeout_s: int = 20,
    ) -> None:
        self.timeout_s = timeout_s
        # 初始化 SSO 会话客户端
        self.client = SmartSSOSession()
        
        # 园区别名（可按团队使用习惯扩展）
        self._garden_aliases: Dict[str, str] = {
            "元中心": "北京·元中心",
            "北京元中心": "北京·元中心",
            "万家灯火": "北京·万家灯火大厦",
            "万家灯火大厦": "北京·万家灯火大厦",
            "百度国际": "深圳·百度国际大厦",
            "百度国际大厦": "深圳·百度国际大厦",
            "欧美金融": "杭州·欧美金融中心",
            "欧美金融中心": "杭州·欧美金融中心",
            "星耀": "杭州·星耀中心",
            "星耀中心": "杭州·星耀中心",
        }

    # -----------------------------
    # OpenClaw entrypoint
    # -----------------------------
    def execute(self, **kwargs: Any) -> str:
        """
        OpenClaw 主执行函数：kwargs 由大模型解析后传入。
        返回人类可读的推荐字符串。
        """
        # 必填参数缺失时，优先返回"反问用户"的文案，而非技术性报错
        garden_name = str(kwargs.get("garden_name") or "").strip()
        if not garden_name:
            return (
                "为了帮你查到准确菜单，我需要先确认你在哪个园区。\n"
                "请告诉我园区名称（例如：元中心 / 万家灯火 / 欧美金融中心）。"
            )

        max_results_was_set = "max_results" in kwargs
        per_store_max_was_set = "per_store_max_dishes" in kwargs

        try:
            params = CafeteriaRecommendationParams(**kwargs)
        except Exception as e:
            return (
                f"参数格式有点问题：{e}\n"
                "请补充或修正必填参数：园区（garden_name）。"
            )

        # 外卖/订餐意图隔离：本 Skill 只支持堂食菜单查询
        takeout_hint_text = " ".join(
            [
                str(params.taste_preference or ""),
                str(kwargs.get("user_query") or ""),
                str(kwargs.get("intent") or ""),
            ]
        )
        if self._contains_takeout_intent(takeout_hint_text):
            return (
                "当前能力：我仅支持食堂堂食菜单查询（按园区/档口/餐型/口味）。\n"
                "暂不支持：外卖下单、外卖查单、取消外卖订单。\n"
                "建议操作：请使用 cafeteria-takeout Skill 处理外卖相关需求。"
            )

        # A) 自动推断日期/餐次（减少大模型幻觉）
        target_date = params.custom_date or datetime.now().date().isoformat()
        meal_time = self._infer_meal_time(datetime.now())

        # 支持显式餐型参数优先
        if params.meal_type is not None:
            meal_time = self._meal_type_id_to_name(params.meal_type)
        else:
            # 其次从 taste_preference 文案中识别"早餐/午餐/晚餐"
            meal_from_text = self._infer_meal_time_from_text(params.taste_preference)
            if meal_from_text:
                meal_time = meal_from_text

        try:
            # 1) 园区名 -> gardenId +（尽可能）返回"全部可用区域"
            garden, area_names = self._resolve_garden_and_area_names(
                garden_name=params.garden_name,
            )
        except Exception as e:
            return f"获取园区失败：{e}"

        dishes: List[Dish] = []
        garden_id = garden.get("gardenId")
        if garden_id is None:
            return "获取园区失败：gardenId 为空"

        try:
            selected_area = (params.area_name or "").strip()
            if selected_area:
                stores = self._get_stores(
                    garden_id=str(garden_id),
                    area_name=selected_area,
                )
                stores = self._filter_stores_by_area_name(stores, selected_area)
                if not stores:
                    return (
                        f"在「{garden.get('gardenName','')}」没有找到匹配「{selected_area}」的档口。\n"
                        "你可以换一个档口关键词试试，或不指定档口让我查全园区菜单。"
                    )
                for s in stores:
                    self._append_store_menu_into_dishes(
                        dishes=dishes,
                        garden=garden,
                        area_name=selected_area,
                        store=s,
                        meal_time=meal_time,
                        target_date=target_date,
                        meal_type=params.meal_type,
                    )
            elif area_names:
                for area_name in area_names:
                    stores = self._get_stores(
                        garden_id=str(garden_id),
                        area_name=area_name,
                    )
                    for s in stores:
                        self._append_store_menu_into_dishes(
                            dishes=dishes,
                            garden=garden,
                            area_name=area_name,
                            store=s,
                            meal_time=meal_time,
                            target_date=target_date,
                            meal_type=params.meal_type,
                        )
            else:
                stores = self._get_stores(
                    garden_id=str(garden_id),
                    area_name=None,
                )
                for s in stores:
                    self._append_store_menu_into_dishes(
                        dishes=dishes,
                        garden=garden,
                        area_name="",
                        store=s,
                        meal_time=meal_time,
                        target_date=target_date,
                        meal_type=params.meal_type,
                    )
        except Exception as e:
            return f"拉取档口/菜单失败：{e}"

        if not dishes:
            return (
                f"{target_date} {meal_time} 在「{garden.get('gardenName','')}」没有拉到菜单数据。"
                "你可以换个园区名或餐型再试（或让维护者确认当前账号是否有该园区的访问权限）。"
            )

        # 4) 偏好匹配聚合
        store_mentions = self._extract_store_mentions_from_text(
            params.taste_preference,
            dishes,
        )
        matched = self._filter_dishes_by_preference(
            dishes,
            params.taste_preference,
            store_mentions=store_mentions,
        )
        if not matched:
            return (
                f"{target_date} {meal_time}（{garden.get('gardenName','')}）没有找到符合「{params.taste_preference}」的菜。\n"
                "你可以换个偏好词（例如：辣/清淡/低热量/鸡胸/素食），或不填偏好让我直接列菜单。"
            )

        effective_max_results = params.max_results
        if store_mentions and not max_results_was_set:
            effective_max_results = 200

        effective_per_store_max_dishes = max(params.per_store_max_dishes, effective_max_results)
        if store_mentions and not per_store_max_was_set:
            effective_per_store_max_dishes = effective_max_results

        deduped = self._dedupe_dishes(matched)
        total_count = len(deduped)
        use_category_view = (not store_mentions) and self._is_no_specific_taste_keyword(params.taste_preference)
        if use_category_view:
            matched = self._select_round_robin_by_store(deduped, limit=effective_max_results)
        else:
            matched = deduped[:effective_max_results]
        return self._format_output(
            date_str=target_date,
            garden_name=str(garden.get("gardenName") or ""),
            area_name=(params.area_name or "全园区"),
            meal_time=meal_time,
            dishes=matched,
            taste_preference=params.taste_preference,
            per_store_max_dishes=effective_per_store_max_dishes,
            group_by_category=use_category_view,
            total_count=total_count,
            has_more=total_count > len(matched),
        )

    def _is_no_specific_taste_keyword(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return True
        cleaned = re.sub(r"(早餐|早上|早饭|早晨|上午|午餐|中午|下午|晚餐|晚上|晚饭|晚间|夜宵)", "", t)
        cleaned = cleaned.replace("今天", "").replace("今晚", "").replace("今日", "").replace("今夜", "")
        cleaned = cleaned.strip(" ,，/\t\n")
        cleaned_norm = cleaned.replace(" ", "")
        if not cleaned_norm:
            return True
        no_taste_set = {
            "好吃的", "好吃", "美味", "什么好吃", "有什么好吃",
            "想吃", "想吃什么", "吃什么", "推荐", "随便",
            "有什么吃的", "想吃的", "吃的",
        }
        if cleaned_norm in no_taste_set:
            return True
        return False

    def _select_round_robin_by_store(self, dishes: List[Dish], *, limit: int) -> List[Dish]:
        store_to_list: Dict[str, List[Dish]] = {}
        for d in dishes:
            sn = str(d.store_name or "").strip()
            if not sn:
                sn = "未知档口"
            store_to_list.setdefault(sn, []).append(d)
        stores = sorted(store_to_list.keys())
        out: List[Dish] = []
        idx = 0
        while len(out) < limit:
            advanced = False
            for sn in stores:
                arr = store_to_list.get(sn, [])
                if idx < len(arr):
                    out.append(arr[idx])
                    advanced = True
                    if len(out) >= limit:
                        break
            if not advanced:
                break
            idx += 1
        return out

    def _extract_store_mentions_from_text(self, text: str, dishes: List[Dish]) -> set:
        if not (text or "").strip():
            return set()
        pref_norm = self._normalize_text(text)
        store_names = {str(d.store_name).strip() for d in dishes if getattr(d, "store_name", None)}
        out: set = set()
        for sn in store_names:
            sn = (sn or "").strip()
            if len(sn) < 2:
                continue
            if sn and sn in text:
                out.add(sn)
                continue
            sn_norm = self._normalize_text(sn)
            if sn_norm and sn_norm in pref_norm:
                out.add(sn)
        return out

    # -----------------------------
    # HTTP client（使用 SmartSSOSession）
    # -----------------------------
    def _make_request(
        self,
        *,
        method: Literal["GET", "POST"],
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """使用 SmartSSOSession 发起请求，自动处理 SSO 认证"""
        url = f"{self.BASE_URL}{path}"
        
        # 使用 client.request() 发起请求，自动处理 SSO 认证
        response = self.client.request(
            method=method,
            url=url,
            params=params,
            json=json_body,
            timeout=self.timeout_s,
        )
        
        if response.status_code == 401:
            raise RuntimeError("未授权（401）：Cookie 会话失效或未完成公司内网登录")
        
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, dict):
            raise RuntimeError("接口返回不是 JSON object")
        if "code" in data and data.get("code") != 0:
            raise RuntimeError(f"接口 code!=0: {data.get('code')} {data.get('message')}")
        
        return data

    # -----------------------------
    # API calls
    # -----------------------------
    def _get_gardens(self) -> List[Dict[str, Any]]:
        data = self._make_request(method="GET", path="/cafeteria/api/v2/getGardenAndArea")
        result = data.get("result")
        if not isinstance(result, list):
            raise RuntimeError("getGardenAndArea: result 非数组")
        return [x for x in result if isinstance(x, dict)]

    def _get_stores(self, *, garden_id: str, area_name: Optional[str]) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"gardenId": garden_id}
        if area_name:
            params["areaName"] = area_name
        data = self._make_request(method="GET", path="/cafeteria/api/v2/getStore", params=params)
        result = data.get("result")
        if not isinstance(result, list):
            raise RuntimeError("getStore: result 非数组")
        return [x for x in result if isinstance(x, dict)]

    def _get_meal_types(self, *, store_id: int, date_str: str) -> List[Dict[str, Any]]:
        data = self._make_request(
            method="GET",
            path="/cafeteria/api/v2/restaurantDish/mealType",
            params={"storeId": store_id, "date": date_str},
        )
        result = data.get("result")
        if not isinstance(result, list):
            raise RuntimeError("mealType: result 非数组")
        return [x for x in result if isinstance(x, dict)]

    def _get_menu(self, *, store_id: int, meal_type: int, date_str: str) -> List[Dict[str, Any]]:
        data = self._make_request(
            method="GET",
            path="/cafeteria/api/v2/restaurantDish/get",
            params={"storeId": store_id, "mealType": meal_type, "date": date_str},
        )
        result = data.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("restaurantDish/get: result 非对象")
        dish_list = result.get("dishList")
        if not isinstance(dish_list, list):
            raise RuntimeError("restaurantDish/get: result.dishList 非数组")
        return [x for x in dish_list if isinstance(x, dict)]

    # -----------------------------
    # Resolve logic
    # -----------------------------
    def _infer_meal_time(self, now: datetime) -> Literal["早餐", "午餐", "晚餐"]:
        h = now.hour + now.minute / 60.0
        if h < 10.0:
            return "早餐"
        if 10.0 <= h < 14.0:
            return "午餐"
        return "晚餐"

    def _infer_meal_time_from_text(self, text: str) -> Optional[Literal["早餐", "午餐", "晚餐"]]:
        t = (text or "").strip()
        if not t:
            return None
        if re.search(r"(早餐|早上|早饭|早晨|上午)", t):
            return "早餐"
        if re.search(r"(午餐|中午|下午|午饭)", t):
            return "午餐"
        if re.search(r"(晚餐|晚上|晚饭|晚间|夜宵)", t):
            return "晚餐"
        return None

    def _extract_area_names_from_garden(self, garden: Dict[str, Any]) -> List[str]:
        areas: List[str] = []
        if isinstance(garden.get("areaList"), list):
            areas = [str(x) for x in garden.get("areaList") if x]
        if not areas and isinstance(garden.get("areaLists"), list):
            areas = [
                str(x.get("areaName"))
                for x in garden.get("areaLists")
                if isinstance(x, dict) and x.get("areaName")
            ]
        return areas

    def _resolve_garden_and_area_names(
        self,
        *,
        garden_name: str,
    ) -> Tuple[Dict[str, Any], List[str]]:
        gardens = self._get_gardens()
        if not gardens:
            raise RuntimeError("园区列表为空")

        garden_query = self._normalize_garden_query(garden_name)
        q = (garden_query or "").strip()
        if not q:
            raise RuntimeError("园区名为空")

        qn = self._normalize_text(q)
        parts = [p for p in re.split(r"[\s·\-—_]+", q) if p]

        def score_g(g: Dict[str, Any]) -> int:
            if not isinstance(g, dict):
                return -(10**9)
            name = str(g.get("gardenName") or "")
            if not name:
                return -(10**9)
            if q and q in name:
                return 1_000_000
            nn = self._normalize_text(name)
            score = 0
            if qn and qn in nn:
                score += 1000
            for p in parts:
                pn = self._normalize_text(p)
                if pn and pn in nn:
                    score += 100
            score -= max(0, len(nn) - len(qn))
            return score

        def name_match(g: Dict[str, Any]) -> bool:
            if not isinstance(g, dict):
                return False
            name = str(g.get("gardenName") or "")
            if not name:
                return False
            if q and q in name:
                return True
            nn = self._normalize_text(name)
            if qn and qn in nn:
                return True
            for p in parts:
                pn = self._normalize_text(p)
                if pn and pn in nn:
                    return True
            return False

        matched_by_name = [g for g in gardens if isinstance(g, dict) and name_match(g)]
        search_pool = matched_by_name if matched_by_name else gardens
        candidates = sorted(search_pool, key=score_g, reverse=True)
        if not candidates:
            raise RuntimeError("无法匹配园区")

        for g in candidates:
            areas = self._extract_area_names_from_garden(g)
            if areas:
                g2 = dict(g)
                g2["gardenId"] = str(g2.get("gardenId"))
                return g2, areas

        best = candidates[0]
        g2 = dict(best)
        g2["gardenId"] = str(g2.get("gardenId"))
        return g2, []

    def _append_store_menu_into_dishes(
        self,
        *,
        dishes: List[Dish],
        garden: Dict[str, Any],
        area_name: str,
        store: Dict[str, Any],
        meal_time: str,
        target_date: str,
        meal_type: Optional[int] = None,
    ) -> None:
        try:
            store_id = int(store.get("storeId"))
            store_name = str(store.get("storeName") or "").strip() or f"store:{store_id}"
            area_display_name = area_name or str(store.get("areaName") or "").strip()
        except Exception:
            return

        meal_candidates = self._resolve_meal_types(
            store_id=store_id,
            date_str=target_date,
            meal_name=meal_time,
            meal_type=meal_type,
        )
        if not meal_candidates:
            return

        for meal_type_id, meal_type_name in meal_candidates:
            try:
                dish_list = self._get_menu(
                    store_id=store_id,
                    meal_type=meal_type_id,
                    date_str=target_date,
                )
            except Exception:
                continue

            for item in dish_list:
                try:
                    dish_name = str(item.get("dishName") or "").strip()
                    if not dish_name:
                        continue
                    dishes.append(
                        Dish(
                            garden_name=str(garden.get("gardenName") or ""),
                            area_name=area_display_name,
                            store_id=store_id,
                            store_name=store_name,
                            meal_time=meal_type_name,
                            dish_name=dish_name,
                            cate_name=str(item.get("cateName") or ""),
                            description=str(item.get("description") or ""),
                        )
                    )
                except Exception:
                    continue

    def _resolve_meal_types(
        self,
        *,
        store_id: int,
        date_str: str,
        meal_name: str,
        meal_type: Optional[int],
    ) -> List[Tuple[int, str]]:
        meal_types = self._get_meal_types(store_id=store_id, date_str=date_str)
        if not meal_types:
            return []

        out: List[Tuple[int, str]] = []
        if meal_type is not None:
            target_name = self._meal_type_id_to_name(meal_type)
            for m in meal_types:
                try:
                    mid = int(m.get("id"))
                except Exception:
                    continue
                mname = str(m.get("mealTypeName") or self._meal_type_id_to_name(mid))
                if mid == meal_type or target_name == mname or target_name in mname:
                    out.append((mid, mname))
            return out

        hit = None
        for m in meal_types:
            mname = str(m.get("mealTypeName") or "")
            if mname == meal_name or (meal_name and meal_name in mname):
                hit = m
                break

        if hit is None:
            return []

        try:
            out.append((int(hit.get("id")), str(hit.get("mealTypeName") or meal_name)))
        except Exception:
            return []
        return out

    # -----------------------------
    # Filtering & formatting
    # -----------------------------
    def _filter_dishes_by_preference(
        self,
        dishes: List[Dish],
        taste_preference: str,
        *,
        store_mentions: Optional[set] = None,
    ) -> List[Dish]:
        pref = (taste_preference or "").strip()
        if not pref:
            return dishes

        pref = re.sub(r"(早餐|早上|早饭|早晨|上午|午餐|中午|下午|晚餐|晚上|晚饭|晚间|夜宵)", "", pref)
        pref = pref.strip(" ,，/\t\n")

        if store_mentions:
            mentioned = {s for s in store_mentions if s and str(s).strip()}
            if mentioned:
                dishes = [d for d in dishes if d.store_name in mentioned]
                for sn in mentioned:
                    pref = pref.replace(sn, "")
                pref = pref.strip(" ,，/\t\n")

        if self._is_no_specific_taste_keyword(taste_preference):
            return dishes

        if pref in {"今天", "今晚", "今日", "今夜"}:
            return dishes

        if not pref:
            return dishes

        pref_norm = pref.replace(" ", "")
        if pref_norm in {
            "好吃的", "好吃", "美味", "什么好吃", "有什么好吃",
            "想吃", "想吃什么", "吃什么", "推荐", "随便",
        }:
            return dishes

        tokens = self._preference_to_tokens(pref)
        tokens = [t for t in tokens if not re.match(r"^(不要|不吃|不想)", t)]
        neg_tokens = self._extract_negative_tokens(pref)
        tokens_empty = len(tokens) == 0

        def score(d: Dish) -> int:
            text = f"{d.dish_name} {d.description} {d.cate_name}".lower()
            s = 0
            for t in tokens:
                if t and t in text:
                    s += 3
            for nt in neg_tokens:
                if nt and nt in text:
                    s -= 10
            if pref.lower() in text:
                s += 2
            return s

        scored = [(d, score(d)) for d in dishes]
        if tokens_empty:
            scored = [x for x in scored if x[1] >= 0]
        else:
            scored = [x for x in scored if x[1] > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [d for d, _ in scored]

    def _preference_to_tokens(self, pref: str) -> List[str]:
        p = pref.lower()
        tokens: List[str] = []
        if any(k in p for k in ["辣", "麻辣", "重口", "重口味"]):
            tokens += ["辣", "麻", "麻辣", "香辣", "椒", "孜然"]
        if any(k in p for k in ["清淡", "不油", "少油", "低油", "健康", "低脂", "低热量", "减脂", "轻食"]):
            tokens += ["清淡", "少油", "低脂", "轻食", "蒸", "水煮", "凉拌", "沙拉", "鸡胸", "鱼", "虾"]
        if any(k in p for k in ["素", "素食", "不吃肉"]):
            tokens += ["素", "豆腐", "菌", "青菜", "蔬菜", "沙拉"]
        for t in re.split(r"[\s,，/]+", p):
            t = t.strip()
            if len(t) >= 2:
                tokens.append(t)
        seen: set = set()
        out: List[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out

    def _extract_negative_tokens(self, pref: str) -> List[str]:
        p = pref.lower()
        neg: List[str] = []
        # 匹配"不要XX"或"不吃XX"模式，XX为1-4个中文字符
        m = re.findall(r"不(?:要|吃)?([一-龥]{1,4})", p)
        for word in m:
            if word:
                neg.append(word)
        return neg

    def _dedupe_dishes(self, dishes: List[Dish]) -> List[Dish]:
        seen: set = set()
        out: List[Dish] = []
        for d in dishes:
            key = (d.store_id, d.meal_time, d.dish_name)
            if key in seen:
                continue
            seen.add(key)
            out.append(d)
        return out

    def _format_output(
        self,
        *,
        date_str: str,
        garden_name: str,
        area_name: str,
        meal_time: str,
        dishes: List[Dish],
        taste_preference: str,
        per_store_max_dishes: int,
        group_by_category: bool = False,
        total_count: Optional[int] = None,
        has_more: bool = False,
    ) -> str:
        if group_by_category:
            return self._format_output_by_category(
                date_str=date_str,
                garden_name=garden_name,
                meal_time=meal_time,
                dishes=dishes,
                taste_preference=taste_preference,
                per_store_max_dishes=per_store_max_dishes,
                total_count=total_count,
                has_more=has_more,
            )
        area_bucket: Dict[str, Dict[str, List[str]]] = {}
        for d in dishes:
            a_name = d.area_name.strip() if d.area_name else "其他区域"
            s_name = d.store_name.strip() if d.store_name else "未知档口"
            if a_name not in area_bucket:
                area_bucket[a_name] = {}
            if s_name not in area_bucket[a_name]:
                area_bucket[a_name][s_name] = []
            if d.dish_name not in area_bucket[a_name][s_name]:
                area_bucket[a_name][s_name].append(d.dish_name)
        pref_str = f"符合「{taste_preference}」的" if taste_preference else ""
        lines: List[str] = [f"{date_str} {meal_time}，在 {garden_name}，为您找到以下{pref_str}菜品：\n"]
        for a_name, stores in area_bucket.items():
            lines.append(f"### 📍 {a_name}")
            for s_name, dish_names in stores.items():
                if not dish_names:
                    continue
                display_names = dish_names[:per_store_max_dishes]
                suffix = " 等..." if len(dish_names) > per_store_max_dishes else ""
                lines.append(f"- **【{s_name}】**: " + "、".join(display_names) + suffix)
            lines.append("")
        self._append_more_guidance(lines, total_count=total_count, shown_count=len(dishes), has_more=has_more)
        return "\n".join(lines).strip()

    def _format_output_by_category(
        self,
        *,
        date_str: str,
        garden_name: str,
        meal_time: str,
        dishes: List[Dish],
        taste_preference: str,
        per_store_max_dishes: int,
        total_count: Optional[int] = None,
        has_more: bool = False,
    ) -> str:
        cate_bucket: Dict[str, Dict[str, List[str]]] = {}
        for d in dishes:
            cate = self._map_food_court_category(d)
            store = d.store_name.strip() if d.store_name else "未知档口"
            cate_bucket.setdefault(cate, {})
            cate_bucket[cate].setdefault(store, [])
            if d.dish_name not in cate_bucket[cate][store]:
                cate_bucket[cate][store].append(d.dish_name)
        pref_str = f"符合「{taste_preference}」的" if taste_preference else ""
        lines: List[str] = [
            f"{date_str} {meal_time}，在 {garden_name}，为您找到以下{pref_str}菜品（按美食广场品类展示）：\n"
        ]
        ordered_categories = [
            "中式快餐/正餐", "粉面水饺", "健康轻食", "特色风味",
            "小吃炸串", "汤粥与简餐", "饮品甜点", "其他",
        ]
        cate_order_map = {name: i for i, name in enumerate(ordered_categories)}
        sorted_cates = sorted(
            cate_bucket.keys(),
            key=lambda x: (cate_order_map.get(x, len(ordered_categories)), x),
        )
        for cate_name in sorted_cates:
            lines.append(f"### 🍱 {cate_name}")
            stores = cate_bucket[cate_name]
            for store_name in sorted(stores.keys()):
                dish_names = stores[store_name]
                if not dish_names:
                    continue
                display_names = dish_names[:per_store_max_dishes]
                suffix = " 等..." if len(dish_names) > per_store_max_dishes else ""
                lines.append(f"- **【{store_name}】**: " + "、".join(display_names) + suffix)
            lines.append("")
        self._append_more_guidance(lines, total_count=total_count, shown_count=len(dishes), has_more=has_more)
        return "\n".join(lines).strip()

    def _map_food_court_category(self, dish: Dish) -> str:
        text = f"{dish.cate_name} {dish.store_name} {dish.dish_name}".lower()
        if any(k in text for k in ["轻食", "沙拉", "鸡胸", "低脂", "减脂", "超级碗", "能量碗"]):
            return "健康轻食"
        if any(k in text for k in ["粉", "面", "米线", "刀削", "拉面", "拌面", "水饺", "馄饨", "锅贴"]):
            return "粉面水饺"
        if any(k in text for k in ["炸串", "串", "烤肠", "鸡块", "薯", "卷饼", "夹馍", "小吃"]):
            return "小吃炸串"
        if any(k in text for k in ["汤", "粥", "茶碗蒸", "蒸蛋", "瓦罐"]):
            return "汤粥与简餐"
        if any(k in text for k in ["饮", "奶茶", "冰粉", "甜", "曲奇", "可乐", "茶", "果汁", "糍粑"]):
            return "饮品甜点"
        if any(k in text for k in ["麻辣", "藤椒", "湘", "川", "粤", "港", "日式", "叻沙", "风味", "烧腊"]):
            return "特色风味"
        if any(k in text for k in ["套餐", "盖饭", "拌饭", "炒饭", "快餐", "正餐", "零点", "自选"]):
            return "中式快餐/正餐"
        return "其他"

    def _append_more_guidance(
        self,
        lines: List[str],
        *,
        total_count: Optional[int],
        shown_count: int,
        has_more: bool,
    ) -> None:
        if not has_more:
            return
        if total_count is None or total_count <= shown_count:
            return
        lines.append("────────────────────")
        lines.append(
            f"提示：当前共找到 {total_count} 道菜，以上为您精选展示的 {shown_count} 道，便于快速浏览。"
        )
        lines.append("想继续缩小范围的话，你可以直接告诉我：")
        lines.append("- 查特定档口：例如「西部马华今天有什么」")
        lines.append("- 查特定口味：例如「有没有辣的 / 低热量的」")
        lines.append("- 查特定餐型：例如「晚餐有什么」")

    def _meal_type_id_to_name(self, meal_type: int) -> str:
        return self._MEAL_TYPE_ID_TO_NAME.get(int(meal_type), "午餐")

    def _contains_takeout_intent(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return False
        return bool(self._TAKEOUT_INTENT_PATTERN.search(t))

    def _filter_stores_by_area_name(self, stores: List[Dict[str, Any]], area_name: str) -> List[Dict[str, Any]]:
        kw = (area_name or "").strip()
        if not kw:
            return stores
        kw_norm = self._normalize_text(kw)

        def matched(store: Dict[str, Any]) -> bool:
            sname = str(store.get("storeName") or "")
            aname = str(store.get("areaName") or "")
            if kw in sname or kw in aname or sname in kw or aname in kw:
                return True
            return (
                kw_norm in self._normalize_text(sname)
                or kw_norm in self._normalize_text(aname)
                or self._normalize_text(sname) in kw_norm
                or self._normalize_text(aname) in kw_norm
            )

        result = [s for s in stores if isinstance(s, dict) and matched(s)]
        return result

    # -----------------------------
    # small helpers
    # -----------------------------
    def _best_match(self, items: Iterable[Any], keyword: str, key_fn) -> Optional[Any]:
        kw = (keyword or "").strip().lower()
        if not kw:
            return None
        best = None
        for it in items:
            try:
                text = str(key_fn(it) or "").lower()
            except Exception:
                continue
            if kw in text:
                return it
            if kw.replace(" ", "") in text.replace(" ", ""):
                best = it
        return best

    def _normalize_text(self, s: str) -> str:
        x = (s or "").strip().lower()
        x = re.sub(r"[\s·\-—_()（）\[\]{}]+", "", x)
        return x

    def _normalize_garden_query(self, garden_name: str) -> str:
        raw = (garden_name or "").strip()
        if not raw:
            return raw
        for k, v in self._garden_aliases.items():
            if k and k in raw:
                return v
        return raw


# ─────────────────────────────────────────────────────────────────
# CLI 入口（供 uv run 调用）
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="公司食堂菜单查询脚本（uv 运行时）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  uv run scripts/cafeteria-recommendation.py --garden_name "元中心" --taste_preference "辣"
  uv run scripts/cafeteria-recommendation.py --garden_name "杭州" --custom_date 2025-07-01
        """,
    )
    parser.add_argument("--garden_name", required=True, help="园区名称（必填），如：元中心、杭州")
    parser.add_argument("--taste_preference", default="", help="口味偏好（可选），如：辣、低热量、素食")
    parser.add_argument("--custom_date", default=None, help="指定日期 YYYY-MM-DD（可选，默认今天）")
    parser.add_argument("--area_name", default="", help="指定档口/区域（可选），如：西部马华")
    parser.add_argument("--meal_type", type=int, default=None, choices=[1, 2, 3, 4], help="餐型：1=早餐,2=午餐,3=晚餐,4=夜宵（可选）")
    parser.add_argument("--max_results", type=int, default=50, help="最多返回菜品数（默认50）")
    parser.add_argument("--per_store_max_dishes", type=int, default=50, help="每档口展示菜品数（默认50）")

    args = parser.parse_args()

    skill = CafeteriaRecommendationSkill()
    try:
        result = skill.execute(
            garden_name=args.garden_name,
            taste_preference=args.taste_preference,
            custom_date=args.custom_date,
            area_name=args.area_name,
            meal_type=args.meal_type,
            max_results=args.max_results,
            per_store_max_dishes=args.per_store_max_dishes,
        )
        print(result)
    except Exception as e:
        print(f"执行失败：{e}\n请检查 SSO 认证状态或园区名称是否正确。", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
