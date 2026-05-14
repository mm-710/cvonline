# Kwai Gym 数据模型

## Gym (健身房)

```python
class Gym:
    id: int                    # 健身房 ID
    gymName: str               # 健身房名称
    gymType: str               # 类型 (workplace/office 等)
    cityCode: str              # 城市编码
    cityName: str              # 城市名称
    locationDesc: str          # 地址描述
    locationDescLink: str      # 地图链接
    point: str                 # 经纬度 "lat,lng"
    businessStatus: str        # 营业状态
    description: str           # 描述信息
    gymStatus: str             # 状态 (open/closed)
    imageUrl: str              # 图片 URL
    link: str                  # 详情页链接
    sortedLevel: int           # 排序权重
```

## ShopDetail (健身房详情)

```python
class ShopDetail:
    id: int                    # 店铺 ID
    name: str                  # 店铺名称
    address: str               # 详细地址
    phone: str                 # 联系电话
    area: float                # 面积 (平方米)
    category: int              # 分类
    gd_lat: float              # 纬度
    gd_lng: float              # 经度
    start: str                 # 开始时间 "HH:MM"
    end: str                   # 结束时间 "HH:MM"
    opentime: List[OpenTime]   # 营业时间配置
    shop_services: List[Service]  # 服务设施
    shop_images: List[str]     # 图片列表
    brand: Brand               # 品牌信息
    description: str           # 详细介绍
    tags: List                 # 标签
    weixin: str                # 微信
    business_start: str        # 开业日期
```

## OpenTime (营业时间)

```python
class OpenTime:
    id: int
    day: int                   # 星期 (1-7)
    start: str                 # 开始时间 "HH:MM"
    end: str                   # 结束时间 "HH:MM"
```

## Service (服务设施)

```python
class Service:
    id: int
    key: str                   # 服务标识
    # 常见 key: locker-room, shower, wifi, air-conditioner, 
    # air-cleaner, dd-water, leisure-area, parking
```

## Brand (品牌)

```python
class Brand:
    id: int
    name: str                  # 品牌名称
    cloud_brand_id: int
    photo: str                 # 品牌 Logo
```

## Teacher (教练)

```python
class Teacher:
    id: int                    # 教练 ID
    shop_id: int               # 所属店铺 ID (⚠️ 已废弃)
    username: str              # 姓名
    phone: str                 # 电话
    area_code: str             # 区号 "+86"
    gender: int                # 性别 (0:男，1:女)
    avatar: str                # 头像 URL
    score: float               # 评分
    description: str           # 详细介绍
    short_description: str     # 简短介绍
    tags: List                 # 标签
    support_private: bool      # ⚠️ 已废弃 - 是否支持私教（所有值都是false）
    support_public: bool       # ⚠️ 已废弃 - 是否支持团课（所有值都是false）
    priority: int              # 展示优先级（不代表私教/团课分类）
    coach_enable: bool         # 是否启用
    start_teach_date: str      # 开始执教日期
    cloud_user: CloudUser      # 云用户信息
    teacher: TeacherInfo       # 教练信息
```

**⚠️ 重要提示：**
- `support_private`、`support_public`、`shop_id` 字段已在API返回中标注为废弃
- 所有教练的 `support_private` 和 `support_public` 都是 `false`
- `priority` 字段表示列表展示优先级，**不代表私教/团课职能分类**
- 实际所有教练的 `priority` 值都是 `1`
- 如需区分团课教练，应查询团课API(`/api/mobile/schedules/group/`)动态判断

## CloudUser (云用户)

```python
class CloudUser:
    cloud_id: int              # 云用户 ID
    username: str              # 用户名
    weixin: str                # 微信
    weixin_active: bool        # 微信是否激活
    phone_active: bool         # 手机是否激活
    hash_id: str               # 哈希 ID
```

## Schedule (课程排期)

```python
class Schedule:
    id: int                    # 排期 ID
    shop: ShopRef              # 店铺引用
    course: Course             # 课程信息
    teacher: TeacherRef        # 教练引用
    space: Space               # 场地信息
    start: str                 # 开始时间 ISO8601
    end: str                   # 结束时间 ISO8601
    max_users: int             # 最大人数
    current_users: int         # 当前报名人数
    can_order: bool            # 是否可预约
    is_free: bool              # 是否免费
    candidate_num: int         # 候补人数
    rules: List[Rule]          # 预约规则
    trial_course: TrialCourse  # 体验课信息
```

## Course (课程)

```python
class Course:
    id: int
    name: str                  # 课程名称
    course_type_tag: str       # 课程类型标签
    difficulty_level: int      # 难度等级
    length: int                # 时长 (秒)
    sports_effect_tags: List   # 运动效果标签
```

## Space (场地)

```python
class Space:
    id: int
    name: str                  # 场地名称 (如：静态、动态)
```

## Rule (预约规则)

```python
class Rule:
    card_tpl_id: int           # 卡种模板 ID
    card_tpl_name: str         # 卡种名称
    card_tpl_type: int         # 卡种类型
    cost: int                  # 费用
    from_number: int           # 最小预约人数
    to_number: int             # 最大预约人数
    channel: str               # 渠道 (CARD)
    no_limit: bool             # 是否无限制
    limits: Dict               # 限制条件
```

## MobileSetting (移动端设置)

```python
class MobileSetting:
    id: int
    title: str                 # 标题
    theme: str                 # 主题
    skin: str                  # 皮肤
    color: str                 # 主色调
    description: str           # 描述
    is_member: bool            # 是否会员制
    is_teacher: bool           # 是否教练端
    is_visitor: bool           # 是否访客模式
    modules: List[Module]      # 功能模块
    ads: List[Ad]              # 广告位
    shops: List[ShopRef]       # 关联店铺
```

## Module (功能模块)

```python
class Module:
    title: str                 # 模块标题
    path: str                  # 跳转路径
    icon: str                  # 图标
    icon_type: str             # 图标类型 (system/custom)
    color: str                 # 背景色
    title_color: str           # 标题颜色
    icon_color: str            # 图标颜色
    size: int                  # 尺寸 (2 或 3)
    opacity: float             # 透明度
    show_title: bool           # 是否显示标题
    need_permission: bool      # 是否需要权限
    bg_type: str               # 背景类型
```

## 常见课程类型

- 塑形 (腰腹塑形、臀腿美腿)
- 舞蹈 (DD 潮流炫舞、Zumba 尊巴、爵士舞)
- 瑜伽
- 搏击操
- 拉伸

## 常见服务设施

- locker-room: 更衣室
- shower: 淋浴
- wifi: WiFi
- air-conditioner: 空调
- air-cleaner: 空气净化器
- dd-water: 直饮水
- leisure-area: 休息区
- parking: 停车场
