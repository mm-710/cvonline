# KIM 媒体资源规则

## 为什么需要 ks:// 链

KIM mixCard 中的图片/视频等资源必须使用 `ks://` 链（KIM 媒体 ID），不能直接使用内网 CDN URL 或本地路径：

- 内网 CDN URL 在移动端/外网无法访问
- 本地文件路径在 KIM 客户端无法渲染

## kim_media_id 工具

当 mixCard 中包含图片、视频、音频或文件资源时，使用 `kim_media_id` 工具上传后获取 `ks://` 媒体 ID。

### 工具参数

```json
{
  "action": "upload",
  "media": "<文件路径或 URL>",
  "mediaType": "image"
}
```

- `media`：支持以下格式，**直接传路径，不要 base64 编码**：
  - 本地绝对路径：`/Users/alice/photo.png`
  - 本地相对路径：`./report/chart.png`
  - `~` 路径：`~/Downloads/banner.jpg`
  - `file://` URL：`file:///tmp/image.png`
  - HTTP/HTTPS URL：`https://cdn.example.com/img.jpg`（含内网 CDN）
- `mediaType`：`image`/`video`/`audio`/`file`，可省略（自动检测）
- `accountId`：可省略，使用默认 KIM 账号

### 工具返回

```json
{
  "mediaId": "ks://xxxxxxxxxxxx",
  "mediaType": "image",
  "filename": "photo.png"
}
```

## 标准流程

发送含资源的 mixCard 时，必须按以下顺序操作：

1. **调用 `kim_media_id`** 上传每个资源，获取对应的 `ks://mediaId`
2. **将 `ks://mediaId` 填入 mixCard 结构** 对应字段
3. **调用 `message` 工具** 发送 mixCard

## image block 格式硬规则 ⚠️

MixCard 中的图片 block 必须严格遵循以下结构，**缺少任何字段都会导致图片无法渲染**：

```json
{
  "type": "image",
  "blockId": "image_001",
  "mode": "contain",
  "image": {
    "type": "image",
    "imageUrl": "ks://xxxxxxxxxxxx",
    "width": 800,
    "height": 600
  }
}
```

**每个字段的作用**：

| 字段 | 是否必须 | 说明 |
|------|----------|------|
| `type` | ✅ 必须 | 固定为 `"image"` |
| `blockId` | ✅ 必须 | 整张卡片内唯一标识 |
| `mode` | ✅ 必须 | `"contain"`（完整显示）/ `"cover"`（铺满裁切）/ `"left"`（左对齐） |
| `image` | ✅ 必须 | 嵌套对象，不能省略 |
| `image.type` | ✅ 必须 | 固定为 `"image"` |
| `image.imageUrl` | ✅ 必须 | `ks://` 媒体 ID，不能是 CDN URL 或本地路径 |
| `image.width` | ✅ 必须 | 图片宽度（px），客户端据此计算布局 |
| `image.height` | ✅ 必须 | 图片高度（px），客户端据此计算布局 |

### ❌ 常见错误写法

```json
// 错误：imageUrl 直接挂在 block 顶层，缺少嵌套 image 对象
{
  "type": "image",
  "blockId": "img-1",
  "imageUrl": "ks://abc123456"
}

// 错误：缺少 width/height，客户端无法计算布局
{
  "type": "image",
  "blockId": "img-1",
  "image": {
    "type": "image",
    "imageUrl": "ks://abc123456"
  }
}
```

以上两种写法都会导致图片不渲染（PC 和手机端均显示空白或占位符）。

## elements 中的小图标（非图片 block）

在 `content` block 的 `elements` 数组中使用小图标时，image 元素的结构与图片 block **不同**：

```json
{
  "type": "content",
  "blockId": "content_001",
  "elements": [
    {"type": "plainText", "content": "文本"},
    {"type": "image", "imageUrl": "ks://xxxxxxxxxxxx", "width": 16, "height": 16}
  ]
}
```

注意：`elements` 中的 `image` 是**扁平结构**（`imageUrl` 直接在顶层），与图片 block 的**嵌套结构**（`image.imageUrl`）不同。不要混淆两种写法。

## 禁止行为

- 禁止把内网 CDN URL 直接写入 mixCard 字段
- 禁止把本地文件路径直接写入 mixCard 字段
- 禁止对文件内容做 base64 编码后传给 `kim_media_id`
- 禁止跳过上传步骤直接发送
- 禁止在图片 block 中省略 `image` 嵌套对象
- 禁止在图片 block 中省略 `width`/`height`

## 含图片的 mixCard 示例

```json
// Step 1: 先调用 kim_media_id
{
  "action": "upload",
  "media": "/workspace/charts/weekly.png",
  "mediaType": "image"
}
// 返回: { "mediaId": "ks://abc123456", "mediaType": "image", "filename": "weekly.png" }

// Step 2: 将 mediaId 填入 mixCard，再调用 message
{
  "channel": "kim",
  "target": "space:987654",
  "message": "本周数据报告",
  "kimMixCard": {
    "header": { "title": "周报", "style": "blue" },
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
        "type": "content",
        "blockId": "content_001",
        "text": { "type": "kimMd", "content": "{{message}}" }
      }
    ]
  }
}
```

## 含图片 + @提醒的 mixCard 示例

```json
// Step 1: kim_media_id 上传图片
// Step 2: 发送含图片的群聊卡片并 @某人
{
  "channel": "kim",
  "target": "space:987654",
  "message": "本周数据报告，请 alice 查看。",
  "mentionUsernames": ["alice"],
  "kimMixCard": {
    "header": { "title": "周报", "style": "blue" },
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
        "type": "content",
        "blockId": "content_001",
        "text": { "type": "kimMd", "content": "{{message}}" }
      }
    ]
  }
}
```