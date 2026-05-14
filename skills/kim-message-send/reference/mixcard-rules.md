# MixCard Rules

This skill stabilizes the `message` tool call. It does not replace a dedicated card-design skill.

If a task needs a complex KIM card layout, this skill can be used together with a card-building skill. This skill is responsible for the final `message` tool args.

## Hard Rules

- Put only the inner mixCard JSON in `kimMixCard`.
- Keep `message` as the plain body text.
- message 字段是卡片外的纯文本兜底内容（通知等场景），设为简短摘要或空字符串 ""
- Do not place outer send envelope fields inside `kimMixCard`.
- Native mentions and source suffixes still belong to the message send flow, not to outer envelope fields inside the card JSON.

## Do Not Put These Fields Inside `kimMixCard`

- `msgType`
- `appKey`
- `groupId`
- `userId`
- `username`
- `target`

## Preferred Shape

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "请查看今天的值班安排。",
  "mentionUsernames": ["alice"],
  "kimMixCard": {
    "header": {
      "title": "值班提醒",
      "style": "blue"
    },
    "blocks": [
      {
        "blockId": "content-1",
        "type": "content",
        "text": {
          "type": "kimMd",
          "content": "## 今日安排\n{{message}}"
        }
      }
    ]
  }
}
```

## 含资源的 mixCard

如果 mixCard 中需要展示图片、视频等媒体资源，必须先通过 `kim_media_id` 工具上传获取 `ks://` 媒体 ID，再将 ID 填入对应字段。

详见 `<skill_directory>/reference/media-rules.md`。
