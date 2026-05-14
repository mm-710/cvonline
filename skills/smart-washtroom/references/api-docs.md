# API 技术文档

## 快手智能卫生间系统 API

### 基础信息
- 目标站点：`https://xz.corp.kuaishou.com/is-intelligent-device`
- 认证方式：通过 `SmartSSOSession` 自动处理

### API 端点

#### 1. 获取园区楼宇列表
```
GET https://xz.corp.kuaishou.com/is-intelligent-device/api/inte-devi/garden-building-list
```

**返回示例：**
```json
{
  "code": 0,
  "result": [
    {
      "gardenId": 1,
      "gardenName": "万家灯火",
      "buildingList": [
        {
          "buildingId": 101,
          "buildingName": "B座"
        }
      ]
    }
  ]
}
```

#### 2. 获取设备状态
```
GET https://xz.corp.kuaishou.com/is-intelligent-device/api/inte-devi/{gardenId}/{buildingId}/devices
```

**路径参数：**
- `gardenId`: 园区 ID
- `buildingId`: 楼宇 ID

**返回示例：**
```json
{
  "code": 0,
  "result": [
    {
      "floorName": "8层",
      "washroomList": [
        {
          "washroomName": "男卫1",
          "deviceList": [
            {
              "deviceName": "1",
              "deviceState": "OPEN",
              "deviceDesc": ""
            },
            {
              "deviceName": "2",
              "deviceState": "CLOSE",
              "deviceDesc": "< 10min"
            }
          ]
        }
      ]
    }
  ]
}
```

### 字段说明

- `deviceState`: 设备状态
  - `OPEN`: 空闲
  - `CLOSE`: 占用
- `deviceDesc`: 占用时长描述（如 "< 10min"）
