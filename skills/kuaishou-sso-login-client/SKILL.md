---
name: kuaishou-sso-login-client
description: 处理快手内网 SSO 登录认证，当 agent-browser 访问任何 corp.kuaishou.com 域名返回无权限或未登录时自动完成登录流程。以下场景唤醒：访问快手内网服务时提示没有权限或需要登录；通过 agent-browser 访问 corp.kuaishou.com 域名出现认证失败。以下场景不唤醒：用户访问公网地址或非快手内网服务；用户只是询问 SSO 登录的概念或原理。
user_invocable: false
---

# 快手内网 SSO 登录客户端

## 使用方法

当需要登录快手内网服务时，运行以下脚本：

```bash
uv run <skill_directory>/scripts/sso_session.py --target_url <目标URL>
```

**参数说明：**
- `--target_url`: 需要访问的快手内网地址（例如：https://xz.corp.kuaishou.com 或 https://docs.corp.kuaishou.com）

**示例：**
```bash
uv run <skill_directory>/scripts/sso_session.py --target_url https://xz.corp.kuaishou.com/is-intelligent-device
```

脚本会自动处理 SSO 认证流程，必要时会生成二维码供用户扫码登录。

## ⚠️ 使用禁忌（必须遵守）

### 1. 任务完成判断
- `sso_session.py` 输出状态码 **200** 即表示认证并访问成功，**任务到此结束**
- **禁止**在 sso_session.py 成功后额外执行 `mkdir`、创建 workspace 目录或处理路径权限问题
- **禁止**在 sso_session.py 成功后再去读取 `agent-browser/SKILL.md`——本 Skill 已覆盖所有认证逻辑，无需引入 agent-browser

### 2. 输出即完整响应
- `sso_session.py` 的标准输出已是**完整响应内容**，不存在截断
- **禁止**用 `| tail -N`、`| head -N`、`2>&1 | grep ...` 等管道命令对输出进行截取或重试
- **禁止**将输出重定向到文件再读取（如 `> output.html && cat output.html`）
- 如果第一次调用返回了状态码和内容，**不要重复调用** sso_session.py

### 3. JSON API 直接用 sso_session.py，不走 agent-browser
- 访问返回 **JSON 格式**的内网接口时，直接使用 `sso_session.py --target_url <url>`
- **禁止**对 JSON API 使用 `agent-browser open` + DOM 操作（如截图、eval、snapshot）
- `agent-browser` 仅在需要与**可视化页面**交互（点击按钮、填写表单、截图）时使用
