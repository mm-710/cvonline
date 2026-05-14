---
name: gym-query
description: 查询快手内网健身房信息，包括健身房列表、教练信息、团课安排等。当用户询问快手健身房、教练、团课安排、预约信息时触发。不支持团课预约操作、非快手健身房查询、教练排班修改等管理功能。
---

# kwai-gym

快手内网健身房信息查询，包含元中心和万家灯火两个健身房。

## 说明

认证由脚本内部自动处理，无需手动登录或传入 token。

## 已知健身房

| gym_id | shop_id | 名称 | 位置 |
|--------|---------|------|------|
| 2 | 4655 | 元中心健身房 | 北京市海淀区西二旗中路 29 号元中心地下 1 层南区 |
| 3 | 4247 | 万家灯火健身房 | 北京市海淀区唐家岭路 188 号万家灯火地下 1 层 |
| 4 | - | 万家灯火运动场（试运行） | 北京市海淀区唐家岭路 188 号万家灯火北侧 |

> `gym_id` 是快手内部 ID，`shop_id` 是青橙健身系统 ID（用于教练、团课接口）。

## 脚本调用

直接调用 `client.py` 执行查询，认证由脚本内部自动处理，无需人工干预：

**命令示例：**

```bash
uv run <skill_directory>/scripts/client.py list
uv run <skill_directory>/scripts/client.py teachers 4655
uv run <skill_directory>/scripts/client.py lessons 4247 2026-04-02
uv run <skill_directory>/scripts/client.py detail 4655
```

## 教练信息处理

**⚠️ 重要：正确区分私教/团课教练**

- API返回的 `support_private` 和 `support_public` 字段**已废弃**，所有值都是 `false`
- `priority` 字段表示教练在列表中的**展示优先级**，不代表职能分类
- **禁止使用 `priority` 或废弃字段来区分私教/团课教练**

### API权限说明

教练API使用 `show_all=1` 参数，返回**完整的管理级数据**（包括电话、微信），这是因为：

1. **内部工具定位** - 面向快手员工，不是公开页面
2. **SSO认证保护** - 需要通过快手SSO登录才能访问
3. **实用性考虑** - 员工需要联系教练预约私教或咨询

**前端页面**可能不传 `show_all` 参数，因此不显示联系方式，这是前端的**隐私保护设计**。

### 隐私保护选项

如果需要隐藏敏感信息，可以在展示时过滤：

```python
# 过滤敏感字段
safe_fields = ['username', 'avatar', 'score', 'description', 'short_description']
for teacher in teachers:
    display_teacher = {k: teacher[k] for k in safe_fields if k in teacher}
```

或在SKILL.md中指示Agent：
> "展示教练信息时，仅显示姓名、头像、评分和介绍，不展示电话和微信。"

### 推荐展示方式

**方式1：完整信息（推荐）**
展示姓名、电话、微信，方便员工联系：

```
元中心健身房共有 27 位教练：

1. 刘莹 - 微信：安稳 | 电话：17606383561
2. 王晨 - 电话：15910431050
3. 肖涵 - 微信：肖涵Austin | 电话：17614456363
   ...
```

**方式2：仅基础信息**
如果担心隐私，仅展示姓名和评分：

```
元中心健身房共有 27 位教练：

1. 刘莹 - 评分：5.0
2. 王晨 - 评分：5.0
3. 肖涵 - 评分：5.0 | 简介：曾服役于中国人民解放军...
   ...
```

**方式2：动态反推团课教练**
如果用户明确要求区分团课教练，需要**额外查询团课API**来动态判断：

1. 调用 `lessons` 命令查询最近一周的团课排期
2. 从 `schedules[].teacher.username` 中提取出现过的教练名字
3. 将教练列表分为"团课教练"和"其他教练"展示

示例逻辑：
```python
# 查询近期团课
lessons_recent = get_lessons(shop_id, recent_dates)
group_teachers = set(schedule['teacher']['username'] for schedule in lessons_recent)

# 分类展示
for teacher in all_teachers:
    if teacher['username'] in group_teachers:
        print(f"团课教练：{teacher['username']}")
    else:
        print(f"其他教练：{teacher['username']}")
```

## 注意事项

- **团课预约**：仅支持查询，无法自动化预约。当用户提出预约请求时，使用以下标准回复：
  > 「团课预约需要在快手健身房小程序或网页端手动操作，我帮你查到了以下课程信息，请前往 [快手健身房小程序](https://xz.corp.kuaishou.com/kwai-gym-h5) 自行预约：[课程列表]」

- **日期推断**：团课查询（`lessons` 命令）需要具体日期参数。**禁止 AI 自行推断或补充日期**；若用户未提供日期，必须主动询问，如「请问您想查哪天的团课？（格式：YYYY-MM-DD）」。

- **健身房 ID**：仅支持已知健身房（元中心 shop_id=4655，万家灯火 shop_id=4247）。若用户询问其他位置的健身房，**禁止 AI 自行补充 shop_id**，应明确告知不支持。

## 参考文档

- [API 接口文档](references/api-map.md)
- [数据模型定义](references/data-models.md)
