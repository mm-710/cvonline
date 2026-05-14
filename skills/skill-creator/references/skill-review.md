# Skill 质量评审清单

⚠️ **核心原则：脚本校验和模型校验都必须执行，缺一不可。只跑脚本不跑模型、或只跑模型不跑脚本，都属于不完整校验，不能给出"通过"结论。脚本覆盖确定性规则避免模型误判，模型覆盖语义性规则确保合理性和完整性。**

---

## 第一阶段：脚本化校验（必须运行，不可跳过）

确定性规则全部由脚本检查，避免模型误判和效果不一致。运行以下命令：

```bash
uv run <skill_directory>/scripts/skill_validate.py <skill_dir> --auto-fix --summary && echo "NONCE=$SESSION_NONCE"
```

脚本覆盖的检查项：

| 类别 | 检查项 | 脚本规则名 |
|------|--------|------------|
| **Frontmatter** | `name` 使用 kebab-case，无特殊字符 | `name_not_kebab_case` |
| | `description` ≤1024 字符 | `description_too_long` |
| | `description` 不应包含尖括号 | `description_angle_brackets` |
| | frontmatter 禁止 `version` 字段 | `version_in_frontmatter` |
| | frontmatter 禁止 `tags` 字段 | `tags_in_frontmatter` |
| | `description` 触发场景关键词检测 | `missing_trigger_keywords` |
| | `description` 不触发场景关键词检测 | `missing_no_trigger_keywords` |
| **长度** | SKILL.md ≤200 行 | `skill_md_too_long` |
| **路径** | 禁止出现绝对路径 | `absolute_path` |
| **脚本** | Python 语法检查（AST） | `python_syntax_error` |
| | 无 `input()` 调用（AST级别，不误报注释/字符串） | `input_call` |
| | 无裸 `except:`（AST级别） | `bare_except` |
| | 包含 PEP 723 `# /// script` 依赖声明 | `missing_pep723` |
| | Python 用 `uv run`，TypeScript 用 `bun run` | `python_direct_run` / `node_direct_run` |
| **鉴权** | 内网请求用 `SmartSSOSession`，非裸 `requests.Session` | `requests_session_without_sso` |
| | 无硬编码 token / secretKey / password / Cookie | `sensitive_hardcode` |
| | 手动读取本地文件获取用户名 → 应使用 `get_username()` | `manual_token_read` |
| **快手标准** | `manifest.json` 存在 | `manifest_missing` |
| | manifest.json 字段完整性（name/version/ks-meta） | `manifest_missing_*` |
| | `ks-meta.platform` 值合法 | `manifest_illegal_platform` |
| | manifest.json name 与文件夹名一致 | `manifest_name_mismatch` |
| | `ks-meta.displayName` 建议添加 | `manifest_missing_displayName` |
| **内容规范** | 不得出现废弃产品名（openclaw、LangbridgeClaw、Klaw 等，大小写不敏感） | `deprecated_product_name` |
| **目录洁净** | 不得存在 `__pycache__` 目录 | `pycache_exists` |
| | 不得存在编译器/IDE 产物（`.idea`、`.vscode`、`.codeflicker`、`.DS_Store`、`.git` 等） | `ide_artifact_exists` |

**自动修复项**（`--auto-fix` 会自动处理）：
- 删除 `__pycache__` 目录
- 删除编译器/IDE 产物（`.idea`、`.vscode`、`.codeflicker`、`.DS_Store`、`.git` 等）
- 绝对路径替换为 `<skill_directory>` 占位符
- 裸 `except:` 替换为 `except Exception as e:`
- 移除 frontmatter 中的 `version` 和 `tags` 字段

---

## 第二阶段：模型语义校验（必须运行，不可跳过）

⚠️ **模型校验不是可选的补充项，而是必须执行的步骤。脚本校验和模型校验是互补关系，不是替代关系。最终结论必须综合两部分结果，只给一半结论是不完整的。**

脚本校验完成后，必须再由模型检查以下语义性项目：

| 类别 | 检查项 | 说明 |
|------|--------|------|
| **Frontmatter** | `description` 第三人称动词开头 | "创建..." / "根据..." / "引导..." |
| | `description` 中英混杂检测 | 同一句中中文和英文叙述混用，允许纯中文或纯英文，专有名词可保留英文 |
| | `description` 触发场景语义合理性 | 关键词存在≠语义合理，需人工确认 |
| | `description` 不触发场景语义合理性 | 是否覆盖了近义但不适用场景 |
| **路径** | 脚本路径是否应该使用 `<skill_directory>` 占位符 | SKILL.md 中引用脚本时应使用占位符 |
| **内容** | SKILL.md 内容质量 | 是否有实质指导意义、是否过于冗长/空洞 |
| | references/ 渐进披露是否合理 | 大量内容是否已拆分到 references/ |
| | 脚本参数值防御性约束 | 脚本的命令行参数（如 `--title`）值是否在 SKILL.md 中有显式约束，防止 AI 运行时动态生成违反规则的值（如友商名称、敏感词等）。脚本校验只能发现硬编码，无法覆盖 AI 运行时生成的内容 |

---

## 脚本化 vs 模型校验对比

| 检查项 | 方式 | 原因 |
|--------|------|------|
| name kebab-case | ✅ 脚本 | 正则匹配，确定性100% |
| description 长度 | ✅ 脚本 | 字符计数，确定性100% |
| description 中英混杂 | ❌ 模型 | 边界案例多（专有名词/命令/路径等），模型语义理解更准确 |
| description 触发关键词 | ✅ 脚本 | 关键词匹配，确定性高（但语义合理性需模型补充） |
| 绝对路径 | ✅ 脚本 | 正则匹配，确定性100% |
| __pycache__ | ✅ 脚本 | 目录检测，确定性100% |
| Python语法 | ✅ 脚本 | AST解析，确定性100% |
| input() | ✅ 裸脚本 | AST级别，确定性100% |
| 裸except | ✅ 脚本 | AST级别，确定性100% |
| PEP 723 | ✅ 脚本 | 字符串匹配，确定性100% |
| 鉴权规范 | ✅ 脚本 | grep检测，确定性高 |
| manifest字段 | ✅ 脚本 | JSON解析+字段枚举，确定性100% |
| 废弃产品名 | ✅ 脚本 | grep字符串匹配，确定性100% |
| description 动词开头 | ❌ 模型 | 语义判断，需要理解"第三人称动词" |
| description 语义合理性 | ❌ 模型 | 需理解用户意图和场景 |
| 内容质量 | ❌ 模型 | 需理解指导意义的实质 |

---

## 评审结果输出格式

⚠️ **最终结论必须综合脚本校验和模型校验两部分结果，只给一半结论是不完整的。**

展示给用户的完整 summary 表格：

| 项目 | 脚本校验 | 模型校验 | 综合状态 |
|------|----------|----------|----------|
| Frontmatter | ✅/❌ | ✅/❌ | ✅/❌ |
| 长度 | ✅/❌ | — | ✅/❌ |
| 路径规范 | ✅/❌ | ✅/❌ | ✅/❌ |
| 脚本质量 | ✅/❌ | ✅/❌ | ✅/❌ |
| 鉴权规范 | ✅/❌ | — | ✅/❌ |
| 快手标准 | ✅/❌ | — | ✅/❌ |
| 目录洁净 | ✅/❌ | — | ✅/❌ |
| 内容质量 | — | ✅/❌ | ✅/❌ |
| 废弃产品名 | ✅/❌ | — | ✅/❌ |

只有综合状态全部 ✅ 才可给出"质量审查通过"结论并进入下一步。