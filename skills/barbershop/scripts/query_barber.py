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
#!/usr/bin/env -S uv run --refresh-package ks_aimate --quiet --script
"""
快手理发店查询工具（kaleido-xz 平台）

用法:
  uv run --refresh-package ks_aimate scripts/query_barber.py --list-shops                                   # 列出所有可用职场
  uv run --refresh-package ks_aimate scripts/query_barber.py --list --shop 万家灯火                          # 查看所有理发师今日状态
  uv run --refresh-package ks_aimate scripts/query_barber.py --date 2026-03-25 --shop 万家灯火               # 查询3-25日所有理发师可约时间段
  uv run --refresh-package ks_aimate scripts/query_barber.py --date 2026-03-25 --barber 阿荣 --shop 万家灯火 # 查询3-25阿荣的可约时间段
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders                                    # 查询已预约记录（默认）
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders --status completed                # 查询已完成记录
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders --status cancelled                # 查询已取消记录
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders --status notArrived              # 查询未到店记录

⚠️ 写操作（谨慎使用）:
  uv run --refresh-package ks_aimate scripts/query_barber.py --book --barber 阿荣 --date 2026-03-25 --time 10:00 --service 洗剪吹 --phone 18600008888 --shop 万家灯火 --confirm
  uv run --refresh-package ks_aimate scripts/query_barber.py --cancel --order-id <orderId>

认证方式:
  集成 SmartSSOSession，认证由脚本内部自动处理，无需人工干预
"""
import os, sys, argparse, warnings, datetime
from ks_aimate.sso_login_client import SmartSSOSession
warnings.filterwarnings("ignore")

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE     = "https://kaleido-xz.corp.kuaishou.com"
API_BASE = f"{BASE}/api/runtime/jLPKe54PRyOD/env/online"

# ──────────────────────────────────────────────────────────
# HTTP 工具（使用 SmartSSOSession）
# ──────────────────────────────────────────────────────────

class BarberShopClient:
    """理发店查询客户端 - 使用 SmartSSOSession 自动处理认证"""
    
    def __init__(self):
        # 初始化 SSO 会话客户端
        self.client = SmartSSOSession()
    
    def execute_flow(self, flow_id, **kwargs):
        """执行 kaleido-xz flow 请求"""
        body = {"flowId": flow_id, **kwargs}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": f"{BASE}/m/app/jLPKe54PRyOD/env/online/page/homePage",
        }
        
        response = self.client.request(
            "POST",
            f"{API_BASE}/executeFlow",
            json=body,
            headers=headers
        )
        return response.json()
    
    def get_account(self):
        """获取账户信息"""
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = self.client.request("GET", f"{API_BASE}/account", headers=headers)
        return response.json()


# ──────────────────────────────────────────────────────────
# 解析工具
# ──────────────────────────────────────────────────────────

def get_outputs(resp):
    """解析 executeFlow 响应，返回 outputs 字典。
    注意：outputs 可能为空字典 {} 表示成功但无数据，此时返回空字典而非 None。
    只有在外层 code != 0 时才返回 None 表示请求失败。
    """
    if not resp or resp.get("code") != 0:
        return None
    # outputs 为 None/缺失时返回空字典（不返回 None，避免误判为失败）
    return (resp.get("data") or {}).get("outputs") or {}


def get_outputs_data(resp):
    outputs = get_outputs(resp)
    if not outputs:
        return None
    if outputs.get("code") not in (None, 0):
        return None
    return outputs.get("data")


def fmt_date(s):
    return str(s)[:10] if s else "-"


# ──────────────────────────────────────────────────────────
# 业务查询
# ──────────────────────────────────────────────────────────

def query_shops(client):
    params = {'pageInfo': {'pageNum': 1, 'pageSize': 1000}}
    resp = client.execute_flow('default#barber_shop#QUERY_SELECT_LIST', params=params)
    docs = resp.get('data', {}).get('outputs', {}).get('data', {}).get('documents', [])
    return docs


def query_barbers(client, shop_id):
    params = {'barber_shop_id': shop_id}
    resp = client.execute_flow("JpZolpOqCYXIXRrX", params=params)
    data = get_outputs_data(resp)
    return data if isinstance(data, list) else []


def query_time_slots(client, date_str, barber_username=None):
    """查询可约时间段。
    ⚠️ barber 参数必须传 username（如 ext_shipengshen），传数据库 _id 会返回 10202。
    """
    params = {"choose_date": date_str, "duration": 30}
    if barber_username:
        params["barber"] = barber_username
    resp = client.execute_flow("qUOdRHCN3v4QZAEY", params=params)
    outputs = get_outputs(resp)
    if not outputs:
        return [], "接口请求失败"
    code = outputs.get("code")
    if code == 10202:
        # 不传 barber 时如果返回 10202，表示已过营业时间段
        msg = outputs.get("errorDisplayMsg") or "已过营业时间段"
        return [], msg
    if code not in (0, None):
        return [], outputs.get("errorDisplayMsg") or f"错误码 {code}"

    data = outputs.get("data")
    if isinstance(data, dict):
        all_slots = data.get("periods", [])
    elif isinstance(data, list):
        all_slots = data
    else:
        return [], None
    # 过滤 reducible=False 的不可约时段（已被预约或已过时间）
    available = [s for s in all_slots if s.get("reducible", True) is not False]
    if not available and all_slots:
        # 全部时段均不可约：判断是已过还是约满
        import datetime as _dt
        try:
            qdate = _dt.date.fromisoformat(date_str)
            today = _dt.date.today()
            if qdate <= today:
                return [], "[DATE_PASSED] 查询日期已过，请改查未来工作日"
        except Exception:
            pass
        return [], "[ALL_TAKEN] 该日该理发师所有时段已被预约"
    return available, None


def check_ban_status(client):
    """检查用户是否被封禁。
    flowId: yAxE8XITaNI1Osx8
    返回: {"banned": bool, "free_time": str | None}
    free_time 示例: "2026-04-25 13:30"
    """
    try:
        resp = client.execute_flow("yAxE8XITaNI1Osx8", params={})
        data = get_outputs_data(resp)
        if isinstance(data, dict):
            return {
                "banned": bool(data.get("banned", False)),
                "free_time": data.get("free_time") or None,
            }
    except Exception:
        pass
    return {"banned": False, "free_time": None}


def query_my_orders(client, status=None):
    """查询我的预约记录。
    status 可选值（对应页面 Tab）：
      "toBeUsed"   → 已预约（待使用）—— 默认值，也是取消预约时必须查询的状态
      "completed"  → 已完成
      "cancelled"  → 已取消
      "notArrived" → 未到店
    ⚠️ 必须传 params.status 参数，否则 Kaleido 平台不返回数据（$UserID 上下文限制）。
    """
    status_val = status if status else "toBeUsed"
    resp = client.execute_flow("f5xOvm2XaufsIjIE", params={"status": [status_val]})
    data = get_outputs_data(resp)
    return data if isinstance(data, list) else []


# ──────────────────────────────────────────────────────────
# 打印格式
# ──────────────────────────────────────────────────────────

# 理发师状态英文 → 中文映射
_STATUS_MAP = {
    "hurry":   "今日可约",
    "rest":    "今日休息",
    "busy":    "今日已满",
    "full":    "今日已满",
    "holiday": "节假日休息",
    "off":     "今日休息",
}


def print_barber(i, b):
    # 优先展示 nick_name（昵称，页面显示的名字），其次是 name（真实姓名）
    nick     = b.get("nick_name") or b.get("name") or b.get("barber_name") or "-"
    position = b.get("rank") or b.get("position") or b.get("title") or "-"
    price    = b.get("price") or "-"
    raw_status = b.get("today_status") or b.get("status") or ""
    status   = _STATUS_MAP.get(raw_status, raw_status) or "状态未知"
    bid      = b.get("_id") or "-"
    print(f"  {i+1}. {nick}（{position}）  洗剪吹 ¥{price}  {status}")
    print(f"     ID: {bid}")
    print()


def print_time_slots(slots, barber_name="", date_str=""):
    label = f"理发师:{barber_name}  " if barber_name else ""
    print(f"\n  {label}日期:{date_str}")
    if not slots:
        print("  ⏰ 暂无可预约时间段")
        return
    times = [s.get("time") or s.get("timeSlot") or f"{s.get('startTime','')}-{s.get('endTime','')}" for s in slots]
    print(f"  ✅ 可预约时间段:{', '.join(times)}")
    print(f"     共 {len(slots)} 个时间段可约")


# 服务类型英文 id → 中文
_SERVICE_NAME_MAP = {
    "washCutBlowDry": "洗剪吹",
    "washBlowDry":    "洗吹",
    "washBlowStyle":  "洗吹+造型",
}


def print_order(i, o):
    oid      = o.get("_id") or o.get("orderId") or "-"
    barber   = o.get("nick_name") or o.get("name") or o.get("barber_name") or o.get("barberId") or "-"
    date_s   = fmt_date(o.get("arrivalTime") or o.get("serviceDate") or o.get("date") or o.get("appoint_date"))
    time_s   = o.get("time") or o.get("timeSlot") or (o.get("arrivalTime") or "-")[-5:]
    svc_raw  = o.get("service_name") or o.get("service") or o.get("serviceName") or "-"
    service  = _SERVICE_NAME_MAP.get(svc_raw, svc_raw)
    status   = o.get("order_status") or o.get("status") or "-"
    shop     = o.get("shopName") or "-"
    cancel_d = o.get("cancelDate") or ""
    restrict = o.get("restrictionEndTime") or ""
    print(f"  {i+1}. [{status}] {barber}  {date_s} {time_s}  {service}  {shop}")
    if cancel_d:
        print(f"     取消日期: {cancel_d}" + (f"  限制解除: {restrict}" if restrict else ""))
    print(f"     _id: {oid}")
    print()


# ──────────────────────────────────────────────────────────
# 写操作
# ──────────────────────────────────────────────────────────

# 服务名称 → service_id 映射（根据页面抓包确认）
_SERVICE_ID_MAP = {
    "洗剪吹":   "zXltWg4WRsCQ",
    "洗吹":     "KCjuqrWZfVSO",
    "洗吹+造型": "YXhWJUeYJlCC",
}


def book_barber(client, shop_id, barber_username, barber_name, date_str, time_slot, service, phone, confirm=False):
    """提交预约。barber_username 为理发师的 username 字段（如 ext_mawei），而非数据库 _id。"""
    parts = time_slot.split("-")
    start_time = parts[0].strip() if parts else time_slot
    if len(parts) > 1 and parts[1].strip():
        end_time = parts[1].strip()
    else:
        # 自动计算结束时间（+30分钟），避免服务端 Java 解析空字符串崩溃
        try:
            h, m = map(int, start_time.split(":"))
            total = h * 60 + m + 30
            end_time = f"{total // 60:02d}:{total % 60:02d}"
        except Exception:
            end_time = start_time  # 解析失败时原样传递
    service_id = _SERVICE_ID_MAP.get(service, service)  # 未知服务名时透传原值

    # 同时传两套字段名以兼容服务端：
    # - api-map.md 文档记录：phoneNumber / orderDate / startTime / endTime / service
    # - 抓包确认字段名：phone / date / start_time / end_time / service_id
    # 服务端接受其中一套，两套都传确保兼容
    params = {
        # 文档字段名（api-map.md）
        "phoneNumber": phone,
        "orderDate":   date_str,
        "startTime":   start_time,
        "endTime":     end_time,
        "service":     service_id,
        "shopId":      shop_id,
        "servicesName": service,
        # 抓包字段名（兼容）
        "phone":       phone,
        "date":        date_str,
        "start_time":  start_time,
        "end_time":    end_time,
        "service_id":  service_id,
        # 公共字段
        "barber":      barber_username,   # ⚠️ 必须传 username（如 ext_mawei），不能传数据库 _id
    }
    print(f"\n⚠️  即将提交预约,请确认:")
    print(f"  理发师:{barber_name}（username: {barber_username}）")
    print(f"  日期:{date_str}  时间:{time_slot}")
    print(f"  服务:{service}  手机号:{phone}")
    if not confirm:
        print("\n请使用 --confirm 参数确认提交预约。未传 --confirm 时不会实际提交。")
        return
    resp = client.execute_flow("AvrUvE7LRLI79e59", params=params)
    # 注意：get_outputs 在外层 code=0 时返回 outputs 字典（可能为空 {}），
    # 在外层 code!=0 时返回 None。所以用 `is None` 判断请求级别失败。
    outputs = get_outputs(resp)
    if outputs is None:
        raw_msg = (resp or {}).get("message") or "接口请求错误"
        print(f"❌ 预约失败:{raw_msg}")
        return
    inner_code = outputs.get("code")
    if inner_code == 0 or inner_code is None:
        raw_data = outputs.get("data")
        # data 可能是字符串（如 "成功"）或字典，需做类型检查
        order_data = raw_data if isinstance(raw_data, dict) else {}
        order_id = order_data.get("orderId") or order_data.get("_id") or ""
        if not order_id:
            # 服务端未在响应中直接返回 orderId，立即通过查询接口反查（只查已预约状态）
            try:
                qresp = client.execute_flow("f5xOvm2XaufsIjIE", params={"status": ["toBeUsed"]})
                qdata = get_outputs_data(qresp)
                if isinstance(qdata, list) and qdata:
                    order_id = qdata[0].get("_id") or qdata[0].get("orderId") or ""
            except Exception:
                pass
        if order_id:
            print(f"✅ 预约成功！预约单号:{order_id}")
            print(f"   如需取消，请使用: --cancel --order-id {order_id}")
        else:
            print(f"✅ 预约已成功提交！")
            print(f"[NEED_ORDER_ID] 未能自动获取预约单号。请执行 --my-orders 查询后再用 --cancel --order-id <_id> 取消。")
    else:
        msg = outputs.get("errorDisplayMsg") or f"错误码 {inner_code}"
        if inner_code == 10202:
            # 10202 = 用户已有未完成的预约，不是时段被抢，需要先取消旧预约
            print(f"[HAS_EXISTING_ORDER] {msg}")
        else:
            print(f"❌ 预约失败:{msg}")


def cancel_order(client, order_id):
    """取消预约。
    flowId: wkEL3MLGDNgUT8Ge（由页面抓包确认）。
    ⚠️ 接口参数名是 order_id（不是 orderId），值为查询接口返回的 _id 字段。
    """
    params = {"order_id": order_id}  # ⚠️ 必须用 order_id，不能用 orderId
    resp = client.execute_flow("wkEL3MLGDNgUT8Ge", params=params)
    outputs = get_outputs(resp)
    if outputs is None:
        raw_msg = (resp or {}).get("message") or "接口请求错误"
        print(f"❌ 取消预约失败:{raw_msg}")
        return
    inner_code = outputs.get("code")
    if inner_code == 0 or inner_code is None:
        print(f"✅ 预约 {order_id} 已成功取消。")
    else:
        msg = outputs.get("errorDisplayMsg") or f"错误码 {inner_code}"
        print(f"❌ 取消预约失败:{msg}")


# ──────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="快手理发店查询工具（kaleido-xz 平台）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run --refresh-package ks_aimate scripts/query_barber.py --list-shops                                    # 列出所有职场
  uv run --refresh-package ks_aimate scripts/query_barber.py --list --shop 万家灯火                           # 今日所有理发师状态
  uv run --refresh-package ks_aimate scripts/query_barber.py --date 2026-03-25 --shop 万家灯火               # 3-25日所有可约时间段
  uv run --refresh-package ks_aimate scripts/query_barber.py --date 2026-03-25 --barber 阿荣 --shop 万家灯火 # 3-25阿荣的可约时间段
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders                                     # 我的已预约记录（默认）
  uv run --refresh-package ks_aimate scripts/query_barber.py --my-orders --status completed                # 已完成记录
  uv run --refresh-package ks_aimate scripts/query_barber.py --book --barber 阿荣 --date 2026-03-25 --time 10:00 --service 洗剪吹 --phone 18600008888 --shop 万家灯火 --confirm
""",
    )
    parser.add_argument("--list-shops", action="store_true", help="列出所有可用的理发店职场")
    parser.add_argument("--shop",       help="指定理发店（职场）名称（如果不填,默认选取列表第一个）")
    parser.add_argument("--list",       action="store_true", help="查看所有理发师今日状态")
    parser.add_argument("--date",       help="查询指定日期可约时间段（格式:YYYY-MM-DD 或 MM-DD）")
    parser.add_argument("--barber",     help="指定理发师姓名（配合 --date）")
    parser.add_argument("--my-orders",  action="store_true", dest="my_orders",
                        help="查询我的预约记录")
    parser.add_argument("--status",     default="toBeUsed",
                        choices=["toBeUsed", "completed", "cancelled", "notArrived"],
                        help="查询订单状态（配合 --my-orders）: toBeUsed=已预约(默认) completed=已完成 cancelled=已取消 notArrived=未到店")
    # 写操作
    parser.add_argument("--book",       action="store_true", help="提交预约（写操作）")
    parser.add_argument("--confirm",    action="store_true", help="确认提交预约（与 --book 配合使用，不加则只预览不提交）")
    parser.add_argument("--time",       help="预约时间段（如 10:00-10:30 或 10:00）")
    parser.add_argument("--service",    default="洗剪吹", help="服务项目（默认:洗剪吹）")
    parser.add_argument("--phone",      help="手机号码")
    parser.add_argument("--cancel",     action="store_true", help="取消预约（写操作）")
    parser.add_argument("--order-id",   dest="order_id", help="要取消的预约单号")

    args = parser.parse_args()

    if not any([args.list_shops, args.list, args.date, args.my_orders, args.book, args.cancel]):
        parser.print_help()
        sys.exit(0)

    # ── 写操作参数前置校验（在认证之前,快速失败）──
    if args.book and not all([args.barber, args.date, args.time, args.phone, args.shop]):
        print("❌ 提交预约需要:--barber <姓名> --date <日期> --time <时间> --phone <手机号> --shop <职场>")
        sys.exit(1)
    if args.cancel and not args.order_id:
        print("❌ 请指定要取消的预约单号:--order-id <_id>")
        print("   提示：可先执行 --my-orders 查询已预约订单的 _id")
        sys.exit(1)

    # ── 初始化客户端（自动处理认证）──
    print("🔐 初始化 SSO 认证...")
    try:
        client = BarberShopClient()
    except Exception as e:
        print(f"❌ SSO 认证初始化失败:{e}")
        print("   建议:请确认 kuaishou-sso-login-client skill 已安装,或重启 IDE 后重试。")
        sys.exit(1)
    print("✅ 认证就绪\n")

    # ── WB 员工校验（理发店服务仅对正式员工开放）──
    try:
        account_resp = client.get_account()
        account_data = account_resp.get("data", {})
        username = account_data.get("username", "")
        
        # 外包员工的 username 以 "wb_"、"sf_" 或 "ext_" 开头（这是最可靠的判断依据）
        username_lower = username.lower()
        is_wb_employee = (username_lower.startswith("wb_") or 
                         username_lower.startswith("sf_") or 
                         username_lower.startswith("ext_"))
        
        if is_wb_employee:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("❌ 理发店预约服务仅对快手正式员工开放")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print()
            print("💡 温馨提示:")
            print(f"   - 当前账号 ({username}) 为外包员工账号")
            print("   - 理发店预约功能暂不支持外包员工使用")
            print("   - 如有疑问，请联系 HR 或理发店管理员")
            print()
            sys.exit(1)
    except Exception as e:
        # 账户信息获取失败时给出警告，但不阻断流程（避免因为接口问题导致正式员工无法使用）
        print(f"⚠️  警告:无法验证账户类型:{e}")
        print("   如遇到权限问题，请联系管理员。\n")

    # ── 理发店（职场）解析 ──
    try:
        shops = query_shops(client)
    except Exception as e:
        print(f"❌ 获取职场列表失败:{e}")
        print("   建议:请检查网络连接或重新进行 SSO 认证。")
        sys.exit(1)

    if args.list_shops:
        print("🔍 查询可用理发店（职场）列表...")
        if not shops:
            print("  ❌ 暂无可用职场（接口返回空）。请检查网络/认证状态后重试。")
        else:
            for i, s in enumerate(shops):
                sid = s.get("_id")
                sname = s.get("barber_name") or s.get("name")
                sloc = s.get("location") or ""
                print(f"  {i+1}. {sname} ({sloc})  ID: {sid}")
        return

    # ── 职场 ID 解析 ──
    shop_id = None
    shop_name = None

    if args.shop:
        for s in shops:
            sname = s.get("barber_name") or s.get("name")
            if sname == args.shop:
                shop_id = s.get("_id")
                shop_name = sname
                break
        if not shop_id:
            print(f"❌ 未找到名为 '{args.shop}' 的门店,请通过 --list-shops 确认可用门店。")
            sys.exit(1)
    else:
        if not shops:
            print("❌ 无法获取职场列表（接口返回空），请检查网络/认证状态后重试。")
            print("   或者使用 --shop <职场名称> 手动指定职场（如：--shop 万家灯火）。")
            sys.exit(1)
        s = shops[0]
        shop_id = s.get("_id")
        shop_name = s.get("barber_name") or s.get("name")

    if any([args.list, args.date, args.book]):
        print(f"🏥 当前选定门店:{shop_name}")

    # ── 我的预约 ──
    if args.my_orders:
        status_label = {"toBeUsed": "已预约", "completed": "已完成", "cancelled": "已取消", "notArrived": "未到店"}
        label = status_label.get(args.status, args.status)
        print(f"🔍 查询我的预约记录（{label}）...")
        try:
            orders = query_my_orders(client, status=args.status)
        except Exception as e:
            print(f"❌ 查询预约记录失败:{e}")
            sys.exit(1)
        if not orders:
            print(f"  暂无{label}记录。")
        else:
            print(f"\n共 {len(orders)} 条{label}记录:\n")
            for i, o in enumerate(orders):
                print_order(i, o)
        return

    # ── 取消预约 ──
    if args.cancel:
        cancel_order(client, args.order_id)
        return

    # ── 理发师列表 ──
    if args.list and not args.date:
        print(f"🔍 查询理发师列表（今日状态）...")
        try:
            barbers = query_barbers(client, shop_id)
        except Exception as e:
            print(f"❌ 查询理发师列表失败:{e}")
            sys.exit(1)
        if not barbers:
            print("\n⚠️  理发师列表返回空（该职场今日可能已约满,或接口无排班数据）")
            print("  尝试增加 --date 查询未来可用发型师~")
        else:
            print(f"\n共 {len(barbers)} 位理发师:\n")
            for i, b in enumerate(barbers):
                print_barber(i, b)
        return

    # ── 封禁前置检查（--date 和 --book 均需要）──
    if args.date or args.book:
        ban = check_ban_status(client)
        if ban["banned"]:
            free_time = ban["free_time"]
            if free_time:
                print(f"⛔ [BANNED] 您当前已被限制预约，解封时间：{free_time}，届时可重新预约。")
            else:
                print("⛔ [BANNED] 您当前已被限制预约，请稍后再试。")
            sys.exit(1)

    # ── 提交预约（优先判断,避免 --book --date 误入时段查询分支）──
    if args.book:
        try:
            barbers = query_barbers(client, shop_id)
        except Exception as e:
            print(f"❌ 查询理发师失败:{e}")
            sys.exit(1)
        # ⚠️ barber 接口要求传 username（如 ext_mawei），不能传数据库 _id
        matched = next(
            (b for b in (barbers or [])
             if b.get("barber_name") == args.barber or b.get("nick_name") == args.barber or b.get("name") == args.barber),
            None
        )
        if not matched:
            print(f"❌ 未找到理发师 \"{args.barber}\",请先用 --list 查看可用理发师。")
            sys.exit(1)
        barber_username = matched.get("username") or matched.get("nick_name")
        if not barber_username:
            print(f"❌ 理发师 \"{args.barber}\" 缺少 username 字段,无法提交预约。")
            sys.exit(1)
        date_str = args.date
        if len(date_str) == 5 and "-" in date_str:
            date_str = f"{datetime.date.today().year}-{date_str}"
        book_barber(client, shop_id, barber_username, args.barber, date_str, args.time, args.service, args.phone, confirm=args.confirm)
        return

    # ── 查询特定日期 ──
    if args.date:
        date_str = args.date
        if len(date_str) == 5 and "-" in date_str:       # MM-DD
            date_str = f"{datetime.date.today().year}-{date_str}"
        elif len(date_str) == 4 and date_str.isdigit():  # MMDD
            date_str = f"{datetime.date.today().year}-{date_str[:2]}-{date_str[2:]}"

        try:
            barbers = query_barbers(client, shop_id)
        except Exception as e:
            print(f"❌ 查询理发师失败:{e}")
            sys.exit(1)

        # known_barbers: nick_name → username 映射
        # ⚠️ 查询可约时间段接口（qUOdRHCN3v4QZAEY）必须传 username（如 ext_shipengshen），
        #    传数据库 _id 会返回 10202 错误
        known_barbers = {
            (b.get("nick_name") or b.get("name") or b.get("barber_name")): b.get("username")
            for b in barbers
        } if barbers else {}

        if args.barber:
            barber_nick = args.barber
            barber_username = known_barbers.get(barber_nick)
            print(f"🔍 查询 {barber_nick} 在 {date_str} 的可约时间段...")
            slots, err = query_time_slots(client, date_str, barber_username)
            if err and not slots:
                print(f"\n  {barber_nick}  {date_str}:{err}")
            else:
                print_time_slots(slots, barber_nick, date_str)
        else:
            print(f"🔍 查询 {date_str} 所有理发师的可约时间段...\n")
            if known_barbers:
                found_any = False
                for bnick, busername in known_barbers.items():
                    slots, err = query_time_slots(client, date_str, busername)
                    if err and not slots:
                        pass  # 静默忽略，不向用户显示错误
                    else:
                        print_time_slots(slots, bnick, date_str)
                        found_any = True
                if not found_any:
                    print(f"\n⚠️  {date_str} 所有理发师均无可约时间段。")
            else:
                slots, err = query_time_slots(client, date_str)
                if err and not slots:
                    print(f"\n  {date_str}:{err}")
                    if "营业时间" in err:
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        if date_str > today:
                            print(f"  💡 {date_str} 是未来日期,请在工作日 10:00 后重新查询。")
                else:
                    print_time_slots(slots, date_str=date_str)
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生未预期错误:{e}")
        print("   建议:请检查网络连接和 SSO 认证状态，或联系 skill 维护者。")
        sys.exit(1)
