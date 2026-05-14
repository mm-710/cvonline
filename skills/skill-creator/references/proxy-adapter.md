# Skill 脚本鉴权规范（内联自 skills-proxy-adapter）

为 Skill Python 脚本集成三项标准安全能力。**编写任何调用快手内网接口的脚本时必须遵守。**

## 三项必集成能力

| 能力 | 解决什么问题 | 方案 |
|------|------------|------|
| SSO 登录鉴权 | token 泄露、过期、权限越界 | `SmartSSOSession` 自动管理 |
| 接口安全调用 | API Key / secretKey 写死在代码 | MyFlicker Skills Proxy 代理 |
| 获取用户名 | 各 Skill 自己实现不统一 | `get_username()` 统一获取 |

---

## 通用文件头（所有 Skill 脚本必须包含）

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "requests>=2.31.0,<3",
#   "ks-aimate>=1.0.30",
# ]
#
# [tool.uv.sources]
# "ks-aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///
```

> ⛔ **URL 必须一字不差**：`[[tool.uv.index]]` 的 `url` 必须是：
> ```
> https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/
> ```
> 任何其他写法（如缺少 `/kuaishou/prod/`、缺少末尾 `/`、改用其他路径）都会导致 `ks-aimate` 等内网包找不到而脚本不可用。生成脚本后必须逐字核对此 URL。

---

## 能力一：SSO 登录鉴权（必须）

所有调用快手内网接口的脚本，用 `SmartSSOSession` 替代 `requests.Session`。

### 正确 import（必须逐字使用，不可写错路径）

```python
from ks_aimate.sso_login_client import SmartSSOSession
```

> ⛔ 禁止写成 `from ks_aimate.sso_login_client.session import SmartSSOSession`，路径不同会导致 ImportError。

### 推荐封装模式（参考 cal_client.py）

将 `SmartSSOSession` 封装进 Client 类，统一处理 `raise_for_status()` 和业务码校验：

```python
from ks_aimate.sso_login_client import SmartSSOSession

class MyClient:
    def __init__(self):
        self.session = SmartSSOSession()

    def _get(self, url: str, params=None) -> dict:
        resp = self.session.request("GET", url, params=params)
        resp.raise_for_status()
        data = resp.json()
        # 根据实际 API 的业务码字段调整（常见：code、status、result）
        if data.get("code") not in (0, None) and data.get("status") not in (0, None):
            raise RuntimeError(f"API 错误: {data}")
        return data

    def _post(self, url: str, body=None) -> dict:
        resp = self.session.request("POST", url, json=body)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") not in (0, None) and data.get("status") not in (0, None):
            raise RuntimeError(f"API 错误: {data}")
        return data
```

### 调用方式（必须用 `.request()`，不可用 `.get()` / `.post()` 等简写）

```python
# GET 请求：params 传查询参数
resp = self.session.request("GET", "https://example.corp.kuaishou.com/api/list", params={"page": 1})

# POST 请求：json 传请求体
resp = self.session.request("POST", "https://example.corp.kuaishou.com/api/create", json={"name": "test"})

# PUT 请求：json 传更新内容
resp = self.session.request("PUT", "https://example.corp.kuaishou.com/api/item/123", json={"name": "updated"})

# DELETE 请求：params 传资源标识（或 json 传 body，视接口而定）
resp = self.session.request("DELETE", "https://example.corp.kuaishou.com/api/item/123", params={"id": "123"})

# POST 请求：上传文件（multipart）
resp = self.session.request("POST", url, files={"file": ("name.zip", data, "application/zip")}, data={"key": "val"})
```

> ⛔ **严禁**：
> - 使用 `session.get()` / `session.post()` / `session.put()` / `session.delete()` 等简写方法 —— `SmartSSOSession` 只支持 `.request()` 方法
> - 手动读取 token、硬编码 Cookie、自己实现 SSO 逻辑
> - 读取 `~/.openclaw/kim-paired.json` 等本地配对文件
> - 将 `secretKey`/`accessToken` 写入代码（包括注释）

`SmartSSOSession` 会自动处理 token 获取、刷新、浏览器扫码重登录。

---

## 能力二：接口安全调用（有 API Key 或 OpenAPI 时必须）

**接口类型判断：**

| 接口类型 | 示例 | 鉴权模式 |
|---------|------|---------|
| 快手内部 OpenAPI Gateway | `is-gateway.corp.kuaishou.com` | 模式 B：Proxy openapi_token |
| 第三方公网 API（有固定 API Key） | Tavily、OpenAI | 模式 A：Proxy static |
| 快手内网普通接口（无 API Key） | `*.corp.kuaishou.com` 非 OpenAPI | 仅 SmartSSOSession，不走 Proxy |

**模式 A：静态 API Key（第三方服务）**

```python
from ks_aimate.sso_login_client.session import SmartSSOSession

client = SmartSSOSession()
resp = client.request(
    "POST",
    "https://myflicker.corp.kuaishou.com/api/v1/skills/exec/proxy",
    json={
        "url": "https://api.tavily.com/search",
        "method": "POST",
        "body": {"query": query, "max_results": 5},
        # Authorization 由 Proxy 自动注入
    }
)
```

**模式 B：OpenAPI Token（快手内部 OpenAPI Gateway）**

```python
from ks_aimate.sso_login_client.session import SmartSSOSession

APP_KEY = "xxx-xxx-xxx-xxxx"  # 只保留 appKey，secretKey 由管理员托管

client = SmartSSOSession()
resp = client.request(
    "POST",
    "https://myflicker.corp.kuaishou.com/api/v1/skills/exec/proxy",
    json={
        "url": "https://is-gateway.corp.kuaishou.com/openapi/xxx/method",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "ks-skill-proxy-apikey": APP_KEY,  # 告诉 Proxy 用哪个 appKey 换 token
        },
        "body": payload,
        # Authorization Bearer Token 由 Proxy 自动换取并注入
    }
)
```

---

## 能力三：统一获取用户名（需要时）

```python
from ks_aimate.wanqing_token_username import get_username

username = get_username()  # 自动从 MyFlicker/万擎客户端环境读取
```

> ⛔ **禁止**：自行读取 token 解析、读取本地配对文件、要求用户手动传入 username 参数。

---

## 生成脚本后的检查清单

- [ ] 文件头包含 `uv run --script` 格式依赖声明
- [ ] 依赖列表包含 `ks-aimate` 及 kuaishou pypi 源配置
- [ ] `[[tool.uv.index]]` 的 `url` 字段**逐字核对**为 `https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/`（错误的 URL 会导致内网包找不到，脚本完全不可用）
- [ ] `SmartSSOSession` import 路径正确：`from ks_aimate.sso_login_client import SmartSSOSession`（不是 `.sso_login_client.session`）
- [ ] 所有 HTTP 请求使用 `session.request("GET/POST/PUT/DELETE", url, ...)` 统一调用方式，**禁止使用** `session.get()` / `session.post()` / `session.put()` / `session.delete()` 等简写方法
- [ ] 所有内网请求通过 `SmartSSOSession`，无裸 `requests`
- [ ] 代码中绝对不含 `secretKey`、Bearer token、Cookie 硬编码（包括注释）
- [ ] 调用 OpenAPI Gateway 或第三方 API 时均通过 Proxy，不自己实现换 token 逻辑
- [ ] 用户名统一使用 `get_username()`
- [ ] 脚本文件名使用下划线命名（如 `my_script.py`）
- [ ] 在 SKILL.md 中用 `<skill_directory>` 占位符引用脚本路径
- [ ] **SKILL.md 中不出现「本 skill 依赖 `kuaishou-sso-login-client`」之类的前置条件说明**——`SmartSSOSession` 已内嵌 SSO 逻辑，对用户完全透明，不需要用户感知或手动安装该依赖

---

## 常见问题

**Q：接口文档里有 secretKey 换 token 说明，要在脚本里实现吗？**
不要。secretKey 由管理员托管在 Proxy，脚本只传 `appKey`，Proxy 自动完成换 token。

**Q：Proxy 规则还没配置，可以先写代码吗？**
可以写代码，但需提醒用户找 @lixinjian 将对应的 AppKey 注册到 Proxy。

**Q：如何区分 Proxy 两种模式？**
- URL 是 `is-gateway.corp.kuaishou.com` → 模式 B
- URL 是第三方公网 API 且有固定 Key → 模式 A
- URL 是 `*.corp.kuaishou.com` 普通内网接口，无 API Key → 只用 SmartSSOSession

**Q：脚本用了 SmartSSOSession，SKILL.md 里需要说明「依赖 kuaishou-sso-login-client」吗？**
不需要。`SmartSSOSession` 已将 SSO 能力内嵌进脚本，用户不需要感知底层依赖。在 SKILL.md 里写这段「前置条件」只会造成用户困惑，应当删除。
