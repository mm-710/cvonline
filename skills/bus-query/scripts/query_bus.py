#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
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

"""
快手班车查询脚本 - 集成 SmartSSOSession 自动处理 SSO 认证
用法:
    uv run scripts/query_bus.py [选项]

选项:
    -g, --garden ID    园区 ID（-1=全部，98=元中心，93=万家灯火大厦）
    -t, --type TYPE    线路类型（ALL_TYPE / REVCEIVE / FREQUENT_SHUTTLE）
    -d, --date DATE    日期（格式 YYYY-MM-DD，或中文：今天/明天/后天/周一/下周三/4月5日）
    -h, --help         显示帮助
"""

import re
import sys
import json
import argparse
from datetime import datetime, timedelta
from ks_aimate.sso_login_client import SmartSSOSession

# --------------------------------------------------------------------------- #
# 合法园区白名单
# --------------------------------------------------------------------------- #
VALID_GARDEN_IDS = {-1, 93, 98}
GARDEN_NAMES = {-1: "全部", 93: "北京·万家灯火大厦", 98: "北京·元中心"}

# 中文星期映射（isoweekday: 1=周一 … 7=周日）
_WEEKDAY_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "日": 7,
}

# 日期字符串最大允许长度
_DATE_MAX_LEN = 20

# 允许出现的字符集（ASCII 可打印 + 中文 + 数字 + 常见分隔符）
_SAFE_PATTERN = re.compile(r'^[\x20-\x7E\u4e00-\u9fa5]+$')


def _next_weekday(today: datetime, target_isoweekday: int, next_week: bool = False) -> datetime:
    """返回本周（或下周）对应 ISO 星期几的日期。若已过则顺延到下周（除非 next_week=True 强制下周）。"""
    days_ahead = target_isoweekday - today.isoweekday()
    if next_week:
        # 强制下周
        if days_ahead <= 0:
            days_ahead += 7
        # 再加 7 天确保是"下周"
        if days_ahead < 7:
            days_ahead += 7
        # 实际上只需保证 days_ahead ∈ (0,14]，且 isoweekday 正确
        # 重新计算：下周目标 = 本周该 isoweekday 的日期 + 7
        days_ahead = target_isoweekday - today.isoweekday()
        if days_ahead <= 0:
            days_ahead += 7
        days_ahead += 7
    else:
        if days_ahead < 0:
            days_ahead += 7
        # 如果是今天（days_ahead==0）则不顺延，保留今天
    return today + timedelta(days=days_ahead)


def parse_date(raw) -> str:
    """
    将任意输入解析为 YYYY-MM-DD 字符串。

    支持：
    - None / 空串 → 今天
    - 中文自然语言：今天/明天/后天/大后天/周X/星期X/下周X/M月D日
    - 标准格式：YYYY-MM-DD / YYYY/MM/DD / YYYY-M-D 等
    - 当年简写：M月D日 / M-D / M/D

    不支持/拦截：
    - 长度 > 20
    - 含 emoji 或非法字符
    - 英文 today/tomorrow 等（明确提示使用 YYYY-MM-DD）
    - 数字 0 或纯数字
    - 日历上不存在的日期（如 2月30日、13月1日）
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # ── 1. None / 空白 ──────────────────────────────────────────────────────
    if raw is None:
        return today.strftime("%Y-%m-%d")
    raw = str(raw).strip()
    if not raw:
        return today.strftime("%Y-%m-%d")

    # ── 2. 长度检查 ──────────────────────────────────────────────────────────
    if len(raw) > _DATE_MAX_LEN:
        raise ValueError(
            f"日期输入超长（{len(raw)} 字符），请使用 YYYY-MM-DD 格式（如 {today.strftime('%Y-%m-%d')}）"
        )

    # ── 3. 字符集检查（禁止 emoji / 不可见字符）────────────────────────────
    if not _SAFE_PATTERN.match(raw):
        raise ValueError(
            f"日期包含非法字符：{raw!r}，请使用 YYYY-MM-DD 格式（如 {today.strftime('%Y-%m-%d')}）"
        )

    # ── 4. 纯数字（含 "0"）────────────────────────────────────────────────
    if re.fullmatch(r'\d+', raw):
        raise ValueError(
            f"日期格式非法：{raw!r}，请使用 YYYY-MM-DD 格式（如 {today.strftime('%Y-%m-%d')}）"
        )

    # ── 5. 中文自然语言 ──────────────────────────────────────────────────────
    # 5a. 今天/明天/后天/大后天
    if raw in ("今天", "今日"):
        return today.strftime("%Y-%m-%d")
    if raw in ("明天", "明日"):
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if raw in ("后天", "後天"):
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    if raw in ("大后天", "大後天"):
        return (today + timedelta(days=3)).strftime("%Y-%m-%d")

    # 5b. 下周X
    m = re.fullmatch(r'下周([一二三四五六七日])', raw)
    if not m:
        m = re.fullmatch(r'下星期([一二三四五六七日])', raw)
    if m:
        wd = _WEEKDAY_MAP[m.group(1)]
        return _next_weekday(today, wd, next_week=True).strftime("%Y-%m-%d")

    # 5c. 周X / 星期X（本周，若已过则下周）
    m = re.fullmatch(r'(?:周|星期)([一二三四五六七日])', raw)
    if m:
        wd = _WEEKDAY_MAP[m.group(1)]
        return _next_weekday(today, wd, next_week=False).strftime("%Y-%m-%d")

    # 5d. M月D日（当年）
    m = re.fullmatch(r'(\d{1,2})月(\d{1,2})日?', raw)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        return _validate_and_format(today.year, month, day, raw)

    # ── 6. 英文自然语言（明确拦截给出提示）───────────────────────────────────
    english_natural = re.fullmatch(
        r'(?i)(today|tomorrow|yesterday|next\s+\w+|this\s+\w+)', raw
    )
    if english_natural:
        raise ValueError(
            f"不支持英文自然语言日期 {raw!r}，请使用 YYYY-MM-DD 格式（如 {today.strftime('%Y-%m-%d')}）"
            "，或中文：今天/明天/周一/4月5日"
        )

    # ── 7. 标准日期格式（含多种分隔符，YYYY-M-D / YYYY/M/D / M-D / M/D）────
    # 7a. YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    m = re.fullmatch(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', raw)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _validate_and_format(year, month, day, raw)

    # 7b. M-D / M/D（当年简写）
    m = re.fullmatch(r'(\d{1,2})[-/](\d{1,2})', raw)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        return _validate_and_format(today.year, month, day, raw)

    # ── 8. 其他一切 → 报错 ─────────────────────────────────────────────────
    raise ValueError(
        f"日期格式非法：{raw!r}，请使用 YYYY-MM-DD（如 {today.strftime('%Y-%m-%d')}）"
        "，或中文：今天/明天/后天/周一/下周三/4月5日"
    )


def _validate_and_format(year: int, month: int, day: int, raw: str) -> str:
    """用 datetime 验证日历合法性（含 2月30日 等），通过则返回 YYYY-MM-DD。"""
    try:
        dt = datetime(year, month, day)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"日期不存在：{raw!r}（{year}年{month}月{day}日），请检查后重试"
        )


def validate_garden_id(garden_id: int) -> None:
    """校验园区 ID 是否在白名单内，不合法则抛出 ValueError。"""
    if garden_id not in VALID_GARDEN_IDS:
        valid_desc = "、".join(f"{v}（{GARDEN_NAMES[v]}）" for v in sorted(VALID_GARDEN_IDS))
        raise ValueError(
            f"园区 ID {garden_id} 不支持，可用值：{valid_desc}"
        )


# --------------------------------------------------------------------------- #
# 主查询工具
# --------------------------------------------------------------------------- #

class BusQueryTool:
    """快手班车查询工具 - 使用 SmartSSOSession 自动处理认证"""

    BASE_URL = "https://xz.corp.kuaishou.com"
    API_ENDPOINT = "/is-parking/api/bus/user/line"

    def __init__(self):
        # 初始化 SSO 会话客户端
        self.client = SmartSSOSession()

    def query_bus_lines(self, garden_id=-1, line_type="ALL_TYPE", date=None):
        """
        查询班车线路信息

        Args:
            garden_id: 园区ID (-1=全部, 98=元中心, 93=万家灯火大厦)
            line_type: 线路类型 (ALL_TYPE, REVCEIVE, FREQUENT_SHUTTLE)
            date: 查询日期（YYYY-MM-DD 或中文自然语言，默认今天）

        Returns:
            list: 班车线路列表

        Raises:
            ValueError: 参数校验失败（本地拦截，不发网络请求）
        """
        # ── 前置校验（本地，不触碰网络）────────────────────────────────────
        date = parse_date(date)
        validate_garden_id(garden_id)

        url = f"{self.BASE_URL}{self.API_ENDPOINT}"
        payload = {
            "gardenId": garden_id,
            "lineType": line_type,
            "date": date
        }

        print(f"查询班车信息...")
        print(f"园区: {garden_id} | 线路类型: {line_type} | 日期: {date}")

        try:
            # 使用 SmartSSOSession 发起请求，自动处理 SSO 认证
            response = self.client.request(
                "POST",
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            data = response.json()

            if data.get('code') != 0:
                raise Exception(f"API 返回错误: {data.get('message', '未知错误')}")

            return data.get('result', [])

        except Exception as e:
            print(f"查询失败: {e}", file=sys.stderr)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="快手班车查询脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-g", "--garden",
        type=int,
        default=-1,
        help="园区 ID（-1=全部，98=元中心，93=万家灯火大厦）"
    )
    parser.add_argument(
        "-t", "--type",
        type=str,
        default="ALL_TYPE",
        choices=["ALL_TYPE", "REVCEIVE", "FREQUENT_SHUTTLE"],
        help="线路类型"
    )
    parser.add_argument(
        "-d", "--date",
        type=str,
        default=None,
        help="日期（格式 YYYY-MM-DD，或中文：今天/明天/后天/周一/下周三/4月5日，默认今天）"
    )

    args = parser.parse_args()

    try:
        tool = BusQueryTool()
        result = tool.query_bus_lines(
            garden_id=args.garden,
            line_type=args.type,
            date=args.date
        )

        # 输出 JSON 格式结果
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        # 本地参数校验失败（输入非法），单独展示，exit code=2
        print(f"参数错误: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        # 网络/服务端错误，exit code=1
        print(f"执行失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
