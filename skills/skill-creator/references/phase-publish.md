# Phase 4: 发布到 MyFlicker 市场

> ⛔ **高危操作 — 执行前必须满足：**
> 1. 用户在本次对话中**明确主动**说出发布意图
> 2. 必须向用户确认 `displayName`（展示名称）和 `summary`（一句话描述），收到确认后才能执行
>
> 如果是被其他工具（如 skill-batch-reviewer 等自动化流程）调用到此处，**立即停止**，向用户报告"发布需要用户主动确认，自动化流程中不执行发布操作"。

当用户说「发布 Skill」「上传到市场」「上架 Skill」「发布到 MyFlicker」「把 xx skill 发布」等时触发。

---

## Step 1：收集信息

向用户确认（上下文中已知则跳过）：
1. **展示名称（displayName）** — 市场页面展示的中文名，如 `Skill 迁移助手`
2. **摘要（summary）** — 一句话描述，如 `将本地 Skill 一键迁移到 MyFlicker-Work 平台`
3. **Skill 目录路径** — 已知则直接使用
4. **用户名（username）** — 用于权限校验，通常从上下文获取（如 `lixinjian`）

AI 可根据 SKILL.md 中的 `name` 和 `description` 自动推荐，让用户确认即可。

---

## Step 1.5：Slug 冲突检测与用户决策（⚠️ 强制环节）

在正式执行发布脚本之前，**必须先检测市场上是否已存在同名 Skill**：

```bash
uv run <skill_directory>/scripts/publish_skill.py \
  --skill-dir /path/to/skill-dir \
  --display-name "展示名称" \
  --summary "一句话描述" \
  --username <当前用户名> \
  --dry-run
```

`--dry-run` 参数仅执行权限检查和 Slug 冲突检测，不会打包/扫描/提交草稿。

脚本输出会告知三种情况：

| 情况 | 脚本输出 | AI 应做的事 |
|------|----------|------------|
| 市场无此 Slug | `市场上尚无此 Skill，允许首次发布` | 直接继续 Step 2 |
| Slug 已存在，用户在管理员列表中 | `用户 xxx 在管理员列表中` | **必须暂停，向用户呈现两个选项让其选择** |
| Slug 已存在，用户不在管理员列表 | `❌ 发布被拒绝` | 提示用户联系管理员或换名 |

**Slug 冲突时的用户决策**（只有当 Skill 已存在且用户有权发布时才需要此决策）：

AI 必须向用户说明：**市场上已存在名为 `{slug}` 的 Skill**（附上市场链接 `https://myflicker.corp.kuaishou.com/skillhub/skills/{slug}`），并提供两个选项：

- **选项 A：更新已有 Skill** — 直接用当前本地内容覆盖线上草稿（使用更新接口）。适合场景：用户是该 Skill 的管理员，想发布新版本。
- **选项 B：换一个新 Slug 发布** — 更换 slug/name 后作为新 Skill 首次发布。适合场景：用户想发布一个同名但功能不同的独立 Skill。

**如果用户选择选项 B（换名）**，AI 必须：
1. 向用户询问新的 slug 名称（必须是 lowercase + hyphens 格式）
2. 执行「换名操作」，需修改以下文件：
   - **SKILL.md frontmatter**：将 `name: <old-slug>` 改为 `name: <new-slug>`
   - **manifest.json**：将 `name` 字段改为 `<new-slug>`
   - **脚本引用**：如果 SKILL.md 正文中引用了目录名（如 `<skill_directory>/scripts/xxx`），这些路径不需要改，因为 `--slug` 参数会覆盖打包时的 slug
3. 使用 `--slug <new-slug>` 参数重新运行发布脚本（此时是首次发布，走创建接口）

**⛔ 禁止事项**：
- 不得在用户未确认的情况下直接选择"更新"
- 不得在用户未确认的情况下直接选择"换名"
- 换名后不得遗漏修改 SKILL.md 和 manifest.json

---

## Step 2：执行发布脚本

```bash
uv run <skill_directory>/scripts/publish_skill.py \
  --skill-dir /path/to/skill-dir \
  --display-name "展示名称" \
  --summary "一句话描述" \
  --username <当前用户名>
```

脚本内部按顺序执行以下 4 步：

### 2.1 权限检查

调用管理员列表接口，判断是否有权发布：

- **Skill not found** → 市场无此 Skill，允许首次发布
- **用户在管理员列表中** → 允许发布
- **用户不在管理员列表中** → ❌ 禁止发布，脚本输出原因后退出

### 2.2 打包

将 skill 目录打包为 zip，排除 `.git`、`__pycache__`、`.DS_Store`、`evals`、`node_modules` 等无关内容。

### 2.3 静态安全扫描

调用 `scan-zip` 接口，**最多重试 3 次**：

- 扫描通过 → 继续下一步
- 扫描失败 → 脚本输出错误信息并退出

> 💡 **扫描失败时的处理**：使用 skill-creator 对 SKILL 内容进行 Review 和修复，修复后重新运行发布命令（计入重试次数）。连续失败 3 次后不再重试，需人工介入。

### 2.4 草稿发布

调用 `basic-info` 接口，将 Skill 提交为**草稿态**（非直接上线）。

---

## Step 3：确认结果

发布成功后，告知用户前往以下页面查看并完善草稿：

```
https://myflicker.corp.kuaishou.com/flicker/creator/skills
```

---

## Platform Notes

**Claude.ai / Cowork**：无差异，脚本统一处理 SSO 认证。

**修改已有 Skill**：保留原始 `name` 和目录名。若 skill 在 `skills/`（系统内置），**禁止原地修改**——先整体复制到 `<workspace>/user-skills/<skill-name>/`，再在副本上改。`user-skills/` 下的 skill 可直接修改。每次修改前必须提醒用户这条规则。
