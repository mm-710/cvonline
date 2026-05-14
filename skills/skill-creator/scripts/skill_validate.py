# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pyyaml",
# ]
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# ///

"""
Skill 质量校验脚本 — 确定性规则全部在此脚本中检查，不依赖模型判断。
避免模型误判和效果不一致的问题。

检查项（全部可脚本化确定性校验）：
  - manifest.json 字段完整性 + platform 合法性
  - SKILL.md 存在性、行数、frontmatter 格式
  - frontmatter name kebab-case
  - frontmatter description 长度 (≤1024)
  - frontmatter 禁止 version 字段
  - frontmatter description 触发场景关键词检测
  - 绝对路径检测（/Users/、/home/、/data/aime/ 等）
  - __pycache__ 目录检测 + 自动删除
  - Python 语法检查（AST）
  - input() 调用检测（AST）
  - 裸 except: 检测（AST）
  - PEP 723 依赖声明检测
  - SmartSSOSession vs requests.Session 检测
  - 硬编码敏感词检测（token/secretKey/password/Cookie）
  - get_username() 使用检测
  - SKILL.md 中脚本调用方式检测（uv run / bun run）
  - 编译器/IDE 产物检测（.idea、.vscode、.codeflicker、.DS_Store、.git、origin.json 等）
  - 任意层级隐藏目录/文件检测（以 '.' 开头，如 .clawhub、.myapp 等）

注意：中英混杂检测由模型语义校验阶段负责，脚本不做此项。

输出 JSON，每条 issue 带 severity、rule、message、auto_fixable 等字段。
"""

import argparse
import ast
import json
import re
import shutil
import sys
from pathlib import Path

import yaml


# ─── 绝对路径检测 ──────────────────────────────────────────

_ABS_PATH_RE = re.compile(
    r"(?<![r\"])(?<!')(/(?:Users|home|root|data/aime|opt)/[a-zA-Z0-9_\-./]+)"
)
_ABS_PATH_FIX_RE = re.compile(
    r"(/(?:Users|home|root|data/aime|opt)/[a-zA-Z0-9_\-./]+)"
)
_SKIP_LINE_PATTERNS = [
    re.compile(r"^\s*r['\"].*['\"],?\s*$"),
    re.compile(r"^\s*#"),
    re.compile(r"_RE\s*=\s*re\.compile"),
    re.compile(r"abs_patterns\s*="),
]


def _is_skip_line(line: str) -> bool:
    return any(p.search(line) for p in _SKIP_LINE_PATTERNS)


def check_absolute_paths(skill_dir: Path) -> list[dict]:
    issues = []
    for fpath in skill_dir.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.suffix in {".pyc", ".png", ".jpg", ".zip", ".skill", ".json"}:
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _is_skip_line(line):
                continue
            for m in _ABS_PATH_RE.finditer(line):
                issues.append({
                    "rule": "absolute_path",
                    "severity": "error",
                    "message": "发现绝对路径",
                    "file": str(fpath.relative_to(skill_dir)),
                    "line": i,
                    "content": line.strip()[:120],
                    "matched": m.group(1),
                    "fix_hint": "替换为 <skill_directory> 占位符",
                    "auto_fixable": True,
                })
    return issues


def auto_fix_absolute_paths(skill_dir: Path, issues: list[dict]) -> list[str]:
    fixed = []
    files_to_fix = {i["file"] for i in issues if i.get("auto_fixable") and i["rule"] == "absolute_path"}
    for rel_path in files_to_fix:
        fpath = skill_dir / rel_path
        lines = fpath.read_text(encoding="utf-8").splitlines(keepends=True)
        changed = False
        new_lines = []
        for line in lines:
            if _is_skip_line(line):
                new_lines.append(line)
                continue
            new_line = _ABS_PATH_FIX_RE.sub("<skill_directory>", line)
            if new_line != line:
                changed = True
            new_lines.append(new_line)
        if changed:
            fpath.write_text("".join(new_lines), encoding="utf-8")
            fixed.append(f"  已修复绝对路径: {rel_path}")
    return fixed


# ─── __pycache__ ──────────────────────────────────────────

def check_pycache(skill_dir: Path) -> list[dict]:
    issues = []
    for d in skill_dir.rglob("__pycache__"):
        if d.is_dir():
            issues.append({
                "rule": "pycache_exists",
                "severity": "error",
                "message": "发现 __pycache__ 目录",
                "file": str(d.relative_to(skill_dir)),
                "fix_hint": "删除 __pycache__ 目录",
                "auto_fixable": True,
            })
    return issues


def auto_fix_pycache(skill_dir: Path) -> list[str]:
    fixed = []
    for d in list(skill_dir.rglob("__pycache__")):
        if d.is_dir():
            shutil.rmtree(d)
            fixed.append(f"  已删除: {d.relative_to(skill_dir)}")
    return fixed


# ─── 编译器/IDE 产物检测 ────────────────────────────────────

# 不应出现在 skill 发布目录中的编译器/IDE/构建产物
_IDE_ARTIFACTS = {
    # JetBrains / VS Code / CodeFlicker IDE 配置
    ".idea",
    ".vscode",
    ".codeflicker",
    # OS 产物
    ".DS_Store",
    "Thumbs.db",
    # Git
    ".git",
    ".gitignore",
    ".gitattributes",
    # Python 构建产物
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".eggs",
    # Node / JS / TS 构建产物
    "node_modules",
    ".npm",
    ".yarn",
    ".pnp",
    ".next",
    ".nuxt",
    ".turbo",
    "dist",
    "build",
    "out",
    "coverage",
    ".nyc_output",
    # 依赖锁文件（skill 目录不需要）
    "package-lock.json",
    "yarn.lock",
    "bun.lockb",
    # 环境变量文件
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    # Skill 元数据（仅用于下载时记录来源，不应打包发布）
    "origin.json",
}


def check_ide_artifacts(skill_dir: Path) -> list[dict]:
    """检测 skill 目录中是否存在编译器/IDE/构建产物或隐藏文件/目录"""
    issues = []
    reported = set()  # 避免重复上报同一路径

    # 检测顶层目录/文件（名称匹配白名单）
    for item in skill_dir.iterdir():
        if item.name in _IDE_ARTIFACTS:
            issues.append({
                "rule": "ide_artifact_exists",
                "severity": "error",
                "message": f"发现编译器/IDE/构建产物: {item.name}",
                "file": item.name,
                "fix_hint": f"删除 {item.name}",
                "auto_fixable": True,
            })
            reported.add(item)

    # 检测任意层级的隐藏目录（以 '.' 开头）
    for item in skill_dir.rglob("*"):
        if item in reported:
            continue
        if item.is_dir() and item.name.startswith("."):
            rel = item.relative_to(skill_dir)
            issues.append({
                "rule": "hidden_dir_exists",
                "severity": "error",
                "message": f"发现隐藏目录（不应打包到 skill 中）: {rel}",
                "file": str(rel),
                "fix_hint": f"删除 {rel}",
                "auto_fixable": True,
            })
            reported.add(item)
        elif item.is_file() and item.name.startswith(".") and item.name != ".gitkeep":
            # 跳过已被父级隐藏目录覆盖的文件，避免重复报告
            if any(p in reported for p in item.parents):
                continue
            rel = item.relative_to(skill_dir)
            issues.append({
                "rule": "hidden_file_exists",
                "severity": "error",
                "message": f"发现隐藏文件（不应打包到 skill 中）: {rel}",
                "file": str(rel),
                "fix_hint": f"删除 {rel}",
                "auto_fixable": True,
            })
            reported.add(item)

    # 检测散落的编译产物文件（任意层级）
    _artifact_file_patterns = ["*.pyc", "*.pyo", "*.tsbuildinfo"]
    for pattern in _artifact_file_patterns:
        for fpath in skill_dir.rglob(pattern):
            if fpath in reported:
                continue
            # 跳过已被 __pycache__ 覆盖的（避免重复报告）
            if "__pycache__" in fpath.parts:
                continue
            issues.append({
                "rule": "artifact_file_exists",
                "severity": "error",
                "message": f"发现构建产物文件: {fpath.relative_to(skill_dir)}",
                "file": str(fpath.relative_to(skill_dir)),
                "fix_hint": f"删除 {fpath.name}",
                "auto_fixable": True,
            })
    # 检测 *.egg-info 目录（任意层级）
    for d in skill_dir.rglob("*.egg-info"):
        if d.is_dir() and d not in reported:
            issues.append({
                "rule": "ide_artifact_exists",
                "severity": "error",
                "message": f"发现 Python 包构建产物: {d.relative_to(skill_dir)}",
                "file": str(d.relative_to(skill_dir)),
                "fix_hint": "删除 *.egg-info 目录",
                "auto_fixable": True,
            })
    return issues


def auto_fix_ide_artifacts(skill_dir: Path) -> list[str]:
    """自动删除编译器/IDE/构建产物及隐藏文件/目录"""
    fixed = []
    deleted = set()  # 避免对已删除路径重复操作

    # 顶层名称匹配白名单
    for item in list(skill_dir.iterdir()):
        if item.name in _IDE_ARTIFACTS:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink(missing_ok=True)
            fixed.append(f"  已删除: {item.name}")
            deleted.add(item)

    # 任意层级的隐藏目录（以 '.' 开头）—— 深度优先，先删父目录
    for item in sorted(skill_dir.rglob("*"), key=lambda p: len(p.parts)):
        if item in deleted:
            continue
        # 若祖先已被删除则跳过
        if any(p in deleted for p in item.parents):
            continue
        if item.is_dir() and item.name.startswith("."):
            shutil.rmtree(item)
            fixed.append(f"  已删除: {item.relative_to(skill_dir)}")
            deleted.add(item)
        elif item.is_file() and item.name.startswith(".") and item.name != ".gitkeep":
            item.unlink(missing_ok=True)
            fixed.append(f"  已删除: {item.relative_to(skill_dir)}")
            deleted.add(item)

    # 散落文件
    for pattern in ["*.pyc", "*.pyo", "*.tsbuildinfo"]:
        for fpath in list(skill_dir.rglob(pattern)):
            if fpath in deleted or any(p in deleted for p in fpath.parents):
                continue
            if "__pycache__" in fpath.parts:
                continue
            fpath.unlink(missing_ok=True)
            fixed.append(f"  已删除: {fpath.relative_to(skill_dir)}")
    # egg-info
    for d in list(skill_dir.rglob("*.egg-info")):
        if d in deleted or any(p in deleted for p in d.parents):
            continue
        if d.is_dir():
            shutil.rmtree(d)
            fixed.append(f"  已删除: {d.relative_to(skill_dir)}")
    return fixed


# ─── Python AST 检查 ──────────────────────────────────────

class _InputCallFinder(ast.NodeVisitor):
    """收集所有 input() 调用的行号"""
    def __init__(self):
        self.calls: list[int] = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "input":
            self.calls.append(node.lineno)
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "input":
            self.calls.append(node.lineno)
        self.generic_visit(node)


class _BareExceptFinder(ast.NodeVisitor):
    """收集所有裸 except: 的行号"""
    def __init__(self):
        self.lines: list[int] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is None and node.name is None:
            self.lines.append(node.lineno)
        self.generic_visit(node)


def check_python_syntax(skill_dir: Path) -> list[dict]:
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            ast.parse(source)
        except SyntaxError as e:
            issues.append({
                "rule": "python_syntax_error",
                "severity": "error",
                "message": f"Python 语法错误: {e.msg} (第 {e.lineno} 行)",
                "file": str(py_file.relative_to(skill_dir)),
                "line": e.lineno,
                "auto_fixable": False,
            })
    return issues


def check_input_calls(skill_dir: Path) -> list[dict]:
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError:
            continue
        finder = _InputCallFinder()
        finder.visit(tree)
        src_lines = source.splitlines()
        for lineno in finder.calls:
            line_content = src_lines[lineno - 1].strip() if lineno <= len(src_lines) else ""
            issues.append({
                "rule": "input_call",
                "severity": "error",
                "message": "脚本不允许使用 input()（禁止交互式输入）",
                "file": str(py_file.relative_to(skill_dir)),
                "line": lineno,
                "content": line_content[:120],
                "auto_fixable": False,
            })
    return issues


def check_bare_except(skill_dir: Path) -> list[dict]:
    """检测裸 except:（不带异常类型的 except）"""
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError:
            continue
        finder = _BareExceptFinder()
        finder.visit(tree)
        src_lines = source.splitlines()
        for lineno in finder.lines:
            line_content = src_lines[lineno - 1].strip() if lineno <= len(src_lines) else ""
            issues.append({
                "rule": "bare_except",
                "severity": "error",
                "message": "不允许裸 except:（应改为 except Exception as e:）",
                "file": str(py_file.relative_to(skill_dir)),
                "line": lineno,
                "content": line_content[:120],
                "fix_hint": "改为 except Exception as e:",
                "auto_fixable": True,
            })
    return issues


def auto_fix_bare_except(skill_dir: Path, issues: list[dict]) -> list[str]:
    fixed = []
    files_to_fix = {i["file"] for i in issues if i["rule"] == "bare_except"}
    for rel_path in files_to_fix:
        fpath = skill_dir / rel_path
        content = fpath.read_text(encoding="utf-8")
        # 替换裸 except: 为 except Exception as e:
        new_content = re.sub(r'^(\s*)except\s*:', r'\1except Exception as e:', content, flags=re.MULTILINE)
        if new_content != content:
            fpath.write_text(new_content, encoding="utf-8")
            fixed.append(f"  已修复裸 except: {rel_path}")
    return fixed


# ─── PEP 723 ──────────────────────────────────────────────

def check_pep723(skill_dir: Path) -> list[dict]:
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        if "# /// script" not in text:
            issues.append({
                "rule": "missing_pep723",
                "severity": "warning",
                "message": "缺少 PEP 723 依赖声明（# /// script 块）",
                "file": str(py_file.relative_to(skill_dir)),
                "fix_hint": "在文件顶部添加 # /// script ... # /// 块",
                "auto_fixable": False,
            })
    return issues


# ─── 鉴权规范检测 ──────────────────────────────────────────

_SENSITIVE_PATTERNS = [
    (re.compile(r'(?:secret[_-]?key|secretKey|SECRET_KEY)\s*[=:]\s*["\'][^"\']+["\']', re.IGNORECASE), "secretKey 硬编码"),
    (re.compile(r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']', re.IGNORECASE), "密码硬编码"),
    (re.compile(r'(?:token|access_token|auth_token)\s*[=:]\s*["\'][^"\']+["\']', re.IGNORECASE), "token 硬编码"),
    (re.compile(r'Cookie\s*[=:]\s*["\'][^"\']+["\']', re.IGNORECASE), "Cookie 硬编码"),
]

# 跳过的行：注释中的说明性文字（如 "包括注释里也不允许" 这样的文档描述）
_SENSITIVE_SKIP_RE = re.compile(r'^(?:\s*#.*不允许|\s*#.*禁止|\s*#.*包括注释|\s*#\s*❌)', re.IGNORECASE)


def check_sensitive_hardcode(skill_dir: Path) -> list[dict]:
    """检测硬编码的 token/secretKey/password/Cookie"""
    issues = []
    for fpath in skill_dir.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.suffix in {".pyc", ".png", ".jpg", ".zip", ".skill"}:
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _SENSITIVE_SKIP_RE.search(line):
                continue
            for pattern, desc in _SENSITIVE_PATTERNS:
                if pattern.search(line):
                    issues.append({
                        "rule": "sensitive_hardcode",
                        "severity": "error",
                        "message": f"发现{desc}",
                        "file": str(fpath.relative_to(skill_dir)),
                        "line": i,
                        "content": line.strip()[:120],
                        "fix_hint": "使用环境变量或 SmartSSOSession 替代",
                        "auto_fixable": False,
                    })
    return issues


def check_smart_sso(skill_dir: Path) -> list[dict]:
    """检测内网请求是否使用 SmartSSOSession，而非裸 requests.Session"""
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.rglob("*.py"):
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        # 检测 requests.Session 的使用（排除 SmartSSOSession 继承场景）
        has_requests_session = False
        has_smart_sso = False
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if re.search(r'requests\.\s*Session\s*\(', stripped):
                has_requests_session = True
            if re.search(r'SmartSSOSession', stripped):
                has_smart_sso = True
        if has_requests_session and not has_smart_sso:
            issues.append({
                "rule": "requests_session_without_sso",
                "severity": "error",
                "message": "内网请求应使用 SmartSSOSession，而非裸 requests.Session",
                "file": str(py_file.relative_to(skill_dir)),
                "fix_hint": "替换为 SmartSSOSession（from ks_aimate.sso_login_client.session import SmartSSOSession）",
                "auto_fixable": False,
            })
    return issues


def check_get_username(skill_dir: Path) -> list[dict]:
    """检测脚本中是否有获取用户名的需求，是否使用了 get_username()"""
    issues = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for py_file in scripts_dir.rglob("*.py"):
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        # 检测是否有获取用户名的意图但未使用 get_username()
        username_intent_patterns = [
            re.compile(r'username\s*[=:]'),
            re.compile(r'get_username'),
            re.compile(r'user[_-]?name'),
            re.compile(r'kim[_-]?paired'),
            re.compile(r'session\.json'),
        ]
        has_username_intent = any(p.search(text) for p in username_intent_patterns[:2])
        has_get_username = username_intent_patterns[1].search(text) is not None
        has_manual_token_read = any(p.search(text) for p in username_intent_patterns[3:])

        if has_manual_token_read and not has_get_username:
            issues.append({
                "rule": "manual_token_read",
                "severity": "error",
                "message": "检测到手动读取本地文件获取用户名/token，应使用 get_username()",
                "file": str(py_file.relative_to(skill_dir)),
                "fix_hint": "使用 get_username()（from ks_aimate.wanqing_token_username import get_username）",
                "auto_fixable": False,
            })
    return issues


# ─── SKILL.md 中脚本调用方式检测 ──────────────────────────

def check_script_invocation(skill_dir: Path) -> list[dict]:
    """检测 SKILL.md 中是否使用正确的脚本调用方式（uv run / bun run）"""
    issues = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return issues

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # 跳过注释和示例中的说明
        if stripped.startswith("#") or stripped.startswith(">"):
            continue
        # 检测 Python 脚本调用是否使用 python3 而非 uv run
        if re.search(r'python3?\s+<skill_directory>/scripts/', stripped):
            issues.append({
                "rule": "python_direct_run",
                "severity": "error",
                "message": "Python 脚本应使用 uv run 而非 python3",
                "file": "SKILL.md",
                "line": i,
                "content": stripped[:120],
                "fix_hint": "改为 uv run <skill_directory>/scripts/xxx.py",
                "auto_fixable": True,
            })
        # 检测 TypeScript 脚本调用是否使用 node 而非 bun run
        if re.search(r'node\s+<skill_directory>/scripts/', stripped):
            issues.append({
                "rule": "node_direct_run",
                "severity": "error",
                "message": "TypeScript 脚本应使用 bun run 而非 node",
                "file": "SKILL.md",
                "line": i,
                "content": stripped[:120],
                "fix_hint": "改为 bun run <skill_directory>/scripts/xxx.ts",
                "auto_fixable": True,
            })
    return issues


# ─── 触发场景关键词检测 ────────────────────────────────────

_TRIGGER_KEYWORDS = re.compile(r'触发|唤醒|当.*说|用户说|以下场景唤醒|当用户|使用本技能|使用此技能|使用此 skill|使用此skill')
_NO_TRIGGER_KEYWORDS = re.compile(r'不触发|不唤醒|不负责|不支持|不适用|以下场景不唤醒|以下场景不触发|注意[：:]\S|仅处理|不处理|只处理')


def check_trigger_keywords(skill_dir: Path) -> list[dict]:
    """检测 description 是否包含触发场景和不触发场景关键词"""
    issues = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return issues

    content = skill_md.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return issues

    try:
        fm = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        return issues

    description = fm.get("description", "")
    if not description or not isinstance(description, str):
        return issues

    desc = description.strip()

    has_trigger = _TRIGGER_KEYWORDS.search(desc) is not None
    has_no_trigger = _NO_TRIGGER_KEYWORDS.search(desc) is not None

    if not has_trigger:
        issues.append({
            "rule": "missing_trigger_keywords",
            "severity": "warning",
            "message": "description 缺少触发场景关键词（建议包含「触发」「唤醒」「当用户说」等）",
            "file": "SKILL.md",
            "fix_hint": "在 description 中添加触发场景描述",
            "auto_fixable": False,
        })

    if not has_no_trigger:
        issues.append({
            "rule": "missing_no_trigger_keywords",
            "severity": "warning",
            "message": "description 缺少不触发场景关键词（建议包含「不触发」「不支持」「不负责」等）",
            "file": "SKILL.md",
            "fix_hint": "在 description 中添加不触发场景描述",
            "auto_fixable": False,
        })

    return issues


# ─── manifest.json ────────────────────────────────────────

def check_manifest(skill_dir: Path) -> list[dict]:
    issues = []
    manifest_path = skill_dir / "manifest.json"

    if not manifest_path.exists():
        issues.append({
            "rule": "manifest_missing",
            "severity": "error",
            "message": "缺少 manifest.json",
            "auto_fixable": False,
        })
        return issues

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        issues.append({
            "rule": "manifest_invalid_json",
            "severity": "error",
            "message": f"manifest.json JSON 格式错误: {e}",
            "auto_fixable": False,
        })
        return issues

    ks_meta = manifest.get("ks-meta", {})

    for field in ("name", "version", "ks-meta"):
        if field not in manifest:
            issues.append({
                "rule": f"manifest_missing_{field}",
                "severity": "error",
                "message": f"manifest.json 缺少字段: {field}",
                "auto_fixable": False,
            })

    legal_platforms = {"MyFlicker-Work", "MyFlicker-Code", "MyFlicker-Personal"}
    platforms = ks_meta.get("platform", [])
    if isinstance(platforms, list):
        illegal = [p for p in platforms if p not in legal_platforms]
        if illegal:
            issues.append({
                "rule": "manifest_illegal_platform",
                "severity": "error",
                "message": f"platform 包含非法值: {illegal}，合法值: {sorted(legal_platforms)}",
                "auto_fixable": False,
            })
    elif platforms:
        issues.append({
            "rule": "manifest_platform_not_list",
            "severity": "error",
            "message": "manifest.json platform 应为数组",
            "auto_fixable": False,
        })

    if "displayName" not in ks_meta:
        issues.append({
            "rule": "manifest_missing_displayName",
            "severity": "warning",
            "message": "manifest.json 缺少 ks-meta.displayName（建议添加人可读的中文名）",
            "auto_fixable": False,
        })

    # name 与文件夹名一致性
    manifest_name = manifest.get("name", "")
    folder_name = skill_dir.name
    if manifest_name and manifest_name != folder_name:
        issues.append({
            "rule": "manifest_name_mismatch",
            "severity": "error",
            "message": f"manifest.json name ({manifest_name}) 与文件夹名 ({folder_name}) 不一致",
            "auto_fixable": False,
        })

    return issues


# ─── SKILL.md frontmatter ──────────────────────────────────

def check_skill_md(skill_dir: Path) -> list[dict]:
    issues = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        issues.append({
            "rule": "skill_md_missing",
            "severity": "error",
            "message": "缺少 SKILL.md",
            "auto_fixable": False,
        })
        return issues

    content = skill_md.read_text(encoding="utf-8")
    lines = content.splitlines()
    line_count = len(lines)

    if line_count > 200:
        issues.append({
            "rule": "skill_md_too_long",
            "severity": "warning",
            "message": f"SKILL.md 超过 200 行（当前 {line_count} 行），建议将详细内容移至 references/",
            "auto_fixable": False,
        })

    has_frontmatter = content.startswith("---") and content.count("---") >= 2
    if not has_frontmatter:
        issues.append({
            "rule": "skill_md_no_frontmatter",
            "severity": "error",
            "message": "SKILL.md 缺少 YAML frontmatter (--- 块)",
            "auto_fixable": False,
        })
        return issues

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return issues

    fm_text = fm_match.group(1)

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        issues.append({
            "rule": "invalid_yaml_frontmatter",
            "severity": "error",
            "message": f"YAML frontmatter 解析失败: {e}",
            "auto_fixable": False,
        })
        return issues

    if not isinstance(fm, dict):
        issues.append({
            "rule": "frontmatter_not_dict",
            "severity": "error",
            "message": "frontmatter 必须是 YAML 字典",
            "auto_fixable": False,
        })
        return issues

    # name 字段
    name = fm.get("name", "")
    if not name:
        issues.append({
            "rule": "name_missing",
            "severity": "error",
            "message": "frontmatter 缺少 name 字段",
            "auto_fixable": False,
        })
    elif not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', str(name)):
        issues.append({
            "rule": "name_not_kebab_case",
            "severity": "error",
            "message": f"name '{name}' 不符合 kebab-case 规范",
            "auto_fixable": False,
        })

    # description 字段
    description = fm.get("description", "")
    if not description:
        issues.append({
            "rule": "description_missing",
            "severity": "error",
            "message": "frontmatter 缺少 description 字段",
            "auto_fixable": False,
        })
    elif isinstance(description, str):
        desc = description.strip()
        if len(desc) > 1024:
            issues.append({
                "rule": "description_too_long",
                "severity": "error",
                "message": f"description 超过 1024 字符（当前 {len(desc)} 字符）",
                "auto_fixable": False,
            })
        # description 不应包含尖括号
        if '<' in desc or '>' in desc:
            issues.append({
                "rule": "description_angle_brackets",
                "severity": "error",
                "message": "description 不应包含尖括号 (< 或 >)",
                "auto_fixable": False,
            })

    # 禁止 version 字段在 frontmatter 中
    if "version" in fm:
        issues.append({
            "rule": "version_in_frontmatter",
            "severity": "error",
            "message": "frontmatter 中禁止包含 version 字段（版本号应在 manifest.json 中）",
            "auto_fixable": True,
        })

    # 禁止 tags 字段在 frontmatter 中
    if "tags" in fm:
        issues.append({
            "rule": "tags_in_frontmatter",
            "severity": "warning",
            "message": "frontmatter 中不建议包含 tags 字段",
            "auto_fixable": True,
        })

    return issues


def auto_fix_frontmatter(skill_dir: Path, issues: list[dict]) -> list[str]:
    """自动修复 frontmatter 中的 version 和 tags 字段"""
    fixed = []
    rules_to_fix = {"version_in_frontmatter", "tags_in_frontmatter"}
    relevant = [i for i in issues if i["rule"] in rules_to_fix]
    if not relevant:
        return fixed

    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return fixed

    fm_text = fm_match.group(1)
    new_fm_text = fm_text

    # 移除 version 行
    new_fm_text = re.sub(r'^version:\s*.*\n', '', new_fm_text, flags=re.MULTILINE)
    # 移除 tags 行
    new_fm_text = re.sub(r'^tags:\s*.*\n', '', new_fm_text, flags=re.MULTILINE)

    if new_fm_text != fm_text:
        new_content = f"---\n{new_fm_text}---" + content[content.index("---", 3) + 3:]
        skill_md.write_text(new_content, encoding="utf-8")
        fixed.append("  已移除 frontmatter 中的 version/tags 字段")

    return fixed


# ─── 主流程 ──────────────────────────────────────────────

def validate_skill(skill_dir: Path, auto_fix: bool = False) -> dict:
    fixes_applied = []

    # 先做自动修复（清理后再检测）
    if auto_fix:
        ide_issues = check_ide_artifacts(skill_dir)
        if ide_issues:
            fixes_applied.extend(auto_fix_ide_artifacts(skill_dir))

        pycache_issues = check_pycache(skill_dir)
        if pycache_issues:
            fixes_applied.extend(auto_fix_pycache(skill_dir))

        abs_issues = check_absolute_paths(skill_dir)
        if abs_issues:
            fixes_applied.extend(auto_fix_absolute_paths(skill_dir, abs_issues))

        bare_issues = check_bare_except(skill_dir)
        if bare_issues:
            fixes_applied.extend(auto_fix_bare_except(skill_dir, bare_issues))

        fm_issues = check_skill_md(skill_dir)
        fm_fixable = [i for i in fm_issues if i["rule"] in {"version_in_frontmatter", "tags_in_frontmatter"}]
        if fm_fixable:
            fixes_applied.extend(auto_fix_frontmatter(skill_dir, fm_fixable))

    # 全量检查（修复后的状态）
    all_issues = (
        check_manifest(skill_dir)
        + check_skill_md(skill_dir)
        + check_absolute_paths(skill_dir)
        + check_ide_artifacts(skill_dir)
        + check_pycache(skill_dir)
        + check_python_syntax(skill_dir)
        + check_input_calls(skill_dir)
        + check_bare_except(skill_dir)
        + check_pep723(skill_dir)
        + check_sensitive_hardcode(skill_dir)
        + check_smart_sso(skill_dir)
        + check_get_username(skill_dir)
        + check_script_invocation(skill_dir)
        + check_trigger_keywords(skill_dir)
    )

    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]

    return {
        "name": skill_dir.name,
        "path": str(skill_dir),
        "status": "failed" if errors else ("warning" if warnings else "passed"),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": all_issues,
        "fixes_applied": fixes_applied,
    }


def main():
    parser = argparse.ArgumentParser(description="Skill 质量校验脚本（确定性规则，不依赖模型）")
    parser.add_argument("skill_dir", help="Skill 目录路径")
    parser.add_argument("--auto-fix", action="store_true",
                        help="自动修复可修复的问题")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式结果")
    parser.add_argument("--summary", action="store_true",
                        help="在 stderr 输出人类可读的摘要")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    if not skill_dir.is_dir():
        print(f"错误：目录不存在: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    result = validate_skill(skill_dir, auto_fix=args.auto_fix)

    status_icon = "✅" if result["status"] == "passed" else ("⚠️" if result["status"] == "warning" else "❌")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读输出
        print(f"\n{status_icon} {result['name']}: {result['status']} (errors: {result['error_count']}, warnings: {result['warning_count']})")

        if result["fixes_applied"]:
            print(f"\n  自动修复:")
            for fix in result["fixes_applied"]:
                print(f"    {fix}")

        if result["issues"]:
            print(f"\n  问题清单:")
            for issue in result["issues"]:
                loc = ""
                if issue.get("file"):
                    loc = f" [{issue['file']}:{issue.get('line', '')}]"
                severity_icon = "❌" if issue["severity"] == "error" else "⚠️"
                print(f"    {severity_icon} [{issue['rule']}] {issue['message']}{loc}")
                if issue.get("fix_hint"):
                    print(f"       修复建议: {issue['fix_hint']}")

    if args.summary:
        print(f"\n{'─'*55}", file=sys.stderr)
        print(f"校验完成  {result['name']}  {status_icon} {result['status']}", file=sys.stderr)
        if result["fixes_applied"]:
            print(f"自动修复项: {len(result['fixes_applied'])}", file=sys.stderr)
        print(f"结果已输出", file=sys.stderr)


if __name__ == "__main__":
    main()