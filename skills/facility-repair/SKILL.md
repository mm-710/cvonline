---
name: facility-repair
description: 提供快手行政报修工单服务，支持提交报修工单和查询工单进度。当用户说「帮我报修」「提交维修工单」「我要报修」「查询工单」「我的报修进度」「空调太热/太冷」「暖通报修」「设施故障」「修灯/修空调/打扫卫生」「提交维修申请」等行政报修相关操作时使用。支持：提交报修工单、查询工单进度（进行中/待评价/已完成）。不支持外卖订餐/取消订单、访客预约、会议室预订、班车查询等非报修场景。
---

# 快手行政服务报修 Skill

## 功能范围

| 操作 | 脚本动作 |
|------|---------|
| 查询工单进度（进行中/待评价/已完成） | `query_orders` |
| 提交报修工单 | `submit` |
| 查询可用的园区/楼栋/楼层/服务类型 | `get_enums` |

---

## 操作一：查询工单进度

直接调用脚本，自动处理 SSO 认证：

```bash
# 查询进行中工单
uv run --refresh-package ks_aimate <skill_directory>/scripts/repair_api.py --action query_orders --type 1

# 查询待评价工单
uv run --refresh-package ks_aimate <skill_directory>/scripts/repair_api.py --action query_orders --type 2

# 查询已完成工单
uv run --refresh-package ks_aimate <skill_directory>/scripts/repair_api.py --action query_orders --type 3
```

如需全部状态，分别运行 `--type 1`、`--type 2`、`--type 3` 并汇总展示。

**工单状态（state 字段）**：`PROCESSING`=进行中，`FINISH`=待评价，`FOLLOWUP`=已评价，`CANCEL`=已取消

**展示规范**：必须直接使用接口返回的 `location` 字段原值展示位置，禁止修改、简化或推断。必须包含 `location`、`description`、`type`、`state`、`date` 所有字段。

---

## 操作二：提交报修工单

### 第一步：信息收集

**必填项**：
1. 问题描述（至少 5 个字）
2. **园区 + 楼栋 + 楼层**（必须从用户描述中提取，不得假设默认园区）
3. 联系手机号（必须是 11 位大陆手机号）

### 第二步：调用 get_enums 获取枚举（必须执行）

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/repair_api.py --action get_enums
```

从返回结果中：
1. 找到对应的 `parkId`（园区）
2. 找到用户说的楼栋（如 T1、T2、C）→ 获取 `buildId`
3. 找到用户说的楼层（如 4层、2层、5FC）→ 获取 `floorId`
4. 找到问题类型对应的 `typeId`（子类型 ID，不能用父分类 ID）

> 楼层匹配策略和园区关键词速查，参见 `references/floor-matching.md`  
> 问题类型关键词匹配表，参见 `references/type-keywords.md`  
> 枚举数据结构和完整服务类型列表，参见 `references/enums.md`

**关键原则（禁止违反）**：
- 禁止使用默认园区/楼栋，用户未明确说明园区时必须询问
- 禁止硬编码任何 ID，必须通过 `get_enums` 动态查询
- 当多个楼层匹配时，必须向用户确认

### 第三步：提交工单

```bash
uv run --refresh-package ks_aimate <skill_directory>/scripts/repair_api.py --action submit \
  --phone   13800138000 \
  --parkId  58 \
  --buildId 76 \
  --floorId 334 \
  --typeId  101 \
  --description "工位附近空调温度太低，请调节"
```

**关键字段说明**：

| 脚本参数 | 实际发送字段 | 注意 |
|---------|------------|------|
| `buildId` | `buildingId` | 脚本自动映射 |
| `typeId` | `type` | 脚本自动映射 |
| — | `typeText` | 脚本自动推导，缺失导致服务端 500 |

> `typeText` 由脚本根据 `typeId` 自动调用 `get_service_types()` 推导，无需手动传入。

**成功判断**：
- 仅当脚本返回 `verifiedCreated=true` 才可对用户说"提交成功"
- 若返回 `code=0` 但 `verifiedCreated=false`，必须按"核验未通过"口径回复

**关于超时**：submit 接口服务端处理慢（触发工单分配/通知等异步流程），脚本发出请求后即视为成功，不等待服务端完整响应。

---

## 回复规范

用户只看到结果，感受不到任何内部执行过程：
- 禁止暴露技术参数（parkId、buildId、floorId、typeId 等内部 ID）
- 禁止提及枚举查询、脚本执行等内部操作
- 所有答复必须来自脚本输出或接口返回原始数据，严禁推测补全
- 位置信息必须使用接口返回的 `location` 字段原值

> 详细回复示例和违规示例，参见 `references/reply-examples.md`

---

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| HTTP 500 NPE | 脚本已自动推导 typeText，如仍报错检查 typeId 是否为叶子节点 |
| HTTP 401 | 脚本自动重新认证 |
| 网络超时 | 稍后重试 |
| 手机号格式错误 | 拒绝提交并提示输入 11 位大陆手机号 |
