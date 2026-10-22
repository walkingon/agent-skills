# agent-skills

存放可复用的 Agent Skill 集合。每个 Skill 是一个独立目录，包含 `SKILL.md`（说明与使用方式）以及可选的 `scripts/` 脚本。

## Skill 列表

| Skill | 功能 | 依赖 |
| --- | --- | --- |
| [csb-inspector](csb-inspector/SKILL.md) | 解析 Cocos Studio 导出的 `.csb` 二进制界面文件（FlatBuffers），输出节点树、控件属性与引用的资源 | Python 3，无第三方依赖 |

## 添加新 Skill

1. 新建 `<skill-name>/` 目录，编写 `SKILL.md`，包含 YAML front matter 的 `name` 和 `description`。
2. 脚本放在 `<skill-name>/scripts/` 下，优先使用无第三方依赖的实现。
3. 在本 README 的 Skill 列表中添加一行，并补充使用说明。
