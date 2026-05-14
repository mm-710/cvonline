---
name: agent-browser
description: 浏览器自动化 CLI 工具。当用户需要与网站交互时使用，包括打开网页、填写表单、点击按钮、截图、数据抓取、Web 应用测试或任何浏览器自动化任务。不支持非浏览器场景，如纯后端请求、本地文件操作、桌面原生应用自动化。
allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*)
---

# Browser Automation with agent-browser

The CLI uses Chrome/Chromium via CDP directly. Install via `npm i -g agent-browser`, `brew install agent-browser`, or `cargo install agent-browser`. Run `agent-browser install` to download Chrome.

## Core Workflow

Every browser automation follows this pattern:

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i` (get element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Check result
```

## Command Chaining

Commands can be chained with `&&` in a single shell invocation. The browser persists between commands via a background daemon.

```bash
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser snapshot -i
agent-browser fill @e1 "user@example.com" && agent-browser fill @e2 "password123" && agent-browser click @e3
```

**When to chain:** Use `&&` when you don't need to read intermediate output. Run commands separately when you need to parse output first (e.g., snapshot to discover refs).

## Handling Authentication

| Approach | Best For |
|---|---|
| `--auto-connect` + `state save` | One-off tasks, user already logged in |
| `--profile <path>` | Recurring tasks with persistent profile |
| `--session-name <name>` | Auto-save/restore cookies + localStorage |
| `auth save` / `auth login` | Encrypted credential vault (recommended) |
| `state save` / `state load` | Manual save/load of session state |

```bash
# Auth vault (recommended): credentials encrypted, LLM never sees password
echo "$PASSWORD" | agent-browser auth save myapp --url https://app.example.com/login --username user --password-stdin
agent-browser auth login myapp

# State file: save after login, restore in future sessions
agent-browser state save ./auth.json
agent-browser state load ./auth.json
```

See [references/authentication.md](references/authentication.md) for OAuth, 2FA, cookie-based auth, and token refresh patterns.

## Essential Commands

```bash
# Navigation
agent-browser open <url>              # Navigate (aliases: goto, navigate)
agent-browser close                   # Close browser

# Snapshot
agent-browser snapshot -i             # Interactive elements with refs (recommended)
agent-browser snapshot -i -C          # Include cursor-interactive elements
agent-browser snapshot -s "#selector" # Scope to CSS selector

# Interaction (use @refs from snapshot)
agent-browser click @e1               # Click element
agent-browser click @e1 --new-tab     # Click and open in new tab
agent-browser fill @e2 "text"         # Clear and type text
agent-browser type @e2 "text"         # Type without clearing
agent-browser select @e1 "option"     # Select dropdown option
agent-browser check @e1               # Check checkbox
agent-browser press Enter             # Press key
agent-browser keyboard type "text"    # Type at current focus
agent-browser scroll down 500         # Scroll page

# Get information
agent-browser get text @e1            # Get element text
agent-browser get url                 # Get current URL
agent-browser get title               # Get page title

# Wait
agent-browser wait @e1                # Wait for element
agent-browser wait --load networkidle # Wait for network idle
agent-browser wait --url "**/page"    # Wait for URL pattern
agent-browser wait 2000               # Wait milliseconds
agent-browser wait --text "Welcome"   # Wait for text to appear
agent-browser wait "#spinner" --state hidden  # Wait for element to disappear

# Capture
agent-browser screenshot              # Screenshot to temp dir
agent-browser screenshot --full       # Full page screenshot
agent-browser screenshot --annotate   # Annotated screenshot with element labels
agent-browser pdf output.pdf          # Save as PDF

# Network
agent-browser network requests        # Inspect tracked requests
agent-browser network route "**/api/*" --abort  # Block matching requests
agent-browser network har start       # Start HAR recording
agent-browser network har stop ./capture.har    # Stop and save HAR

# Downloads
agent-browser download @e1 ./file.pdf           # Click element to trigger download
agent-browser wait --download ./output.zip      # Wait for download to complete

# Diff (compare page states)
agent-browser diff snapshot                     # Compare current vs last snapshot
agent-browser diff screenshot --baseline b.png  # Visual pixel diff
agent-browser diff url <url1> <url2>            # Compare two pages
```

## Key Concepts

- **Refs** (`@e1`, `@e2`): Invalidated on page change — always re-snapshot after navigation, form submit, or dynamic content load.
- **Sessions**: Use `--session <name>` for parallel automations; always `close` when done to avoid leaked processes.
- **Vision Mode**: `screenshot --annotate` overlays numbered labels; refs are cached so you can interact immediately.
- **Semantic Locators**: `agent-browser find text "Sign In" click` — use when refs are unavailable.
- **Security**: `--content-boundaries`, `AGENT_BROWSER_ALLOWED_DOMAINS`, `AGENT_BROWSER_ACTION_POLICY` are all opt-in.

## Deep-Dive Documentation

| Reference | When to Use |
|---|---|
| [references/usage-patterns.md](references/usage-patterns.md) | Common patterns: forms, auth, iframes, data extraction, mobile |
| [references/advanced-features.md](references/advanced-features.md) | Security, diffing, timeouts, eval, config, browser engines |
| [references/commands.md](references/commands.md) | Full command reference with all options |
| [references/snapshot-refs.md](references/snapshot-refs.md) | Ref lifecycle, invalidation rules, troubleshooting |
| [references/session-management.md](references/session-management.md) | Parallel sessions, state persistence, concurrent scraping |
| [references/authentication.md](references/authentication.md) | Login flows, OAuth, 2FA handling, state reuse |
| [references/video-recording.md](references/video-recording.md) | Recording workflows for debugging and documentation |
| [references/profiling.md](references/profiling.md) | Chrome DevTools profiling for performance analysis |
| [references/proxy-support.md](references/proxy-support.md) | Proxy configuration, geo-testing, rotating proxies |

## Ready-to-Use Templates

| Template | Description |
|---|---|
| [templates/form-automation.sh](templates/form-automation.sh) | Form filling with validation |
| [templates/authenticated-session.sh](templates/authenticated-session.sh) | Login once, reuse state |
| [templates/capture-workflow.sh](templates/capture-workflow.sh) | Content extraction with screenshots |

```bash
./templates/form-automation.sh https://example.com/form
./templates/authenticated-session.sh https://app.example.com/login
./templates/capture-workflow.sh https://example.com ./output
```
