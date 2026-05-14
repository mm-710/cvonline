# Skill 依赖管理标准流程

当创建的 Skill 需要依赖其他 Skill 才能运行时，必须按本流程处理。

---

## 什么时候需要声明依赖

- Skill 的 SKILL.md 中明确要求用户先安装另一个 Skill
- Skill 的脚本在运行时会调用另一个 Skill 的接口或能力
- `manifest.json` 的 `ks-meta.dependency` 字段中列出了依赖项

> ⛔ **例外：`kuaishou-sso-login-client` 不需要声明**
> 使用 `SmartSSOSession` 的脚本已将 SSO 能力内嵌，用户无需手动安装该依赖。
> **禁止**在 SKILL.md 中出现「本 skill 依赖 `kuaishou-sso-login-client`」之类的前置条件说明。

---

## 环境检测

脚本会自动检测当前运行环境：

| 环境 | 判断条件 | 安装方式 |
|------|---------|---------|
| CodeFlicker | `SmartSSOSession.ap_token` 有值 | 检查本地目录，使用 `codeflicker://` 协议 |
| MyFlicker Work | `SmartSSOSession.ap_token` 为空 | 调用 MyFlicker API |

---

## 标准流程∏

### Step 1：在 manifest.json 中声明依赖

```json
{
  "ks-meta": {
    "dependency": ["dep-skill-slug-1", "dep-skill-slug-2"]
  }
}
```

平台安装该 Skill 时会自动提示用户安装依赖。

### Step 2：运行时检查并安装（在 SKILL.md 中描述）

在 SKILL.md 的使用说明中，用以下标准格式描述依赖检查，**不要写绝对路径、不要用 clawhub 命令**：

```markdown
## 前置依赖

本 Skill 依赖 `<dep-slug>`。运行前请确认已安装：

\`\`\`bash
uv run <skill_directory>/scripts/check_install_dep.py ensure <dep-slug>
\`\`\`

安装成功后即可继续使用。
```

### Step 3：脚本中的依赖检查（可选，适用于自动化流程）

```bash
# 只检查，不安装（返回 0=已安装，1=未安装）
uv run <skill_directory>/scripts/check_install_dep.py check <dep-slug>

# 检查+自动安装（返回 0=成功，2=失败）
uv run <skill_directory>/scripts/check_install_dep.py ensure <dep-slug1> <dep-slug2>
```

---

## 各环境的安装逻辑

### CodeFlicker 环境

1. **检查本地目录**：按顺序检查以下目录
   - `<workspace>/skills/<slug>/`
   - `<workspace>/.codeflicker/skills/<slug>/`
   - `<workspace>/.codeflicker/remote-personal-skills/<slug>/`
   - `<workspace>/.codeflicker/remote-skills/<slug>/`

2. **未找到时**：
   - 调用 `GET /api/v1/fe/skills/detail/{slug}` 获取 `latestVersion.cdnUrl`
   - 拼接 `codeflicker://` 协议链接并打开：
     ```
     codeflicker://kuaishou.codeflicker/skill/install?url={encodedCdnUrl}&name={slug}&preInstall=false
     ```

3. **用户确认**：在 CodeFlicker 中确认安装

### MyFlicker Work 环境

1. **检查已安装状态**：调用 `GET /api/v1/fe/skills/installed/{slug}`
2. **未安装时**：调用 `POST /api/v1/fe/skills/install/{slug}?autoDispatchUpdate=true`

---

## ❌ 反模式：禁止使用的写法

以下写法**一律禁止**，在创建或审查 Skill 时必须纠正：

### 反模式 1：检查绝对路径
```markdown
# ❌ 禁止
检查路径：`/data/aime/$SANDBOX_UUID/workspace/skills/kuaishou-sso-login-client`
（从环境变量 `SANDBOX_UUID` 获取）
```
**原因**：路径是运行时沙箱内部细节，SKILL.md 不应依赖它。跨平台（CodeFlicker、MyFlicker）路径不一致。

### 反模式 2：用 clawhub 命令安装
```markdown
# ❌ 禁止
运行 `clawhub install kuaishou-sso-login-client`
```
**原因**：`clawhub` 是旧版工具，标准安装渠道是 MyFlicker 市场 API。

### 反模式 3：要求用户手动访问市场页面
```markdown
# ❌ 禁止
请到 https://myflicker.corp.kuaishou.com/flicker/skills/xxx 手动点击安装
```
**原因**：应通过脚本自动化完成，减少用户手动操作。

---

## 接口说明（供脚本参考）

| 操作 | 方法 | 路径 |
|------|------|------|
| 检查是否安装 | GET | `/api/v1/fe/skills/installed/{slug}` |
| 安装（WORK 模式） | POST | `/api/v1/fe/skills/install/{slug}?autoDispatchUpdate=true` |
| 获取详情（含 CDN URL） | GET | `/api/v1/fe/skills/detail/{slug}` |

所有接口均需 SSO 鉴权，使用 `SmartSSOSession` 自动处理。在 CodeFlicker 环境下，Session 会自动从 Debug Server 获取 `ap_token` 进行鉴权。
