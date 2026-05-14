# Skill Creator Reference Files

This directory contains detailed reference documentation for the Skill Creator workflow.

## Reference Files Overview

### Phase 1: Create
- **market-dedup.md** — 市场判重流程（Phase 1 前置检查）
- **quality-check.md** — Quality Check 两阶段详细流程（脚本校验 + 模型校验）
- **script-lint.md** — 脚本质量检查规则与命令
- **skill-review.md** — 质量评审清单（脚本/模型检查项对照）
- **proxy-adapter.md** — 脚本鉴权与接口安全规范
- **phase-dependency.md** — Skill 依赖管理标准流程（反模式警示包含在内）
- **kuaishou-skill-standards.md** — 快手 Skill 强制规范（创建前必读）

### Phase 2: Eval
- **schemas.md** — evals.json / grading.json / benchmark.json Schema

### Phase 3: Improve
- **phase-improve.md** — 迭代改进流程
- **phase-description-opt.md** — description 触发优化（Steps 1–4）

### Phase 5: Publish
- **phase-publish.md** — Phase 5 发布流程 + 平台差异说明

## Related Scripts

Located in `../scripts/`:
- **publish_skill.py** — 打包并上传到 MyFlicker 市场（Phase 5 调用）
- **search_market_skills.py** — 市场关键词检索（Phase 1 判重调用）
- **check_install_dep.py** — 检查并安装 Skill 依赖（依赖管理标准脚本）
