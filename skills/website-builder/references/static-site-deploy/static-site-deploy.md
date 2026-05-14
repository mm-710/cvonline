---
name: static-site-deploy
description: 使用 npx -y @codeflicker/frontend-cloud-cli@latest 将静态网站部署到 frontend-cloud 平台；本地配置 authtoken、无临时文件打包上传。
---

# 静态网站托管部署（CLI）

使用 **`npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest`** 一键部署静态站点到 frontend-cloud，**不再使用 curl / shell 脚本**。

## 登录说明（重要）

> - **登录**：必须且只能使用快手 SSO（`OAuthProvider.Kuaishou`），禁止邮箱/手机号/第三方 OAuth/匿名登录
> - **禁止通过浏览器访问页面完成登录**：不允许用浏览器打开应用页面、点击登录按钮等方式来获取或刷新登录态，**一律在终端执行 `appwrite-cf login-ks`** 完成鉴权
> - **登录问题统一入口**：无论是数据库操作遇到登录态失效，还是部署流程遇到鉴权问题，**一律使用 `appwrite-cf` 的登录方式**（`appwrite-cf login-ks`），不要单独为部署或其他环节引入额外的登录机制，详见 [appwrite-cf/SKILL.md](../appwrite-cf/SKILL.md)
> - **如果系统中没有安装 `appwrite-cf`**，请先参考 [appwrite-cf/SKILL.md](../appwrite-cf/SKILL.md) 进行安装：
>   ```bash
>   npm install -g @codeflicker/appwrite-cli
>   ```
>   安装后执行 `appwrite-cf login-ks` 完成快手 SSO 登录。

**执行任何操作前，先检查登录态，避免重复登录：**

```bash
appwrite-cf whoami
# 若输出包含 Email，说明已登录，直接跳过登录步骤
# 若报错或无输出，再执行登录
```

快手内部使用 SSO 一键登录，**无需输入账号密码**：

```bash
appwrite-cf login-ks
# 会自动打开浏览器完成快手 SSO 授权，授权后 CLI 自动保存会话
```
---

## 安装与调用

**统一通过 npx 执行最新版本**（无需全局安装）：

```bash
npx -y --registry https://npm.corp.kuaishou.com @codeflicker/frontend-cloud-cli@latest --help
```

下文所有示例均以此方式调用；子命令写在包名之后，例如：

```bash
npx -y --registry https://npm.corp.kuaishou.com @codeflicker/frontend-cloud-cli@latest deploy --help
```

要求：**Node.js ≥ 18**。

---

## 命令一览

以下子命令均配合 **`npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest <子命令>`** 使用。

| 子命令 | 作用 |
|--------|------|
| `deploy` | 打包并上传站点（首次可顺带注册项目） |
| `projects create` | 仅注册项目并生成 `.static-site-deploy.json`，不上传 |
| `projects list` | 列出当前账号下静态站项目 |
| `health` | 检查服务健康接口是否可达 |

---

## 部署流程

### 已有项目（推荐）

当前目录已有 **`.static-site-deploy.json`**（内含 `project_id`）时，只需部署资源：

```bash
# 部署整个目录（默认打包当前工作目录，排除 node_modules、.git、.static-site-deploy.json）
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest deploy

# 只部署某个子目录（例如构建产物 dist）
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest deploy --dir dist

# 指定工作目录（配置与相对路径以此为准）
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest deploy --cwd /path/to/project --dir dist
```

### 首次部署（新项目）

当前目录**没有** `.static-site-deploy.json` 时，需指定项目信息，CLI 会 **register → 写配置 → upload**：

```bash
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest deploy \
  --project-id my-demo-site \
  --project-name "我的站点" \
  --dir ./dist
```

### 只上传单个 HTML 作为首页

将指定文件作为站点根目录的 **`index.html`** 打包上传：

```bash
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest deploy --file ./index.html
```

### 仅创建项目（不部署）

```bash
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest projects create \
  --project-id my-demo-site \
  --project-name "我的站点"
```

### 列出项目

```bash
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest projects list
```

### 健康检查

```bash
npx -y --registry https://npm.corp.kuaishou.com  @codeflicker/frontend-cloud-cli@latest health
```

---

## 核心概念

### 项目 ID 命名规则

与 CLI 校验及后端约定一致：

- **允许**：小写字母（a-z）、数字（0-9）、**连字符（-）**
- **长度**：3～50 字符
- **示例**：`my-demo-site`、`site2024`

### 配置文件 `.static-site-deploy.json`

首次部署或执行 `projects create` 后生成，用于记录 `project_id` 等，后续 **`deploy` 可自动读取**，避免重复注册。

```json
{
  "project_id": "my-demo-site",
  "project_name": "我的站点",
  "domain": "https://my-demo-site.frontend-cloud.corp.kuaishou.com"
}
```

### 访问地址

- **固定地址**：`https://<项目ID>.frontend-cloud.corp.kuaishou.com`（指向最新版本）
- **版本地址**：`https://<项目ID>-<版本ID>.frontend-cloud.corp.kuaishou.com`（永久不变）

---

## 工作原理（与 CLI 一致）
1. 检查当前 **`--cwd`**（默认 `.`）下是否存在 **`.static-site-deploy.json`**。
2. **首次**：Register → 写入配置 → 内存中打 ZIP → Upload。  
   **后续**：跳过 Register，直接打 ZIP → Upload。
3. 打包在**内存**中完成，**不落盘临时 zip**；目录模式会排除 `node_modules`、`.git`、`.static-site-deploy.json` 等，且需包含 **`index.html`**（根路径或可被包含的路径）。

---

## 常见问题

**Q: 部署失败、提示鉴权相关错误？**

- 若 API 基地址不是默认域名，确认 **`FRONTEND_CLOUD_BASE_URL`** 指向正确。
- ⚠️ **如果 `authtoken` 失效或不知道如何获取**，统一使用 `appwrite-cf` 重新登录：
  ```bash
  appwrite-cf login-ks
  ```
  登录成功后，CLI 会刷新凭证，再重新执行部署命令即可。
- ⚠️ **如果系统中没有安装 `appwrite-cf`**，请先参考 [appwrite-cf/SKILL.md](../appwrite-cf/SKILL.md) 安装：
  ```bash
  npm install -g @codeflicker/appwrite-cli
  ```
  安装后执行 `appwrite-cf login-ks` 完成登录。

**Q: 目录部署提示缺少 index.html？**

- 打包内容中必须能包含 **`index.html`**（一般在站点根目录）。

**Q: 如何更新网站？**

- 在已有 `.static-site-deploy.json` 的项目目录执行 **`npx -y @codeflicker/frontend-cloud-cli@latest deploy`**（可加 `--dir` 指向构建输出），会生成新版本。

**Q: 配置文件丢失？**

- 若项目在平台已存在，可手工新建 `.static-site-deploy.json`，填入正确的 **`project_id`**，再执行 **`deploy`**。重复注册可能返回冲突，需与平台侧规则一致。

**Q: 如何确认服务可用？**

- 见上文「健康检查」；线上默认 BASE 时一般无需改 **`FRONTEND_CLOUD_HEALTH_PATH`**。

**提示**：部署请统一使用 **`npx -y @codeflicker/frontend-cloud-cli@latest`**，无需再维护冗长的 shell / curl 脚本。

---

### 失败处理

| 问题 | 排查方向 |
|------|----------|
| **无法访问** | 检查部署命令返回的 URL 是否正确、项目 ID 是否匹配、网络是否连通 |
| **白屏/404** | 检查 `index.html` 是否在构建产物根目录、资源路径是否正确（通常需配置 `base: './'`） |
| **静态资源 404** | 检查构建配置（Vite `base` 选项）、确认 `dist` 目录结构完整 |
| **功能异常** | 检查环境变量配置（如 Appwrite endpoint/projectId）、API 请求是否正确 |
| **登录失败** | 检查 Appwrite 项目配置中的 OAuth 回调 URL 是否包含生产域名 |
| **性能问题** | 检查资源大小（是否需要代码分割、图片压缩）、CDN 是否生效 |

### 对比本地与生产环境

部署后验证时，建议**同时打开本地开发环境**（`http://localhost:5173`）和生产环境，对比以下差异：

- 功能是否一致
- 样式是否一致
- 性能差异（生产环境通常更快，因为有 CDN 加速）

如果生产环境表现与本地不同，优先检查：
1. 环境变量配置（`.env.production` vs `.env.development`）
2. 构建配置（`vite.config.ts` 的 `base` 选项）
3. Appwrite 项目的 OAuth 回调 URL 配置
