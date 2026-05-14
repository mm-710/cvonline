---
name: cafeteria-takeout
description: 快手食堂外卖订餐助手（第三方盒饭外送到楼层餐柜）。当用户明确要「订外卖」「预约外卖」「帮我订明天的午餐」「下单午餐」「查外卖订单」「取消外卖订单」等涉及外卖下单、查单、取消的操作时触发。注意：本 Skill 是独立的外卖订餐系统，菜品与食堂堂食完全不同；不支持查询食堂今天有什么菜、查看堂食菜单、查食堂营业时间等堂食相关查询，这类需求请使用 `kuaishou-cafeteria-recommendation` Skill。
---

# 外卖订餐 Skill

预订公司食堂外卖盒饭（第三方商家配送），送到指定楼层餐柜，用餐当天自取。**支持下单、查单、取消。**

---

## ❗ 认证说明

- 脚本通过 uv 内联依赖引入 `ks_aimate`
- 认证由 `SmartSSOSession` 自动处理，无需手动安装额外 skill、维护 Cookie 或 Session

---

## 业务规则

| 规则 | 说明 |
|------|------|
| 预订时间窗口 | 每天两段：12:00-13:30（午间，可订当天晚餐+以后）和 18:00-次日10:00（晚间，可订明天及以后） |
| 菜单发布 | 每周五 18:00 发布下一整周菜单；周五 18:00 前最多订到本周日 |
| 每日限单 | 每天同餐型限 1 单 |
| 取消时限 | 就餐当天 10:00 前均可取消 |

> 详细时间窗口判断逻辑、菜品 state 处理、下单失败处理见 [reference/agent-rules.md](reference/agent-rules.md)

---

## 订餐流程

用户说「帮我订饭」时，**按步骤引导，不要跳步直接下单**。

### Step 0：检查时间窗口
判断当前时间是否在预订窗口内，窗口外直接告知用户，**不继续后续步骤，也不要先收集园区、区域、日期、餐型等信息**。
详见 [reference/agent-rules.md](reference/agent-rules.md)。

### Step 1：查默认取餐位置
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py default-location
```

**重要规则：**
- 如果用户对话中**已明确说明园区**（如「在万家灯火订」「元中心的外卖」），**跳过历史位置确认，直接使用用户指定的园区**，不要再问「还是在 XX 取餐吗？」
- 如果用户**没有提供明确地址信息**，或根据用户表达**无法可靠识别园区/区域**，**先查询默认取餐位置**，不要直接追问用户
- 查询到默认位置后，优先用确认式话术继续（如「检测到你上次在 XX 园区 · XX 区域取餐，这次还是这里吗？」）
- **地点一旦进入确认环节，应尽量一次确认到“园区 + 区域”两个层级**，不要只确认园区，后面再补问区域
- 如果用户只说了园区，而该园区下有多个区域，**必须在同一轮直接列出全部区域让用户选择**
- 只有在**查不到默认位置**，或默认位置仍不足以确定具体区域时，才继续询问用户园区/区域
- 当所选园区下有**多个 area（区域）**时（如万家灯火有东侧/西侧），**必须列出全部区域让用户明确选择**，不得自动默认其中一个

**推荐问法：**
- 默认位置完整："检测到你上次在 北京·元中心 · T3 取餐，这次还是这里吗？"
- 只明确了园区、多区域待确认："北京·万家灯火大厦有东侧、西侧两个取餐区域，你这次选哪一个？"
- 园区和区域都不明确："请告诉我你这次订餐的园区和区域；如果你不确定，我也可以先按你上次的取餐位置帮你确认。"

### Step 2：收集日期和餐型

**前置要求：先确认地点到“园区 + 区域”。** 如果地点还不完整，不要先进入日期和餐型确认。

午间窗口默认推荐今天晚餐；晚间/跨天窗口默认推荐明天午餐。

> **餐型参数对照**（调命令时必须用数字，不得用名称猜测）：
> - 午餐 → `--meal_type 2`
> - 晚餐 → `--meal_type 3`
> - 早餐 → `--meal_type 1`（外卖订餐极少涉及）

### Step 3：展示菜单
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py list \
  --garden_name "元中心" --area_name "T3" \
  --date "2026-04-08" --meal_type 2
```
> ⚠️ 午餐用 `--meal_type 2`，晚餐用 `--meal_type 3`，不要混淆。

按商家分组展示菜品名、价格、余量，让用户选择。

### Step 4：查询取餐楼层
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py floors \
  --garden_name "元中心" --area_name "T3" \
  --date "2026-04-08" --dish_id <菜品标识> --meal_type 2
```

### Step 5：确认单
展示确认单（菜品、价格、取餐点、日期），等用户明确确认后再下单。

### Step 6：下单
```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py order \
  --garden_name "元中心" --area_name "T3" \
  --date "2026-04-08" --dish_id <菜品标识> --floor_id <楼层标识> --meal_type 2
```

---

## 取消订单

**必须先查询订单，不得要求用户自己提供订单号。**

```bash
# Step 1：查询订单
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py query

# Step 2：取消
uv run --refresh-package ks_aimate <skill_directory>/scripts/meal_order.py cancel --order_id <从查询结果获取>
```

---

## 命令速查

| 命令 | 用途 |
|------|------|
| `default-location` | 查用户上次取餐位置 |
| `list` | 查可预订菜品 |
| `floors` | 查指定菜品取餐楼层 |
| `order` | 下单 |
| `query` | 查我的订单 |
| `cancel` | 取消订单 |

---

## 支持文件

- `scripts/meal_order.py`
- `reference/order-guide.md` — API 接口详情
- `reference/agent-rules.md` — Agent 行为细则（时间窗口/state/失败处理/对话规范）
