---
name: find-skills
description: 发现并安装 MyFlicker 市场中的技能，支持语义搜索、安装、更新、卸载及 ZIP 包本地安装。以下场景唤醒：用户明确要求搜索技能（「帮我找个xx技能」「搜索能做xx的skill」）；用户询问能力可用性（「有没有xx能帮我」「能不能做xx」）；用户希望卸载某个技能（「帮我卸载xxxx」）；用户希望使用已有地址上传技能（「帮我上传一个skill」）；当前已安装技能无法满足用户诉求时主动搜索市场。以下场景不唤醒：用户直接使用某个已有 skill 完成具体任务；用户想编写或修改自己的 skill（应使用 skill-creator）；用户询问 skill 平台管理操作（上架、下架、版本管理）；用户询问非 MyFlicker 的插件市场。
---

# MyFlicker 技能搜索与安装

## 目录管理原则
- `skills/` 目录为系统内置技能目录，用户可以对话安装、删除、更新，或在市场上执行对应操作，但用户不可修改这些 skill，以保证系统稳定与安全。
- `user-skills/` 目录为用户自定义技能目录，用户自己建设的 skill 都放在这里，支持用户自行增删改查。

## 市场搜索

如果用户意图是搜索某个技能然后进行相应的操作的话可以使用下面的命令

```bash
# 语义搜索
myflicker search <关键词>

# 限制返回数量
myflicker search <关键词> --limit 5
```

返回格式：`slug version name (score)`，分数越高越相关。

## 安装技能

```bash
myflicker install <slug>
```

安装后可立即使用。

如果用户贴入技能市场链接(https://myflicker.corp.kuaishou.com/flicker/skills/{slug}或者https://myflicker.staging.kuaishou.com/flicker/skills/{slug})进行安装的话需要解析出slug然后使用上面的命令行工具进行处理

## 卸载技能

```bash
myflicker uninstall <slug>
```

如果卸载技能失败,想要强制删除目录的话可以增加--force的选项(注意:--force会强制删除某个skill的目录,卸载优先使用uninstall命令)


## 自定义技能

1.所有的自定义技能在安装之后需要强制使用 kwai-skill-vetter 技能进行扫描

2.所有用户自建的 skill 都统一放在 `user-skills/` 目录下：

```
当前工作目录/
└── user-skills/
    └── my-custom-skill/
        └── SKILL.md
```

**新建 skill**：在 `user-skills/` 下创建以 skill 名称命名的文件夹，放入 SKILL.md。

**修改自定义 skill**：后续对这些 skill 的任何修改，都需到 `user-skills/<skill名称>/` 目录下进行。

**ZIP 包安装**：需要先使用用户提供的地址下载zip安装包,然后解压到 `user-skills/` 目录即可（ZIP 需要已包含 skill 名称文件夹结构）。


---

> 搜索引擎支持语义匹配，无需精确关键词。
