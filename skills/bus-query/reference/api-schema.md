# 班车查询接口说明

## 接口一：获取园区及线路类型枚举

### 请求

```
GET https://xz.corp.kuaishou.com/is-parking/api/feign/hasLineTypeGarden
```

脚本通过 `SmartSSOSession` 自动处理认证。

### 响应示例

```json
{
  "code": 0,
  "message": "OK",
  "result": [
    {
      "id": 98,
      "chineseName": "北京·元中心",
      "lineTypeL": ["REVCEIVE", "FREQUENT_SHUTTLE"]
    },
    {
      "id": 93,
      "chineseName": "北京·万家灯火大厦",
      "lineTypeL": ["REVCEIVE", "FREQUENT_SHUTTLE"]
    }
  ]
}
```

### agent-browser 调用示例

```bash
agent-browser eval "
  fetch('https://xz.corp.kuaishou.com/is-parking/api/feign/hasLineTypeGarden', {
    credentials: 'include'
  }).then(r=>r.json()).then(d=>JSON.stringify(d))
"
```

---

## 接口二：查询班车线路

### 请求

```
POST https://xz.corp.kuaishou.com/is-parking/api/bus/user/line
Content-Type: application/json
```

### 请求体参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| gardenId | number | 是 | 园区 ID，-1=全部，98=元中心，93=万家灯火大厦 |
| lineType | string | 是 | 线路类型：ALL_TYPE / REVCEIVE / FREQUENT_SHUTTLE |
| date | string | 是 | 日期，格式 YYYY-MM-DD |

### 请求体示例

```json
{
  "gardenId": -1,
  "lineType": "ALL_TYPE",
  "date": "2026-03-31"
}
```

### 响应结构

```json
{
  "code": 0,
  "message": "OK",
  "result": [
    {
      "id": 37,
      "managerLineName": "西二旗-元中心（早接驳）",
      "lineType": "REVCEIVE",
      "lineMoveType": "ONE_WAY",
      "lineState": "ONLINE_RUN",
      "description": "西二旗站A口出，数码科技广场东门北侧候车，高峰期9:35-10:15满员即发车",
      "directType": "DIRECT",
      "startingStation": {
        "id": 109,
        "userStationName": "西二旗",
        "managerStationName": "西二旗地铁站-早（元中心）",
        "gardenId": 98,
        "gps": "40.051526,116.303801",
        "description": "数码科技广场东门北侧（西二旗地铁站A口出...）"
      },
      "terminalStation": {
        "id": 103,
        "userStationName": "元中心",
        "managerStationName": "元中心（西二旗&永丰早）",
        "gardenId": 98,
        "gps": "40.051437,116.317378",
        "description": "西二旗中路元中心东北门或东门"
      },
      "scheduleDisplayVoL": [
        {
          "id": 382678,
          "departureTime": "09:00",
          "isAddBus": "FALSE",
          "isValid": "FALSE",
          "busDeviceId": "ddc30799",
          "plateName": "预告",
          "seatsNumber": 49
        },
        {
          "id": 382698,
          "departureTime": "19:50",
          "isAddBus": "FALSE",
          "isValid": "TRUE",
          "busDeviceId": "ddc30723",
          "plateName": "预告",
          "seatsNumber": 47
        }
      ],
      "isFavorite": "FALSE",
      "isRemind": "FALSE"
    }
  ]
}
```

### 关键响应字段说明

| 字段路径 | 说明 |
|---------|------|
| `result[].managerLineName` | 线路名称，如"西二旗-元中心（早接驳）" |
| `result[].description` | 线路候车说明（含候车位置和注意事项） |
| `result[].lineType` | 线路类型：REVCEIVE=接驳，FREQUENT_SHUTTLE=通勤 |
| `result[].lineState` | 线路状态：ONLINE_RUN=运行中 |
| `result[].startingStation.userStationName` | 起始站用户可见名称 |
| `result[].terminalStation.userStationName` | 终点站用户可见名称 |
| `result[].startingStation.description` | 起始站详细候车说明 |
| `result[].scheduleDisplayVoL[].departureTime` | 发车时间，格式 HH:mm |
| `result[].scheduleDisplayVoL[].seatsNumber` | 座位数 |
| `result[].scheduleDisplayVoL[].isValid` | TRUE=当前有效可乘坐，FALSE=已过或未开放 |
| `result[].scheduleDisplayVoL[].plateName` | 车牌显示状态（"预告"/"实时"） |
| `result[].scheduleDisplayVoL[].isAddBus` | 是否为加班车 |

### agent-browser 调用示例

```bash
agent-browser eval "
  fetch('https://xz.corp.kuaishou.com/is-parking/api/bus/user/line', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify({gardenId: -1, lineType: 'ALL_TYPE', date: '2026-03-31'})
  }).then(r=>r.json()).then(d=>JSON.stringify(d))
"
```

---

## 枚举值速查

### gardenId

| 值 | 含义 |
|-----|------|
| -1 | 全部园区 |
| 98 | 北京·元中心 |
| 93 | 北京·万家灯火大厦 |

### lineType

| 值 | 含义 |
|-----|------|
| ALL_TYPE | 全部线路 |
| REVCEIVE | 地铁接驳班车 |
| FREQUENT_SHUTTLE | 通勤班车 |

### isValid

| 值 | 含义 |
|-----|------|
| TRUE | 班次当前有效（可乘坐） |
| FALSE | 班次已过或尚未开放 |
