# 认证与错误处理

## SSO 认证

- 两个脚本均集成 `SmartSSOSession`，自动从 CodeFlicker Debug Server 获取 token
- **401/403 自动重试**：检测到凭证过期时，脚本自动重建 `SmartSSOSession` 实例重新获取 token，无缝重试一次（共最多 2 次请求），无需人工干预
- 需确保 CodeFlicker 插件在运行中；脚本依赖通过内网 PyPI (`https://pypi.corp.kuaishou.com`) 自动安装

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| SSO Cookie 过期（401/403） | 脚本自动重建 Session 重试一次；若二次仍失败，告知用户确认 CodeFlicker 插件是否运行 |
| 请求超时 | 自动重试一次 |
| `success: false` | 输出 `message` 字段，简化提示词后重试 |
| 图片文件不存在 | 提示用户确认路径 |
| 超过 14 张图片 | 提示用户减少数量 |
| CDN 上传失败 | 降级为 base64 data URL 内嵌输出 |

**AI Agent 兜底话术**（二次重试仍失败时输出给用户）：
```
SSO 认证重试失败，请检查：
1. CodeFlicker 插件是否正在运行
2. 重新在 IDE 中完成 SSO 扫码登录
3. 确认后重新告诉我「生成」，我将重新执行
```
