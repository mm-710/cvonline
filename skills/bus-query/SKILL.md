---
name: bus-query
description: 查询快手公司班车时刻表。当用户询问"班车"、"通勤车"、"接驳车"、"几点有车"、"今天的班车"、"元中心班车"、"西二旗班车"等相关问题时触发此技能。支持按园区、线路类型（接驳/通勤）、日期进行筛选，并记忆用户的园区偏好。仅支持快手公司内部班车查询（只读），不支持高铁/地铁/公交等公共交通查询，不支持收藏、提醒、预约等写操作。
---

# 班车查询

## 功能说明

> ⚠️ 本 Skill 为**只读查询**，仅支持快手公司内部通勤/接驳班车。**不支持**收藏、提醒、预约等写操作，**不支持**高铁、地铁、公交等公共交通查询。若用户请求超出上述范围，直接礼貌告知不支持，无需调用脚本。

通过快手行政平台 API 查询公司班车时刻表，支持：
- 按日期查询（默认今天，支持"明天"、"周五"、"4月5日"等自然语言）
- 按园区筛选（元中心、万家灯火大厦，或全部）
- 按线路类型筛选（接驳班车、通勤班车，或全部）
- 记忆用户常用园区偏好

## 执行流程

### Step 1：解析用户意图

**首先判断请求是否在支持范围内：**

| 用户意图 | 处理方式 |
|---------|----------|
| 询问收藏线路、设置提醒、预约班车 | 直接回复：「本功能暂不支持，班车查询 Skill 目前仅支持查询时刻表。」不调用脚本 |
| 询问高铁、地铁、公交、航班等公共交通 | 直接回复：「本 Skill 仅支持快手公司内部班车查询，公共交通信息请通过其他渠道查询。」不调用脚本 |
| 询问班车时刻、是否有车、几点发车等 | 继续执行后续步骤 |

确认属于班车查询范围后，从用户输入中提取以下信息（均为可选，未提及则使用默认值）：

| 参数 | 默认值 | 用户表达关键词 |
|------|--------|---------------|
| 日期 `date` | 今天（YYYY-MM-DD） | "明天"、"周五"、"4月5日" |
| 园区 `gardenId` | 优先使用记忆偏好，无则 `-1`（全部） | "元中心"(98)、"万家灯火"(93) |
| 线路类型 `lineType` | `ALL_TYPE` | "接驳"→`REVCEIVE`、"通勤"→`FREQUENT_SHUTTLE` |

### Step 2：检查用户园区偏好记忆

使用 `search_memory` 搜索关键词「班车 园区 偏好」，查看是否有已保存的园区偏好。如有，当用户未指定园区时自动使用记忆中的 gardenId。

### Step 3：执行查询

直接调用 `query_bus.py` 执行查询，脚本会自动处理 SSO 认证：

**命令示例：**

```bash
# 查询今天的全部班车（使用默认参数）
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_bus.py

# 查询元中心园区的班车
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_bus.py --garden 98

# 查询接驳班车
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_bus.py --type REVCEIVE

# 查询指定日期的班车
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_bus.py --date 2026-04-10

# 组合参数查询
uv run --refresh-package ks_aimate <skill_directory>/scripts/query_bus.py --garden 98 --type ALL_TYPE --date 2026-04-10
```

**参数说明：**
- `-g, --garden`：园区 ID（-1=全部，98=元中心，93=万家灯火大厦）
- `-t, --type`：线路类型（ALL_TYPE / REVCEIVE / FREQUENT_SHUTTLE）
- `-d, --date`：日期（格式 YYYY-MM-DD，默认今天）

### Step 4：格式化输出

**【强制】只展示 `isValid=TRUE` 的有效班次，绝对不展示已过或 `isValid=FALSE` 的班次，不展示任何「完整时刻表」「已过」列表。**

#### 规则1：时间格式
- 所有时间一律使用 **24小时制**（如 `20:15`，禁止写成「下午8:15」「8:15 PM」「晚上8点」）

#### 规则2：无有效班次
- 若某条线路无任何 `isValid=TRUE` 的班次 → **直接跳过该线路，不展示**
- 若所有线路均无有效班次 → 只输出一句话：「今天的班车已结束，没有更多班次了。」
- **禁止附加任何其他引导语**（不推荐地铁、不建议查官网等）

#### 规则3：输出格式（用 Markdown 表格展示班次，每条线路独立呈现）

```
🚌 **线路名称**
📍 起点：XXX → 终点：XXX
📝 候车说明（description 字段内容）

| 发车时间 | 座位数 |
|----------|--------|
| 20:15    | 47     |
| 20:20    | 49     |
| 20:25    | 49     |
```

- 每条有效线路之间用空行分隔
- 发车时间按升序排列
- **不加「✅」「⏳」等无关符号前缀，表格本身已代表可乘坐**
- **不添加总结语、建议语或额外说明**

### Step 5：更新园区偏好记忆

若用户本次明确指定了园区（gardenId ≠ -1），使用 `update_memory` 保存：
- category: `user_info`
- 内容：`用户常用班车园区：[chineseName]（gardenId=[id]）`

## 枚举值参考

| 字段 | 值 | 含义 |
|------|-----|------|
| gardenId | -1 | 全部园区 |
| gardenId | 98 | 北京·元中心 |
| gardenId | 93 | 北京·万家灯火大厦 |
| lineType | ALL_TYPE | 全部线路 |
| lineType | REVCEIVE | 地铁接驳班车 |
| lineType | FREQUENT_SHUTTLE | 通勤班车 |
| isValid | TRUE | 班次当前有效（可乘坐） |
| isValid | FALSE | 班次已过或尚未开放 |

## 典型用法示例

| 用户输入 | 查询参数 |
|---------|---------|
| 查今天的班车 | date=今天, gardenId=-1, lineType=ALL_TYPE |
| 元中心今晚几点有班车 | date=今天, gardenId=98, lineType=ALL_TYPE |
| 明天早上西二旗的接驳车 | date=明天, gardenId=98, lineType=REVCEIVE |
| 下周一万家灯火的通勤班车 | date=下周一, gardenId=93, lineType=FREQUENT_SHUTTLE |

## 详细接口文档

参见 `reference/api-schema.md`。
