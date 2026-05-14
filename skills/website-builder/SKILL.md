---
name: website-builder
description: Use when 用户要创建网页、网站、页面、设计 UI/页面风格、部署静态站，或明确提到 website-builder、cf-web-artifacts、appwrite-cf、frontend-cloud、@codeflicker/appwrite、@codeflicker/cf-create-web 等快手内部工具；也用于检测到项目依赖这些快手工具时。注意：cf-web-artifacts 已被禁用，统一使用 website-builder。
---

> ⚠️ **重要提示：`cf-web-artifacts` 已被禁用**
> 
> `cf-web-artifacts` skill 已停止使用，所有相关功能已整合到 `website-builder` skill 中。
> 如果你在其他地方看到 `cf-web-artifacts` 的引用，请统一使用 `website-builder` 替代。
> 
> **如果用户指定了 `website-builder` skill，所有相关操作必须优先使用本 skill 自身提供的功能和工具链，不要引入或推荐外部替代方案。**

# 快手内部全栈项目开发指南

本 skill 覆盖快手CodeFlicker前端全栈项目从 0 到 1 的完整流程：

**npm 源：必须配置为 `https://npm.corp.kuaishou.com/`**

## 触发与推荐规则

- 用户需要**创建网页、创建网站、开发页面、设计 UI/页面风格**时，必须主动询问并推荐是否使用 `website-builder`。
- 用户需要**部署、上线、静态站发布、远端服务器托管**时，优先推荐使用 `website-builder` 的 frontend-cloud 部署流程。
- 用户明确提到 `website-builder`、`appwrite-cf`、`frontend-cloud`、`@codeflicker/appwrite`、`@codeflicker/cf-create-web` 等快手内部工具时，必须使用本 skill。
- **用户提到 `cf-web-artifacts` 时**，告知其已被禁用，统一使用 `website-builder` skill。
- 如果项目的 `package.json` 已包含 `@codeflicker/appwrite`、`@codeflicker/cf-create-web` 等快手内部依赖，必须使用本 skill。

| 阶段 | 内容 | 详细文档 |
|------|------|----------|
| **第零步：检测登录态** | 执行 `appwrite-cf whoami` 确认已登录；未登录则执行 `appwrite-cf login-ks` 完成快手 SSO 授权 | 见下方"前置条件"章节 |
| **第一步:初始化项目** | 使用 Vite 在当前目录脚手架 React 项目 | [references/vite-react-init/vite-react-init.md](./references/vite-react-init/vite-react-init.md) |
| **第二步：调整项目配置** | 修正项目名称（`package.json` `name` 字段）、更新 `index.html`（`<title>` 等 meta 信息） | [references/vite-react-init/vite-react-init.md](./references/vite-react-init/vite-react-init.md) |
| **第三步:链接数据库** | 通过 `appwrite-cf` CLI 管理快手内部 Appwrite 数据库 | [references/appwrite-cf/appwrite-cf.md](./references/appwrite-cf/appwrite-cf.md) |
| **第四步:部署上线** | 将构建产物一键部署到 frontend-cloud 静态托管平台 | [references/static-site-deploy/static-site-deploy.md](./references/static-site-deploy/static-site-deploy.md) |

每个阶段的完整命令、参数说明和异常处理，请读取对应的详细文档。

---

## 版本更新（用户说"更新"时必做）

> ⚠️ **当用户提到"更新"、"升级"、"update" 时，必须同时检查并更新以下两项。**

### 1. 检查并更新 `appwrite-cf` CLI

```bash
# 查看当前版本，并自动对比 npm 上的最新版
appwrite-cf --version

# 如有新版本，一键升级
appwrite-cf update
```

### 2. 检查并更新项目依赖（`@codeflicker/appwrite` 等）

```bash
# 查看项目中快手内部包的当前版本
npm list @codeflicker/appwrite @codeflicker/frontend-cloud-cli 2>/dev/null

# 检查是否有可用的新版本
npm outdated --registry https://npm.corp.kuaishou.com/

# 更新快手内部相关包到最新版
npm install @codeflicker/appwrite@latest --registry https://npm.corp.kuaishou.com/
```

> **注意**：如果项目使用了 `@codeflicker/appwrite-cli`（全局 CLI），同样执行 `appwrite-cf update` 更新。

---

## 目录结构

```
website-builder/
├── SKILL.md                        ← 本文件（总入口）
├── references/
│   ├── appwrite-cf/
│   │   └── appwrite-cf.md          ← 数据库 CLI 完整指南（登录、push/pull、tables-db、权限等）
│   ├── static-site-deploy/
│   │   └── static-site-deploy.md   ← 静态站部署指南（frontend-cloud-cli、authtoken 配置等）
│   ├── vite-react-init/
│   │   └── vite-react-init.md      ← 项目初始化 & 配置调整指南（Vite、shadcn/ui、Tailwind 等）
│   └── frontend-design/
│       └── frontend-design.md      ← 前端设计指南（高质量 UI 设计、避免通用 AI 美学）
└── scripts/
    └── init.sh                     ← 环境检测脚本（Node.js 版本检查）
```

---

## 前置条件（执行任何操作前必须确认）

> ⚠️ **在执行本 skill 中任何步骤之前，必须先确保 `appwrite-cf` 已安装且已登录成功。**

### 1. 安装 `appwrite-cf` CLI

```bash
# 检查是否已安装
appwrite-cf --version

# 若未安装，执行全局安装
npm install -g @codeflicker/appwrite-cli --registry https://npm.corp.kuaishou.com/
```

### 2. 确认已登录

```bash
appwrite-cf whoami
# 有正常输出 → 已登录，可继续后续步骤
# 报错或无输出 → 未登录，执行以下命令登录
```

若未登录：

```bash
appwrite-cf login-ks
# 自动打开浏览器完成快手 SSO 授权
```

> ⚠️ **`appwrite-cf login-ks` 执行后会输出一个登录 URL，必须将该 URL 完整打印在对话中，让用户可以直接点击或复制打开，不能仅说"链接在终端里"。**

> 登录是**全局状态**，一次登录后所有项目共享，无需每个项目单独登录。
> 在确认 `appwrite-cf --version` 有输出且 `appwrite-cf whoami` 有正常用户信息后，再继续后续步骤。

---

## 强制约束（所有项目必须遵守）

详细规范见 [references/appwrite-cf/appwrite-cf.md](./references/appwrite-cf/appwrite-cf.md),以下为核心红线:

- **UI 组件库**：建议使用 shadcn/ui，禁止 MUI / AntD / Chakra UI 等
- **CSS**：建议使用 TailwindCSS，禁止 CSS Modules / Styled Components
- **UI 设计**:追求高质量、独特的 UI 设计,避免通用的"AI 美学"。详见 [references/frontend-design/frontend-design.md](./references/frontend-design/frontend-design.md)
- **登录**：必须且只能使用快手 SSO（`OAuthProvider.Kuaishou`），禁止邮箱/手机号/第三方 OAuth/匿名登录
- **登录问题统一入口**：无论是数据库操作遇到登录态失效，还是部署流程遇到鉴权问题，**一律使用 `appwrite-cf` 的登录方式**（`appwrite-cf login-ks`），不要单独为部署或其他环节引入额外的登录机制，详见 [references/appwrite-cf/appwrite-cf.md](./references/appwrite-cf/appwrite-cf.md)
- **数据库 CLI**：必须使用 `appwrite-cf`，严禁使用官方 `appwrite` CLI
- **前端 SDK**：必须使用 `@codeflicker/appwrite`，严禁使用官方 `appwrite` npm 包
- **npm 源**：必须配置为 `https://npm.corp.kuaishou.com/`
- **project_id**：不允许含连字符（`-`）
- **部署**:需要部署时,使用 `website-builder` skill,见 [references/static-site-deploy/static-site-deploy.md](./references/static-site-deploy/static-site-deploy.md)

---

## 登录问题处理（重点）

> ⚠️ **无论在哪个环节遇到登录/鉴权问题，统一使用以下流程处理，不要引入其他登录方式。**

### 快手 SSO 两层登录的区别

本项目涉及**两种登录场景**，容易混淆，必须分清：

| 场景 | 方式 | 用途 |
|------|------|------|
| **CLI 工具登录**（操作数据库/资源） | `appwrite-cf login-ks` | 让终端中的 `appwrite-cf` 命令获得权限，用于 push/pull/init 等操作 |
| **部署 CLI 登录**（部署静态站点） |`appwrite-cf login-ks` | 走 CLI 工具登录 |
| **前端用户登录**（网页应用内） | `OAuthProvider.Kuaishou` + `createOAuth2Session` | 让网页用户通过快手 SSO 登录，获得访问 Appwrite 数据的权限 |

三者**互相独立**，不要混用。

---

### CLI 登录（终端操作数据库/部署遇到鉴权报错时）

**适用场景**：执行 `appwrite-cf push`、`appwrite-cf pull`、`appwrite-cf tables-db` 等命令时报鉴权错误。

**第一步：检查当前登录态**

```bash
appwrite-cf whoami
# 有输出 → 已登录，不需要重新登录
# 报错或无输出 → 未登录，执行下一步
```

**第二步：登录**

```bash
appwrite-cf login-ks
# 自动打开浏览器完成快手 SSO 授权，无需输入账号密码
```

> ⚠️ **执行 `appwrite-cf login-ks` 后，命令输出中会包含一个登录链接（URL）。必须将该链接原文打印在对话中告知用户，不能只说"点击上方链接"或"链接在终端里"。用户需要看到完整 URL 才能在浏览器中打开完成授权。**

> ⚠️ 登录是**全局状态**，一次登录后所有项目共享，无需每个项目单独登录。

---

### 部署 CLI 登录（部署静态站点遇到鉴权报错时）

**适用场景**：执行 `npx -y @codeflicker/frontend-cloud-cli@latest deploy` 时报 401 / 鉴权失败。

部署工具**必须且只能走 `appwrite-cf login-ks`**

---

### 前端用户登录（网页应用的登录功能）

**适用场景**：开发网页应用的登录页面，或前端请求 Appwrite API 时报 401。

**唯一允许的方式**：

```typescript
import { OAuthProvider } from '@codeflicker/appwrite';
import { account } from '@/lib/appwrite';

account.createOAuth2Session({
    provider: OAuthProvider.Kuaishou,   // ← 必须是这个，不允许其他
    success: `${window.location.origin}/`,
    failure: `${window.location.origin}/login`,
});
```

**SSO 回调后必须处理 token 兑换**（否则登录成功但 `account.get()` 仍返回 401）：

```typescript
import { handleOAuth2Token } from '@codeflicker/appwrite';

async function checkAuth() {
  try {
    await handleOAuth2Token(client);   // ⚠️ 必须 await，内部是 fire-and-forget
  } catch (_) {}

  try {
    const user = await account.get();
    // 已登录
  } catch (_) {
    // 未登录，跳转登录页
  }
}
```

详细说明见 [references/appwrite-cf/appwrite-cf.md](./references/appwrite-cf/appwrite-cf.md)。

---

### 强制前置：先读设计原则文件

只要任务属于页面类任务，在动手之前，必须先实际读取：

`references/frontend-design/frontend-design.md`

不是"我记得这个文件大概说了什么"，而是**必须现在打开读**。

这份文档里的关键约束包括但不限于：
- 避免 Inter / Roboto / Arial / 系统字体等通用 AI 字体
- 避免白底紫色渐变等陈词滥调
- 避免可预测的布局和组件模式
- 做出真正符合上下文的出人意料选择
- **永远不要在多次生成中收敛到常见选择（例如 Space Grotesk）**

如果没有读这份文件，就不要开始做页面。

### 坚持设计原则文件里的负向约束：
- 不要通用 AI 审美
- 不要陈词滥调配色
- 不要可预测组件模式
- 不要在多次任务中收敛到固定安全牌


---

## 完成后写入项目文档

> ⚠️ **每完成一个阶段，必须同步更新 `AGENTS.md` 和 `README.md`，这是强制步骤，不可跳过。**

### 规则

- 项目初始化完成后，**默认生成** `AGENTS.md` 和 `README.md`
- 每完成一个阶段，将新增的技术栈、配置、接入信息**追加**到这两份文件
- **只追加，不覆盖**：新内容追加到对应章节末尾，不得重写或清空已有记录；已确认过时的内容可直接删除
- 目的：确保后续 agent 能完整感知项目上下文，避免重复踩坑

### `AGENTS.md` 写入操作规范（参考 [agents.md](https://agents.md/) 规范）

> ⚠️ **操作前必读**：
> 1. **先读文件**：用 `read_file` 读取现有的 `AGENTS.md` 全文
> 2. **只追加**：在文件末尾或对应章节末尾追加新内容
> 3. **严禁覆盖**：不能用模板替换已有内容，不能删除任何已存在的记录
> 4. **不存在时才创建**：文件不存在时，使用以下初始结构新建

**初始结构（仅文件不存在时使用）：**

```markdown
# AGENTS.md

## 项目概述
<!-- 填写项目用途 -->

## 技术栈
<!-- 每完成一个阶段在此追加，格式示例：
- 框架：React + Vite
- UI：shadcn/ui + TailwindCSS
- 数据库 SDK：@codeflicker/appwrite
- 登录：快手 SSO（OAuthProvider.Kuaishou）
- npm 源：https://npm.corp.kuaishou.com/
-->

## 注意事项
<!-- 每完成一个阶段在此追加坑点、约束、特殊配置 -->
```

### `README.md` 写入操作规范

同上：**先读、再追加，不覆盖**。每次在文件末尾追加本阶段新增的：
- 依赖包及用途
- 启动 / 部署命令
- 非标准配置说明
