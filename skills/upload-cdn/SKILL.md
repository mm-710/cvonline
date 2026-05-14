---
name: upload-cdn
description: This skill should be used when the user asks to "upload a file", "upload image to CDN", "share a file via link", "get a CDN link for a file", "上传文件", "上传图片", "上传到 CDN", "获取文件链接", "分享文件链接", "把文件传到服务器", or discusses uploading local files to CDN for sharing. Supports images, documents, archives, code files, and any binary files. Returns a CDN URL for sharing. Not for downloading files from CDN or cloud storage operations unrelated to Kuaishou CDN.
---

# Upload-cdn

Upload-cdn 是一个将本地文件上传到 CDN 并获取可分享链接的 skill。支持内网和外网两种上传模式，自动检测文件 MIME 类型。

## 核心功能

- 上传任意本地文件到 CDN
- 自动检测文件类型（MIME type）
- 支持内网（默认）和外网两种上传目标
- 返回可直接访问的 CDN URL

## 使用场景

**触发短语**：
- "帮我上传这个文件"
- "把这张图片上传到 CDN"
- "获取文件的分享链接"
- "upload this file"
- "get CDN link for this file"

## 执行上传

当用户要上传文件时，执行以下脚本：

```bash
# 上传到内网（默认）
bash "<skill_directory>/scripts/upload_file.sh" "/path/to/your/file"

# 上传到外网
bash "<skill_directory>/scripts/upload_file.sh" --public "/path/to/your/file"

# 指定 MIME 类型（可选）
bash "<skill_directory>/scripts/upload_file.sh" --type "image/png" "/path/to/your/file.png"
```

> 注意：`<skill_directory>` 来自 skill 加载时系统上下文中的路径信息。

## 工作流程

### 1. 确认文件路径

- 询问用户要上传哪个文件（如果未指定）
- 确认文件存在且可读
- 展示文件基本信息（名称、大小、类型）

### 2. 选择上传目标

- 默认上传到**内网 CDN**（仅内网可访问）
- 如果用户需要对外分享，使用 `--public` 参数上传到**外网 CDN**

| 类型 | 参数 | 访问范围 | 适用场景 |
|------|------|----------|----------|
| 内网 | 默认 | 仅内网可访问 | 团队内部分享 |
| 外网 | `--public` | 公网可访问 | 对外发布 |

### 3. 执行上传

调用 `upload_file.sh` 脚本执行上传，脚本会：

1. 自动检测文件 MIME 类型
2. 调用上传 API（`https://design-out.staging.kuaishou.com/private-api/common/upload-file`）
3. 返回 CDN URL

### 4. 返回结果

上传成功后，向用户展示：
- CDN URL（可直接访问）
- 文件信息摘要

**示例输出**：
```
File:    screenshot.png
CDN URL: https://cdnfile.corp.kuaishou.com/kc/files/...

Note: This file is on internal CDN (内网). Use --public for external access.

<a href="https://cdnfile.corp.kuaishou.com/kc/files/..." target="_blank">🔗 点击这里访问</a>
```

## 支持的文件类型

脚本会根据文件扩展名自动检测 MIME 类型：

| 类别 | 扩展名 |
|------|--------|
| 图片 | `.png` `.jpg` `.jpeg` `.gif` `.webp` `.svg` `.ico` `.bmp` |
| 文档 | `.pdf` `.doc` `.docx` `.xls` `.xlsx` `.ppt` `.pptx` |
| 压缩包 | `.zip` `.tar` `.gz` `.rar` |
| 文本/代码 | `.txt` `.md` `.json` `.yaml` `.yml` `.xml` `.csv` `.html` `.css` `.js` `.ts` `.py` `.sh` |
| 其他 | 自动标记为 `application/octet-stream` |

如需手动指定 MIME 类型，使用 `--type` 参数。

## 脚本参数

```
bash upload_file.sh [OPTIONS] <file_path>

Options:
  --public            上传到外网 CDN（type=7），默认内网（type=2）
  --type <mime_type>  指定 MIME 类型（默认自动检测）
  -h, --help          显示帮助信息
```

## 错误处理

| 错误 | 说明 | 解决方案 |
|------|------|----------|
| `File not found` | 文件路径不存在 | 检查文件路径是否正确 |
| `Upload failed - ...` | API 返回错误 | 检查网络连接和权限 |
| `Network request failed` | 网络请求失败 | 确认内网连接是否正常 |
| `No URL returned` | 上传成功但无 URL | 可能是服务临时故障 |

## 使用示例

**示例 1：上传图片到内网**

用户：帮我把这张截图上传到 CDN：`~/Desktop/screenshot.png`

```bash
bash "<skill_directory>/scripts/upload_file.sh" ~/Desktop/screenshot.png
```

**示例 2：上传文档到外网**

用户：把这个 PDF 上传到外网 CDN，我要发给外部同学

```bash
bash "<skill_directory>/scripts/upload_file.sh" --public ~/Documents/report.pdf
```

**示例 3：上传 ZIP 包**

用户：帮我上传这个压缩包，获取下载链接

```bash
bash "<skill_directory>/scripts/upload_file.sh" ~/Downloads/package.zip
```
