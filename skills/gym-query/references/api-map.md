# Kwai Gym API 接口文档

## 基础信息

- **主域名**: https://xz.corp.kuaishou.com
- **第三方服务域名**: https://saas.qingchengfit.cn
- **认证方式**: Cookie (accessproxy_session, k-token, csrftoken)

## 接口列表

### 1. 查询健身房列表

**请求**
```
POST /xz-gym/api/user/gym/query
Host: xz.corp.kuaishou.com
Content-Type: application/json

{}
```

**响应**
```json
{
  "code": 0,
  "message": "OK",
  "result": [
    {
      "id": 2,
      "gymName": "元中心健身房",
      "gymType": "workplace",
      "cityCode": "beijing",
      "cityName": "北京",
      "locationDesc": "北京市海淀区西二旗中路 29 号元中心地下 1 层南区",
      "locationDescLink": "https://surl.amap.com/6a4tqMnb8gi",
      "point": "40.050092,116.317283",
      "businessStatus": "yes",
      "description": "营业时间：\n周一至周日\n7:00-23:00（法定节假日除外）",
      "gymStatus": "open",
      "imageUrl": "https://...",
      "link": "https://saas.qingchengfit.cn/shop/4655/mobile/settings/8273/welcome/",
      "sortedLevel": 0
    }
  ]
}
```

### 2. 获取健身房详情

**请求**
```
GET /api/shops/{shop_id}/detail/
Host: saas.qingchengfit.cn
```

**响应字段**
- `id`: 健身房 ID
- `name`: 健身房名称
- `address`: 详细地址
- `phone`: 联系电话
- `area`: 面积 (平方米)
- `opentime`: 营业时间配置
- `shop_services`: 服务设施 (更衣室、淋浴、WiFi 等)
- `shop_images`: 图片列表
- `brand`: 品牌信息
- `gd_lat`, `gd_lng`: 经纬度

### 3. 获取教练列表

**请求**
```
GET /api/v2/shops/{shop_id}/teachers/?show_all=1
Host: saas.qingchengfit.cn
```

**参数说明**
- `show_all=1`: 返回完整的管理级数据（包括电话、微信等敏感信息）
- `show_all=0` 或不传: 返回公开数据（可能隐藏敏感字段）

**响应字段**
- `total_count`: 教练总数
- `teachers`: 教练列表
  - `id`: 教练 ID
  - `username`: 姓名
  - `phone`: 电话 (⚠️ 敏感信息，需SSO认证)
  - `avatar`: 头像 URL
  - `gender`: 性别 (0:男，1:女)
  - `score`: 评分
  - `description`: 详细介绍
  - `short_description`: 简短介绍
  - `tags`: 标签
  - `cloud_user.weixin`: 微信 (⚠️ 敏感信息，需SSO认证)
  - `support_private`: 是否支持私教 (⚠️ 已废弃)
  - `support_public`: 是否支持团课 (⚠️ 已废弃)

**隐私说明**
- 该API返回教练的联系方式（电话、微信）是因为使用了 `show_all=1` 参数
- 这是内部管理API，需要SSO认证，面向快手员工使用
- 前端公开页面可能不传此参数，因此不显示敏感信息
- Skill展示时可根据需要决定是否显示联系方式

### 4. 获取团课列表

**请求**
```
GET /api/mobile/schedules/group/?shop_id={shop_id}&date={date}
Host: saas.qingchengfit.cn
```

**响应字段**
- `schedules`: 课程列表
  - `id`: 课程排期 ID
  - `course`: 课程信息
    - `name`: 课程名称
    - `course_type_tag`: 课程类型
    - `length`: 时长 (秒)
  - `teacher`: 教练信息
    - `username`: 姓名
    - `gender`: 性别
    - `score`: 评分
  - `start`, `end`: 开始/结束时间
  - `space`: 场地信息
    - `name`: 场地名称
  - `max_users`: 最大人数
  - `current_users`: 当前报名人数
  - `can_order`: 是否可预约
  - `rules`: 预约规则
    - `card_tpl_name`: 卡种名称
    - `cost`: 费用

### 5. 获取设置信息

**请求**
```
GET /api/v2/setting/{setting_id}/detail/
Host: saas.qingchengfit.cn
```

**响应字段**
- `mobile_index_setting`: 移动端首页设置
  - `title`: 标题
  - `theme`: 主题
  - `skin`: 皮肤
  - `modules`: 功能模块配置
  - `ads`: 广告位配置

### 6. 获取用户通知

**请求**
```
GET /api/user/notices/no/?shop_id={shop_id}&timestamp={ts}
Host: saas.qingchengfit.cn
```

### 7. 获取活动列表

**请求**
```
GET /api/v2/shops/{shop_id}/homepage/grant-activites/
Host: saas.qingchengfit.cn
```

> **注意**：URL 中的 `grant-activites` 为上游 saas.qingchengfit.cn 原始拼写（少一个字母 `i`，正确英文应为 `activities`），这是上游系统固有拼写，请勿修改，否则接口将调用失败。

### 8. 获取课程标签

**请求**
```
GET /api/mobile/schedules/tags/?shop_id={shop_id}&date={date}
Host: saas.qingchengfit.cn
```

## 错误处理

所有接口返回统一的 JSON 格式：
- `code`/`status`: 状态码 (0 或 200 表示成功)
- `message`/`msg`: 错误信息
- `result`/`data`: 返回数据

## 注意事项

1. 所有接口都需要有效的 Cookie 认证
2. 第三方服务 (saas.qingchengfit.cn) 需要额外的 csrftoken
3. 部分接口有访问频率限制
4. 时间格式统一使用 ISO 8601 (YYYY-MM-DDTHH:MM:SS)
