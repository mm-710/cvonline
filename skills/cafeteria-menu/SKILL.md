---
name: cafeteria-menu
description: 根据员工园区、档口、餐型与口味偏好，查询公司食堂堂食菜单（早餐/午餐/晚餐/夜宵），按偏好过滤并返回推荐清单。仅支持堂食菜品查询，不支持外卖下单/查单/取消。
---

# 食堂堂食菜单查询 Skill

## 能力边界（必须遵守）

- 本 Skill **只支持食堂堂食菜品查询/推荐**。
- 本 Skill **不支持** 外卖订餐相关操作（下单、查订单、取消订单、配送进度等）。
- 用户出现外卖意图时，应明确告知：请使用 `cafeteria-takeout` Skill。

### 外卖意图标准路由回复模板

当用户表达外卖相关需求时，统一回复：

```text
当前能力：我仅支持食堂堂食菜单查询（按园区/档口/餐型/口味）。
暂不支持：外卖下单、外卖查单、取消外卖订单。
建议操作：请使用 cafeteria-takeout Skill 处理外卖相关需求。
```

## 前置条件

- 查询脚本已集成 `SmartSSOSession`，认证由脚本内部自动处理，无需人工干预
- 目标站点：`https://xz.corp.kuaishou.com`

## 参数说明

| 参数 | 是否必填 | 说明 |
|------|----------|------|
| `garden_name` | **必填** | 园区名称/简称，如 `元中心`、`杭州`，支持模糊匹配 |
| `area_name` | 可选 | 档口/区域名称，如 `西部马华`；不填则查询园区全部档口 |
| `meal_type` | 可选 | 餐型：`1=早餐` `2=午餐` `3=晚餐` `4=夜宵`；不填则自动推断 |
| `taste_preference` | 可选 | 口味偏好，如 `辣`、`低热量`、`不要葱`；留空则返回全部菜单 |
| `custom_date` | 可选 | 指定日期，格式 `YYYY-MM-DD`；不填则默认今天 |
| `max_results` | 可选 | 最多返回菜品数（默认 50） |

> 缺少 `garden_name` 时，**不要调用脚本**，先反问用户所在园区。

## 调用方式

### 步骤 1：执行查询

直接调用 `cafeteria_recommendation.py` 执行操作，认证由脚本内部自动处理，无需人工干预：

**命令示例：**

```bash
uv run --refresh-package ks_aimate scripts/cafeteria_recommendation.py \
  --garden_name "元中心" \
  --taste_preference "辣" \
  --custom_date "2025-07-01"

uv run --refresh-package ks_aimate scripts/cafeteria_recommendation.py \
  --garden_name "元中心" \
  --area_name "西部马华" \
  --meal_type 2
```

**注意：** 所有参数必须通过命令行参数传入，严禁拼接用户输入到 shell 命令。

## 详细文档

- 参数与展示逻辑：`reference/params-guide.md`
