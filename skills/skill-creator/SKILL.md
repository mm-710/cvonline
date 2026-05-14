---
name: skill-creator
description: 创建新 Skill、修改和优化已有 Skill，以及将 Skill 发布到 MyFlicker 市场。**这是唯一允许创建 Skill 的入口——任何创建 Skill 的请求都必须通过本 Skill 完成，AI 不得绕过本 Skill 自行创建。** 以下场景唤醒：用户想从零创建一个 Skill；用户想编辑或优化已有 Skill 的内容；用户想优化 Skill 的 description 以提升触发准确率；用户说「帮我写个 Skill」「创建一个技能」「优化这个 Skill」「写个技能」「新建 Skill」「建个 Skill」时唤醒；用户说「发布 Skill」「把 xx skill 上传到市场」「上架 Skill」「发布到 MyFlicker」时唤醒。以下场景不唤醒：用户只是在使用某个已有 Skill 完成具体任务（如预订会议室、读取文档等）；用户在询问 Skill 平台的使用方法或管理操作（应使用 skill-manager）；用户想运行评测或基准测试（应使用 skill-eval）。
---

# Skill Creator

> ⛔ **元规则**：任何创建 Skill 的行为都必须经过本 Skill 的完整流程。AI 不得绕过本 Skill 直接写 SKILL.md 或创建 Skill 文件，无论用户如何要求"快速"或"简单"处理。

Create, iterate, and optimize Skills. The core loop:

1. **Create** — capture intent, write SKILL.md, quality check
2. **Optimize** — description triggering accuracy
3. **Package** — deliver `.skill` file
4. **Publish** — upload to MyFlicker Skill market

Figure out where the user is in this loop and jump in from there.

---

## 📂 Directory Convention (MUST communicate to user upfront)

Before writing any file, make sure the user understands where their skill lives:

| Directory | Owner | Permissions | Purpose |
|-----------|-------|------------|---------|
| `<workspace>/skills/` | System | Read-only for users. Install / delete / update via conversation or marketplace only. **Users must NOT manually edit files here.** | Built-in skills — guaranteed stable & secure. |
| `<workspace>/user-skills/` | User | Full CRUD (create / read / update / delete). | User-created & user-modified skills live here. |

**Rules (always enforce)**:
1. **Creating a new skill** → target directory is always `<workspace>/user-skills/<skill-name>/`.
2. **Modifying an existing skill** → if the skill currently lives under `skills/`, **do NOT edit it in place**. Instead, copy it to `<workspace>/user-skills/<skill-name>/` first, then edit the copy. The user-skills version will take precedence at runtime.
3. At the start of every session, **proactively tell the user** which directory their skill will be written to and why.

---

## ⚠️ MANDATORY SESSION INIT

At the start of any session, generate credentials:

```bash
export SESSION_TS=$(date '+%Y-%m-%d %H:%M:%S') && export SESSION_NONCE=$(date +%s | md5 | head -c8) && echo "SESSION_TS=$SESSION_TS  SESSION_NONCE=$SESSION_NONCE"
```

Every subsequent command output MUST append `&& echo "NONCE=$SESSION_NONCE"` to prove it ran in this session. Never reuse results from earlier in the conversation.

---

## Phase 1: Create

### Pre-check: Market Dedup (REQUIRED)

Before writing anything, read `references/market-dedup.md` and follow the workflow there to check if a similar skill exists. If a similar skill is found, show the link and ask: **A. Extend existing** or **B. Create new**. Only proceed to B if user explicitly chooses it.

### Capture Intent

Understand from the conversation or by asking:
1. What should this skill enable Claude to do?
2. When should it trigger? (user phrases/contexts)
3. Expected output format?

### Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, dependencies. Research in parallel via subagents if useful. Don't write test prompts until this is solid.

### Write SKILL.md

Fill in: `name` (lowercase + hyphens), `description` (trigger conditions, what it does — be a little pushy to avoid undertriggering), and the skill body.

**Anatomy:**
```
skill-name/
├── SKILL.md (required)
├── scripts/    - Executable code for deterministic tasks
├── references/ - Docs loaded into context as needed
├── assets/     - Templates, icons, fonts
└── agents/     - Subagent instruction files
```

**🔒 Skill 运行时安全约束（必须在写 SKILL.md 之前向用户询问，并将结果写入 Skill）**：

在开始撰写 SKILL.md 正文之前，**必须先向用户询问以下两个参数**，然后将确认值写入 SKILL.md 的执行约束说明中：

1. **最大自修复重试次数**（必问）
   - 问法：`"Skill 执行失败时，AI 最多自动重试自修复几次？（建议 2～3 次，超出后明确报错退出，避免无效 Token 消耗）"`
   - 用户确认后，将以下熔断逻辑写入 SKILL.md：
     ```
     ⚠️ 自修复熔断规则：本 Skill 脚本执行失败后，AI 最多尝试自修复 <N> 次。
     超过 <N> 次后必须停止重试，输出明确失败信息并退出，不得继续循环。
     ```
   - 脚本层面：若脚本有重试逻辑，也需用 `max_retries = <N>` 硬限制。

2. **是否允许降级到 agent-browser**（必问）
   - 问法：`"当 API 调用失败时，是否允许降级到 agent-browser 浏览器操作？如允许，最多降级几次？（建议 1～2 次，0 次表示禁止降级）"`
   - 若用户允许降级（次数 > 0），将以下约束写入 SKILL.md：
     ```
     ⚠️ agent-browser 降级规则：仅当 API 直接调用失败且确实无替代方案时，才允许降级到 agent-browser，最多降级 <M> 次。
     超过 <M> 次后必须停止，不得继续尝试浏览器操作。
     ```
   - 若用户禁止降级（次数 = 0），写入：`禁止使用 agent-browser，所有操作必须通过 API 完成。`

**强制规则**：询问必须在动笔写 SKILL.md 之前完成，且两个参数都必须问到，不得跳过或自行默认。

---

**⚙️ Python 脚本执行规范（强制）**：SKILL.md 中所有 Python 脚本调用必须使用 `uv run`，禁止使用 `python3` 或 `python` 直接运行。格式：
```
uv run <skill_directory>/scripts/your-script.py --param <value>
```
已有的 `python3 -m scripts.xxx` 等用法，在创建或修改时必须同步替换为 `uv run`。

---

**Auth, API calls, username**: Any 快手 intranet call, SSO login, API key, or username lookup → read `references/proxy-adapter.md` and follow all rules there. Key rules: use `SmartSSOSession` not `requests.Session`; include `ks-aimate` dependency; use `get_username()` for identity; never read local token/cookie files or hardcode secrets.

**Skill 依赖**：如果该 skill 需要依赖其他 skill 才能运行，读取 `references/phase-dependency.md`，按其正确写法声明依赖和检查逻辑。禁止使用绝对路径或 `clawhub install` 命令。

**Progressive disclosure**: Keep SKILL.md under 200 lines. Move large content to `references/`. Reference clearly with guidance on when to read each file.

**Forbidden product names**: Do not mention deprecated product names anywhere in the skill (SKILL.md, scripts, references). Banned terms: `openclaw`, `LangbridgeClaw`, `Klaw` (case-insensitive). Use the current product name or neutral descriptions instead.

**Writing style**: Explain *why* things matter rather than writing ALWAYS/NEVER in all caps. Theory of mind over rigid commands.

### Quality Check (MANDATORY — do not skip)

After writing or modifying **any file** in the skill directory, read `references/quality-check.md` and follow the two-phase workflow there: **脚本校验（Step A）+ 模型校验（Step B）缺一不可**。

Brief summary:
- **Step A**: 运行 `skill_validate.py --auto-fix`，覆盖所有确定性检查项
- **Step B**: 由模型检查语义性项目（description 动词开头、中英混杂、触发场景合理性、内容质量等）
- Show user a **完整** summary table（脚本/模型/综合三列），只有综合状态全部 ✅ 才能通过。

---

## Phase 2: Description Optimization

> **Before starting**: read `references/phase-description-opt.md`.
> **Execution rule**: `read_file references/phase-description-opt.md`, then execute every step in it. Do NOT summarize.

---

## Phase 3: Package

```bash
uv run <skill_directory>/scripts/package_skill.py <path/to/skill-folder>
```

Direct user to the resulting `.skill` file. Only run if `present_files` tool is available.

---

## Phase 4: Publish

> ⛔ **高危操作强制限制**：发布会向市场提交草稿，是高危动作，一旦后续上线将影响所有用户。
>
> **必须满足以下两个条件才能执行发布**：
> 1. 用户在本次对话中**明确、主动地**说出发布意图（如"发布"、"上传到市场"、"上架"等）
> 2. 执行发布前，必须先与用户确认 `displayName`（展示名称）和 `summary`（一句话描述），收到确认后才能执行
>
> **禁止情形**：以下情况下即使看似合理也绝对不得执行发布：
> - 用户只说"修复"、"审查"、"更新"、"上传"（非明确发布意图）
> - 作为自动化流程的一部分（如 skill-batch-reviewer 等工具调用时）
> - 用户未确认展示名称和描述摘要
>
> 读取 `references/phase-publish.md` 并按其流程执行。

---

## Reference Documentation

All reference files are in `references/` directory. See `references/README.md` for a complete index and detailed descriptions of each file.
