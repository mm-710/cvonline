---
name: appwrite-cf
description: 快手内部 Appwrite CLI（appwrite-cf）的使用技能。当用户需要使用 appwrite-cf 命令行工具管理快手内部 Appwrite 资源时使用，包括：登录（login-ks）、初始化项目、推送/拉取资源（push/pull/push-cf）、管理数据库/表（tables-db）、云函数、存储桶、团队、消息 Topics，以及在 CI/CD 或脚本中以非交互方式调用 CLI。关键词：appwrite-cf、push-cf、tables-db、init project、push、pull、login-ks、appwrite-cf.config.json、非交互模式、CI/CD。
---

# appwrite-cf CLI 使用指南

> ⚠️ **严禁使用官方 `appwrite` CLI**
>
> 本项目使用的是快手内部定制版 `appwrite-cf`，**绝对不允许**使用官方的 `appwrite` 命令操作任何资源。
> 原因：官方 CLI 连接的是公共 Appwrite 服务，无法访问快手内部实例，执行操作会报错或影响错误的环境。
> **所有命令必须使用 `appwrite-cf`，不得使用 `appwrite`。**

`appwrite-cf` 是快手内部定制的 Appwrite 命令行工具，连接快手内部 Appwrite 实例。

- **可执行文件**：`appwrite-cf`（开发期用 `node dist/cli.cjs`）
- **默认服务端点**：`https://frontend-cloud.corp.kuaishou.com/v1`
- **帮助**：任何命令加 `--help` 查看完整参数列表

---

## 包说明

本仓库发布了**两个独立的 npm 包**，用途不同，请按场景选用：

| 包名 | 用途 | 使用场景 |
|------|------|---------|
| `@codeflicker/appwrite-cli` | **命令行工具（CLI）** | 资源管理：push/pull/init，在终端或 CI/CD 中运行 |
| `@codeflicker/appwrite` | **前端 SDK** | 在浏览器/前端代码中调用 Appwrite API（账号、数据库、存储等） |

> **npm 源**：两个包均发布在快手内部私有 registry `https://npm.corp.kuaishou.com/`

确保已配置快手内部源（项目根目录 `.npmrc` 文件，或全局配置）：

```
registry=https://npm.corp.kuaishou.com/
```

---

## 安装 CLI（命令行工具）

> 包名：`@codeflicker/appwrite-cli`

**推荐：CI/CD 场景（无需全局安装）**

```bash
npx -y @codeflicker/appwrite-cli@latest push-cf all
```

**全局安装（本地开发使用）**

```bash
npm install -g @codeflicker/appwrite-cli
```

安装后即可直接使用 `appwrite-cf` 命令。

**检查是否为最新版本 / 升级**

```bash
appwrite-cf --version   # 查看当前版本，并自动对比 npm 上的最新版
appwrite-cf update      # 一键升级到最新版
```

---

## 安装前端 SDK

> 包名：`@codeflicker/appwrite`

在前端项目中安装，用于在浏览器/客户端代码里调用 Appwrite API：

```bash
npm install @codeflicker/appwrite
```

**基本用法**

```typescript
import { Client, Account, Databases } from '@codeflicker/appwrite';

const client = new Client()
    // 必须用 location.origin + '/v1'；禁止 setEndpoint('https://...') 等纯字符串或 env 写死 URL
    .setEndpoint(location.origin + '/v1')
    .setProject('<your-project-id>');

const account = new Account(client);
const databases = new Databases(client);
```

> **Endpoint（强制）**  
> - 浏览器端 **`setEndpoint` 必须使用表达式 `location.origin + '/v1'`**（或先把 `location.origin` 赋给变量再拼接 `'/v1'`，但**来源仍须是 `location` 对象上的 `origin`**）。**禁止**用**纯字符串字面量**作为 Endpoint 或作为“域名来源”，例如 `setEndpoint('https://app.example.com/v1')`、把 `import.meta.env` / `process.env` 里写死的完整 URL 直接传入 `setEndpoint`、仅用环境变量拼出固定域名等——**一律不允许**；也禁止相对路径（如 `'/v1'`）、省略协议/主机。  
> - **不允许**用 `window.location.href` 截取、`new URL(...)` 包一层写死入参等方式**间接替代** `location.origin`；同源基址**只能**来自运行时 **`location.origin`**。

> ⚠️ **注意**：前端 SDK 包名是 `@codeflicker/appwrite`，**不是** `appwrite`（官方包）。
> 导入时必须使用 `from '@codeflicker/appwrite'`，否则会连接到公共 Appwrite 实例。

---

## 命名规范（强制约束）

> ⚠️ **所有资源 ID、字段 key 必须使用英文，严禁使用中文或特殊字符。**

### 核心规则

| 资源类型 | 命名要求 | ✅ 正确示例 | ❌ 错误示例 |
|---------|---------|-----------|-----------|
| **Database ID** | 纯英文，允许下划线/连字符 | `my_database`, `user-db` | `用户数据库`, `数据库-1` |
| **Table ID** | 纯英文，允许下划线/连字符 | `users`, `todo_items` | `用户表`, `待办事项` |
| **Column key** | 纯英文，允许下划线 | `user_name`, `createdAt` | `用户名`, `创建时间` |
| **Project ID** | 纯英文，**禁止连字符** | `myproject`, `todoapp` | `my-project`（含连字符）, `我的项目` |
| **Function ID** | 纯英文，允许连字符 | `send-email`, `process_data` | `发送邮件`, `处理数据` |
| **Bucket ID** | 纯英文，允许连字符 | `user-avatars`, `documents` | `用户头像`, `文档` |

### 命名约定建议

- **数据库/表/字段**：推荐使用 **snake_case**（`user_profile`）或 **camelCase**（`userProfile`）
- **Project ID**：纯小写，无连字符（`myproject`，不是 `my-project`）
- **避免缩写**：使用完整单词（`user_name` 优于 `usrnm`）
- **保持简洁**：名称长度 ≤ 30 字符

### 为什么必须使用英文

1. **跨平台兼容性**：避免编码问题（URL 编码、数据库字符集）
2. **代码可读性**：前端代码中 `user.userName` 比 `user.用户名` 更易维护
3. **URL 友好性**：API 路径 `/v1/databases/my_db/tables/users` 比 `/v1/databases/我的数据库/tables/用户` 更规范
4. **团队协作**：统一英文命名避免歧义（如"用户" = `user` vs `member`）

### 常见错误示例

**❌ 错误**（使用中文）：

```bash
# 创建数据库（中文 ID）
appwrite-cf tables-db create --database-id "用户数据库" --name "用户数据库"

# 创建表（中文字段）
appwrite-cf tables-db create-string-column \
  --database-id "my-db" --table-id "users" \
  --key "用户名" --size 256
```

**✅ 正确**（纯英文）：

```bash
# 创建数据库（英文 ID）
appwrite-cf tables-db create --database-id "user_database" --name "User Database"

# 创建表（英文字段）
appwrite-cf tables-db create-string-column \
  --database-id "my-db" --table-id "users" \
  --key "user_name" --size 256
```

> **注意**：`--name`（资源显示名称）可以使用中文，但 `--database-id`、`--table-id`、`--key` 等 ID/key 类参数必须纯英文。

---

## 第一步:登录

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

退出登录：
```bash
appwrite-cf logout
```

---

## 第二步：初始化项目

在你的工作目录下运行，生成 `appwrite-cf.config.json`：

```bash
appwrite-cf init project   --organization-id <org-id> \
  --project-id <project-id> \
  --project-name "My Project"
```

获取组织 ID：
```bash
appwrite-cf organizations list
```

初始化其他资源（需要已有 `appwrite-cf.config.json`）：
```bash
# ⚠️ init function / init bucket 等均为纯交互命令，不支持 CLI flag，脚本中请勿使用
# 脚本中创建云函数请改用：appwrite-cf functions create（见下方"云函数"章节）
appwrite-cf init function   # 新建云函数（仅交互模式，脚本/CI 请用 functions create）
appwrite-cf init bucket     # 新建存储桶（仅交互模式）
appwrite-cf init team       # 新建团队（仅交互模式）
appwrite-cf init table      # 新建表（TablesDB，仅交互模式）
appwrite-cf init collection # 新建集合（传统 DB，仅交互模式）
```

### 初始化后：在用户项目中留下标记

**`init project` 完成后，必须在用户的项目目录中写入禁用 `appwrite` 的说明**，确保后续任何人（包括其他 AI）都知道只能使用 `appwrite-cf`。

根据项目情况选择一种或多种方式：

**方式一：写入项目 `README.md`（推荐，若已有 README 则追加）**

在 README 中添加如下内容：

```markdown
## Appwrite 配置说明

本项目使用快手内部定制版 Appwrite CLI（`appwrite-cf`）进行资源管理。

> ⚠️ **严禁使用官方 `appwrite` 命令**，必须使用 `appwrite-cf`。
> 官方 CLI 无法连接快手内部 Appwrite 实例，误用将导致错误或操作到错误环境。

- 登录：`appwrite-cf login-ks`
- 同步配置：`appwrite-cf pull all`
- 推送变更：`appwrite-cf push-cf all`
```

**方式二：创建 `.appwrite-cf` 标记文件（适合不便修改 README 的情况）**

```bash
# 在项目根目录创建标记文件
cat > .appwrite-cf << 'EOF'
此项目由 appwrite-cf（快手内部定制版 Appwrite CLI）初始化管理。
严禁使用官方 appwrite 命令，所有操作必须使用 appwrite-cf。
EOF
```

---

## 核心工作流：push-cf / pull

> **重要：操作前先同步本地配置。** 在执行任何推送或资源管理操作之前，应先运行 `appwrite-cf pull all` 确保本地 `appwrite-cf.config.json` 与服务器状态一致，避免覆盖他人的变更或基于过期数据操作。

### pull（服务器 → 本地）

将服务器上的资源定义同步到本地 `appwrite-cf.config.json`：

```bash
appwrite-cf pull all                              # 拉取所有资源
appwrite-cf pull function                         # 只拉云函数定义（alias: functions）
appwrite-cf pull function --with-variables        # 拉云函数（含环境变量）
appwrite-cf pull table                            # 只拉 TablesDB 表结构（alias: tables）
appwrite-cf pull collection                       # 只拉传统数据库集合（alias: collections）
appwrite-cf pull bucket                           # 只拉存储桶（alias: buckets）
appwrite-cf pull team                             # 只拉团队（alias: teams）
appwrite-cf pull topic                            # 只拉消息 Topics（alias: topics）
```

### push-cf（本地 → 服务器）

将本地 `appwrite-cf.config.json` 的定义推送到服务器（创建或更新资源）。统一使用 `push-cf`，它会自动跳过所有确认提示，无需手动加 `--force`。

> `push-cf` 支持与 `push` 完全相同的子命令和参数规则，需传入资源范围：`all`、`table --all`、`table --id ...`、`function -f ...` 等。

```bash
appwrite-cf push-cf all                       # 推送所有资源
appwrite-cf push-cf table --all               # 推送所有 TablesDB 表（alias: tables）
appwrite-cf push-cf table --id my-db|my-table # 推送指定表（格式：databaseId|tableId）
appwrite-cf push-cf function --all            # 推送所有云函数（alias: functions）
appwrite-cf push-cf function -f <function-id> # 推送指定云函数（⚠️ 用 -f/--function-id，不是全局 --id）
appwrite-cf push-cf bucket --all              # 推送所有存储桶（alias: buckets）
appwrite-cf push-cf team --all                # 推送所有团队（alias: teams）
appwrite-cf push-cf topic --all               # 推送所有 Topics（alias: topics）
```

---

## 非交互模式（脚本 / CI/CD）

**CLI 默认就是非交互模式**，所有参数必须通过 flag 传入，不会出现交互提示。

推送资源统一使用 `push-cf`，它会自动跳过确认提示。注意 `push-cf` 不会替你补齐资源范围，仍需传入 `all`、`table --all`、`table --id ...`、`function --all`、`function -f ...` 等子命令参数。

遇到 `non-interactive mode` 报错时，按提示补全缺少的 flag 即可：

```bash
# ✗ 错误示例（缺少资源范围）
appwrite-cf push-cf table

# ✅ 正确写法
appwrite-cf push-cf table --all
```

---

## 资源管理：TablesDB（tables-db）

快手定制的关系型数据库资源，层级：**Database → Table → Column / Index**

> **关于 `appwrite-cf.config.json`**：`tables-db` 的直接操作命令（create / delete / get / list 等）只与服务器交互，**不会**读写本地 `appwrite-cf.config.json`。
> 如需将服务器最新结构同步到本地，执行 `appwrite-cf pull table`；
> 如需将本地配置批量推送到服务器，执行 `appwrite-cf push-cf table --all`。

### 数据库操作

```bash
# 列出所有数据库
appwrite-cf tables-db list

# 创建数据库
appwrite-cf tables-db create \
  --database-id "my-db" \
  --name "My Database"

# 查看数据库详情
appwrite-cf tables-db get --database-id "my-db"

# 删除数据库
appwrite-cf tables-db delete --database-id "my-db"
```

### 表操作

> ⚠️ **创建表时必须同时配置权限**，默认 `$permissions` 为空会导致所有用户无法读写。
> 推荐在 `create-table` 时就传入 `--permissions` 和 `--row-security`，一步到位。

```bash
# 列出所有表
appwrite-cf tables-db list-tables --database-id "my-db"

# 创建表（推荐：创建时直接配好权限）
# --permissions "create(\"users\")"  允许所有已登录用户创建新文档
# --row-security true                开启行级安全，文档的读写删由创建时附带的 Permission 控制
appwrite-cf tables-db create-table \
  --database-id "my-db" \
  --table-id "todos" \
  --name "Todos" \
  --permissions "create(\"users\")" \
  --row-security true

# 查看表详情（验证权限是否正确）
appwrite-cf tables-db get-table --database-id "my-db" --table-id "todos"

# 删除表
appwrite-cf tables-db delete-table --database-id "my-db" --table-id "todos"
```

### 列操作

```bash
# 创建字符串列
appwrite-cf tables-db create-string-column \
  --database-id "my-db" --table-id "users" \
  --key "username" --size 256 --required false

# 创建整数列
appwrite-cf tables-db create-integer-column \
  --database-id "my-db" --table-id "users" \
  --key "age" --required false

# 创建布尔列
appwrite-cf tables-db create-boolean-column \
  --database-id "my-db" --table-id "users" \
  --key "isActive" --required false

# 创建日期时间列
appwrite-cf tables-db create-datetime-column \
  --database-id "my-db" --table-id "users" \
  --key "createdAt" --required false

# 列出所有列
appwrite-cf tables-db list-columns \
  --database-id "my-db" --table-id "users"

# 删除列
appwrite-cf tables-db delete-column \
  --database-id "my-db" --table-id "users" --key "age"
```

---

## 资源管理：传统数据库（databases）

```bash
appwrite-cf databases list
appwrite-cf databases create --database-id "db1" --name "My DB"
appwrite-cf databases list-collections --database-id "db1"
appwrite-cf databases create-document \
  --database-id "db1" \
  --collection-id "col1" \
  --document-id "unique()" \
  --data '{"name": "Alice"}'
```

---

## 资源管理：云函数（functions）

### ⚠️ `init function` vs `functions create`：必须区分

| 命令 | 作用 | 参数方式 | 非交互可用 |
|------|------|----------|-----------|
| `appwrite-cf init function` | 本地脚手架：写 `appwrite-cf.config.json` + clone 模板代码 | 纯 inquirer 交互，**无** CLI flag | ❌ 会被非交互拦截 |
| `appwrite-cf functions create` | 直接调 Appwrite API 在服务端创建 function 实体 | Commander `--requiredOption` flags | ✅ 完全支持 |

**结论：在脚本 / CI/CD 中创建 function，必须用 `functions create`，不能用 `init function`。**

### 创建云函数（非交互 / 脚本）

```bash
# 必填三个参数：--function-id、--name、--runtime
appwrite-cf functions create \
  --function-id "my-fn" \
  --name "My Function" \
  --runtime "node-22"
```

> ⚠️ **Runtime 名称**：服务端只支持实际部署的 runtime，必须先查可用列表：
> ```bash
> appwrite-cf functions list-runtimes
> # 当前支持：node-22（其他版本如 node-18.0 会报 "Runtime is not supported"）
> ```
> 缺少任意必填 flag 时，Commander 直接报 `required option '...' not specified`，不会进入交互。

### push-cf function（上传代码到服务端）

推送前依赖**两个前置条件**，缺一不可：

1. **`appwrite-cf.config.json` 中有 `functions[]` 配置**
   - `functions create` 只创建服务端实体，**不会**写入本地 config
   - 需要手动在 config 的 `functions` 数组中补充配置，或先 `pull function` 从服务端同步

2. **本地代码目录存在且非空**（`func.path` 指向的目录）

```bash
# 先同步服务端的 function 定义到本地 config
appwrite-cf pull function

# 推送指定函数（⚠️ 用 -f/--function-id，不是全局 --id）
appwrite-cf push-cf function -f "my-fn"

# 推送所有函数
appwrite-cf push-cf function --all
```

`appwrite-cf.config.json` 中 function 配置的最小结构：

```json
{
  "projectId": "my-project",
  "functions": [
    {
      "$id": "my-fn",
      "name": "My Function",
      "runtime": "node-22",
      "entrypoint": "index.js",
      "commands": "",
      "path": "functions/my-fn",
      "execute": [],
      "events": [],
      "scopes": [],
      "schedule": "",
      "timeout": 15,
      "enabled": true,
      "logging": true
    }
  ]
}
```

### 其他查询命令

```bash
appwrite-cf functions list
appwrite-cf functions get --function-id "fn-id"
appwrite-cf functions list-runtimes       # 查看当前支持的所有 runtime

# 本地运行函数（开发调试，需要已有 appwrite-cf.config.json）
appwrite-cf run function --function-id "fn-id"
```

---

## 资源管理：存储（storage）

### 创建 Bucket（非交互 / 脚本）

`--bucket-id` 和 `--name` 均为 `requiredOption`，缺省时 Commander 直接报 `required option '...' not specified`，不会进入交互。

```bash
appwrite-cf storage create-bucket \
  --bucket-id "my-bucket" \
  --name "My Bucket"
```

> ⚠️ **`$permissions` 默认为空**，客户端无法读写文件。需要按场景传入权限：
> ```bash
> # 允许所有已登录用户上传，文件级安全（每个文件有独立权限）
> appwrite-cf storage create-bucket \
>   --bucket-id "my-bucket" \
>   --name "My Bucket" \
>   --permissions "create(\"users\")" \
>   --file-security true
> ```

### 常用命令

```bash
appwrite-cf storage list-buckets
appwrite-cf storage get-bucket --bucket-id "my-bucket"
appwrite-cf storage list-files --bucket-id "my-bucket"
appwrite-cf storage delete-bucket --bucket-id "my-bucket"
```

---

## 资源管理：团队（teams）

```bash
appwrite-cf teams list
appwrite-cf teams create --team-id "team1" --name "My Team"
appwrite-cf teams list-memberships --team-id "team1"
```

---

### appwrite-cf.config.json 结构

`init project` 会在当前目录生成此文件，`push`/`pull` 命令依赖它：

```json
{
  "projectId": "my-project",
  "projectName": "My Project",
  "endpoint": "https://frontend-cloud.corp.kuaishou.com/v1",
  "functions": [],
  "tablesDB": [],
  "tables": [],
  "buckets": [],
  "teams": [],
  "topics": []
}
```

> ⚠️ **`init project` 实际只写入 `projectId`**（实测生成的文件只有 `{"projectId": "..."`}），其余字段在首次 `pull all` 后才会补全。

**运行 push/pull 命令时，必须先 `cd` 到包含 `appwrite-cf.config.json` 的目录。**

---

## 生成类型安全 SDK

从 Appwrite 数据库 Schema 自动生成 TypeScript 类型定义：

```bash
appwrite-cf generate typescript
```


---

## 客户端 SDK：OAuth2 登录

在前端/客户端代码中使用 `@codeflicker/appwrite` SDK 发起 OAuth2 登录时，**必须使用 `OAuthProvider.Kuaishou`**，快手内部实例仅支持快手 SSO，不支持 Google、GitHub 等其他 OAuth 提供商。

```typescript
import { account } from '../lib/appwrite';
import { OAuthProvider } from '@codeflicker/appwrite';

// ✅ 正确：使用 OAuthProvider 枚举
account.createOAuth2Session({
    provider: OAuthProvider.Kuaishou,
    success: window.location.origin,
    failure: window.location.origin,
});

// ❌ 禁止使用其他 provider
account.createOAuth2Session({ provider: OAuthProvider.Google, ... });   // 不支持
account.createOAuth2Session({ provider: OAuthProvider.Github, ... });   // 不支持
```

### OAuth2 回调处理：`checkAuth` 正确写法

SSO 授权回调后，需要在应用入口（如 `App.tsx`）中正确处理 token 兑换，**顺序和 await 不能省略**。

#### 两个辅助函数的职责

| 函数 | 触发条件 | 作用 | 是否需要手动调 |
|------|----------|------|--------------|
| `handleOAuth2Fallback()` | URL 含 `?oauthFallback=1` | 把 `key`/`secret` 存入 `localStorage.cookieFallback`，让后续请求带上 `X-Fallback-Cookies` | **`new Client()` 构造时已自动调用**，无需手动调 |
| `handleOAuth2Token(client)` | URL 含 `?userId=&secret=` | 用 token 换取真实 session（POST `/account/sessions/token`） | ⚠️ **必须手动 `await`**，SDK 内部是 fire-and-forget |

> ⚠️ **已知 Bug**：`handleOAuth2Token` 内部不会等待 token 兑换完成就 resolve，**必须在外部手动 `await`**。
> 若漏写 `await`，`account.get()` 会在 session 建立前执行，导致用户登录失败（返回 401）。

#### 推荐写法（精简版）

```tsx
import { client, account } from '@/lib/appwrite';
import { handleOAuth2Token } from '@codeflicker/appwrite';

async function checkAuth() {
  // handleOAuth2Fallback 已在 new Client() 时自动执行，无需手动调用

  // ⚠️ 必须 await，否则 token 未兑换完 account.get() 就执行，导致登录失败
  try {
    await handleOAuth2Token(client);
  } catch (_) {}

  // 确认最终登录态
  try {
    await account.get();
    setAuthState('logged-in');
  } catch (_) {
    setAuthState('logged-out');
  }
}
```

#### 保守写法（同时保留 `handleOAuth2Fallback`，无副作用）

```tsx
import { client, account } from '@/lib/appwrite';
import { handleOAuth2Fallback, handleOAuth2Token } from '@codeflicker/appwrite';

async function checkAuth() {
  handleOAuth2Fallback();                  // 幂等，重复调用无副作用

  try {
    await handleOAuth2Token(client);       // ⚠️ 必须 await
  } catch (_) {}

  try {
    await account.get();
    setAuthState('logged-in');
  } catch (_) {
    setAuthState('logged-out');
  }
}
```

---

## 表权限配置（重要）

> ⚠️ **新建的表默认 `$permissions` 为空，任何用户都无法读写，必须正确配置权限。**

Appwrite 权限分为**两层**，必须同时配置：

```
表级权限（$permissions）  ← 控制"谁可以 CREATE 新文档"（登录用户 = "users"）
       ↓
文档级权限（rowSecurity） ← 控制"谁可以 READ / UPDATE / DELETE 已有文档"
```

### 推荐方案：行级安全（rowSecurity）

适用场景：每个用户只能访问自己的数据（如 Todo、笔记、个人设置等）。

**第一步：同时设置表级 `create` 权限 + 开启行级安全**

> ⚠️ `--permissions` 和 `--row-security` **必须在同一条命令中传入**，否则后执行的会覆盖前者的配置（例如单独执行 `--row-security true` 会把 `$permissions` 重置为空）。

```bash
appwrite-cf tables-db update-table \
  --database-id "my-db" \
  --table-id "my-table" \
  --name "My Table" \
  --permissions "create(\"users\")" \
  --row-security true
```

- `create("users")` 表示所有**已登录用户**都可以创建新文档
- `--row-security true` 开启行级安全，让每条文档有独立的读写权限

**第二步：创建文档时附带当前用户的文档级权限**

在客户端 SDK（`@codeflicker/appwrite` npm 包）中，`createDocument` 的第 5 个参数传权限数组：

```typescript
import { Permission, Role, ID } from '@codeflicker/appwrite';

await databases.createDocument(DATABASE_ID, TABLE_ID, ID.unique(), {
  title: 'My Todo',
  userId: user.$id,
  // ...其他字段
}, [
  Permission.read(Role.user(user.$id)),    // 本用户可读
  Permission.update(Role.user(user.$id)),  // 本用户可改
  Permission.delete(Role.user(user.$id)),  // 本用户可删
  Permission.write(Role.user(user.$id)),   // 等价于 update + delete，加上更保险
]);
```

这样每条记录只有创建它的用户才能访问，其他用户无法读写。

### 报错 `The current user is not authorized to perform the requested action` 排查清单

遇到此报错，按顺序逐项检查：

1. **表级权限** — 检查 `$permissions` 是否包含 `create("users")`：
   ```bash
   appwrite-cf tables-db get-table --database-id <db> --table-id <table>
   # 确认输出中 "$permissions" 含 "create(\"users\")" 且 "rowSecurity": true
   ```

2. **文档级权限** — 确认 `createDocument` 代码传入了 `Permission` 数组（见上方代码示例）

3. **`--permissions` 覆盖问题** — 如果之前单独执行过 `update-table`，确认 `rowSecurity` 和 `$permissions` 没有被意外重置

---

## 常见问题

**Q：报错 `non-interactive mode`，怎么办？**
查看报错中列出的缺失 flag，按提示补全参数。

**Q：报错 `project not initialized`？**
确保当前目录有 `appwrite-cf.config.json`，若没有先运行 `appwrite-cf init project`。

**Q：`update-table` 报错 `Param "name" is not optional`？**
`update-table` 命令必须带 `--name` 参数，即使只想修改其他字段也需要传入表名。

