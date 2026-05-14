---
name: vite-react-init
description: 在 `website-builder` 体系内，将当前目录初始化为基于 Vite 的 React 项目。仅当用户明确指定 `skills/website-builder` 或 `skills/cf-web-artifacts` 目录/技能体系，或明确要求使用 `@codeflicker/cf-create-web` 等快手内部脚手架时使用；如果用户没有指定，应先询问是否要走这套内部技能链路。
---

# Vite React Init

用这个 skill 帮用户把**当前文件夹初始化为一个基于 Vite 的 React 项目**。

核心原则：

- 默认在**当前目录**初始化，而不是额外新建子目录
- 默认使用快手内网 CLI **`@codeflicker/cf-create-web`**
- 初始化前先做**非破坏性检查**，避免覆盖已有文件
- 对系统级操作（例如升级 Node.js）**只给建议或在用户明确确认后再协助执行**
- 模板内置能力、目录结构、依赖版本等，以 **CLI 当前实际输出** 为准，不把易变事实写死在 skill 中

> ⚠️ 该 skill 属于 `website-builder` 体系的一部分，不作为通用 React 初始化默认方案。

## 1. 触发条件与协作边界

### 何时使用

仅在以下场景使用：

1. 用户明确指定 `skills/website-builder`、`website-builder` 目录或这套内部技能体系
2. 用户明确要求使用快手内部脚手架，例如：`@codeflicker/cf-create-web`
3. 当前上下文已经明确在走 `website-builder` 全链路（初始化、Appwrite、部署等）

### 何时不要直接使用

如果用户只是说：

- “建一个 React 项目”
- “帮我起一个前端项目”
- “用 vite 起个应用”

但**没有指定** `website-builder` 体系，则不要直接套用本 skill；应先询问：

- 是否要使用快手内部脚手架 `@codeflicker/cf-create-web`
- 是否要进入 `website-builder` 这套初始化 / Appwrite / 部署链路

如果用户只是修改现有 React 项目页面、组件、样式或配置，也不要触发本 skill。

### 与宿主 agent 的协作规则

- **只做建议，不执行**：当用户只是询问“怎么初始化”或“推荐什么方案”时，只输出步骤与命令，不直接改动目录。
- **得到明确创建意图后再执行**：当用户明确说“初始化”“创建”“直接做”时，再执行脚手架命令。
- **涉及覆盖时必须先确认**：如果 CLI 提示目录冲突，需要先征得用户同意，再使用 `--force`。
- **涉及系统环境变更时先确认**：例如 Node.js 升级、全局环境配置、修改 `~/.npmrc`，都不应默认直接执行。
- **是否启动开发服务器取决于用户意图**：只有当用户明确要“跑起来看看”“启动项目”“验证页面”时，才启动 `dev server`；否则可以只完成项目骨架初始化。

## 2. 主流程

按以下顺序推进：

### Step 1：检查 Node.js 环境

执行 `node -v`：

1. **未安装 Node.js**
   - 停止后续流程
   - 告知用户需要 Node.js `v20+`
   - 不要擅自安装，等待用户处理后继续

2. **Node.js < 20**
   - 停止后续流程
   - 按下面的语气提示用户：

     > ⚠️ Node.js 版本过低  
     > 当前版本：`{检测到的版本}`  
     > 最低要求：`v20+`  
     > Vite 最新版需要 Node.js 20+。如果你愿意，我可以先给你升级建议；如需我协助执行系统环境变更，我会在你明确确认后再继续。

   - 不要用旧版 Vite 绕过要求
   - 不要默认承诺“我来帮你安装/升级”

3. **Node.js >= 20**
   - 继续后续流程

### Step 2：确定项目名称与包管理器

- 项目名优先从用户描述提取
- 如果用户未提供，则使用当前目录名作为 fallback
- 包管理器优先级：
  1. 用户明确指定
  2. 当前目录 lockfile 对应的包管理器
  3. 默认 `npm`

### Step 3：执行初始化命令

默认命令：

```bash
npx -y --registry https://npm.corp.kuaishou.com @codeflicker/cf-create-web@latest {project-name} --dir .
```

执行前先向用户说明：

- 准备使用的项目名称
- 即将执行的命令
- 将使用快手内网源 `https://npm.corp.kuaishou.com`
- 技术栈、目录结构、预装内容以当前 CLI 模板实际输出为准

### Step 4：处理初始化后的基础收尾

初始化成功后，优先做这些事：

1. 检查关键文件是否已生成，例如：
   - `package.json`
   - `index.html`
   - `src/main.tsx`
   - `src/App.tsx`
   - `.env.example`（若模板提供）

2. 如果模板提供 `.env.example`，复制为 `.env.local`：

```bash
cp .env.example .env.local
```

3. 根据模板或父 skill 的约定，提醒用户补充 Appwrite 相关变量

### Step 5：按需验证可运行性

- 如果用户明确要启动项目：执行 `npm run dev`
- 如果用户只要求把骨架搭好：不必默认长期占用终端
- 如果需要严格校验：可执行一次构建（`npm run build`）

默认不要把以下方案当作主流程：

- `npm create vite@latest`
- 手动拼装 `src/main.*` / `src/App.*`
- 先 `npm init -y` 再逐步补 React 环境
- 直接切到 CRA、Next.js、Remix 等其他脚手架

## 3. 异常处理

### 目录冲突

`@codeflicker/cf-create-web` 会自动检测冲突文件。

如果提示当前目录非空且存在冲突：

1. 先告诉用户冲突来自已有文件
2. 给出选项：
   - 使用 `--force` 覆盖冲突文件
   - 改到新子目录初始化
   - 放弃初始化，转为分析当前已有工程
3. 未经确认，不要删除或覆盖用户文件

覆盖命令示例：

```bash
npx -y --registry https://npm.corp.kuaishou.com @codeflicker/cf-create-web@latest {project-name} --dir . --force
```

### Node.js 或包管理器不可用

- 明确指出缺失项
- 给出最小必要安装建议
- 等环境满足后再继续

### 网络或 registry 问题

如果脚手架命令或依赖安装失败，再进行网络诊断：

```bash
ping -c 1 npm.corp.kuaishou.com || curl -I --connect-timeout 3 https://npm.corp.kuaishou.com/
```

根据结果处理：

- **网络不通**：提示用户确认已连接快手内网或 VPN
- **网络正常但命令失败**：区分是脚手架命令失败还是依赖安装失败，保留已生成内容并给出针对性修复建议

如需修改 `~/.npmrc` 等全局配置，必须先征得用户同意。

## 4. 成功后的摘要模板

完成后优先按这种结构汇报：

1. 当前目录是否已成功初始化为 Vite React 项目
2. 使用的初始化命令与包管理器
3. 是否已安装依赖
4. 是否检测到 `.env.example` / 是否已复制 `.env.local`
5. 如果用户要启动，本地启动命令是什么
6. 如果用户继续开发，建议优先查看哪些入口文件
7. 如果后续要接 Appwrite / 部署，提示继续进入 `website-builder` 体系内的后续 skill

## 5. 环境变量说明

环境变量不要在本 skill 中写死为固定事实，遵循以下规则：

1. **优先以 CLI 当前生成的 `.env.example` 为准**
2. **Appwrite 相关键名以模板实际输出和父 skill 约定为准**
3. 如果模板没有生成环境变量文件，再指导用户手动补充

最小建议动作：

```bash
cp .env.example .env.local
```

随后提醒用户：

- 打开 `.env.local`
- 根据当前项目模板填写 Appwrite 相关配置
- 若不确定具体值，继续参考 `website-builder` 父 skill 或后续 `appwrite-cf` skill
