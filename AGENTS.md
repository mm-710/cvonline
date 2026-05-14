# AGENTS.md

> [!IMPORTANT]
> **用户认证、数据库操作、部署等详细说明，请读取并使用 `cf-web-artifacts` 或者 `website-builder` skill，本文件不重复记录。**

> 本文件遵循 [agents.md](https://agents.md/) 规范，为 AI Agent 提供项目上下文。

## 项目概览

本项目为**个人简历网页**，基于 `website-builder` skill 构建。

- **用途**：个人简历展示页，Neo-Editorial 设计风格
- **设计风格**：新拟态编辑风（暖白背景 #FFFBF7 + 活力橙 #FF5533 + 衬线标题 Playfair Display）
- **前端**：Vite 8 + React 18 + TypeScript 5
- **UI**：shadcn/ui + TailwindCSS v4
- **路由**：单页应用（仅 ResumePage，无多路由）
- **状态管理**：useState（简单交互）
- **数据请求**：静态数据（resumeData 常量）
- **后端 / 部署**：参见 `website-builder` skill

## 目录结构

```
src/
├── pages/            # 页面组件（每个路由对应一个文件）
├── components/
│   └── ui/           # shadcn/ui 组件（用 npx shadcn@latest add 添加，不要手动修改）
├── lib/
│   ├── appwrite.ts   # Appwrite client、account、databases、storage、loginWithKuaishou 导出（endpoint 已固定，禁止修改）
│   └── utils.ts      # cn() 工具函数（tailwind-merge + clsx）
├── App.tsx           # 路由配置（React Router <Routes>）
├── main.tsx          # 应用入口（BrowserRouter 包裹）
└── index.css         # 全局样式（TailwindCSS 入口）
```

## 路由开发规范

路由统一在 `src/App.tsx` 的 `<Routes>` 中配置，页面组件放在 `src/pages/` 目录。

### 新增页面步骤

1. 在 `src/pages/` 下创建页面组件文件（如 `ProfilePage.tsx`）
2. 在 `src/App.tsx` 中添加对应的 `<Route>`

### App.tsx 示例

```tsx
import { Routes, Route } from 'react-router'
import HomePage from '@/pages/HomePage'
import AboutPage from '@/pages/AboutPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/profile/:id" element={<ProfilePage />} />
    </Routes>
  )
}
```

### 页面内跳转

```tsx
import { Link, useNavigate, useParams } from 'react-router'

// 声明式跳转
<Link to="/about">关于</Link>

// 编程式跳转
const navigate = useNavigate()
navigate('/about')
navigate(-1) // 返回上一页

// 动态路由参数
const { id } = useParams<{ id: string }>()
```

## 构建与启动命令

```bash
# 安装依赖（必须使用快手内部 npm 源）
pnpm install

# 启动开发服务器
pnpm dev

# 构建产物
pnpm build

# 预览构建产物
pnpm preview
```

## 已安装的 shadcn/ui 组件

`button` `card`

添加更多组件：
```bash
npx shadcn@latest add <component-name>
```

## 登录实现经验（项目踩坑记录）

### 报错 `User (role: guests) missing scopes (["account"])`

**现象**：用户完成 SSO 授权后，页面跳回业务页，但 `account.get()` 报 `missing scopes (["account"])`，等同于未登录。

**根本原因**：`loginWithKuaishou` 的 `success` URL 写成了业务页（如 `/`），SSO 回调后直接落到业务页，而业务页没有调 `handleOAuth2Token`，token 未兑换成真实 session，所有后续 API 调用均以 guest 身份执行。

**修复**：`success` 和 `failure` 都指向 `/login`，由 `LoginPage` 统一兑换 token。

### OAuth2 回调 success URL 必须指向 `/login`，不能指向 `/`

```typescript
// ✅ 正确：success 指向 /login，统一由 LoginPage 处理 token 兑换
account.createOAuth2Session({
  provider: OAuthProvider.Kuaishou,
  success: `${window.location.origin}/login`,
  failure: `${window.location.origin}/login`,
})

// ❌ 错误：success 指向业务页，token 无法兑换 → missing scopes
account.createOAuth2Session({
  provider: OAuthProvider.Kuaishou,
  success: `${window.location.origin}/`,   // ← 业务页没有 handleOAuth2Token
  failure: `${window.location.origin}/login`,
})
```

**原因**：`success` 若指向业务页，该页面没有调 `handleOAuth2Token`，token 无法兑换为 session，`account.get()` 报 `missing scopes`。统一让 `LoginPage` 负责兑换 token 再跳转，路径单一，无竞争。

### token 兑换只在 LoginPage 做，业务页不重复调用

```typescript
// LoginPage.tsx —— 统一处理 token 兑换
async function checkAuth() {
  try { await handleOAuth2Token(client) } catch (_) {}  // ← 必须 await，否则 session 未建立就执行 account.get()
  try {
    await account.get()
    navigate('/')       // 兑换成功 → 跳到业务页
  } catch (_) {
    setChecking(false)  // 未登录 → 显示登录按钮
  }
}

// 业务页（如 HomePage）—— 不调 handleOAuth2Token，直接 account.get()
async function init() {
  try {
    const u = await account.get()
    setUser(u as User)
  } catch (_) {
    navigate('/login')  // 无 session → 回登录页
  }
}
```

### handleOAuth2Token 必须 await

`handleOAuth2Token` 内部是 fire-and-forget，**不 await 的话 token 还没兑换完 `account.get()` 就执行**，同样导致 `missing scopes`。

## 安全约束（禁止违反）

| 规则 | ✅ 允许 | ❌ 禁止 |
|------|---------|---------|
| 登录方式 | `loginWithKuaishou()` / `OAuthProvider.Kuaishou` | 邮箱/手机号/Google/GitHub |
| Appwrite SDK | `@codeflicker/appwrite` | 官方 `appwrite` npm 包 |
| 数据库 CLI | `appwrite-cf` | 官方 `appwrite` CLI |
| UI 组件库 | shadcn/ui + TailwindCSS（推荐） | — |
| npm 源 | `https://npm.corp.kuaishou.com/` | npmjs.org 直连（网络受限）|
| Endpoint | 禁止手动修改 | 硬编码其他 URL 字符串 |
| project_id 格式 | 纯字母数字下划线 | 含连字符 `-` |
| `appwrite-cf.config.json` | 只读，由 `appwrite-cf` 工具自动管理 | 手动修改文件内容 |
| `.static-site-deploy.json` | 只读，由部署工具自动管理 | 手动修改文件内容 |

> 用户认证、数据库操作、部署等详细说明，请读取并使用 `cf-web-artifacts` 或者 `website-builder` skill。

## 测试指令

- **开发中**：`pnpm dev` 启动后，使用浏览器自动化工具验证无白屏、无 JS 报错
- **构建验证**：`pnpm build`（无报错即通过）
- **代码检查**：`pnpm lint`
