# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate",
#   "requests",
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

"""Kim 日历会议室预订客户端"""

import argparse
import calendar
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ks_aimate.sso_login_client import SmartSSOSession

BASE_URL = "https://cal.corp.kuaishou.com"


class CalClient:
    """会议室预订客户端"""

    def __init__(self):
        self.session = SmartSSOSession()

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        resp = self.session.request("GET", f"{BASE_URL}{path}", params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != 0:
            raise RuntimeError(f"API 错误: {json.dumps(data, ensure_ascii=False)}")
        return data

    def _post(self, path: str, body: Any) -> Dict:
        resp = self.session.request("POST", f"{BASE_URL}{path}", json=body)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != 0:
            raise RuntimeError(f"API 错误: {json.dumps(data, ensure_ascii=False)}")
        return data

    def get_calendar_id(self) -> str:
        resp = self.session.request("POST", f"{BASE_URL}/api/calendar/v4/list", json={})
        resp.raise_for_status()
        data = resp.json()
        cal_id = data.get("data", {}).get("userInfo", {}).get("calendarId", "")
        if not cal_id:
            for cal in data.get("data", {}).get("calendars", []):
                if cal.get("isPersonalCal"):
                    cal_id = cal.get("id", "")
                    break
        if not cal_id:
            raise RuntimeError("无法获取用户日历 ID")
        return cal_id

    @staticmethod
    def parse_time(time_str: str) -> int:
        """将时间字符串转为毫秒时间戳（上海时区）"""
        for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(time_str.strip(), fmt)
                ts = calendar.timegm(dt.timetuple()) - 8 * 3600
                return ts * 1000
            except ValueError:
                continue
        raise ValueError(f"无法解析时间：{time_str}")

    @staticmethod
    def format_time(ms: int) -> str:
        """毫秒时间戳转可读时间"""
        dt = datetime.utcfromtimestamp(ms / 1000) + timedelta(hours=8)
        return dt.strftime("%Y-%m-%d %H:%M")

    def rooms(self, from_time: str, to_time: str, building: Optional[str] = None, min_capacity: Optional[int] = None, 
              user_location: Optional[str] = None, json_output: bool = False, limit: Optional[int] = None) -> int:
        """查询空闲会议室"""
        from_ms = self.parse_time(from_time)
        to_ms = self.parse_time(to_time)

        print("正在获取会议室列表...")
        data = self._get("/api/meetingroom/v2/list", {"fromTime": from_ms, "toTime": to_ms})

        available = []
        for b in data["data"].get("meetingRoomInfo", []):
            b_name = b.get("building") or b.get("buildingName", "")
            if building and building not in b_name:
                continue
            for r in b.get("meetingRoom", []):
                if not r.get("idle", False):
                    continue
                cap = r.get("capacity", 0)
                if min_capacity and cap < min_capacity:
                    continue
                device = r.get("device", "") or ""
                available.append({
                    "building": b_name,
                    "name": r.get("name", ""),
                    "shortName": r.get("shortName", ""),
                    "capacity": cap,
                    "floor": r.get("floor", 0),
                    "device": device,
                    "calendarId": r.get("calendarId", ""),
                    "meetingRoomId": r.get("id", ""),
                })

        if not available:
            print(f"❌ 未找到可用会议室（{from_time} - {to_time}）")
            return 0

        # 智能排序：优先显示用户位置附近的会议室
        if user_location:
            # 解析用户位置，如 "T1-2层" -> building_key="T1", user_floor=2
            parts = user_location.upper().replace("层", "").replace("-", " ").split()
            user_building_key = parts[0] if parts else ""
            user_floor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            
            def sort_key(room):
                # 优先级：同楼栋同楼层 > 同楼栋邻层 > 同楼栋其他层 > 其他楼栋
                is_same_building = user_building_key in room["building"]
                floor_diff = abs(room["floor"] - user_floor) if user_floor > 0 else 999
                return (not is_same_building, floor_diff, room["building"], room["floor"])
            
            available.sort(key=sort_key)
        else:
            available.sort(key=lambda x: (x["building"], x["floor"]))

        # 应用数量限制
        total = len(available)
        if limit and limit > 0:
            available = available[:limit]

        # JSON 格式输出
        if json_output:
            result = {
                "total": total,
                "displayed": len(available),
                "time_range": {"from": from_time, "to": to_time.split(' ')[-1]},
                "rooms": available
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        # 普通文本输出
        display_info = f"（共 {total} 间）" if limit is None else f"（共 {total} 间，显示前 {len(available)} 间）"
        print(f"\n✅ 可用会议室 {display_info}：")
        for r in available:
            video = f" 📹[{r['device']}]" if r["device"] else ""
            print(f"  • {r['building']} {r['shortName'] or r['name']}（容量{r['capacity']}人）{video}")
            print(f"    meetingRoomId: {r['meetingRoomId']}")
        
        if limit and total > limit:
            print(f"\n💡 提示：还有 {total - limit} 间未显示，可使用 --limit 参数查看更多")
        
        return 0

    def validate_booking(self, from_ms: int, to_ms: int) -> bool:
        """预订前置校验，返回 True 表示通过，False 表示拒绝"""
        now_ms = int(datetime.utcnow().timestamp() * 1000)

        # 规则3：不能预订超出当前时间 90 天的会议室
        max_ms = now_ms + 90 * 24 * 3600 * 1000
        if from_ms > max_ms:
            print(f"❌ 预订失败：不能预订超过当前时间 90 天后的会议室（最晚可预订至 {self.format_time(max_ms)}）")
            return False

        # 查当天全天日程，用于规则 1 和规则 2
        date_str = datetime.utcfromtimestamp(from_ms / 1000).strftime("%Y-%m-%d")
        # from_ms 是 UTC 时间戳，需转为上海时间的当天范围
        day_from_ms = self.parse_time(f"{date_str} 00:00")
        day_to_ms = self.parse_time(f"{date_str} 23:59")

        calendar_id = self.get_calendar_id()
        data = self._get("/api/v2/event/list", {"calendarIds": calendar_id, "fromTime": day_from_ms, "toTime": day_to_ms})

        room_events = []
        owned_room_events = []  # 仅包含当前用户作为创建者的事件
        for cal_event in data.get("data", {}).get("calendarEvent", []):
            for e in cal_event.get("simpleEvent", []):
                if e.get("meetingRoom"):
                    event_info = {
                        "title": e.get("title", "(无标题)"),
                        "startTime": e.get("startTime"),
                        "endTime": e.get("endTime"),
                        "meetingRoom": e.get("meetingRoom", ""),
                        "ownerCalendarId": e.get("ownerCalendarId", ""),
                    }
                    room_events.append(event_info)
                    # 只统计用户作为创建者的会议室事件
                    if e.get("ownerCalendarId") == calendar_id:
                        owned_room_events.append(event_info)

        # 规则1：创建者同一时段不能有多个带会议室的日程（仅检查用户作为创建者的事件）
        for e in owned_room_events:
            if from_ms < e["endTime"] and to_ms > e["startTime"]:
                print(f"❌ 预订失败：该时段你已创建了带会议室的日程「{e['title']}」"
                      f"（{self.format_time(e['startTime'])} ~ {self.format_time(e['endTime']).split(' ')[-1]}，会议室：{e['meetingRoom']}）")
                return False

        # 规则2：当天创建的带会议室的日程总时长不超过 4 小时（240 分钟）（仅统计用户作为创建者的事件）
        used_ms = sum(e["endTime"] - e["startTime"] for e in owned_room_events)
        new_duration_ms = to_ms - from_ms
        total_ms = used_ms + new_duration_ms
        if total_ms > 4 * 3600 * 1000:
            used_min = used_ms // 60000
            remaining_min = max(0, 240 - used_min)
            print(f"❌ 预订失败：当天带会议室的日程已用 {used_min} 分钟，"
                  f"本次需 {new_duration_ms // 60000} 分钟，超出每日 4 小时限制（剩余可用 {remaining_min} 分钟）")
            return False

        return True

    def book(self, meeting_room_id: str, from_time: str, to_time: str, title: str = "会议", participants: Optional[str] = None) -> int:
        """预约会议室"""
        from_ms = self.parse_time(from_time)
        to_ms = self.parse_time(to_time)

        if not self.validate_booking(from_ms, to_ms):
            return 1

        calendar_id = self.get_calendar_id()

        participants_list = [{"id": meeting_room_id, "participantUpdateType": "ADD", "type": "MEETING_ROOM"}]
        if participants:
            for prefix in participants.split(","):
                prefix = prefix.strip()
                if prefix:
                    kwai_id = self.resolve_user_id(prefix)
                    if kwai_id:
                        participants_list.append({"id": kwai_id, "participantUpdateType": "ADD", "type": "USER"})
                        print(f"  已找到用户 {prefix} -> {kwai_id}")
                    else:
                        print(f"  ⚠️  找不到用户 {prefix}，跳过添加")

        print("正在预约会议室...")
        body = {
            "title": title,
            "startTime": from_ms, "endTime": to_ms,
            "start": from_ms, "end": to_ms,
            "isAllDay": False, "allDay": False,
            "calendarId": calendar_id, "ownerCalendarId": calendar_id,
            "timezone": "Asia/Shanghai",
            "participant": participants_list,
            "checkReserveBeforeEventAction": True,
            "groupFlag": False, "viewFrom": "Room",
            "needToNotify": True, "attachments": [],
        }

        result = self._post("/api/event/create", body)
        event_id = result.get("data", {}).get("eventId", "")
        results = result.get("data", {}).get("result", {}).get("result", [])
        if results and results[0].get("bookSuccess"):
            print(f"✅ 预约成功！时间：{from_time} ~ {to_time.split(' ')[-1]}")
            if event_id:
                print(f"   eventId: {event_id}")
        else:
            detail = results[0].get("detail", "") if results else ""
            print(f"❌ 预约失败：{detail or '会议室可能已被抢占'}")
            return 1
        return 0

    def my_events(self, date: Optional[str] = None, from_time: Optional[str] = None, to_time: Optional[str] = None) -> int:
        """查看我的日程"""
        if date:
            from_ms = self.parse_time(f"{date} 00:00")
            to_ms = self.parse_time(f"{date} 23:59")
        else:
            from_ms = self.parse_time(from_time)
            to_ms = self.parse_time(to_time)

        calendar_id = self.get_calendar_id()
        data = self._get("/api/v2/event/list", {"calendarIds": calendar_id, "fromTime": from_ms, "toTime": to_ms})

        events = []
        for cal_event in data.get("data", {}).get("calendarEvent", []):
            for e in cal_event.get("simpleEvent", []):
                events.append({
                    "id": e.get("id"),
                    "title": e.get("title", "(无标题)"),
                    "startTime": e.get("startTime"),
                    "endTime": e.get("endTime"),
                    "meetingRoom": e.get("meetingRoom", ""),
                    "calendarId": cal_event.get("calendarId"),
                })

        if not events:
            print("暂无日程")
            return 0

        events.sort(key=lambda x: x["startTime"])
        print(f"📅 日程列表（共 {len(events)} 条）：")
        for e in events:
            room = f" [{e['meetingRoom']}]" if e["meetingRoom"] else ""
            print(f"  • {e['title']}{room}")
            print(f"    时间：{self.format_time(e['startTime'])} ~ {self.format_time(e['endTime']).split(' ')[-1]}")
            print(f"    eventId: {e['id']}")
            print(f"    calendarId: {e['calendarId']}")
        return 0

    def cancel(self, event_id: str, calendar_id: str) -> int:
        """取消预约"""
        try:
            self._post("/api/event/delete", {"eventId": event_id, "calendarId": calendar_id, "repeatedEventUpdateType": 0})
            print(f"✅ 已取消预约（eventId: {event_id}）")
        except RuntimeError as e:
            print(f"❌ 取消失败：{e}")
            print(f"   请检查 eventId 和 calendarId 是否正确")
            return 1
        return 0

    def search_user(self, keyword: str) -> int:
        """搜索用户"""
        print(f"正在搜索用户: {keyword}...")
        data = self._get("/api/calendar/search", {"content": keyword, "type": 1})
        # API 返回 data 直接是列表
        results = data.get("data", [])

        if not results:
            print(f"❌ 未找到用户: {keyword}")
            return 0

        print(f"\n✅ 找到 {len(results)} 个用户：")
        for u in results:
            print(f"  • {u.get('name', '')} ({u.get('email', '')})")
            print(f"    kwaiUserId: {u.get('kwaiUserId', '')}")
        return 0

    def resolve_user_id(self, keyword: str) -> Optional[str]:
        """将邮箱前缀解析为 kwaiUserId"""
        data = self._get("/api/calendar/search", {"content": keyword, "type": 1})
        results = data.get("data", [])
        if results:
            return results[0].get("kwaiUserId")
        return None

    def verify_user_exists(self, kwai_user_id: str) -> Optional[Dict]:
        """验证用户是否存在且有效，返回用户信息"""
        try:
            # 通过搜索 API 验证用户是否存在
            data = self._get("/api/calendar/search", {"content": kwai_user_id, "type": 1})
            results = data.get("data", [])
            # 查找 kwaiUserId 完全匹配的用户
            for user in results:
                if str(user.get("kwaiUserId")) == str(kwai_user_id):
                    return user
            return None
        except Exception:
            return None

    def add_participant(self, event_id: str, kwai_user_id: str) -> int:
        """向已有事件添加参与者"""
        calendar_id = self.get_calendar_id()
        print(f"获取事件详情: {event_id}...")
        event_data = self._get("/api/v3/event/detail", {"eventId": event_id, "calendarId": calendar_id})
        event = event_data.get("data", {}).get("event", {})

        # update 接口只传 USER 类型参与者（type=1），会议室由系统自动保留
        # participantUpdateType 用整数 0（ADD）
        participants = []
        for p in event.get("participant", []):
            pid = p.get("id") or p.get("kwaiUserId")
            if pid:
                participants.append({"id": pid, "participantUpdateType": 0, "type": 1})

        for prefix in kwai_user_id.split(","):
            prefix = prefix.strip()
            if prefix:
                kwai_id = self.resolve_user_id(prefix)
                if kwai_id and not any(p.get("id") == kwai_id for p in participants):
                    participants.append({"id": kwai_id, "participantUpdateType": 0, "type": 1})
                    print(f"  已找到用户 {prefix} -> {kwai_id}")
                elif not kwai_id:
                    print(f"  ⚠️  找不到用户 {prefix}，跳过")

        print("正在添加参与者...")
        body = {
            "id": event_id,
            "eventId": event_id,
            "title": event.get("title", "会议"),
            "startTime": event.get("startTime"),
            "endTime": event.get("endTime"),
            "start": event.get("startTime"),
            "end": event.get("endTime"),
            "isAllDay": False,
            "allDay": False,
            "calendarId": calendar_id,
            "ownerCalendarId": event.get("ownerCalendarId", calendar_id),
            "timezone": "Asia/Shanghai",
            "participant": participants,
            "checkReserveBeforeEventAction": False,
            "groupFlag": False,
            "viewFrom": "Room",
            "needToNotify": True,
            "attachments": [],
            "repeatedEventUpdateType": 0,
        }
        try:
            self._post("/api/event/update", body)
            print(f"✅ 已添加参与者")
        except RuntimeError as e:
            print(f"❌ 添加参与者失败：{e}")
            return 1
        return 0

    def remove_participant(self, event_id: str, kwai_user_id: str) -> int:
        """从已有事件移除参与者"""
        calendar_id = self.get_calendar_id()
        print(f"获取事件详情: {event_id}...")
        event_data = self._get("/api/v3/event/detail", {"eventId": event_id, "calendarId": calendar_id})
        event = event_data.get("data", {}).get("event", {})

        # 解析要移除的用户 ID 列表
        remove_ids = set()
        for prefix in kwai_user_id.split(","):
            prefix = prefix.strip()
            if not prefix:
                continue
            kwai_id = self.resolve_user_id(prefix)
            if kwai_id:
                remove_ids.add(kwai_id)
                print(f"  已找到用户 {prefix} -> {kwai_id}")
            else:
                print(f"  ⚠️  找不到用户 {prefix}，跳过")

        if not remove_ids:
            print("❌ 没有找到任何要移除的用户")
            return 1

        # 保留的用 0(ADD/KEEP)，移除的用 1(REMOVE)
        participants = []
        for p in event.get("participant", []):
            pid = p.get("id") or p.get("kwaiUserId")
            if not pid:
                continue
            if str(pid) in remove_ids:
                participants.append({"id": pid, "participantUpdateType": 1, "type": 1})
            else:
                participants.append({"id": pid, "participantUpdateType": 0, "type": 1})

        print("正在移除参与者...")
        body = {
            "id": event_id,
            "eventId": event_id,
            "title": event.get("title", "会议"),
            "startTime": event.get("startTime"),
            "endTime": event.get("endTime"),
            "start": event.get("startTime"),
            "end": event.get("endTime"),
            "isAllDay": False,
            "allDay": False,
            "calendarId": calendar_id,
            "ownerCalendarId": event.get("ownerCalendarId", calendar_id),
            "timezone": "Asia/Shanghai",
            "participant": participants,
            "checkReserveBeforeEventAction": False,
            "groupFlag": False,
            "viewFrom": "Room",
            "needToNotify": True,
            "attachments": [],
            "repeatedEventUpdateType": 0,
        }
        try:
            self._post("/api/event/update", body)
            print(f"✅ 已移除参与者")
        except RuntimeError as e:
            print(f"❌ 移除参与者失败：{e}")
            return 1
        return 0
    def add_room(self, event_id: str, meeting_room_id: str) -> int:
        """为已有事件绑定会议室（重建方式：创建带会议室的新事件，取消原事件）"""
        calendar_id = self.get_calendar_id()
        print(f"获取事件详情: {event_id}...")
        event_data = self._get("/api/v3/event/detail", {"eventId": event_id, "calendarId": calendar_id})
        event = event_data.get("data", {}).get("event", {})

        # 检查是否已有会议室
        if event.get("meetingRoom"):
            mr = event["meetingRoom"]
            print(f"❌ 该日程已绑定会议室：{mr.get('building')} {mr.get('name')}")
            return 1

        from_ms = event.get("startTime")
        to_ms = event.get("endTime")

        # 验证会议室在该时间段是否空闲
        print("验证会议室空闲状态...")
        data = self._get("/api/meetingroom/v2/list", {"fromTime": from_ms, "toTime": to_ms})
        room_info = None
        for b in data["data"].get("meetingRoomInfo", []):
            for r in b.get("meetingRoom", []):
                if str(r.get("id")) == str(meeting_room_id):
                    room_info = r
                    break
        if not room_info:
            print(f"❌ 找不到会议室 {meeting_room_id}")
            return 1
        if not room_info.get("idle"):
            print(f"❌ 会议室 {room_info.get('name')} 在该时段不空闲")
            return 1

        # update 接口不支持新增会议室，用 create 重建：保留原参与者 + 绑定会议室，再取消原事件
        participants_list = [
            {"id": meeting_room_id, "participantUpdateType": "ADD", "type": "MEETING_ROOM"}
        ]
        for p in event.get("participant", []):
            pid = p.get("id") or p.get("kwaiUserId")
            if pid:
                participants_list.append({"id": pid, "participantUpdateType": "ADD", "type": "USER"})

        print("正在创建带会议室的新事件...")
        body = {
            "title": event.get("title", "会议"),
            "startTime": from_ms, "endTime": to_ms,
            "start": from_ms, "end": to_ms,
            "isAllDay": False, "allDay": False,
            "calendarId": calendar_id, "ownerCalendarId": calendar_id,
            "timezone": "Asia/Shanghai",
            "participant": participants_list,
            "checkReserveBeforeEventAction": True,
            "groupFlag": False, "viewFrom": "Room",
            "needToNotify": True, "attachments": [],
        }
        try:
            result = self._post("/api/event/create", body)
            new_event_id = result.get("data", {}).get("eventId", "")
            results = result.get("data", {}).get("result", {}).get("result", [])
            if not (results and results[0].get("bookSuccess")):
                detail = results[0].get("detail", "") if results else ""
                print(f"❌ 绑定失败：{detail or '会议室可能已被抢占'}")
                return 1
        except RuntimeError as e:
            print(f"❌ 绑定失败：{e}")
            return 1

        # 取消原事件
        print("正在取消原事件...")
        try:
            self._post("/api/event/delete", {"eventId": event_id, "calendarId": calendar_id, "repeatedEventUpdateType": 0})
        except RuntimeError as e:
            print(f"⚠️  新事件已创建（eventId: {new_event_id}），但取消原事件失败：{e}")
            return 1

        room_name = f"{room_info.get('building', '')} {room_info.get('name', '')}"
        print(f"✅ 已绑定会议室：{room_name}")
        if new_event_id:
            print(f"   新 eventId: {new_event_id}")
        return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Kim 日历会议室预订客户端")
    sub = p.add_subparsers(dest="cmd", required=True)

    # rooms
    pr = sub.add_parser("rooms", help="查询空闲会议室")
    pr.add_argument("--from-time", required=True, help="开始时间 YYYY-MM-DD HH:MM")
    pr.add_argument("--to-time", required=True, help="结束时间 YYYY-MM-DD HH:MM")
    pr.add_argument("--building", default=None, help="楼栋过滤")
    pr.add_argument("--min-capacity", type=int, default=None, help="最小容量")
    pr.add_argument("--user-location", default=None, help="用户位置（如 'T1-2层'），用于优先显示附近会议室")
    pr.add_argument("--json", dest="json_output", action="store_true", help="输出 JSON 格式")
    pr.add_argument("--limit", type=int, default=None, help="限制显示数量（默认显示全部）")
    pr.set_defaults(handler=lambda a: CalClient().rooms(a.from_time, a.to_time, a.building, a.min_capacity, 
                                                         a.user_location, a.json_output, a.limit))

    # book
    pb = sub.add_parser("book", help="预约会议室")
    pb.add_argument("--meeting-room-id", required=True, help="会议室ID")
    pb.add_argument("--from-time", required=True, help="开始时间")
    pb.add_argument("--to-time", required=True, help="结束时间")
    pb.add_argument("--title", default="会议", help="会议主题")
    pb.add_argument("--participants", default=None, help="参与者邮箱前缀或kwaiUserId，逗号分隔，如 yangqian07,gaowen03")
    pb.set_defaults(handler=lambda a: CalClient().book(a.meeting_room_id, a.from_time, a.to_time, a.title, a.participants))

    # my-events
    pm = sub.add_parser("my-events", help="查看我的预约")
    pm.add_argument("--date", default=None, help="查询日期 YYYY-MM-DD")
    pm.add_argument("--from-time", default=None, help="开始时间")
    pm.add_argument("--to-time", default=None, help="结束时间")
    pm.set_defaults(handler=lambda a: CalClient().my_events(a.date, a.from_time, a.to_time))

    # cancel
    pc = sub.add_parser("cancel", help="取消预约")
    pc.add_argument("--event-id", required=True, help="事件ID")
    pc.add_argument("--calendar-id", required=True, help="日历ID")
    pc.set_defaults(handler=lambda a: CalClient().cancel(a.event_id, a.calendar_id))

    # search-user
    ps = sub.add_parser("search-user", help="搜索用户")
    ps.add_argument("--keyword", required=True, help="搜索关键词")
    ps.set_defaults(handler=lambda a: CalClient().search_user(a.keyword))

    # add-participant
    pa = sub.add_parser("add-participant", help="添加参与者")
    pa.add_argument("--event-id", required=True)
    pa.add_argument("--kwai-user-id", required=True, help="参与者邮箱前缀，逗号分隔，如 yangqian07,gaowen03")
    pa.set_defaults(handler=lambda a: CalClient().add_participant(a.event_id, a.kwai_user_id))

    # remove-participant
    pr2 = sub.add_parser("remove-participant", help="移除参与者")
    pr2.add_argument("--event-id", required=True)
    pr2.add_argument("--kwai-user-id", required=True, help="参与者邮箱前缀，逗号分隔，如 yangqian07,gaowen03")
    pr2.set_defaults(handler=lambda a: CalClient().remove_participant(a.event_id, a.kwai_user_id))

    # add-room
    par = sub.add_parser("add-room", help="为已有日程绑定会议室")
    par.add_argument("--event-id", required=True, help="事件ID")
    par.add_argument("--meeting-room-id", required=True, help="会议室ID（meetingRoomId）")
    par.set_defaults(handler=lambda a: CalClient().add_room(a.event_id, a.meeting_room_id))

    return p


def main() -> int:
    try:
        parser = build_parser()
        args = parser.parse_args()
        return args.handler(args)
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
