# 快手理发店 API 地图

**平台**：Kaleido 低代码平台  
**App ID**：`jLPKe54PRyOD`  
**Base URL**：`https://kaleido-xz.corp.kuaishou.com/api/runtime/jLPKe54PRyOD/env/online`  
**认证方式**：Kuaishou Corp SSO，由 `kuaishou-sso-login-client` 的 `SmartSSOSession` 自动处理  
**扫描时间**：2026-03-23（浏览器抓包 + DOM 分析）

---

## 审查目标

- 确认 `flowId` 引用与实际接口一致，避免脚本使用错误 flowId 导致静默空数据。
- 确认 `barber_shop_id`、`barber` 等必填参数在脚本中均有传递。
- 确认认证由 `SmartSSOSession` 自动处理 SSO 认证，文档无 Cookie 或登录相关操作描述。

## 常见违规与推荐修复

### 脚本未传 barber_shop_id 导致接口返回空数组

- 违反规范：flowId `JpZolpOqCYXIXRrX` 要求 `barber_shop_id` 必填，缺少时接口静默返回空数组。
- 推荐修复：调用前检查 `shop_id` 是否已解析，为空则先调用 `query_shops` 或报错退出。
- 自动修复：不支持。

### 直接 hardcode shop_id 绕过职场列表

- 违反规范：使用固定 ID 时若职场已变更，会导致查询结果异常。
- 推荐修复：始终通过 `QUERY_SELECT_LIST` 接口动态获取职场列表，为空时显式报错。
- 自动修复：不支持。

### 认证方式配置不当

- 违反规范：应由 `kuaishou-sso-login-client` 的 `SmartSSOSession` 统一处理认证，不得自行维护 Cookie 或 Session。
- 推荐修复：删除 Cookie 字段相关说明，改为调用 `SmartSSOSession` 自动处理。
- 自动修复：不支持。

---

## 通用接口规则

所有业务接口统一入口：
```
POST /executeFlow
Content-Type: application/json
Body: { "flowId": "<flowId>", ...其他业务参数 }
```

---

## 接口列表（GET/POST 全覆盖）

### 1. 账户信息（页面加载时自动触发）
```
GET /account
```
**请求参数**：无（依赖 Cookie）  
**响应关键字段**：
```json
{
  "code": 0,
  "data": {
    "accountInfo": { "accountId": "chenshulin06", "accountSource": "KUAISHOU_EMPLOYEE" },
    "name": "陈姝霖",
    "username": "chenshulin06",
    "number": "80698",
    "email": "chenshulin06@kuaishou.com",
    "department": { "code": "D7462", "name": "综合产品中心" }
  }
}
```

---

### 2. 查询理发店（职场）列表（flowId: default#barber_shop#QUERY_SELECT_LIST）
```json
POST /executeFlow
Body: { "flowId": "default#barber_shop#QUERY_SELECT_LIST", "params": { "pageInfo": { "pageNum": 1, "pageSize": 1000 } } }
```
**功能**：获取系统内所有的理发店（职场）列表，如“万家灯火”、“北京元中心”。
**触发时机**：首页加载时用于构建职场切换菜单（或默认选中）。
**响应关键字段**：
```json
{
  "code": 0,
  "data": {
    "outputs": {
      "data": {
        "documents": [
          { "_id": "tOrAYXsTuiz5", "barber_name": "万家灯火", "location": "B1层" },
          { "_id": "FhlFzy1j2Y9o", "barber_name": "北京元中心", "location": "B1层（东下沉广场进入可直达）" }
        ]
      }
    }
  }
}
```

---

### 3. 查询理发师列表+时间安排+价格（flowId: JpZolpOqCYXIXRrX）
```
POST /executeFlow
Body: { "flowId": "JpZolpOqCYXIXRrX", "params": { "barber_shop_id": "FhlFzy1j2Y9o" } }
```
**功能**：查询**指定理发店下**所有理发师的信息、今日时间安排、洗剪吹服务价格  
**注意**：`barber_shop_id` 参数是**必填项**，如遗漏，接口将返回空数组，而不是报错。
**触发时机**：首页加载或切换职场时  
**响应关键字段**（data.outputs.data 为理发师数组）：
```json
{
  "code": 0,
  "data": {
    "outputs": {
      "code": 0,
      "data": [
        {
          "_id": "...",
          "barber_name": "阿荣",
          "position": "资深理发师",
          "shop_id": "FhlFzy1j2Y9o",
          "price": 30,
          "today_status": "今日已约满"
        }
      ]
    }
  }
}
```
**注意**：今日已约满时 data 可能返回空数组或含状态字段的数组。

---

### 4. 查询用户是否被封禁（flowId: yAxE8XITaNI1Osx8）
```
POST /executeFlow
Body: { "flowId": "yAxE8XITaNI1Osx8" }
```
**功能**：检查当前用户是否因爽约等原因被封禁预约  
**触发时机**：进入预约页时  
**响应关键字段**：
```json
{ "code": 0, "data": { "outputs": { "code": 0, "data": { "banned": false } } } }
```

---

### 5. 查询历史预约记录（flowId: Qhikb5WQ72CASoPW）
```
POST /executeFlow
Body: { "flowId": "Qhikb5WQ72CASoPW" }
```
**功能**：查询当前用户的历史预约记录（含待预约/已完成/已取消）  
**触发时机**：进入预约页 / "我的预约" Tab  
**响应关键字段**：
```json
{
  "code": 0,
  "data": { "outputs": { "code": 0, "data": [] } }
}
```
data 数组每个元素为一条预约记录（字段待进一步确认）。

---

### 6. 查询用户绑定手机号（flowId: x2ZyrY6JVxyH06Mv）
```
POST /executeFlow
Body: { "flowId": "x2ZyrY6JVxyH06Mv" }
```
**功能**：获取用户在平台绑定的手机号（预填在预约表单中）  
**触发时机**：进入预约页时  
**响应关键字段**：
```json
{ "code": 0, "data": { "outputs": { "code": 0, "data": { "phoneNumber": "18600008888" } } } }
```

---

### 7. 查询可预约时间段（flowId: qUOdRHCN3v4QZAEY）

**功能**：查询某理发师在某天可预约的时间段

```json
POST /executeFlow
Body: { 
  "flowId": "qUOdRHCN3v4QZAEY", 
  "params": { 
    "choose_date": "2026-03-27", 
    "barber": "ext_mawei", 
    "duration": 30 
  } 
}
```
**触发时机**：在预约页选择日期时  
**内部执行逻辑**：返回当天所有的时间段，以及它们是否 `reducible`（可约）。若未传 `barber`，则返回 10202 错误。

**响应（正常有时间段）**：
```json
{
  "code": 0,
  "data": {
    "outputs": {
      "code": 0,
      "data": {
        "periods": [
          { "startTime": "10:00", "endTime": "10:30", "time": "10:00-10:30", "reducible": true },
          { "startTime": "10:30", "endTime": "11:00", "time": "10:30-11:00", "reducible": false }
        ]
      }
    }
  }
}
```

**响应（今日已过营业时间/无时间段）**：
```json
{
  "code": 0,
  "data": { "outputs": { "code": 10202, "errorDisplayMsg": "今日已过营业时间段" } }
}
```

### 8. 提交预约（flowId: AvrUvE7LRLI79e59）

**功能**：提交真实的理发预约

```json
POST /executeFlow
Body: {
  "flowId": "AvrUvE7LRLI79e59",
  "params": {
    "phoneNumber": "18600008888",
    "orderDate": "2026-03-27",
    "startTime": "14:00",
    "endTime": "14:30",
    "barber": "ext_mawei",
    "service": "zXltWg4WRsCQ",
    "shopId": "FhlFzy1j2Y9o",
    "servicesName": "洗剪吹"
  }
}
```
**⚠️ 写操作，会实际创建预约记录**  
**响应（成功）**：
```json
{ "code": 0, "data": { "outputs": { "code": 0, "data": { "orderId": "..." } } } }
```
**响应（失败 - 已有预约）**：
```json
{ "code": 0, "data": { "outputs": { "code": 10202, "errorDisplayMsg": "由于您当前存在已预约的服务项目，请在...重新尝试。" } } }
```

---

### 9. 图片资源下载
```
GET /file/download/{blob-id}?alt=image/*
```
**功能**：下载理发师头像等图片资源（skill 不需要实现）

---

## 已知业务错误码

| code | 含义 |
|------|------|
| 0 | 成功 |
| 10202 | 今日已过营业时间段（当天时间已过营业时间，或当日无可用时间段） |

---

## 审查目标

- 确认 `flowId` 引用与实际接口一致，避免脚本使用错误 flowId 导致静默空数据。
- 确认 `barber_shop_id`、`barber` 等必填参数在脚本中均有传递。
- 确认认证由 `SmartSSOSession` 自动处理，文档无 Cookie 或登录相关操作描述。

## 常见违规与推荐修复

### 脚本未传 barber_shop_id 导致接口返回空数组

- 违反规范：flowId `JpZolpOqCYXIXRrX` 要求 `barber_shop_id` 必填，缺少时接口静默返回空数组。
- 推荐修复：调用前检查 `shop_id` 是否已解析，为空则先调用 `query_shops` 或报错退出。
- 自动修复：不支持。

### 直接 hardcode shop_id 绕过职场列表

- 违反规范：使用固定 ID 时若职场已变更，会导致查询结果异常。
- 推荐修复：始终通过 `QUERY_SELECT_LIST` 接口动态获取职场列表，为空时显式报错。
- 自动修复：不支持。

### 认证配置不当

- 违反规范：应由 `kuaishou-sso-login-client` 的 `SmartSSOSession` 统一处理认证。
- 推荐修复：删除 Cookie 字段说明，改为「由 SmartSSOSession 自动处理 SSO 认证」。
- 自动修复：不支持。

---

## 认证方式

认证由 `kuaishou-sso-login-client` skill 的 `SmartSSOSession` 自动处理，脚本调用无需任何额外配置。

- 目标站点需要快手 Corp SSO 认证（CAS 体系）
- 脚本通过 `SANDBOX_UUID` 环境变量定位 `kuaishou-sso-login-client/scripts/sso_session.py`，并使用 `SmartSSOSession` 发起所有请求
- 首次访问或会话过期时，`SmartSSOSession` 会自动处理 SSO 认证，引导完成身份验证
- 若认证失败，脚本会打印建议操作（检查 `kuaishou-sso-login-client` 是否已安装，或重启 IDE）
