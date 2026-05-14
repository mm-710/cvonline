# 万擎图片生成 API 文档

## 接口信息

- **URL**: `POST https://pre-kinsight.test.gifshow.com/eapi/kwaipilot/image/generate`
- **Content-Type**: `application/json`

## 请求头

| Header | 值 |
|--------|---|
| `Content-Type` | `application/json` |
| `kwaipilot-platform` | `myflicker` |
| `kwaipilot-version` | `1.0.0` |

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `chatId` | string | 是 | 会话聊天ID |
| `sessionId` | string | 是 | 会话ID |
| `requestId` | string | 是 | 请求唯一ID |
| `model` | string | 是 | 固定：`Gemini-3.1-Flash-Image-Preview` |
| `prompt` | string | 是 | 生成指令 |
| `images` | array | 否 | 参考图（不传=文生图） |
| `autoSize` | boolean | 否 | 自动尺寸（true时忽略generationConfig） |
| `timeout` | number | 否 | 超时秒数，建议120 |
| `generationConfig` | object | 否 | 图片尺寸配置 |

### generationConfig

```json
{
  "responseModalities": ["IMAGE"],
  "imageConfig": {
    "aspectRatio": "1:1",
    "imageSize": "1K"
  }
}
```

## 枚举值

**model**: `Gemini-3.1-Flash-Image-Preview`

**imageSize**: `512` | `1K` | `2K` | `4K`

**aspectRatio**: `1:1` | `1:4` | `1:8` | `2:3` | `3:2` | `3:4` | `4:1` | `4:3` | `4:5` | `5:4` | `8:1` | `9:16` | `16:9` | `21:9`

## 响应

```json
{
  "images": [{"mimeType": "image/png", "data": "base64..."}],
  "success": true,
  "message": "图像生成成功",
  "usageInfo": {
    "mode": "TEXT_TO_IMAGE",
    "inputImageCount": 0,
    "outputImageCount": 1,
    "sizeMode": "CUSTOM",
    "aspectRatio": "1:1",
    "imageSize": "1K",
    "promptTokenCount": 12,
    "totalTokenCount": 357,
    "finishReason": "STOP"
  }
}
```
