# -*- coding: utf-8 -*-
"""
Cocos Studio CSB 二进制结构定义（FlatBuffers schema）。

来源：frameworks/cocos2d-x/cocos/editor-support/cocostudio/fbs-files/*.fbs
字段顺序即 FlatBuffers 的 field id，**不可随意调整**（调整会导致解析错位）。

类型写法：
    'int8' / 'uint8' / 'int16' / 'uint16' / 'int32' / 'uint32' / 'float' / 'bool'
    'string'
    'table:表名'
    'struct:结构名'
    'vector:string' / 'vector:table:表名' / 'vector:struct:结构名' / 'vector:标量'
"""

# ---------------------------------------------------------------------------
# 标量：类型 -> (struct 格式符, 字节数)
# ---------------------------------------------------------------------------
SCALARS = {
    'int8': ('b', 1),
    'uint8': ('B', 1),
    'int16': ('h', 2),
    'uint16': ('H', 2),
    'int32': ('i', 4),
    'uint32': ('I', 4),
    'float': ('f', 4),
    'bool': ('B', 1),
}

# ---------------------------------------------------------------------------
# struct（内联存储，无 vtable）
# ---------------------------------------------------------------------------
STRUCTS = {
    'RotationSkew': [('rotationSkewX', 'float'), ('rotationSkewY', 'float')],
    'Position': [('x', 'float'), ('y', 'float')],
    'Scale': [('scaleX', 'float'), ('scaleY', 'float')],
    'AnchorPoint': [('scaleX', 'float'), ('scaleY', 'float')],
    'Color': [('a', 'uint8'), ('r', 'uint8'), ('g', 'uint8'), ('b', 'uint8')],
    'ColorVector': [('vectorX', 'float'), ('vectorY', 'float')],
    'FlatSize': [('width', 'float'), ('height', 'float')],
    'CapInsets': [('x', 'float'), ('y', 'float'), ('width', 'float'), ('height', 'float')],
    'BlendFunc': [('src', 'int32'), ('dst', 'int32')],
    'Vector2': [('x', 'float'), ('y', 'float')],
    'Vector3': [('x', 'float'), ('y', 'float'), ('z', 'float')],
}

# ---------------------------------------------------------------------------
# table
# ---------------------------------------------------------------------------
TABLES = {
    # ---------------- 根表 ----------------
    'CSParseBinary': [
        ('version', 'string'),
        ('textures', 'vector:string'),
        ('texturePngs', 'vector:string'),
        ('nodeTree', 'table:NodeTree'),
        ('action', 'table:NodeAction'),
        ('animationList', 'vector:table:AnimationInfo'),
    ],

    'NodeTree': [
        ('classname', 'string'),
        ('children', 'vector:table:NodeTree'),
        ('options', 'table:Options'),
        ('customClassName', 'string'),
    ],

    # options.data 的真实类型由 NodeTree.classname 决定，见 CLASS_OPTIONS
    'Options': [
        ('data', 'table:WidgetOptions'),
    ],

    'WidgetOptions': [
        ('name', 'string'),
        ('actionTag', 'int32'),
        ('rotationSkew', 'struct:RotationSkew'),
        ('zOrder', 'int32'),
        ('visible', 'bool'),
        ('alpha', 'uint8'),
        ('tag', 'int32'),
        ('position', 'struct:Position'),
        ('scale', 'struct:Scale'),
        ('anchorPoint', 'struct:AnchorPoint'),
        ('color', 'struct:Color'),
        ('size', 'struct:FlatSize'),
        ('flipX', 'bool'),
        ('flipY', 'bool'),
        ('ignoreSize', 'bool'),
        ('touchEnabled', 'bool'),
        ('frameEvent', 'string'),
        ('customProperty', 'string'),
        ('callBackType', 'string'),
        ('callBackName', 'string'),
        ('layoutComponent', 'table:LayoutComponentTable'),
    ],

    'LayoutComponentTable': [
        ('positionXPercentEnabled', 'bool'),
        ('positionYPercentEnabled', 'bool'),
        ('positionXPercent', 'float'),
        ('positionYPercent', 'float'),
        ('sizeXPercentEnable', 'bool'),
        ('sizeYPercentEnable', 'bool'),
        ('sizeXPercent', 'float'),
        ('sizeYPercent', 'float'),
        ('stretchHorizontalEnabled', 'bool'),
        ('stretchVerticalEnabled', 'bool'),
        ('horizontalEdge', 'string'),
        ('verticalEdge', 'string'),
        ('leftMargin', 'float'),
        ('rightMargin', 'float'),
        ('topMargin', 'float'),
        ('bottomMargin', 'float'),
    ],

    # ---------------- 各控件 options ----------------
    'SingleNodeOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
    ],

    'SpriteOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fileNameData', 'table:ResourceData'),
        ('blendFunc', 'struct:BlendFunc'),
    ],

    'ParticleSystemOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fileNameData', 'table:ResourceData'),
        ('blendFunc', 'struct:BlendFunc'),
    ],

    'GameMapOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fileNameData', 'table:ResourceData'),
    ],

    'ButtonOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('normalData', 'table:ResourceData'),
        ('pressedData', 'table:ResourceData'),
        ('disabledData', 'table:ResourceData'),
        ('fontResource', 'table:ResourceData'),
        ('text', 'string'),
        ('isLocalized', 'bool'),
        ('fontName', 'string'),
        ('fontSize', 'int32'),
        ('textColor', 'struct:Color'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('scale9Enabled', 'bool'),
        ('displaystate', 'bool'),
        ('outlineEnabled', 'bool'),
        ('outlineColor', 'struct:Color'),
        ('outlineSize', 'int32'),
        ('shadowEnabled', 'bool'),
        ('shadowColor', 'struct:Color'),
        ('shadowOffsetX', 'float'),
        ('shadowOffsetY', 'float'),
        ('shadowBlurRadius', 'int32'),
    ],

    'CheckBoxOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('backGroundBoxData', 'table:ResourceData'),
        ('backGroundBoxSelectedData', 'table:ResourceData'),
        ('frontCrossData', 'table:ResourceData'),
        ('backGroundBoxDisabledData', 'table:ResourceData'),
        ('frontCrossDisabledData', 'table:ResourceData'),
        ('selectedState', 'bool'),
        ('displaystate', 'bool'),
    ],

    'ImageViewOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('fileNameData', 'table:ResourceData'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('scale9Enabled', 'bool'),
    ],

    'TextAtlasOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('charMapFileData', 'table:ResourceData'),
        ('stringValue', 'string'),
        ('startCharMap', 'string'),
        ('itemWidth', 'int32'),
        ('itemHeight', 'int32'),
    ],

    'TextBMFontOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('fileNameData', 'table:ResourceData'),
        ('text', 'string'),
        ('isLocalized', 'bool'),
    ],

    'TextOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('fontResource', 'table:ResourceData'),
        ('fontName', 'string'),
        ('fontSize', 'int32'),
        ('text', 'string'),
        ('isLocalized', 'bool'),
        ('areaWidth', 'int32'),
        ('areaHeight', 'int32'),
        ('hAlignment', 'int32'),
        ('vAlignment', 'int32'),
        ('touchScaleEnable', 'bool'),
        ('isCustomSize', 'bool'),
        ('outlineEnabled', 'bool'),
        ('outlineColor', 'struct:Color'),
        ('outlineSize', 'int32'),
        ('shadowEnabled', 'bool'),
        ('shadowColor', 'struct:Color'),
        ('shadowOffsetX', 'float'),
        ('shadowOffsetY', 'float'),
        ('shadowBlurRadius', 'int32'),
    ],

    'TextFieldOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('fontResource', 'table:ResourceData'),
        ('fontName', 'string'),
        ('fontSize', 'int32'),
        ('text', 'string'),
        ('isLocalized', 'bool'),
        ('placeHolder', 'string'),
        ('passwordEnabled', 'bool'),
        ('passwordStyleText', 'string'),
        ('maxLengthEnabled', 'bool'),
        ('maxLength', 'int32'),
        ('areaWidth', 'int32'),
        ('areaHeight', 'int32'),
        ('isCustomSize', 'bool'),
    ],

    'LoadingBarOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('textureData', 'table:ResourceData'),
        ('percent', 'int32'),
        ('direction', 'int32'),
    ],

    'SliderOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('barFileNameData', 'table:ResourceData'),
        ('ballNormalData', 'table:ResourceData'),
        ('ballPressedData', 'table:ResourceData'),
        ('ballDisabledData', 'table:ResourceData'),
        ('progressBarData', 'table:ResourceData'),
        ('percent', 'int32'),
        ('displaystate', 'bool'),
    ],

    'PanelOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('backGroundImageData', 'table:ResourceData'),
        ('clipEnabled', 'bool'),
        ('bgColor', 'struct:Color'),
        ('bgStartColor', 'struct:Color'),
        ('bgEndColor', 'struct:Color'),
        ('colorType', 'int32'),
        ('bgColorOpacity', 'uint8'),
        ('colorVector', 'struct:ColorVector'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('backGroundScale9Enabled', 'bool'),
    ],

    'ScrollViewOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('backGroundImageData', 'table:ResourceData'),
        ('clipEnabled', 'bool'),
        ('bgColor', 'struct:Color'),
        ('bgStartColor', 'struct:Color'),
        ('bgEndColor', 'struct:Color'),
        ('colorType', 'int32'),
        ('bgColorOpacity', 'uint8'),
        ('colorVector', 'struct:ColorVector'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('backGroundScale9Enabled', 'bool'),
        ('innerSize', 'struct:FlatSize'),
        ('direction', 'int32'),
        ('bounceEnabled', 'bool'),
        ('scrollbarEnabeld', 'bool'),
        ('scrollbarAutoHide', 'bool'),
        ('scrollbarAutoHideTime', 'float'),
    ],

    'PageViewOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('backGroundImageData', 'table:ResourceData'),
        ('clipEnabled', 'bool'),
        ('bgColor', 'struct:Color'),
        ('bgStartColor', 'struct:Color'),
        ('bgEndColor', 'struct:Color'),
        ('colorType', 'int32'),
        ('bgColorOpacity', 'uint8'),
        ('colorVector', 'struct:ColorVector'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('backGroundScale9Enabled', 'bool'),
    ],

    'ListViewOptions': [
        ('widgetOptions', 'table:WidgetOptions'),
        ('backGroundImageData', 'table:ResourceData'),
        ('clipEnabled', 'bool'),
        ('bgColor', 'struct:Color'),
        ('bgStartColor', 'struct:Color'),
        ('bgEndColor', 'struct:Color'),
        ('colorType', 'int32'),
        ('bgColorOpacity', 'uint8'),
        ('colorVector', 'struct:ColorVector'),
        ('capInsets', 'struct:CapInsets'),
        ('scale9Size', 'struct:FlatSize'),
        ('backGroundScale9Enabled', 'bool'),
        ('innerSize', 'struct:FlatSize'),
        ('direction', 'int32'),
        ('bounceEnabled', 'bool'),
        ('itemMargin', 'int32'),
        ('directionType', 'string'),
        ('horizontalType', 'string'),
        ('verticalType', 'string'),
    ],

    'ProjectNodeOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fileName', 'string'),
        ('innerActionSpeed', 'float'),
    ],

    'ComponentOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('type', 'string'),
        ('comAudioOptions', 'table:ComAudioOptions'),
    ],

    'ComAudioOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('name', 'string'),
        ('enabled', 'bool'),
        ('loop', 'bool'),
        ('volume', 'int32'),
        ('fileNameData', 'table:ResourceData'),
    ],

    # ---------------- 动画 ----------------
    'AnimationInfo': [
        ('name', 'string'),
        ('startIndex', 'int32'),
        ('endIndex', 'int32'),
    ],

    'NodeAction': [
        ('duration', 'int32'),
        ('speed', 'float'),
        ('timeLines', 'vector:table:TimeLine'),
        ('currentAnimationName', 'string'),
    ],

    'TimeLine': [
        ('property', 'string'),
        ('actionTag', 'int32'),
        ('frames', 'vector:table:Frame'),
    ],

    'Frame': [
        ('pointFrame', 'table:PointFrame'),
        ('scaleFrame', 'table:ScaleFrame'),
        ('colorFrame', 'table:ColorFrame'),
        ('textureFrame', 'table:TextureFrame'),
        ('eventFrame', 'table:EventFrame'),
        ('intFrame', 'table:IntFrame'),
        ('boolFrame', 'table:BoolFrame'),
        ('innerActionFrame', 'table:InnerActionFrame'),
        ('blendFrame', 'table:BlendFrame'),
    ],

    'PointFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('position', 'struct:Position'),
        ('easingData', 'table:EasingData'),
    ],

    'ScaleFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('scale', 'struct:Scale'),
        ('easingData', 'table:EasingData'),
    ],

    'ColorFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('color', 'struct:Color'),
        ('easingData', 'table:EasingData'),
    ],

    'TextureFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('textureFile', 'table:ResourceData'),
        ('easingData', 'table:EasingData'),
    ],

    'EventFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('value', 'string'),
        ('easingData', 'table:EasingData'),
    ],

    'IntFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('value', 'int32'),
        ('easingData', 'table:EasingData'),
    ],

    'BoolFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('value', 'bool'),
        ('easingData', 'table:EasingData'),
    ],

    'InnerActionFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('innerActionType', 'int32'),
        ('currentAniamtionName', 'string'),
        ('singleFrameIndex', 'int32'),
        ('easingData', 'table:EasingData'),
    ],

    'EasingData': [
        ('type', 'int32'),
        ('points', 'vector:struct:Position'),
    ],

    'BlendFrame': [
        ('frameIndex', 'int32'),
        ('tween', 'bool'),
        ('blendFunc', 'struct:BlendFunc'),
        ('easingData', 'table:EasingData'),
    ],

    # ---------------- 资源 ----------------
    'ResourceData': [
        ('path', 'string'),
        ('plistFile', 'string'),
        ('resourceType', 'int32'),
    ],

    # ---------------- 3D（CSParse3DBinary.fbs） ----------------
    'Node3DOption': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('position3D', 'struct:Vector3'),
        ('rotation3D', 'struct:Vector3'),
        ('scale3D', 'struct:Vector3'),
        ('cameramask', 'int32'),
    ],

    'Sprite3DOptions': [
        ('node3DOption', 'table:Node3DOption'),
        ('fileData', 'table:ResourceData'),
        ('runAction', 'bool'),
        ('isFlipped', 'bool'),
        ('lightFlag', 'int32'),
    ],

    'Particle3DOptions': [
        ('node3DOption', 'table:Node3DOption'),
        ('fileData', 'table:ResourceData'),
    ],

    'UserCameraOptions': [
        ('node3DOption', 'table:Node3DOption'),
        ('fov', 'float'),
        ('nearClip', 'float'),
        ('farClip', 'float'),
        ('cameraFlag', 'int32'),
        ('skyBoxEnabled', 'bool'),
        ('leftFileData', 'table:ResourceData'),
        ('rightFileData', 'table:ResourceData'),
        ('upFileData', 'table:ResourceData'),
        ('downFileData', 'table:ResourceData'),
        ('forwardFileData', 'table:ResourceData'),
        ('backFileData', 'table:ResourceData'),
    ],

    'GameNode3DOption': [
        ('name', 'string'),
        ('skyBoxMask', 'int32'),
        ('skyBoxEnabled', 'bool'),
        ('leftFileData', 'table:ResourceData'),
        ('rightFileData', 'table:ResourceData'),
        ('upFileData', 'table:ResourceData'),
        ('downFileData', 'table:ResourceData'),
        ('forwardFileData', 'table:ResourceData'),
        ('backFileData', 'table:ResourceData'),
        ('frameEvent', 'string'),
        ('customProperty', 'string'),
        ('useDefaultLight', 'bool'),
    ],

    'Light3DOption': [
        ('node3DOption', 'table:Node3DOption'),
        ('enabled', 'bool'),
        ('type', 'int32'),
        ('flag', 'int32'),
        ('intensity', 'float'),
        ('range', 'float'),
        ('outerAngle', 'float'),
    ],

    # ---------------- 骨骼 / 换装（CSArmatureNode.fbs / CSBoneBinary.fbs） ----------------
    'CSArmatureNodeOption': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fileData', 'table:ResourceItemData'),
        ('isLoop', 'bool'),
        ('isAutoPlay', 'bool'),
        ('currentAnimationName', 'string'),
    ],

    'ResourceItemData': [
        ('type', 'int32'),
        ('path', 'string'),
    ],

    'BoneOptions': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('length', 'float'),
        ('blendFunc', 'struct:BlendFunc'),
    ],

    # ---------------- TabControl（CSTabControl.fbs） ----------------
    'TabControlOption': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('headerPlace', 'int32'),
        ('headerWidth', 'int32'),
        ('headerHeight', 'int32'),
        ('selectedTabZoom', 'float'),
        ('selectedTabIndex', 'int32'),
        ('ignoreHeaderTextureSize', 'uint8'),
        ('tabItems', 'vector:table:TabItemOption'),
    ],

    'TabHeaderOption': [
        ('nodeOptions', 'table:WidgetOptions'),
        ('fontRes', 'table:ResourceData'),
        ('fontSize', 'int32'),
        ('titleText', 'string'),
        ('textColor', 'struct:Color'),
        ('normalBackFile', 'table:ResourceData'),
        ('pressBackFile', 'table:ResourceData'),
        ('disableBackFile', 'table:ResourceData'),
        ('crossNormalFile', 'table:ResourceData'),
        ('crossDisableFile', 'table:ResourceData'),
    ],

    'TabItemOption': [
        ('header', 'table:TabHeaderOption'),
        ('container', 'table:NodeTree'),
    ],
}

# ---------------------------------------------------------------------------
# NodeTree.classname -> options 表名
# 依据 CSLoader::getGUIClassName 与各 *Reader::createNodeWithFlatBuffers 的强转类型
# ---------------------------------------------------------------------------
CLASS_OPTIONS = {
    'Node': 'WidgetOptions',
    'SingleNode': 'SingleNodeOptions',
    'Sprite': 'SpriteOptions',
    'ParticleSystem': 'ParticleSystemOptions',
    'GameMap': 'GameMapOptions',

    'Button': 'ButtonOptions',
    'TextButton': 'ButtonOptions',
    'CheckBox': 'CheckBoxOptions',
    'ImageView': 'ImageViewOptions',
    'TextAtlas': 'TextAtlasOptions',
    'LabelAtlas': 'TextAtlasOptions',
    'TextBMFont': 'TextBMFontOptions',
    'LabelBMFont': 'TextBMFontOptions',
    'Text': 'TextOptions',
    'Label': 'TextOptions',
    'TextArea': 'TextOptions',
    'TextField': 'TextFieldOptions',
    'LoadingBar': 'LoadingBarOptions',
    'Slider': 'SliderOptions',
    'Panel': 'PanelOptions',
    'Layout': 'PanelOptions',
    'ScrollView': 'ScrollViewOptions',
    'PageView': 'PageViewOptions',
    'ListView': 'ListViewOptions',

    'ProjectNode': 'ProjectNodeOptions',
    'SimpleAudio': 'ComAudioOptions',
    'Component': 'ComponentOptions',

    'ArmatureNode': 'CSArmatureNodeOption',
    'BoneNode': 'BoneOptions',
    'SkeletonNode': 'BoneOptions',
    'TabControl': 'TabControlOption',
    'TabHeader': 'TabHeaderOption',
    'TabItem': 'TabItemOption',

    'Node3D': 'Node3DOption',
    'Sprite3D': 'Sprite3DOptions',
    'Particle3D': 'Particle3DOptions',
    'UserCamera': 'UserCameraOptions',
    'GameNode3D': 'GameNode3DOption',
    'Light3D': 'Light3DOption',
}

# 各 options 表中承载 WidgetOptions 的字段名（用于提取通用属性）
WIDGET_OPTION_KEYS = ('widgetOptions', 'nodeOptions', 'node3DOption')


def struct_size(name):
    """计算 struct 的对齐后字节数（FlatBuffers 内联布局）。"""
    fields = STRUCTS[name]
    off = 0
    max_align = 1
    for _, ftype in fields:
        _, size = SCALARS[ftype]
        off = (off + size - 1) // size * size
        off += size
        max_align = max(max_align, size)
    return (off + max_align - 1) // max_align * max_align
