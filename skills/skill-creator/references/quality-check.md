# Quality Check 详细流程

⚠️ **核心原则：脚本校验和模型校验都必须执行，缺一不可。只跑脚本不跑模型、或只跑模型不跑脚本，都属于不完整校验，不能给出"通过"结论。脚本覆盖确定性规则避免模型误判，模型覆盖语义性规则确保合理性和完整性。**

---

## Step A — 确定性脚本校验（必须执行）

运行 `skill_validate.py`，自动覆盖所有可脚本化的检查项：

```bash
uv run <skill_directory>/scripts/skill_validate.py <skill_dir> --auto-fix --summary && echo "NONCE=$SESSION_NONCE"
```

脚本检查项详见 `references/skill-review.md` 第一阶段表格。覆盖范围：
- frontmatter 格式（name kebab-case、description 长度、禁止 version/tags）
- 触发关键词检测
- 绝对路径替换、__pycache__ 清理、裸 except 修复
- Python 语法/AST 检查（input()、PEP 723）
- 鉴权规范（SmartSSOSession、硬编码敏感词）
- manifest.json 字段完整性
- SKILL.md 行数、脚本调用方式

**备选：若 uv 不可用，使用手动方式**
```bash
cd <skill_dir> && \
python3 -m py_compile scripts/*.py 2>&1 && echo "✅ Python syntax OK" && \
bash -n scripts/*.sh 2>&1 && echo "✅ Shell syntax OK" && \
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; echo "✅ Cache cleared" && \
find . -name "__pycache__" -type d | wc -l | xargs -I {} sh -c 'if [ {} -eq 0 ]; then echo "✅ 目录洁净"; else echo "❌ 仍有 __pycache__"; exit 1; fi' && \
echo "NONCE=$SESSION_NONCE"
```

**禁止分步执行**：必须一条命令完成，不得拆成多步。

---

## Step B — 模型语义校验（必须执行，不可跳过）

⚠️ **脚本校验和模型校验是互补关系，不是替代关系。脚本覆盖确定性规则（格式、语法、长度等），模型覆盖语义性规则（措辞合理性、场景覆盖度等）。两者都必须执行，最终结论需要综合两部分结果。**

模型检查以下语义性项目（详见 `references/skill-review.md` 第二阶段）：
1. **Frontmatter 语义** — `description` 是否第三人称动词开头、是否中英混杂、触发/不触发场景语义合理性
2. **Paths 语义** — SKILL.md 中引用脚本是否应使用 `<skill_directory>` 占位符
3. **Content** — SKILL.md 内容是否有实质指导意义、是否应拆分到 references/

Fix each failing item immediately and re-check before moving on.

---

## 最终结论格式

展示给用户的完整 summary 表格：

| 项目 | 脚本校验 | 模型校验 | 综合状态 |
|------|----------|----------|----------|
| Frontmatter | ✅/❌ | ✅/❌ | ✅/❌ |
| 长度 | ✅/❌ | ✅/❌ | ✅/❌ |
| 路径规范 | ✅/❌ | ✅/❌ | ✅/❌ |
| 脚本质量 | ✅/❌ | ✅/❌ | ✅/❌ |
| 鉴权规范 | ✅/❌ | ✅/❌ | ✅/❌ |
| 快手标准 | ✅/❌ | ✅/❌ | ✅/❌ |
| 目录洁净 | ✅/❌ | — | ✅/❌ |
| 内容质量 | — | ✅/❌ | ✅/❌ |

只有综合状态全部 ✅ 才能给出"质量审查通过"结论。