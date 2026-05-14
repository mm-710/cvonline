#!/usr/bin/env node
/**
 * fetch-page-style.js
 *
 * 跨平台（Windows / macOS / Linux），只需 Node.js 18+，无需额外安装依赖。
 *
 * 用法:
 *   node fetch-page-style.js                   列出所有可用风格
 *   node fetch-page-style.js --list            同上（显式模式）
 *   node fetch-page-style.js --id <style-id>   获取指定风格完整规范
 *   node fetch-page-style.js --help            显示帮助
 *
 * 示例:
 *   node fetch-page-style.js
 *   node fetch-page-style.js --id tech
 *   node fetch-page-style.js --id finance-style
 */

const BASE_URL = 'https://codeflicker.corp.kuaishou.com/api/flow/skills/page-styles';

// ---------- 工具函数 ----------

function usage() {
  console.log(`用法:
  node fetch-page-style.js                   列出所有可用风格
  node fetch-page-style.js --list            同上
  node fetch-page-style.js --id <style-id>   获取指定风格完整规范
  node fetch-page-style.js --help            显示帮助

示例:
  node fetch-page-style.js
  node fetch-page-style.js --id tech
  node fetch-page-style.js --id finance-style`);
}

function die(msg) {
  console.error(`[ERROR] ${msg}`);
  process.exit(1);
}

// ---------- HTTP 请求（使用 Node.js 18+ 内置 fetch）----------

async function fetchJSON(url) {
  let res;
  try {
    res = await fetch(url);
  } catch (e) {
    die(`网络请求失败: ${e.message}\n请检查网络连接或 VPN 状态。`);
  }

  const text = await res.text();

  if (!res.ok) {
    let msg = text;
    try {
      const obj = JSON.parse(text);
      msg = obj.message || obj.error || text;
    } catch (_) {}
    die(`HTTP ${res.status}: ${msg}`);
  }

  try {
    return JSON.parse(text);
  } catch (_) {
    die(`响应解析失败，原始内容:\n${text}`);
  }
}

// ---------- 功能实现 ----------

async function listStyles() {
  const data = await fetchJSON(BASE_URL);
  const styles = data.data.result;
  console.log(`\n可用风格列表: ${JSON.stringify(styles)}`);
}

async function getStyle(id) {
  if (!id) die('--id 参数不能为空');
  const data = await fetchJSON(`${BASE_URL}/${id}`);
  const r = data.data.result;
  console.log(r.detail);
}

// ---------- 参数解析 ----------

async function main() {
  // 检查 Node.js 版本（需要 18+ 内置 fetch）
  const [major] = process.versions.node.split('.').map(Number);
  if (major < 18) {
    die(`需要 Node.js 18 或以上版本（当前: ${process.versions.node}）\n请升级 Node.js: https://nodejs.org/`);
  }

  const args = process.argv.slice(2);
  const cmd = args[0] || '';

  switch (cmd) {
    case '':
    case '--list':
      await listStyles();
      break;
    case '--id':
      await getStyle(args[1] || '');
      break;
    case '--help':
    case '-h':
      usage();
      break;
    default:
      console.error(`[ERROR] 未知参数: ${cmd}\n`);
      usage();
      process.exit(1);
  }
}

main().catch(e => die(e.message));
