#!/bin/bash
set -euo pipefail
# 班车查询辅助脚本
# ⚠️  登录认证必须通过 kuaishou-sso-login Skill 完成，本脚本不自行执行登录。
#
# 用法:
#   bash query-bus.sh [选项]
#
# 选项:
#   -g, --garden   园区 ID（默认 -1=全部，98=元中心，93=万家灯火大厦）
#   -t, --type     线路类型（默认 ALL_TYPE，可选 REVCEIVE / FREQUENT_SHUTTLE）
#   -d, --date     日期（默认今天，格式 YYYY-MM-DD）
#   -h, --help     显示帮助

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

GARDEN_ID=-1
LINE_TYPE="ALL_TYPE"
DATE=$(date +%Y-%m-%d)

show_help() {
    echo "班车查询脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -g, --garden ID    园区 ID（-1=全部，98=元中心，93=万家灯火大厦）"
    echo "  -t, --type TYPE    线路类型（ALL_TYPE / REVCEIVE / FREQUENT_SHUTTLE）"
    echo "  -d, --date DATE    日期（格式 YYYY-MM-DD，默认今天）"
    echo "  -h, --help         显示帮助"
    echo ""
    echo "⚠️  注意：若未登录快手内网，请先使用 kuaishou-sso-login Skill 完成登录。"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--garden) GARDEN_ID="$2"; shift 2 ;;
        -t|--type)   LINE_TYPE="$2"; shift 2 ;;
        -d|--date)   DATE="$2"; shift 2 ;;
        -h|--help)   show_help; exit 0 ;;
        *) echo -e "${RED}未知参数: $1${NC}"; show_help; exit 1 ;;
    esac
done

# ─── Step 0：确保 agent-browser 已安装 ─────────────────────────────────────
if ! command -v agent-browser &> /dev/null; then
    echo -e "${YELLOW}agent-browser 未安装，正在自动安装...${NC}"
    npm install -g agent-browser
    if [ $? -ne 0 ]; then
        echo -e "${RED}安装失败，请手动执行: npm install -g agent-browser${NC}"
        exit 1
    fi
fi

# ─── Step 1：先导航到快手内网域，确保 Cookie 可被正确携带 ──────────────────
echo -e "${GREEN}查询班车信息...${NC}"
echo "园区: $GARDEN_ID | 线路类型: $LINE_TYPE | 日期: $DATE"
echo "→ 导航到快手内网页面..."
agent-browser open https://xz.corp.kuaishou.com/bus/lines 2>/dev/null || true
sleep 2

# ─── Step 2：在快手内网页面下注入 fetch 查询 ──────────────────────────────
RESULT=$(agent-browser eval "
  fetch('https://xz.corp.kuaishou.com/is-parking/api/bus/user/line', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify({gardenId: $GARDEN_ID, lineType: '$LINE_TYPE', date: '$DATE'})
  }).then(r => {
    if (r.status === 401) return JSON.stringify({__status: 401, __auth_error: true});
    return r.text().then(t => {
      try {
        const d = JSON.parse(t);
        if (d.code !== 0) return JSON.stringify({__status: 200, __api_error: true, code: d.code, message: d.message});
        return t;
      } catch(e) { return JSON.stringify({__status: 200, __parse_error: true}); }
    });
  }).catch(e => JSON.stringify({__network_error: true, error: e.message}))
" 2>/dev/null || echo '{"__agent_error": true}')

# ─── Step 3：检测是否需要登录 ──────────────────────────────────────────────
if echo "$RESULT" | grep -q '"__auth_error"\|"__agent_error"\|"__network_error"'; then
    echo -e "${RED}未登录快手内网，无法查询班车。${NC}"
    echo ""
    echo "请按以下步骤操作："
    echo "  1. 使用 kuaishou-sso-login Skill 完成快手内网登录"
    echo "  2. 登录成功后重新运行本脚本"
    exit 1
fi

# ─── Step 4：输出结果 ─────────────────────────────────────────────────────
echo ""
echo "$RESULT"
