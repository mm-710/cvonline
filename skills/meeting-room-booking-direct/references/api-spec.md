# Kim 日历会议室 API 接口文档

**BaseURL**: `https://cal.corp.kuaishou.com`  
**认证**: Cookie `X-Auth-Token` 或独立请求头 `X-Auth-Token`

---

## 1. 搜索用户

| 属性 | 值 |
|------|-----|
| Method | `GET` |
| URL | `/api/calendar/search` |

**Query 参数**：

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `content` | String | ✅ | 搜索关键词（用户名/工号） |
| `type` | int | ✅ | 搜索类型：`1`=用户 |

**返回关键字段**：`kwaiUserId`（用于添加参与者）

---

## 2. 获取会议室列表

| 属性 | 值 |
|------|-----|
| Method | `GET` |
| URL | `/api/meetingroom/v2/list` |

**Query 参数**：

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `fromTime` | long (ms) | ✅ | 查询开始时间戳 |
| `toTime` | long (ms) | ✅ | 查询结束时间戳 |

**返回关键字段**：
- `id` = `meetingRoomId`（用于预订）
- `idle: true` 表示该时间段空闲

---

## 3. 创建预约

| 属性 | 值 |
|------|-----|
| Method | `POST` |
| URL | `/api/event/create` |
| Content-Type | `application/json` |

**Request Body**：

```json
{
  "title": "会议主题",
  "startTime": 1776434400000,
  "endTime": 1776438000000,
  "calendarId": "用户个人日历ID",
  "ownerCalendarId": "用户个人日历ID",
  "timezone": "Asia/Shanghai",
  "participant": [
    {"id": "meetingRoomId", "participantUpdateType": "ADD", "type": "MEETING_ROOM"},
    {"id": "kwaiUserId", "participantUpdateType": "ADD", "type": "USER"}
  ],
  "needToNotify": true
}
```

---

## 4. 获取事件详情

| 属性 | 值 |
|------|-----|
| Method | `GET` |
| URL | `/api/v3/event/detail` |

**Query 参数**：`eventId`、`calendarId`

---

## 5. 更新事件（添加参与者）

| 属性 | 值 |
|------|-----|
| Method | `POST` |
| URL | `/api/event/update` |

Request Body 与 create 类似，需包含完整 `participant` 数组。

---

## 6. 查询事件列表

| 属性 | 值 |
|------|-----|
| Method | `GET` |
| URL | `/api/v2/event/list` |

**Query 参数**：`calendarIds`、`fromTime`、`toTime`

---

## 7. 取消预约

| 属性 | 值 |
|------|-----|
| Method | `POST` |
| URL | `/api/event/delete` |

**Request Body**：
```json
{
  "eventId": "事件ID",
  "calendarId": "用户日历ID",
  "repeatedEventUpdateType": "SELF"
}
```

---

## 8. 获取用户日历信息

| 属性 | 值 |
|------|-----|
| Method | `POST` |
| URL | `/api/calendar/v4/list` |

返回 `userInfo.calendarId`

---

## 枚举值速查

### participant.type

| 字符串 | 数字 | 说明 |
|--------|------|------|
| `USER` | 1 | 普通用户 |
| `MEETING_ROOM` | 2 | 会议室 |

### participantUpdateType

| 字符串 | 数字 | 说明 |
|--------|------|------|
| `ADD` | 0 | 添加参与者 |
| `REMOVE` | 1 | 移除参与者 |
