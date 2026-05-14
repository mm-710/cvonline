# 外卖订餐流程说明

## 审查目标

本文档覆盖快手食堂外卖订餐系统的 API 接口调用规范，供 Agent 脚本开发和审查使用。

- 确认脚本使用正确的接口路径（非废弃版本）
- 确认认证方式使用 `SmartSSOSession`，不手动管理 Cookie
- 确认下单前执行重单检测，取消操作先查询订单再执行
- 确认取餐点余量检查逻辑正确（`remainAmount > 0`）

---

## 整体流程

```
获取可预订日期 → 选择园区/区域 → 查看菜品列表 → 检查是否已下单 → 下单 → 查询订单 → [可选] 取消
```

## API 接口总览

| 步骤 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 1 | GET | `/cafeteria/api/v2/mealReservation/orderMealTimes` | 获取可预订日期列表 |
| 2 | GET | `/cafeteria/api/v2/areaName/mealReservation/gardens` | 获取外卖可用园区+区域（**推荐接口，含 areaNameList**） |
| 3 | GET | `/cafeteria/api/v2/mealReservation/meals` | 获取外卖菜品列表 |
| 4 | POST | `/cafeteria/api/v2/mealReservation/isReOrder` | 检查是否已重复下单（**推荐，替代废弃的 had/order**） |
| 5 | POST | `/cafeteria/api/v2/areaName/mealReservation/order` | **下单（正确接口，含区域参数）** |
| 6 | GET | `/cafeteria/api/v2/order/query/undone` | 查询预定中的未来订单 |
| 6 | GET | `/cafeteria/api/v2/order/query/today` | 查询今日订单列表 |
| 7 | POST | `/cafeteria/api/v2/order/cancel` | 取消订单 |

> ⚠️ **废弃接口**：`GET /cafeteria/api/v2/had/order` 已标注 `@Deprecated`，请改用 `isReOrder`。
> ⚠️ **废弃接口**：`POST /cafeteria/api/v2/mealReservation/order`（不带 areaName 的旧路径）已废弃，请使用 `/areaName/mealReservation/order`。

---

## 接口详情

### 1. 获取可预订日期

```
GET /cafeteria/api/v2/mealReservation/orderMealTimes
```

响应示例：
```json
{
  "code": 0,
  "result": [
    { "dateStr": "2026-04-03", "dayOfWeek": 5 },
    { "dateStr": "2026-04-04", "dayOfWeek": 6 }
  ]
}
```

### 2. 获取外卖园区/区域（推荐）

```
GET /cafeteria/api/v2/areaName/mealReservation/gardens
```

响应示例：
```json
{
  "code": 0,
  "result": [
    {
      "id": "98",
      "name": "北京·元中心",
      "selected": true,
      "areaNameList": [
        { "areaName": "T2", "selected": false },
        { "areaName": "T3", "selected": true }
      ]
    }
  ]
}
```

### 3. 获取外卖菜品列表

```
GET /cafeteria/api/v2/mealReservation/meals?gardenId={gardenId}&areaName={areaName}&date={date}
```

| 参数 | 必填 | 说明 |
|------|------|------|
| gardenId | 是 | 园区ID（来自步骤2） |
| areaName | 否 | 区域名称（来自步骤2的 areaNameList） |
| date | 是 | 日期 YYYY-MM-DD |

响应中每个菜品的关键字段：
```json
{
  "dishId": 719235,
  "name": "犟骨头套餐-犟骨头-T3",
  "mealType": 2,
  "price": 25.0,
  "totalAmount": 20,
  "remainAmount": 17,
  "state": "bookable",   // "1"=已截止，"3"=尚未开放（未到预订时间），其他=可预订
  "description": "可预订",  // state="3" 时此字段包含开放时间，如"18:00 开始"
  "orderDishId": "259511858",
  "list": [
    { "floorId": 440739, "floor": "T3-11F-茶水间", "remainAmount": 10 }
  ]
}
```

### 4. 检查是否已重复下单（推荐）

```
POST /cafeteria/api/v2/mealReservation/isReOrder
Content-Type: application/json
```

请求 Body（List<MealOrderV2Vo>，dishId/floorId 可传 0 用于重单检测）：
```json
[
  { "orderMealDate": "2026-04-07", "dishId": 0, "mealType": 2, "amount": 1, "floorId": 0 }
]
```

响应：`result = true`（已下单）或 `false`（未下单）

> 注：`mealType`：1=早餐，2=美餐午餐，3=美餐晚餐

### 5. 下单（正确接口）

```
POST /cafeteria/api/v2/areaName/mealReservation/order?garden={garden}&areaName={areaName}
Content-Type: application/json
```

| Query 参数 | 必填 | 说明 |
|-----------|------|------|
| garden | 是 | 园区全称，如 `北京·元中心` |
| areaName | 否 | 区域名称，如 `T3` |

请求 Body（**数组格式** `List<MealOrderV2Vo>`）：
```json
[
  {
    "orderMealDate": "2026-04-07",
    "dishId": 719235,
    "mealType": 2,
    "amount": 1,
    "floorId": 440739,
    "floor": "T3-11F-茶水间"
  }
]
```

| Body 字段 | 必填 | 说明 |
|----------|------|------|
| orderMealDate | 是 | 订餐日期 YYYY-MM-DD |
| dishId | 是 | 菜品ID（来自菜品列表） |
| mealType | 是 | 1=早餐, 2=午餐, 3=晚餐 |
| amount | 是 | 数量，通常为 1 |
| floorId | 是 | 取餐点ID（来自菜品列表 `list[].floorId`） |
| floor | 否 | 取餐点描述（来自菜品列表 `list[].floor`，建议传） |

> **注意**：同一天同一餐型只能下单一次，重复下单会失败。

### 6. 查询订单

查询预定中的未来订单（含明天及以后，**用于取消前确认**）：
```
GET /cafeteria/api/v2/order/query/undone?pageNum=1&pageSize=100
```

查询今日订单（含已完成/已取消等历史状态）：
```
GET /cafeteria/api/v2/order/query/today?pageNum=1&pageSize=20
```

> **推荐做法**：取消订单前先同时调用两个接口并合并去重，以完整覆盖今日 + 未来所有有效订单。

### 7. 取消订单

```
POST /cafeteria/api/v2/order/cancel?orderId={orderId}
```

> **注意**：`orderId` 必须是整数类型的 Query 参数，不能放 Body 里。

---

## 预订时间窗口

外卖订餐每天有两段可预订时间，**窗口外无法下单**：

| 窗口 | 时间段 | 可预订日期范围 |
|------|--------|---------------|
| 午间窗口 | 当天 12:00 - 13:30 | 当天晚餐 + 明天及以后 |
| 晚间窗口 | 当天 18:00 - 次日 10:00 | 00:00-10:00 段可订当天午餐/晚餐；18:00-23:59 段只可订明天及以后 |

**菜单发布规则：**
- 每周五 18:00 发布下一整周（周一到周日）菜单
- 周五 18:00 前，最多只能订到本周最后一个工作日
- 周五 18:00 后，可订到下周日

---

## 餐品类型（MealType）说明

| code | 名称 | 说明 |
|------|------|------|
| 1 | BREAKFAST | 早餐 |
| **2** | **MEICAN_LUNCH** | **美餐午餐（外卖订餐主要类型）** |
| **3** | **MEICAN_DINNER** | **美餐晚餐** |
| 7 | HOLIDAY_CANTEEN_BREAKFAST | 假日食堂餐早餐 |
| 8 | HOLIDAY_CANTEEN_LUNCH | 假日食堂餐午餐 |
| 9 | HOLIDAY_CANTEEN_DINNER | 假日食堂餐晚餐 |
| 10 | AFTERNOON_TEA | 下午茶 |

---

## 园区 gardenId 参考

| 园区 | gardenId | 区域示例 |
|------|----------|---------|
| 北京·元中心 | 98 | T2, T3, T10, T11, T12, T13, T1 |
| 北京·万家灯火大厦 | 93 | 万家灯火大厦东侧, 万家灯火大厦西侧 |
| 上海·星联科技园 | 19 | 1号楼, 2号楼 |
| 深圳·百度国际大厦 | 35 | - |
| 杭州·欧美金融中心 | 80 | - |
| 杭州·星耀中心 | 151 | - |

---

## 订单号格式

下单成功后系统生成的订单号格式为 `CARRY_OUT` + 雪花ID，例如：`CARRY_OUT299852201424060417`。
取消订单时使用数字 `orderId`（整数），查询订单明细时可以用 `orderNo`。

---

## 取消时间限制

| 餐型 | 可取消截止时间 |
|------|------|
| 午餐 | 就餐当天 10:00 前 |

> 就餐当天 10:00 前均可预订和取消，10:00 后系统截止。
> 预订时间窗口：12:00-13:30（午间）和 18:00-次日10:00（晚间），窗口外不可预订。

---

## 认证说明

本 Skill 使用 `SmartSSOSession` 自动处理 SSO 认证，**不手动管理 Cookie 或 Session**。

- 脚本通过 uv 内联依赖引入 `ks_aimate` 包，认证由 SmartSSOSession 自动处理
- 所有接口请求统一通过 `SmartSSOSession.request()` 发起，无需手动传 Cookie 字符串

---

## 常见违规与推荐修复

### 使用废弃接口

- 违反规范：`/cafeteria/api/v2/had/order` 和 `/cafeteria/api/v2/mealReservation/order`（不带 areaName）已废弃。
- 推荐修复：改用 `isReOrder` 检查重单，下单使用 `/areaName/mealReservation/order`。
- 自动修复：不支持。

### 手动管理 Cookie 进行认证

- 违反规范：不应在脚本中手动维护 Cookie 字符串或 Session 状态。
- 推荐修复：引入 `SmartSSOSession`，通过 uv 内联依赖导入，使用 `client.request()` 统一发请求。
- 自动修复：不支持。

### 下单前未进行重单检测

- 违反规范：每天同餐型限 1 单，下单前必须调 `isReOrder` 检查。
- 推荐修复：在调下单接口前，先 POST `/cafeteria/api/v2/mealReservation/isReOrder`，`result=true` 时提示用户已有订单。
- 自动修复：不支持。

### 取消订单时直接要求用户提供订单号

- 违反规范：Agent 不得要求用户自己输入订单号。
- 推荐修复：先调 `query/undone` + `query/today` 获取订单列表，从结果中获取 `orderId`，再传给取消接口。
- 自动修复：不支持。

### 下单时选取余量为 0 的楼层

- 违反规范：应过滤 `remainAmount > 0` 的楼层展示给用户。
- 推荐修复：调 `floors` 命令或解析菜品 `list` 字段时，只展示 `remainAmount > 0` 的取餐点。
- 自动修复：不支持。

---

## 注意事项

1. **每天每种餐型限下单一次**：下单前务必调用 `isReOrder` 检查
2. **菜品 state 字段**：
   - `"1"` = 已截止（过了预订截止时间）
   - `"3"` = 尚未开放（还未到预订开放时间），`description` 字段中包含开放时间（如「18:00 开始」）
   - 其他值 = 可预订
3. **预订时间窗口**：只有在 12:00-13:30（午间）或 18:00-次日10:00（晚间）窗口内才可预订
4. **取餐点余量**：下单时选 `remainAmount > 0` 的 `floorId`
5. **取消限制**：只能取消本人订单，就餐当天 10:00 前均可取消
6. **外包员工**：部分外包员工（工时制外包 `isGongShiWaiBao`）没有订餐权限，下单会返回「没有订餐权限」
7. **鉴权**：所有接口均通过 `SmartSSOSession` 自动处理认证，无需手动获取 Cookie
