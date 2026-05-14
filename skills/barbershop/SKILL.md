---
name: barbershop
description: 查询快手正式员工内部理发店的理发师可约状态和时间段，支持预约和取消。仅限快手正式员工使用，外包员工暂不支持。当用户说"理发"、"预约理发师"、"理发店"、"X月X日有没有空"、"帮我约个理发"时使用。不负责会议室/停车/食堂预约，不支持外部理发店。
---

# 快手理发店预约 Skill

**⚠️ 使用限制：此服务仅对快手正式员工开放，外包员工暂不支持。**

## ⛔ 严格执行规则

**所有操作必须通过脚本完成，严禁：**
1. 用浏览器工具操作页面
2. 自行构造 HTTP 请求绕过脚本

**标准方式**：`uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py [参数]`

---

## 📋 内部规则（不对用户提及）

**规则 0：查询前必须确认日期是未来工作日**

- **工作日**：周一至周五，10:00-21:00；周末不营业
- **当前是周末**：告知今天不营业，询问是否查下一个工作日
- **用户说「本周X」而那天已过**：先向用户确认是否查「下周X」，不要自行假设
- **脚本返回 `[DATE_PASSED]`**：日期已过，询问改查哪个未来工作日
- **脚本返回 `[ALL_TAKEN]`**：该日全部约满，建议换日期或换理发师
- **⚠️ 预约下周的业务限制**：
  - 每周五 18:00 之后才可以开始预约下周的理发师
  - **当前是周五 18:00 之前**，用户要查询/预约下周时间 → 告知：「下周的预约需要等到今天下午 18:00 之后才能开始哦，请稍后再试」
  - **当前是周一至周四**，用户要查询/预约下周时间 → 告知：「下周的预约需要等到本周五 18:00 之后才能开始哦」
  - 可以建议用户预约本周剩余的工作日

**规则 1：`--date` 返回空（无标记）时**
直接询问用户期望时间，用 `--book` 提交

**规则 2：取消预约——全程通过脚本完成**

1. **先查 _id**：执行 `--my-orders`（默认查已预约状态 `toBeUsed`，只有已预约的才能取消）
2. **再取消**：执行 `--cancel --order-id <_id>`
3. **禁止**：
   - ❌ 使用浏览器操作页面取消
   - ❌ 指定了 --order-id 但未先执行 --my-orders 确认 _id 正确性

**规则 3：收到 `[HAS_EXISTING_ORDER]` 时**

⚠️ `[HAS_EXISTING_ORDER]`（错误码 10202）有两种完全不同的原因，**必须先区分**：

**第一步：立即调用封禁检查**
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --date <任意未来工作日> --barber <任意理发师> --shop <职场>
```
> 脚本内部会先调用封禁接口（flowId: yAxE8XITaNI1Osx8），若封禁则直接输出 `[BANNED]`。

**两种情况的处理方式：**

- **情况 A：输出 `[BANNED]`** → 账号被封禁，不是真的有旧单
  - 告知用户封禁原因和解封时间（`free_time` 字段）
  - **不要尝试取消旧单**（根本不存在旧单）
  - 建议用户等解封后再预约

- **情况 B：未输出 `[BANNED]`** → 确实有未完成的旧预约
  - 告知用户 → 询问是否取消旧单 → 按规则 2 执行取消 → 重新预约

**禁止**：收到 `[HAS_EXISTING_ORDER]` 后不查封禁状态，直接假设"有旧单"去取消

---

## 能力列表

### 0. 查询职场列表
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --list-shops
```

### 1. 查询理发师列表
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --list --shop 万家灯火
```

### 2. 查询某日可预约时段
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --date 2026-04-14 --barber 明泽 --shop 北京元中心
```
查询前先确认日期是未来工作日（见规则 0）。

### 3. 查询我的预约记录
```bash
# 已预约（默认）——取消预约前必须先用这个命令获取 _id
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --my-orders

# 已完成
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --my-orders --status completed

# 已取消
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --my-orders --status cancelled

# 未到店
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --my-orders --status notArrived
```
> 返回字段：`_id`（取消时使用）、理发师、到店时间、门店、状态

### 4. 提交预约
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --book --barber 明泽 --date 2026-04-14 --time 10:30 --service 洗剪吹 --phone 16601134917 --shop 北京元中心 --confirm
```
不加 `--confirm` 先预览，确认后加 `--confirm` 提交。预约成功后脚本会自动输出 `_id`，该 id 用于取消预约。

### 5. 取消预约
```bash
# 第一步：查询已预约订单，获取 _id
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --my-orders

# 第二步：用 _id 取消
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_barber.py --cancel --order-id <_id>
```
> ⚠️ `--my-orders` 默认只查已预约状态（`toBeUsed`），确保取消的是正确的订单。

---

## 参考文档
- `reference/api-map.md` — 接口文档
- `reference/user-journey.md` — 用户操作旅程
