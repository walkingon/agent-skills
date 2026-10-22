---
name: csb-inspector
description: 解析 Cocos Studio 导出的 .csb 二进制文件结构（FlatBuffers 格式），输出节点树、控件类型、位置/尺寸/锚点/缩放/颜色等通用属性、各控件专有属性（文本、图片、按钮状态图、九宫格、滚动方向等）以及引用的图片/plist/字体资源。当需要查看某个 .csb 界面里有哪些控件、控件叫什么名字、坐标尺寸是多少、用了哪些图片资源，或排查 csb 与 Lua 代码中控件名不匹配、界面元素找不到、资源缺失等问题时使用。
---

# CSB 结构解析

`.csb` 是 Cocos Studio 导出的二进制界面文件。
**FlatBuffers 格式**（文件头 4 字节为 `14 00 00 00`，根表 `CSParseBinary`，version 字段通常为 `2.1.0.0`）。

解析脚本：`scripts/csb_parse.py`（纯 Python 3，无第三方依赖），schema 定义在 `scripts/csb_schema.py`。

## 快速使用

在仓库根目录执行（Windows PowerShell）：

```powershell
# 1. 看节点树（最常用）
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb

# 2. 只看前两层，避免刷屏
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --depth 2

# 3. 统计：节点总数、各控件类型数量、最大层级
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --summary

# 4. 按控件名查找（返回完整 JSON，含所有属性）
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --find head_layout

# 5. 按 name 路径精确定位（同名控件多时用这个）
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --path root/head_layout

# 6. 列出引用的图片 / plist / 字体
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --resources

# 7. 完整 JSON（可写文件后交给其他脚本处理）
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/main_menu.csb --json --out out.json

# 8. 批量扫描目录
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views --batch
```

树形输出示例：

```
version: 2.1.0.0
textures: images/main_ui/ui_common.plist
---
Node "Layer" pos=(0,0) size=(1280,720)
  Panel "root" pos=(641.28,362.16) size=(1280,720)
    Panel "map_layout" pos=(0,716.4) size=(270,100)
    Panel "team_layout" pos=(950,718) size=(500,100) HIDDEN
    Button "item_head_role" pos=(407.142,1012.248) size=(100,100)
      ImageView "bg" pos=(50,50) size=(100,100)
      Text "text_level" pos=(5,20) size=(48,37)
```

## 输出结构说明

每个节点：

| 字段 | 含义 |
| --- | --- |
| `classname` | csb 中记录的原始类型名（如 `Panel`、`Text`、`Label`） |
| `customClassName` | 自定义类名，非空时引擎会用它替代 `classname` |
| `effectiveClassname` | 实际生效的类型（`customClassName` 优先），决定 `options` 的解析方式 |
| `options` | 该控件的属性表，字段随类型不同 |
| `children` | 子节点数组 |

`options` 中承载通用属性的表名不统一，按以下顺序取第一个存在的：
`widgetOptions` → `nodeOptions` → `node3DOption` → 直接是 `options` 本身（`Node` 类型）。

通用属性（`WidgetOptions`）：`name`、`position{x,y}`、`size{width,height}`、`anchorPoint{scaleX,scaleY}`、
`scale{scaleX,scaleY}`、`rotationSkew{rotationSkewX,rotationSkewY}`、`color{a,r,g,b}`、`alpha`、
`visible`、`zOrder`、`tag`、`actionTag`、`flipX`、`flipY`、`ignoreSize`、`touchEnabled`、
`callBackType`、`callBackName`、`frameEvent`、`customProperty`、`layoutComponent`。

各控件专有属性（节选）：

- `Text` / `Label`：`text`、`fontName`、`fontSize`、`fontResource`、`areaWidth`、`areaHeight`、
  `hAlignment`、`vAlignment`、`outlineEnabled`、`shadowEnabled`
- `ImageView`：`fileNameData{path,plistFile}`、`scale9Enabled`、`capInsets`、`scale9Size`
- `Button`：`normalData` / `pressedData` / `disabledData`、`text`、`fontSize`、`scale9Enabled`
- `CheckBox`：`backGroundBoxData`、`frontCrossData`、`selectedState`
- `Slider`：`barFileNameData`、`ballNormalData`、`percent`
- `LoadingBar`：`textureData`、`percent`、`direction`
- `Panel` / `Layout`：`backGroundImageData`、`clipEnabled`、`bgColor`、`bgColorOpacity`
- `ScrollView` / `ListView` / `PageView`：`innerSize`、`direction`、`bounceEnabled`
- `TextField`：`placeHolder`、`maxLength`、`passwordEnabled`
- `TextBMFont`：`fileNameData`、`text`
- `Sprite`：`fileNameData`、`blendFunc`
- `ProjectNode`：`fileName`（引用的子 csb 路径）

## 常见用途

**核对 Lua 代码里的控件名是否存在**

```powershell
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/xxx/xxx.csb --find 控件名
```

无输出即表示该 csb 里没有这个 name，通常是 csb 改名或代码写错。

**确认界面用了哪些图集**

```powershell
python .agents/skills/csb-inspector/scripts/csb_parse.py res/views/xxx/xxx.csb --resources
```

`plists` 为空但 `images` 有内容时，说明图片是散图（直接按路径加载）。

**在 Python 中复用解析逻辑**

```python
import sys
sys.path.insert(0, '.agents/skills/csb-inspector/scripts')
import csb_parse

data = csb_parse.load('res/views/main_menu.csb')
for node in csb_parse.iter_nodes(data['nodeTree']):
    w = csb_parse.widget_options(node)
    print(node['effectiveClassname'], w.get('name'), w.get('position'))
```

## 注意事项

- **动画时间轴默认不解析**（`action` / `animationList` 为 `null`）。需要时加 `--with-action`，
  但 `TimeLine.actionTag` 等字段在部分 csb 中取值异常，动画数据仅供参考。
- `actionTag` 是 Cocos Studio 随机生成的节点绑定 ID，不是动画标签，出现大整数属正常现象。
- `scale` 允许负值（镜像翻转），`anchorPoint` 取值 0~1，`alpha` 取值 0~255。
- 旧版 CocoLoader 格式（Cocos Studio 1.x，文件头以 `CocoStudio` 开头）也能解析，
  但输出的是通用 JSON 节点结构，不是控件属性表。
- 若 csb 解析报「无法识别的 csb 格式」，先用十六进制查看前 4 字节确认是否为 `14 00 00 00`。
- 修改 `csb_schema.py` 时**只能追加字段到末尾**，字段顺序即 FlatBuffers 的 field id，插到中间会导致解析错位。
