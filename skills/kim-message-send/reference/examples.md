# Examples

## Direct Message

User intent: "去 KIM 给 alice 发一句今晚辛苦了。"

```json
{
  "channel": "kim",
  "target": "username:alice",
  "message": "今晚辛苦了。"
}
```

## Group Message With Real Reminder

User intent: "去群里提醒 alice 看下线上告警。"

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "看下线上告警。",
  "mentionUsernames": ["alice"]
}
```

## Group Message With `@all`

User intent: "去群里通知所有人十分钟后发版。"

```json
{
  "channel": "kim",
  "target": "space:987654",
  "message": "十分钟后发版，请提前完成检查。",
  "mentionAll": true
}
```

## Group MixCard With Real Reminder

User intent: "去群里发一个值班卡片，并提醒 alice。"

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
          "content": "**今日安排**\n{{message}}"
        }
      }
    ]
  }
}
```

## Group MixCard With Image + @Reminder

User intent: "去群里发一张数据报告图片，并提醒 alice 查看。"

```json
// Step 1: kim_media_id 上传图片
{
  "action": "upload",
  "media": "/workspace/charts/weekly.png",
  "mediaType": "image"
}
// 返回: { "mediaId": "ks://abc123456", "mediaType": "image" }

// Step 2: 将 mediaId 填入 image block 并发送
{
  "channel": "kim",
  "target": "space:987654",
  "message": "本周数据报告，请 alice 查看。",
  "mentionUsernames": ["alice"],
  "kimMixCard": {
    "header": {
      "title": "周报",
      "style": "blue"
    },
    "blocks": [
      {
        "type": "image",
        "blockId": "image_001",
        "mode": "contain",
        "image": {
          "type": "image",
          "imageUrl": "ks://abc123456",
          "width": 800,
          "height": 600
        }
      },
      {
        "blockId": "content_001",
        "type": "content",
        "text": {
          "type": "kimMd",
          "content": "{{message}}"
        }
      }
    ]
  }
}
```

## Private MixCard With Image

User intent: "给 alice 私聊发一张数据报告图片。"

```json
// Step 1: kim_media_id 上传图片
// Step 2: 发送含图片的私聊卡片
{
  "channel": "kim",
  "target": "username:alice",
  "message": "本周数据报告。",
  "kimMixCard": {
    "header": {
      "title": "周报",
      "style": "green"
    },
    "blocks": [
      {
        "type": "image",
        "blockId": "image_001",
        "mode": "contain",
        "image": {
          "type": "image",
          "imageUrl": "ks://abc123456",
          "width": 800,
          "height": 600
        }
      },
      {
        "blockId": "content_001",
        "type": "content",
        "text": {
          "type": "kimMd",
          "content": "{{message}}"
        }
      }
    ]
  }
}
```