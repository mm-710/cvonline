# Data Agent API 集成指南

## 配置参数（公共变量）

### 认证配置
- **dataAgentId**: `515`

## 完整调用流程

### 第一步:获取 Chat Session ID 与用户凭证

**⚠️ 重要：每次查询必须重新读取最新信息，禁止从上下文中复用之前获取的数据。**

**获取 Session ID 的方法（根据平台环境变量决定）：**

1. 首先读取环境变量 `KS_AGENT_PLATFORM` 的值
2. 根据平台选择获取方式：
   - **如果是 `codeflicker`**：从 `<current_thread />` 里获取 `id` 字段的值
   - **如果是 `myflicker`**：使用 `session_status` 工具获取当前 session id

获取到的值即为 `CHAT_SESSION_ID` 参数。

### 第二步：执行 Python 脚本发送请求并处理流式返回

**⚠️⚠️⚠️ 以下 Python 脚本必须作为一个完整命令执行,禁止拆分、禁止修改、禁止添加额外输出。直接复制使用,只替换 `CHAT_SESSION_ID`、`QUESTION`、`dataAgentId` 两个变量的值。**

**强调** QUESTION 变量必须是用户最近一次提问的原文,禁止任何形式的改写,缩减,翻译；必须完整传递用户的原始问题。dataAgentId 变量必须从上述认证配置中获取，禁止随意推断。

执行时,通过命令行参数传入三个值:

```bash
uv run scripts/data_agent_query.py "<CHAT_SESSION_ID>" "<QUESTION>" "{dataAgentId}"
```

示例:

```bash
uv run scripts/data_agent_query.py "thread-abc123" "查询最近7天各商品类目的订单量" "515"
```

---

## 注意事项

- **每次查询必须重新获取 `CHAT_SESSION_ID`，禁止复用上下文中的值**
- 返回的 `content` 可能包含 markdown、SQL 或表格，注意格式化展示
- 本地字典文件由脚本自动维护（路径根据环境变量 `KS_AGENT_PLATFORM` 动态确定：`~/.codeflicker/` 或 `~/.myflicker/` 或 `~/.default/`），用于多轮对话时传递 `sessionId`
- 若接口返回的 `session_id` 为 `null`，则本次对话不更新字典

## 调用原则

### 1. 原文转发原则
将用户的问题原封不动填入 `question` 字段，不要改写、缩减或翻译。

### 2. 完整上下文传递原则
如果用户的问题中包含 SQL 代码、URL 链接、表名等关键信息，必须一并填入 `question`。

### 3. 结果透传原则
Data Agent 返回什么，就呈现什么，不做额外过滤或修改。

## 触发判断逻辑

以下关键词出现时，立即调用 Data Agent：

- **数据查询类**: 查询数据、取数、数据统计、用户数、GMV、DAU、订单量、转化率、留存率
- **SQL 相关类**: SQL、查询语句、建表语句、hive、Spark SQL
- **表相关类**: Hive表、数据表、字段、分区、表结构、血缘、负责人
- **看板分析类**: KwaiBI、看板、数据看板、kwaibi.corp.kuaishou.com、天玑、adsdata、adsdata.corp.kuaishou.com、多维分析、OLAP、天策
- **业务数据类**: 直播间、电商、订单、商品、用户画像、活跃用户、新增用户
- **数据资产类**: 数据集、数据资产、数仓、数据专题、datasetId、dataset
- **数据集查询类**: 数据集+数字编号（如"数据集12"、"数据集45"）、周同比、环比、占比分析、按日累计、归因分析、RUNNING_SUM、YEAR_ON_YEAR
- **权限运维类**: 数据权限、申请权限、数据安全
