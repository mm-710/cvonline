---
name: scheduled-kim-message
description: 创建定时任务，向用户发送 Kim 消息提醒或定时播报结果。以下场景唤醒：用户需要定时提醒、定时播报、或定时执行任务并推送结果时；用户说「X 分钟后提醒我」「每天 9 点发给我」「定时推送」时唤醒。以下场景不唤醒：用户只是在询问定时任务平台的管理操作（应使用 scheduled-tasks skill）；用户想配置 CodeFlicker Hooks 或 scheduled-tasks 功能；任务不需要通过 Kim 推送结果。
---

# Scheduled Kim Message

创建定时任务，当用户需要定时提醒、定时播报、或定时执行任务并推送结果时使用此 skill。包含一次性提醒和循环任务的完整参数结构。
使用你可用的定时调度工具完成，`action="add"`，参数结构见下方示例。
## ⚠️ 强制要求

**delivery 格式必须为**：

```json
{
  "delivery": {
    "mode": "announce",
    "channel": "kim",
    "to": "username:${username}"
  }
}
```

| 字段 | 要求 |
|------|------|
| `channel` | **必须** 是 `"kim"` |
| `to` | **必须** 是 `"username:${username}"` 格式 |

其中 `${username}` 从 system prompt 中读取，是当前用户信息节点中的 username 属性。如果上下文中没有 username 属性，不允许瞎编，可以从 `/data/aime/$SANDBOX_UUID/user.txt` 中读取，其中 `SANDBOX_UUID` 是环境变量，需要读取环境变量后替换。

---

## ⏰ 一次性 vs 循环

| 用户说的 | schedule | 说明 |
|----------|----------|------|
| "X 分钟后提醒" | `{"kind":"at","at":"<ISO-8601>"}` | 一次性，加 `deleteAfterRun: true` |
| "每天 9 点提醒" | `{"kind":"cron","expr":"0 9 * * *","tz":"Asia/Shanghai"}` | 循环 |
| "每 30 分钟" | `{"kind":"every","everyMs":1800000}` | 循环 |

---

## 📬 收件人（delivery.to）

**固定格式**：`"username:${username}"`

其中 `${username}` 从 system prompt 的当前用户信息的 username 属性中读取：


**示例**：
- 如果 `username=wanger` → `delivery.to = "username:wanger"`
- 如果 `username=zhangsan` → `delivery.to = "username:zhangsan"`

---

## 📝 示例 1：一次性提醒

```json
{
  "action": "add",
  "job": {
    "name": "发版提醒",
    "deleteAfterRun": true,
    "sessionTarget": "isolated",
    "schedule": {
      "kind": "at",
      "at": "2026-03-23T20:30:00+08:00"
    },
    "payload": {
      "kind": "agentTurn",
      "message": "提醒：该准备发版内容了",
      "timeoutSeconds": 60
    },
    "delivery": {
      "mode": "announce",
      "channel": "kim",
      "to": "username:wanger"
    }
  }
}
```

---

## 📝 示例 2：循环任务

```json
{
  "action": "add",
  "job": {
    "name": "早安激励",
    "sessionTarget": "isolated",
    "schedule": {
      "kind": "cron",
      "expr": "0 9 * * *",
      "tz": "Asia/Shanghai"
    },
    "payload": {
      "kind": "agentTurn",
      "message": "写一句今日激励语，简短有力。",
      "timeoutSeconds": 60
    },
    "delivery": {
      "mode": "announce",
      "channel": "kim",
      "to": "username:zhangsan"
    }
  }
}
```

---

## 🔧 管理命令

```json
// 列出所有任务
{ "action": "list" }

// 立即运行任务
{ "action": "run", "jobId": "<id>" }

// 更新任务
{ "action": "update", "jobId": "<id>", "patch": { "schedule": {...} } }

// 删除任务
{ "action": "remove", "jobId": "<id>" }
```

---

## 📊 参数速查表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | ✅ | 固定为 `"add"` |
| `job.name` | string | ✅ | 任务名称 |
| `job.sessionTarget` | string | ✅ | 推荐 `"isolated"` |
| `job.schedule.kind` | string | ✅ | `"at"` / `"cron"` / `"every"` |
| `job.payload.kind` | string | ✅ | 推荐 `"agentTurn"` |
| `job.payload.message` | string | ✅ | 推送消息内容 |
| `job.delivery.mode` | string | ✅ | 固定为 `"announce"` |
| `job.delivery.channel` | string | ✅ | 固定为 `"kim"` |
| `job.delivery.to` | string | ✅ | 固定为 `"username:${username}"` |
| `job.deleteAfterRun` | boolean | ❌ | 一次性任务建议 `true` |

---
