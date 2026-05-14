#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ks_aimate",
# ]
#
# [tool.uv.sources]
# "ks_aimate" = { index = "kuaishou" }
#
# [[tool.uv.index]]
# name = "kuaishou"
# url = "https://pypi.corp.kuaishou.com/kuaishou/prod/+simple/"
# publish = false
# ///

"""
快手内网 SSO 登录客户端

使用 ks_aimate 包中的 SmartSSOSession 自动处理 SSO 认证。

Usage:
    uv run scripts/sso_session.py --target_url <目标URL>
    
Example:
    uv run scripts/sso_session.py --target_url https://xz.corp.kuaishou.com/is-intelligent-device
"""

import json
import argparse

from ks_aimate.sso_login_client import SmartSSOSession


def main() -> None:
    parser = argparse.ArgumentParser(description="快手内网 SSO 登录客户端")
    parser.add_argument("--target_url", type=str, required=True, help="需要访问的快手内网地址")
    parser.add_argument("--workspace", type=str, default=None, help="工作目录路径（可选）")
    args = parser.parse_args()

    # 创建 SSO 客户端（自动处理认证）
    client = SmartSSOSession()
    
    # 发起请求（自动注入认证信息）
    response = client.request("GET", args.target_url, args.workspace)
    
    # 打印结果
    print(f"\n✅ 请求成功！")
    print(f"状态码: {response.status_code}")
    print(f"URL: {response.url}\n")
    
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(response.text[:500])


if __name__ == "__main__":
    main()
