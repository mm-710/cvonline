# 快手 Skill 开发规范

> 来源：[Skills开发指南（BETA）](https://docs.corp.kuaishou.com/d<skill_directory>)
> 规则等级：【强制】违反不得上线；【建议】影响效果；【参考】提升体验

---

## ⛔ 零号规则：所有 Skill 必须通过 skill-creator 创建

> 【强制】这是凌驾于所有其他规则之上的元规则。

**AI 在任何情况下都不得绕过 `skill-creator` 自行创建 Skill**，包括但不限于：
- 直接在对话中写出 SKILL.md 内容并写入文件
- 以"快速创建"、"帮你简单做一个"、"先临时建一个"等理由跳过 skill-creator
- 在没有加载 skill-creator 的情况下创建任何 Skill 文件

**正确做法**：当用户发出任何"创建/写/新建/建一个 Skill"的请求时，必须先加载并进入 `skill-creator` 的创建流程（Phase 1），按规范完成市场判重、撰写、质量检查后才能写文件。

**原因**：直接创建会跳过市场判重、质量检查、鉴权规范审查、description 规范校验等关键步骤，导致产出低质量、不合规、可能与市场已有 Skill 重复的内容。

---

## 一、目录组织规范

### 强制规则

- 文件夹名必须与 skill 名完全相同
- 根目录必须有 `SKILL.md`（SKILL 大写，md 小写）
- 根目录必须有 `manifest.json`
- 所有代码文件必须放在 `scripts/` 文件夹下
- test 脚本（如有）必须放在 `tests/` 文件夹下
- 非代码资源（如有）必须放在 `assets/` 文件夹下
- 所有被引用文档必须放在 `reference/` 文件夹下，以 markdown 形式组织
- skill 命名：必须采用小写字母、数字和连字符（-），禁止使用空格和特殊字符

```
/my-awesome-skill
├── SKILL.md
├── manifest.json
├── scripts/
│   └── awesome-script.py
├── reference/
│   └── detail-instruct.md
├── tests/
│   └── test-scene1.py
└── assets/
    └── example.png
```

### 建议规则

- 多功能脚本中，子功能详细指引放在 `reference/` 中，SKILL.md 只做索引（避免 Token 爆炸）

---

## 二、manifest.json 规范

### 强制规则

- 每个 skill 目录下必须包含 `manifest.json`
- 版本号必须使用三段式版本号（如 `1.0.2`），禁止使用 `v1.0.2` 或单数字

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "ks-meta": {
    "displayName": "中文名",
    "platform": ["MyFlicker-Work", "MyFlicker-Code"],
    "dependency": ["other-skill-name"],
      "type": "user",
      "username": ["your-username"]
    }
  }
}
```

- `dependency` 字段（可选）：当前 skill 运行时依赖的其他 skill 名称列表，使用 `ks-meta.dependency`（字符串数组）声明。例如需要配合 `docs-shuttle` 使用时，填写 `["docs-shuttle"]`。平台安装时会自动提示用户安装依赖 skill。**若无依赖可省略该字段。**

  > **依赖检查标准流程**：SKILL.md 中描述依赖时，必须使用 `scripts/check_install_dep.py` 脚本，禁止写绝对路径或使用 `clawhub install` 命令。详见 `references/phase-dependency.md`。

- `displayName` 字段（软规范）：应使用**人能一眼看懂的中文名**，方便用户在市场中识别。避免使用英文 slug、缩写或技术术语。例如：
  - ✅ `"代码审查助手"`、`"会议室预订"`、`"Skill 创作与发布"`
  - ❌ `"skill-creator"`、`"code-review"`、`"ktest-gen"`

- `platform` 字段（必填）：声明 skill 支持的平台，**大小写敏感**，有效值：
  - `"MyFlicker-Work"` — MyFlicker 工作台 平台
  - `"MyFlicker-Code"` — CodeFlicker（IDE）平台

---

## 三、SKILL.md 规范

### 强制规则

- 必须包含 YAML 头，且包含 `name`、`description` 字段；`name` 必须与文件夹名和 `manifest.json` 中的 name 完全一致
- **严禁**在 YAML 头中包含 `version` 字段（包括放在 `metadata` 字段中）
- `description` 不应包含：参数收集方式、脚本内部实现逻辑、与"大模型是否该用该 skill"无关的内容
- `description` 必须明确声明"不支持"的近义场景
- `description` **不允许中英混杂**（同一句中中文和英文叙述混用），可选择纯中文或纯英文；专有名词（如 `SmartSSOSession`、URL、命令行参数等）可保留英文。示例：
  - ✅ `"根据需求 ID 查询测试用例列表，以 Markdown 格式返回。当用户说'查询需求用例'时触发。"` （纯中文）
  - ✅ `"Query test cases by requirement ID and return as Markdown. Triggered when user asks about 'test cases for requirement'."` （纯英文）
  - ❌ `"根据 requirement ID 查询 test cases，return Markdown 格式结果。"` （中英混杂）
- SKILL.md 文件不允许超过 3000 字，超出后应拆分 reference
- 引用 skill 目录内资源时，必须使用 `<skill_directory>` 占位符，不得使用硬编码绝对路径（如 `/data/aime/$SANDBOX_UUID/workspace/skills/...`、`<skill_directory>` 等）
- SKILL.md 内容中**禁止出现任何绝对路径**，包括示例、说明文字、命令中的路径；涉及 skill 目录时一律用 `<skill_directory>`，涉及 workspace 根目录时用 `<workspace>` 或相对路径（如 `skills/my-skill/`）
- 当需要 SSO 登录或调用内网接口时，必须使用 `SmartSSOSession`（来自 `ks-aimate` 包）替代 `requests.Session`；获取当前用户名使用 `get_username()`（来自 `ks_aimate.wanqing_token_username`）；禁止手动读取本地文件（如 `~/.openclaw/kim-paired.json`、`~/.kuaishou-*/session.json` 等）获取 token 或用户信息；禁止自行实现 token 换取逻辑（`secretKey` 由 Proxy 托管，脚本不可见）。参考 `skills-proxy-adapter` skill。
- 当可以使用 API 完成任务时，禁止使用 `agent-browser`
- 当确实需要浏览器时，必须明确要求使用 `agent-browser` 工具
- **创建或修改 Skill 时，必须在正式撰写 SKILL.md 之前向用户询问以下两个运行时安全参数，并将确认值写入 SKILL.md**：
  1. **最大自修复重试次数**：AI 执行失败后最多重试自修复几次（建议 2～3 次）。超过该次数后必须在 SKILL.md 中写明熔断：输出失败信息并退出，禁止继续循环。
  2. **agent-browser 降级次数**：当 API 失败时是否允许降级到 `agent-browser`，允许几次（0 = 禁止）。超过该次数后禁止继续降级浏览器操作。
  - 以上两个参数必须都问到，不得跳过或自行设默认值。

### 建议规则

- `description` 格式建议：`本技能用于XXX。以下场景唤醒：[3-5个关键词]。以下场景不唤醒：[近义但不适用场景]`
- 使用用户语言，避免技术术语
- 指令保持一致性，同类对象称呼统一
- SKILL.md 中只说明"如何调用脚本"，不解释脚本内部实现

### description 正反例

```yaml
# ✅ 正例
---
name: github-info-getter
description: 获取指定 GitHub.com 仓库的 Release 记录。不能获取 GitLab 等仓库。当用户询问某仓库的"最新版本"、"更新日志"或"发布历史"时调用。
---

# ❌ 反例（包含了内部实现细节）
---
name: github-info-getter
description: 本脚本通过调用 GitHub API V3 接口，传入 org 和 repo 参数，返回 JSON 列表。当用户询问时调用。
---
```

---

## 四、脚本文件规范

### 强制规则

- 固定逻辑必须写成脚本，禁止在 md 中让 AI 运行时生成脚本
- Python 必须使用 **uv 运行时**（PEP 723 内联依赖语法），禁止直接用 `python3` 或 `python` 运行；SKILL.md 中所有 Python 脚本调用格式必须为 `uv run <skill_directory>/scripts/your-script.py --param <value>`，已有的 `python3 -m scripts.xxx` 等用法在修改时必须同步替换
- TypeScript 必须使用 **Bun 运行时**，禁止依赖全局 node_modules
- 禁止交互式输入（`input()`），所有参数通过 CLI 参数传入
- 必须捕获所有异常，并输出带"建议操作"的错误信息
- 所有有价值的输出直接打到 stdout
- **调用内网接口时必须使用 `SmartSSOSession`**（`from ks_aimate.sso_login_client.session import SmartSSOSession`），dependencies 中必须包含 `ks-aimate` 及快手 pypi 源配置；禁止使用裸 `requests.Session`、手动读取本地 token/Cookie 文件、自行实现换 token 逻辑

### Python 脚本标准模板

```python
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests",
# ]
# ///

import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--param", required=True, help="参数说明")
    args = parser.parse_args()

    try:
        # 业务逻辑
        result = {"data": "..."}
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
        print("指引：请检查参数是否正确。")
        sys.exit(0)  # 正常退出，让模型看到错误信息

if __name__ == "__main__":
    main()
```

在 SKILL.md 中调用方式：
```markdown
uv run <skill_directory>/scripts/your-script.py --param <value>
```

### 建议规则

- 优先使用 Python / TypeScript，不使用 sh（除简单环境预检外）
- 对 API 返回值过滤，仅保留对当前 skill 有价值的字段
- 连续操作封装在同一脚本内，不要分拆多个脚本让模型串联
- 操作超过 10 秒时，定时向 stdout 打印保活日志
- 对参数进行合法性校验，避免幻觉参数污染

---

## 五、安全性规范

### 禁止事项（均为强制）

- 禁止明文存储 API Key、Secret Key（使用环境变量）
- 禁止将用户输入直接拼接为 Shell 命令（使用列表/数组形式调用子进程）
- 禁止使用 `eval()`、`exec()`、`sh -c` 执行包含用户输入的字符串
- 必须对路径进行归一化检查，防止目录穿越攻击
- 禁止将隐私数据输出到 Log、本地文件或无权限控制的 CDN
- 禁止执行未经校验的远程脚本（`curl URL | sh` 等）

---

## 六、上架前自检清单

发布前必须完成以下检查：

| 级别 | 检查项 |
|------|--------|
| 【强制】 | 在全新干净环境（无依赖）中重新安装并跑通 skill |
| 【强制】 | 扫描代码中无硬编码 ak/sk/password/内部测试域名 |
| 【强制】 | 确认无 `os.system()`/`exec()` 字符串拼接调用 |
| 【强制】 | 测试"参数缺失"、"非法输入"、"网络超时"三种异常场景 |
| 【强制】 | `manifest.json` 中声明了 `ks-meta.platform` |
| 【建议】 | `tests/` 目录下有至少 3 个覆盖核心路径的测试脚本 |
| 【建议】 | 在多个主流模型下测试唤醒率均 > 90% |
