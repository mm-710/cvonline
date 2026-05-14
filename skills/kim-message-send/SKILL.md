---
name: kim-message-send
description: 使用 message 工具发送 KIM 消息时的参数规范化技能。唤醒场景：发送 KIM 私聊或群聊消息、使用原生 @ 提醒（mentionUsernames/mentionAll）、发送 KIM mixCard 卡片。不唤醒：已经明确知道如何构造参数、非 KIM 平台消息发送。
---

# KIM 消息发送助手

使用此技能让 KIM `message` 工具调用更稳定和可预测。

## 阅读顺序

构建 KIM 工具参数前，**必须先读** `<skill_directory>/reference/target-rules.md`。

以下文件按需阅读：

- 群聊原生 `@` 或 `@all` 提醒: `<skill_directory>/reference/mention-rules.md`
- KIM mixCard 卡片: `<skill_directory>/reference/mixcard-rules.md`
- mixCard 中含图片/视频等资源: `<skill_directory>/reference/media-rules.md` ⚠️ **含 image block 格式硬规则，发送图片前必须阅读**
- 现成的调用模式: `<skill_directory>/reference/examples.md`

## 核心工作流程

1. 区分目标地址和被提醒的人
2. 先确定目标地址
3. 仅对群聊消息添加原生提醒字段
4. 使用原生提醒时保持消息正文为纯文本
5. 发送含图片的 mixCard 时，必须按 `media-rules.md` 中的 image block 格式构建

## 不可违反的规则

- KIM 私聊已知用户名时，使用 `target: "username:<username>"`
- KIM 群聊消息必须使用 `target: "space:<groupId>"`
- 群聊目标和被提醒用户是两个独立的字段
- `mentionUsernames` 仅用于群聊消息
- 使用 `mentionUsernames` 或 `mentionAll` 时，从 `message` 中删除重复的 `@username` 或 `@all` 文本
- 原生提醒优先使用精确的 KIM 用户名如 `alice`，不要用显示名如 `Alice Zhang`
- mixCard 中包含图片/视频等资源时，必须先调用 `kim_media_id` 工具上传获取 `ks://` 媒体 ID，再将 ID 填入 mixCard 字段，禁止直接使用 CDN URL 或本地路径
- **mixCard 中的图片 block 必须使用嵌套 `image` 对象结构**：`imageUrl` 必须放在 `image.imageUrl` 里，不能直接挂在 block 顶层；`width` 和 `height` 不能省略。详见 `media-rules.md`
- 不要编造用户名、用户 ID 或群组 ID
- 除非用户明确要求原始语法，否则不要在 `message` 中手写 KIM 提醒语法

## 发送前检查清单

调用工具前，验证所有这些项：

- `channel` 是 `kim`
- `target` 匹配实际目标类型
- `message` 是纯文本且不包含虚假的重复 `@` 文本
- `mentionUsernames` 仅在群聊消息时包含精确的 KIM 用户名
- `mentionAll` 仅用于群聊消息
- 含图片的 mixCard：每个 image block 都有 `image.imageUrl`（非顶层 `imageUrl`）、`image.width`、`image.height`

## 默认行为

如果用户在群里说"给某人真实的 KIM 提醒"：

- 保持正文为纯文本
- 使用原生提醒字段
- 避免在正文中使用虚假的 `@username` 文本

如果用户只给出显示名而不是精确的 KIM 用户名或群组 ID：

- 如果上下文中已有精确标识符则使用
- 否则一定不要根据中文名猜测username