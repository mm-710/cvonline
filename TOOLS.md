# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## ⚠️ 强制规范

### 定时任务（scheduled-kim-message）

**用户要求设置定时提醒/播报/任务时，必须使用 `scheduled-kim-message` skill，禁止直接用 cron。**

**delivery 格式强制要求**：

```json
{
  "delivery": {
    "mode": "announce",
    "channel": "kim",
    "to": "username:${username}"
  }
}
```

- `channel` 必须是 `"kim"`
- `to` 必须是 `"username:${username}"` 格式（username 从 system prompt 或 /data/aime/$SANDBOX_UUID/user.txt 读取）
- `sessionTarget` 推荐用 `"isolated"`
- `payload.kind` 推荐用 `"agentTurn"`

### Python 执行规范

- **执行 Python 脚本时必须使用 `uv run`**，禁止直接调用 `python` 或 `python3`
- 示例：`uv run script.py` ✅ | `python script.py` ❌ | `python3 script.py` ❌
- 如需指定包版本：`uv run --with <package> script.py`
- 如需使用项目环境：`uv run --refresh-package ks_aimate script.py`

### 文件操作规范

**文件名生成**：

- **禁止生成包含空格的文件名**，使用下划线 `_` 或连字符 `-` 代替
- 示例：`skills_config.json` ✅ | `skills config.json` ❌
- 原因：空格在 shell 命令中需要转义，容易导致路径解析错误

**文件路径处理**：

- **读文件时必须用引号包裹路径**，避免特殊字符（空格、`$`、`&` 等）被 shell 解析
- 示例：`cat "/path/with space/file.txt"` ✅ | `cat /path/with space/file.txt` ❌
- 推荐：使用双引号 `"` 而非单引号 `'`（支持变量展开）

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
