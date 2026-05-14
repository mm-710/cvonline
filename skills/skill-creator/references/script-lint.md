# 脚本质量检查（内联自 script-linter）

对 Skill 内的脚本文件进行语法静态检查，发现问题时自动修复；清理编译产物和无关文件；审查目录结构确保打包干净。

## 强制完整检查流程（每次修改 skill 目录后必须执行）

**推荐方式 1：一条命令（check_all.sh）**

```bash
bash <skill_directory>/scripts/check_all.sh <skill_dir> && echo "NONCE=$SESSION_NONCE"
```

内部自动顺序执行 lint → clean → audit，任意一步失败即终止。

**推荐方式 2：lint --skill-dir**

```bash
uv run <skill_directory>/scripts/lint.py lint <skill_dir>/scripts --fix --skill-dir <skill_dir> && echo "NONCE=$SESSION_NONCE"
```

lint 完成后自动追加 clean（dry-run）和 audit。

**通过标准**：最终输出 `✅ All 3 checks passed`

---

## 各命令说明

```bash
# 语法检查 + 自动修复
uv run <skill_directory>/scripts/lint.py lint <target_dir> --fix

# 清理编译产物（dry-run 预览，加 --delete 才真正删除）
uv run <skill_directory>/scripts/lint.py clean <skill_dir> [--delete]

# 审查目录结构（检测不应存在的文件）
uv run <skill_directory>/scripts/lint.py audit <skill_dir>
```

---

## 检查规则

### Python（`.py`）
- `py_compile` 语法检查
- 缺少 PEP 723 `# /// script` 依赖块
- 裸 `except:` → 自动修复为 `except Exception as e:`
- `input()` 调用（skill 脚本不允许交互式输入）

### TypeScript（`.ts/.tsx`）
- `tsc --noEmit` 或 `ts-node --transpileOnly` 语法验证
- `console.log` 调试语句残留（WARNING）

### Shell（`.sh`）
- `bash -n` 语法检查
- 缺少 shebang → 自动插入 `#!/bin/bash`

---

## 清理规则（clean 命令）

### 目录（整个目录树移除）

| 分类 | 目录 |
|------|------|
| **Python** | `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.tox`, `.venv`, `venv`, `.env`, `env`, `.eggs`, `*.egg-info`, `*.dist-info` |
| **Node/TypeScript** | `node_modules`, `dist`, `build`, `.cache`, `.next`, `.nuxt`, `.turbo` |
| **Rust** | `target` |
| **Java/JVM** | `.gradle`, `gradle`, `.mvn`, `mvn`, `out` |
| **Go** | `vendor` |
| **IDE** | `.idea`, `.vscode`, `.sublime-project`, `.sublime-workspace` |
| **Git** | `.git` |
| **通用** | `tmp`, `temp`, `logs`, `log` |

### 文件 glob 匹配

| 分类 | 文件模式 |
|------|---------|
| **Python 编译** | `*.pyc`, `*.pyo`, `*.pyd`, `*.pyi` |
| **Java/JVM 编译** | `*.class`, `*.jar`, `*.war`, `*.ear` |
| **原生编译** | `*.o`, `*.obj`, `*.a`, `*.lib`, `*.so`, `*.dylib`, `*.dll` |
| **TypeScript 编译** | `*.tsbuildinfo` |
| **JS 压缩** | `*.min.js`, `*.min.js.map` |
| **日志/临时** | `*.log`, `*.tmp`, `*.bak`, `*.swp`, `*.swo`, `*~` |
| **测试覆盖率** | `*.coverage`, `.coverage`, `coverage.xml`, `lcov.info` |
| **Python 元数据** | `*.egg-info`, `*.dist-info` |
| **Lock 文件** | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock` |
| **IDE/编辑器** | `*.iml`, `*.ipr`, `*.iws` |

### 文件名精确匹配

| 分类 | 文件名 |
|------|--------|
| **系统** | `.DS_Store`, `.DS_store`, `Thumbs.db`, `desktop.ini` |
| **Git** | `.gitignore`, `.gitattributes` |
| **编辑器** | `.editorconfig`, `.npmrc`, `.nvmrc`, `.python-version` |
| **文档** | `CHANGELOG.md`, `CHANGELOG`, `changelog.md`, `changelog` |

---

## 目录审查规则（audit 命令）

**合法顶层文件**：`SKILL.md`、`manifest.json`、`LICENSE.txt`、`README.md`

**合法顶层目录**：`scripts/`、`references/`、`reference/`、`tests/`、`assets/`、`agents/`

**合法扩展名**：`.md`、`.txt`、`.py`、`.ts`、`.js`、`.sh`、`.json`、`.yaml`、`.toml`、`.csv`、`.html`、`.css`、`.png`、`.jpg`、`.svg`

**报 ERROR 的情况**：
- 缺少 `SKILL.md` 或 `manifest.json`
- 存在任何编译产物目录（如 `__pycache__`、`node_modules`、`target` 等）
- 存在 IDE 配置目录（如 `.idea`、`.vscode`）

**报 WARNING 的情况**：
- 扩展名为 `.zip`、`.db`、`.lock`
- 路径含 `workspace`、`iteration-`、`eval-`、`output`、`log`、`tmp` 等

---

## 强制清理命令

如果 audit 报告发现编译产物，必须立即清理：

```bash
# Python 缓存
find <skill_dir> -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find <skill_dir> -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
find <skill_dir> -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# Node 缓存
find <skill_dir> -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null
find <skill_dir> -type d -name ".next" -exec rm -rf {} + 2>/dev/null

# IDE 配置
find <skill_dir> -type d -name ".idea" -exec rm -rf {} + 2>/dev/null
find <skill_dir> -type d -name ".vscode" -exec rm -rf {} + 2>/dev/null

# Rust 编译
find <skill_dir> -type d -name "target" -exec rm -rf {} + 2>/dev/null
```

---

## 注意事项

1. **强制执行**：每次创建或修改 Skill 后，必须执行 `clean --delete` 确保无临时产物残留
2. **打包前检查**：发布前必须通过 audit 检查，确保目录结构干净
3. **大文件警告**：如果 Skill 打包后超过 1MB，通常是临时产物未清理导致，重新执行 clean
