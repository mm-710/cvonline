# MixCard 协议编写手册

> 用于 AI Agent 自动生成 MixCard 卡片消息的协议参考

---

## 核心概念

**MixCard** 是快手内部交互式卡片消息协议,通过 JSON 定义卡片结构和交互行为。

### 基本结构

```json
{
  "config": {},      // 卡片配置(可选)
  "header": {},      // 卡片标题(可选)
  "blocks": [],      // 卡片主体(可选)
  "updateMulti": 1,  // 必填,默认为 1
  "appKey": "",      // 必填,默认为"myflicker"
  "id": ""           // 卡片唯一ID(可选)
}
```

### 交互模式

- **独享** (`updateMulti: 1`):每个人看到的卡片状态独立

### 限制

- 消息总大小 ≤ 15KB
- elements 数组最多 20 个元素
- **协议版本:** MixCard Version 6 (支持分栏组件)

---

## config - 卡片配置

```json
{
  "config": {
    "wideSelfAdaptive": true,    // 宽度自适应(默认 false)
    "center": false,             // 居中展示(默认 false)
    "forward": true,             // 必填,支持转发(默认 true)
    "forwardType": 3,            // 必填,1=原始消息 2=调用接入方 3=KIM转发 4=URL链接
    "fold": false,               // 是否折叠(默认 false)
    "cardUrl": {                 // 卡片整体跳转
      "url": "https://example.com"
    },
    "aiLoading": false,          // AI加载框架图(默认 false)
    "streamLoading": false       // 流式加载框架图(默认 false)
  }
}
```

---

## header - 彩色标题

```json
{
  "header": {
    "title": "标题文本",
    "style": "blue",  // red | orange | green | blue
    "icon": {
      "type": "image",
      "imageUrl": "https://..."
    },
    "background": {
      "type": "image",
      "imageUrl": "https://..."
    }
  }
}
```

---

## blocks - 模块列表

### content - 文本内容模块

```json
{
  "type": "content",
  "blockId": "content_001",
  "text": {
    "type": "plainText",  // plainText | kimMd
    "content": "文本内容"
  },
  "remark": false,  // 备注样式(默认 false)
  "click": false,   // 可点击(默认 false)
  "url": ""         // click=true 时生效
}
```

**支持 elements(文本+小图标混合):**

```json
{
  "type": "content",
  "blockId": "content_002",
  "elements": [
    {"type": "plainText", "content": "文本"},
    {"type": "image", "imageUrl": "https://...", "width": 16, "height": 16}
  ]
}
```

---

### divider - 分割线

```json
{
  "type": "divider",
  "blockId": "divider_001"
}
```

---

### image - 图片模块

```json
{
  "type": "image",
  "blockId": "image_001",
  "title": "图片标题",
  "mode": "contain",  // left | contain | cover
  "image": {
    "type": "image",
    "imageUrl": "https://...",
    "width": 800,
    "height": 600
  }
}
```

---

### section - 并排布局

**文本 + 右侧元素:**

```json
{
  "type": "section",
  "blockId": "section_001",
  "text": {
    "type": "plainText",
    "content": "左侧文本"
  },
  "extra": {
    "type": "button",
    "text": {"type": "plainText", "content": "按钮"},
    "style": "blue",
    "value": {"action": "click"}
  }
}
```

**多列文本:**

```json
{
  "type": "section",
  "blockId": "section_002",
  "fields": [
    {"text": {"type": "plainText", "content": "字段1"}},
    {"text": {"type": "plainText", "content": "字段2"}}
  ]
}
```

**extra 支持的元素:** button、image、staticSelect、searchSelect、overflow、datePicker

---

### action - 交互按钮组

```json
{
  "type": "action",
  "blockId": "action_001",
  "layout": "two",  // auto | one | two | three
  "actions": [
    {
      "type": "button",
      "text": {"type": "plainText", "content": "确认"},
      "style": "blue",
      "value": {"action": "confirm"}
    },
    {
      "type": "button",
      "text": {"type": "plainText", "content": "取消"},
      "style": "default",
      "value": {"action": "cancel"}
    }
  ]
}
```

---

### profile - 人员头像

```json
{
  "type": "profile",
  "blockId": "profile_001",
  "profileMode": 3,  // 1=仅头像 2=仅名称 3=头像+名称
  "profiles": [
    {"type": "profile", "userId": 123456789, "mode": 3}
  ],
  "number": 5  // 显示前5个,其余显示数量
}
```

---

### streamRender - 流式渲染

```json
{
  "type": "streamRender",
  "blockId": "stream_001",
  "endFlag": false,  // 是否已完成
  "infoStream": "{\"method\":\"POST\",\"streamUrl\":\"https://...\"}",
  "completeContent": {  // endFlag=true 时直接渲染
    "type": "plainText",
    "content": "完整内容"
  }
}
```

---

### folderBox - 可折叠容器

```json
{
  "type": "folderBox",
  "folderBlocks": ["content_001", "content_002"],  // 要折叠的 blockId
  "foldBoxHeight": {
    "android": 100,
    "ios": 100,
    "pc": 120
  },
  "supportCollapse": true  // 支持收起(默认 true)
}
```

---

### vote - 投票模块

```json
{
  "type": "vote",
  "blockId": "vote_001",
  "vote": {
    "type": "singleVote",  // singleVote | multiVote
    "id": "vote_123",
    "isAnonymous": false,
    "title": {"type": "plainText", "content": "投票主题"},
    "voteOptions": [
      {
        "id": "opt1",
        "text": {"type": "plainText", "content": "选项1"},
        "count": 5,
        "selected": false,
        "value": "value1"
      }
    ],
    "voteNum": 5,
    "totalVotedOptionsCount": 5,
    "isPublic": true,
    "showResult": true,
    "isCompleted": false,
    "creatorId": "creator_id",
    "createTime": 1713430800000,
    "userHasVoted": false,
    "value": {"voteId": "vote_123"}
  }
}
```

---

### columnSet - 分栏布局

**基本结构:**

```json
{
  "type": "columnSet",
  "blockId": "columnset_001",
  "horizontalSpacing": "medium",  // small | medium | large
  "backgroundStyle": "gray",      // none | gray
  "columnStyle": "none",          // none | onePerLine | twoPerLine
  "columns": [
    {
      "type": "columnSetItem",
      "width": "auto",            // "auto" | "100" (数值字符串,单位 px)
      "weight": 1,                // width="auto" 时生效,权重分配
      "verticalSpacing": "small", // 列内子元素纵向间距
      "backgroundStyle": "none",  // 列背景 none | gray
      "children": [               // 列内子元素(支持大部分 block 类型)
        {
          "type": "content",
          "blockId": "content_col1_01",
          "text": {"type": "plainText", "content": "第一列内容"}
        }
      ]
    },
    {
      "type": "columnSetItem",
      "width": "auto",
      "weight": 2,
      "verticalSpacing": "medium",
      "children": [
        {
          "type": "image",
          "blockId": "image_col2_01",
          "image": {"type": "image", "imageUrl": "https://..."}
        }
      ]
    }
  ]
}
```

**字段详解:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `horizontalSpacing` | string | 列间距: `small`(8dp/pt/px)、`medium`(12)、`large`(16) |
| `backgroundStyle` | string | 整体背景: `none` 或 `gray` |
| `columnStyle` | string | 移动端布局: `none`(按协议)、`onePerLine`(一行一列)、`twoPerLine`(一行两列等分) |
| `columns` | array | 列数组,最多 6 列 |
| `columns[].width` | string | 列宽: `"auto"`(自适应) 或 数值字符串如 `"200"`(px),移动端需转 dp/pt |
| `columns[].weight` | number | `width="auto"` 时生效,权重比例分配 |
| `columns[].verticalSpacing` | string | 列内子元素纵向间距: `small` / `medium` / `large` |
| `columns[].children` | array | 列内子元素,支持 content/divider/image/section/action 等 |

**间距映射表:**

| 值 | Android | iOS | PC |
|----|---------|-----|-----|
| `small` | 8dp | 8pt | 8px |
| `medium` | 12dp | 12pt | 12px |
| `large` | 16dp | 16pt | 16px |

**注意事项:**

- ⚠️ **不支持嵌套:** 分栏内不可再嵌套 `columnSet`
- ⚠️ **禁用组件:** 流式渲染(`streamRender`)、文件上传/下载、`feedback` 不可用于分栏内
- ⚠️ **blockId 全局唯一:** 列内子元素的 `blockId` 必须在整个 MixCard 中唯一
- ⚠️ **最小宽度:** 每列最小宽度 32px → 16dp/16pt
- ⚠️ **两列等分:** `columnStyle="twoPerLine"` 时忽略 `width`,强制等分
- ✅ **外边距:** 分栏组件距其他组件/header 上下左右均为 24px → 12dp/12pt

**完整示例:**

```json
{
  "updateMulti": 1,
  "appKey": "myflicker",
  "header": {
    "title": "产品信息",
    "style": "blue"
  },
  "blocks": [
    {
      "type": "columnSet",
      "blockId": "columnset_001",
      "horizontalSpacing": "large",
      "backgroundStyle": "gray",
      "columnStyle": "none",
      "columns": [
        {
          "type": "columnSetItem",
          "width": "100",
          "verticalSpacing": "small",
          "children": [
            {
              "type": "image",
              "blockId": "product_image",
              "image": {
                "type": "image",
                "imageUrl": "https://example.com/product.jpg",
                "width": 100,
                "height": 100
              }
            }
          ]
        },
        {
          "type": "columnSetItem",
          "width": "auto",
          "weight": 1,
          "verticalSpacing": "medium",
          "children": [
            {
              "type": "content",
              "blockId": "product_name",
              "text": {"type": "plainText", "content": "MacBook Pro 16"}
            },
            {
              "type": "content",
              "blockId": "product_price",
              "text": {
                "type": "plainText",
                "content": "¥19,999",
                "style": "red"
              }
            },
            {
              "type": "action",
              "blockId": "product_actions",
              "layout": "two",
              "actions": [
                {
                  "type": "button",
                  "text": {"type": "plainText", "content": "立即购买"},
                  "style": "blue",
                  "value": {"action": "buy"}
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## elements - 交互元素

### button - 按钮

```json
{
  "type": "button",
  "actionId": "btn_001",  // 用于客户端联动
  "text": {"type": "plainText", "content": "按钮文本"},
  "style": "blue",  // default | blue | red | orange | green | disable
  "url": "https://...",  // 跳转URL
  "value": {"action": "submit"},  // 回调数据
  "confirm": {  // 二次确认
    "title": {"type": "plainText", "content": "确认标题"},
    "text": {"type": "plainText", "content": "确认内容"},
    "confirm": {"type": "plainText", "content": "确定"},
    "cancel": {"type": "plainText", "content": "取消"}
  }
}
```

---

### staticSelect - 静态选择器

```json
{
  "type": "staticSelect",
  "actionId": "select_001",
  "placeholder": {"type": "plainText", "content": "请选择..."},
  "options": [
    {
      "id": "opt1",
      "text": {"type": "plainText", "content": "选项1"},
      "value": "value1"
    }
  ],
  "initialOption": {"id": "opt1", "value": "value1"},
  "dispatchAction": "button_submit",  // 关联按钮,将选择追加到按钮 value
  "value": {"select": "value1"}
}
```

---

### searchSelect - 搜索选择器

```json
{
  "type": "searchSelect",
  "searchType": "user",  // user | group | app
  "searchCallback": false,  // 是否回调第三方业务
  "placeholder": {"type": "plainText", "content": "搜索..."},
  "multiLine": true,  // 是否多选
  "options": [],
  "initialOptions": [],
  "dispatchAction": "button_submit",
  "value": {"users": ["user1", "user2"]}
}
```

---

### overflow - 下拉菜单

```json
{
  "type": "overflow",
  "actionId": "overflow_001",
  "options": [
    {
      "id": "edit",
      "text": {"type": "plainText", "content": "编辑"},
      "url": "https://...",  // 可选:直接跳转
      "value": "edit"
    }
  ],
  "value": {"action": "overflow"}
}
```

---

### datePicker - 日期/时间选择器

```json
{
  "type": "datePicker",  // datePicker | timePicker | datetimePicker
  "actionId": "date_001",
  "placeholder": {"type": "plainText", "content": "选择日期"},
  "dateFormat": "YYYY-MM-DD",
  "initial": "1713430800000",  // 时间戳
  "dispatchAction": "button_submit",
  "value": {"date": "2024-04-18", "timezone": "Asia/Shanghai"}
}
```

---

### input - 输入框

```json
{
  "type": "input",
  "actionId": "input_001",
  "placeholder": {"type": "plainText", "content": "请输入..."},
  "initialContent": {"type": "plainText", "content": "默认内容"},
  "multiLine": false,  // 是否多行
  "dispatchAction": "button_submit",
  "value": {"input": "user_input"}
}
```

---

### checkboxes - 多选框

```json
{
  "type": "checkboxes",
  "actionId": "checkbox_001",
  "options": [
    {
      "id": "opt1",
      "text": {"type": "plainText", "content": "选项1"},
      "value": "value1"
    }
  ],
  "initialOptions": [{"id": "opt1", "value": "value1"}],
  "dispatchAction": "button_submit",
  "value": {"checkboxes": ["value1", "value2"]}
}
```

---

### radio - 单选框

```json
{
  "type": "radio",
  "actionId": "radio_001",
  "options": [
    {
      "id": "opt1",
      "text": {"type": "plainText", "content": "选项1"},
      "value": "value1"
    }
  ],
  "initialOption": {"id": "opt1", "value": "value1"},
  "dispatchAction": "button_submit",
  "value": {"radio": "value1"}
}
```

---

### image - 图片元素

```json
{
  "type": "image",
  "imageUrl": "https://...",
  "darkImageUrl": "https://...",  // 暗黑模式
  "width": 64,
  "height": 64,
  "preview": true,  // 是否支持放大
  "imgShape": "square"  // square | circle
}
```

---

### feedback - 意见反馈

```json
{
  "type": "feedback",
  "description": {"type": "plainText", "content": "描述文本"},
  "reactions": [
    {
      "id": "like",
      "type": "reaction",
      "icon": {"type": "image", "imageUrl": "https://..."},
      "tips": true,
      "tipsCnt": "点赞",
      "value": "like"
    }
  ],
  "value": {"feedback": "like"}
}
```

---

## 对象定义

### text - 文本对象

```json
{
  "type": "plainText",  // plainText | kimMd | tag
  "content": "文本内容",
  "i18n": {  // 国际化(优先使用)
    "zhCN": "中文内容",
    "enUS": "English content"
  },
  "fontSize": "14px",
  "fontColor": "#333333",
  "fontBackGround": "#f5f5f5",
  "style": "blue",  // red | yellow | blue | green | orange | pink | gray
  "maxLineNum": 3,
  "remark": false
}
```

---

### url - URL 对象

```json
{
  "url": "https://example.com",
  "multiUrl": {  // 多端差异化
    "pc": "https://...",
    "ios": "kimapp://...",
    "android": "kimapp://..."
  }
}
```

---

### option - 选项对象

```json
{
  "id": "opt1",
  "type": "string",
  "text": {"type": "plainText", "content": "选项文本"},
  "description": {"type": "plainText", "content": "描述"},
  "icon": {"type": "image", "imageUrl": "https://..."},
  "profile": {"type": "profile", "userId": 123456789},
  "url": "https://...",
  "value": "option_value"
}
```

---

### confirm - 二次确认

```json
{
  "title": {"type": "plainText", "content": "确认标题"},
  "text": {"type": "plainText", "content": "确认内容"},
  "confirm": {"type": "plainText", "content": "确定"},
  "cancel": {"type": "plainText", "content": "取消"},
  "style": "red"  // 确认按钮颜色
}
```

---

### profile - 人员对象

```json
{
  "type": "profile",
  "userId": 123456789,  // kwaiUserId
  "mode": 3  // 1=仅头像 2=仅名称 3=头像+名称
}
```

---

## 回调响应格式

### toast - 提示信息

```json
{
  "toast": {
    "style": "success",  // success | warning | error
    "zhCN": "操作成功",
    "enUS": "Operation success",
    "forbid": false,  // 禁止弹toast
    "skipConfig": {
      "type": "skipConfig",
      "url": "https://..."
    }
  }
}
```

---

### operation - 跳转操作

```json
{
  "operation": {
    "url": "https://...",
    "multiUrl": {
      "pc": "https://...",
      "ios": "kimapp://...",
      "android": "kimapp://..."
    }
  }
}
```

---

## 完整示例

### 示例 1:通知卡片

```json
{
  "updateMulti": 1,
  "header": {
    "title": "系统通知",
    "style": "blue"
  },
  "blocks": [
    {
      "type": "content",
      "blockId": "content_001",
      "text": {
        "type": "plainText",
        "content": "您有一条新的系统通知,请及时查看。"
      }
    },
    {
      "type": "divider",
      "blockId": "divider_001"
    },
    {
      "type": "action",
      "blockId": "action_001",
      "layout": "one",
      "actions": [
        {
          "type": "button",
          "text": {"type": "plainText", "content": "查看详情"},
          "style": "blue",
          "url": "https://example.com/detail"
        }
      ]
    }
  ]
}
```

---

### 示例 2:表单卡片

```json
{
  "updateMulti": 1,
  "appKey": "your_app_key",
  "id": "form_card_001",
  "header": {
    "title": "信息填写",
    "style": "green"
  },
  "blocks": [
    {
      "type": "section",
      "blockId": "section_001",
      "text": {"type": "plainText", "content": "姓名:"},
      "extra": {
        "type": "input",
        "actionId": "input_name",
        "placeholder": {"type": "plainText", "content": "请输入姓名"},
        "dispatchAction": "button_submit"
      }
    },
    {
      "type": "section",
      "blockId": "section_002",
      "text": {"type": "plainText", "content": "部门:"},
      "extra": {
        "type": "staticSelect",
        "actionId": "select_dept",
        "placeholder": {"type": "plainText", "content": "请选择部门"},
        "options": [
          {"id": "tech", "text": {"type": "plainText", "content": "技术部"}, "value": "tech"},
          {"id": "product", "text": {"type": "plainText", "content": "产品部"}, "value": "product"}
        ],
        "dispatchAction": "button_submit"
      }
    },
    {
      "type": "action",
      "blockId": "action_001",
      "layout": "two",
      "actions": [
        {
          "type": "button",
          "actionId": "button_submit",
          "text": {"type": "plainText", "content": "提交"},
          "style": "blue",
          "value": {"action": "submit"},
          "confirm": {
            "title": {"type": "plainText", "content": "确认提交"},
            "text": {"type": "plainText", "content": "确定要提交表单吗?"},
            "confirm": {"type": "plainText", "content": "确定"},
            "cancel": {"type": "plainText", "content": "取消"}
          }
        },
        {
          "type": "button",
          "text": {"type": "plainText", "content": "取消"},
          "style": "default",
          "value": {"action": "cancel"}
        }
      ]
    }
  ]
}
```

---

### 示例 3:审批卡片

```json
{
  "updateMulti": 2,
  "appKey": "your_app_key",
  "id": "approval_001",
  "header": {
    "title": "请假审批",
    "style": "orange"
  },
  "blocks": [
    {
      "type": "section",
      "blockId": "section_001",
      "fields": [
        {"text": {"type": "plainText", "content": "申请人:张三"}},
        {"text": {"type": "plainText", "content": "请假类型:年假"}}
      ]
    },
    {
      "type": "section",
      "blockId": "section_002",
      "fields": [
        {"text": {"type": "plainText", "content": "开始时间:2024-04-20"}},
        {"text": {"type": "plainText", "content": "结束时间:2024-04-22"}}
      ]
    },
    {
      "type": "content",
      "blockId": "content_001",
      "text": {"type": "plainText", "content": "请假事由:家中有事需要处理"}
    },
    {
      "type": "divider",
      "blockId": "divider_001"
    },
    {
      "type": "action",
      "blockId": "action_001",
      "layout": "two",
      "actions": [
        {
          "type": "button",
          "text": {"type": "plainText", "content": "同意"},
          "style": "green",
          "value": {"action": "approve"}
        },
        {
          "type": "button",
          "text": {"type": "plainText", "content": "拒绝"},
          "style": "red",
          "value": {"action": "reject"}
        }
      ]
    }
  ]
}
```

---

### 示例 4:分栏卡片 **[NEW]**

```json
{
  "updateMulti": 1,
  "appKey": "myflicker",
  "header": {
    "title": "团队协作",
    "style": "green"
  },
  "blocks": [
    {
      "type": "columnSet",
      "blockId": "columnset_team",
      "horizontalSpacing": "large",
      "backgroundStyle": "gray",
      "columns": [
        {
          "type": "columnSetItem",
          "width": "120",
          "verticalSpacing": "small",
          "children": [
            {
              "type": "image",
              "blockId": "team_avatar",
              "image": {
                "type": "image",
                "imageUrl": "https://example.com/team.jpg",
                "width": 120,
                "height": 120
              }
            }
          ]
        },
        {
          "type": "columnSetItem",
          "width": "auto",
          "weight": 1,
          "verticalSpacing": "medium",
          "children": [
            {
              "type": "content",
              "blockId": "team_title",
              "text": {"type": "plainText", "content": "快手技术团队"}
            },
            {
              "type": "content",
              "blockId": "team_desc",
              "text": {
                "type": "plainText",
                "content": "致力于打造极致用户体验",
                "remark": true
              }
            },
            {
              "type": "divider",
              "blockId": "team_divider"
            },
            {
              "type": "section",
              "blockId": "team_stats",
              "fields": [
                {"text": {"type": "plainText", "content": "成员:50人"}},
                {"text": {"type": "plainText", "content": "项目:12个"}}
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "action",
      "blockId": "team_actions",
      "layout": "two",
      "actions": [
        {
          "type": "button",
          "text": {"type": "plainText", "content": "加入团队"},
          "style": "blue",
          "value": {"action": "join"}
        },
        {
          "type": "button",
          "text": {"type": "plainText", "content": "查看详情"},
          "style": "default",
          "url": "https://example.com/team"
        }
      ]
    }
  ]
}
```

---

## 关键规则

### blockId 规范

- 每个 block 必须有唯一的 `blockId`
- 建议使用有意义的前缀:`content_`、`action_`、`section_`、`image_`、`divider_`、`columnset_`

### 元素联动机制

通过 `actionId` 和 `dispatchAction` 实现:

1. 输入元素设置 `actionId`(如 `input_name`)
2. 按钮设置 `actionId`(如 `button_submit`)
3. 输入元素设置 `dispatchAction: "button_submit"`
4. 用户点击按钮时,输入内容会追加到按钮的 `value` 中:`{button_submit: {input_name: "用户输入"}}`

### 回调触发条件

元素必须设置 `value` 字段才会触发回调:

```json
{
  "type": "button",
  "value": {"action": "submit"}  // 必填
}
```

### 国际化优先级

优先使用 `i18n` 字段而非 `content`:

```json
{
  "type": "plainText",
  "i18n": {
    "zhCN": "确定",
    "enUS": "Confirm"
  }
}
```

---

## 字段速查

| 字段 | 可选值 | 说明 |
|------|--------|------|
| `updateMulti` | `1` / `2` | 1=独享 2=共享 |
| `forwardType` | `1` / `2` / `3` / `4` | 转发类型 |
| `header.style` | `red` / `orange` / `green` / `blue` | 标题颜色 |
| `button.style` | `default` / `blue` / `red` / `orange` / `green` / `disable` | 按钮样式 |
| `image.mode` | `left` / `contain` / `cover` | 图片布局 |
| `action.layout` | `auto` / `one` / `two` / `three` | 按钮排列 |
| `profileMode` | `1` / `2` / `3` | 1=头像 2=名称 3=头像+名称 |
| `searchType` | `user` / `group` / `app` | 搜索类型 |
| `toast.style` | `success` / `warning` / `error` | 提示样式 |
| `horizontalSpacing` | `small` / `medium` / `large` | 分栏列间距(8/12/16) **[NEW]** |
| `columnStyle` | `none` / `onePerLine` / `twoPerLine` | 移动端分栏布局 **[NEW]** |

---

**版本:** v1.1 (支持分栏组件)  
**更新:** 2024-04-19  
**协议版本:** MixCard Version 6
