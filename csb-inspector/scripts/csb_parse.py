#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cocos Studio CSB 二进制解析器（纯 Python，无第三方依赖）。

重点解析 2D 静态结构：节点树、控件类型、通用属性、各控件专有属性、资源引用。
动画时间轴（action / timeLines）默认跳过，需要时加 --with-action。

支持两种格式：
  1. FlatBuffers 格式（Cocos Studio 2.x / Cocos2d-x 3.10+，本仓库 res/ 下 748 个 csb 全部为此格式）
     根表 CSParseBinary，schema 见 csb_schema.py
  2. 旧版 CocoLoader 格式（Cocos Studio 1.x，stCocoFileHeader 头 + 可选 zlib 压缩）
     解析逻辑对应 frameworks/.../cocostudio/CocoLoader.cpp

用法：
    python csb_parse.py <file.csb>                  # 树形文本输出
    python csb_parse.py <file.csb> --json           # 完整 JSON
    python csb_parse.py <file.csb> --summary        # 统计摘要
    python csb_parse.py <file.csb> --find 名字       # 按 name 查找节点
    python csb_parse.py <file.csb> --path a/b/c     # 按 name 路径定位节点
    python csb_parse.py <file.csb> --resources      # 列出引用的图片/字体/plist
    python csb_parse.py <file.csb> --with-action    # 附带动画时间轴
    python csb_parse.py <dir> --batch               # 批量摘要
"""

import argparse
import json
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from csb_schema import (  # noqa: E402
    SCALARS, STRUCTS, TABLES, CLASS_OPTIONS, WIDGET_OPTION_KEYS, struct_size,
)

# ---------------------------------------------------------------------------
# 字段默认值（FlatBuffers 中缺省字段不写入缓冲区，需按 schema 默认值补齐）
# ---------------------------------------------------------------------------
DEFAULTS = {
    ('WidgetOptions', 'actionTag'): 0,
    ('WidgetOptions', 'zOrder'): 0,
    ('WidgetOptions', 'visible'): True,
    ('WidgetOptions', 'alpha'): 255,
    ('WidgetOptions', 'tag'): 0,
    ('WidgetOptions', 'flipX'): False,
    ('WidgetOptions', 'flipY'): False,
    ('WidgetOptions', 'ignoreSize'): False,
    ('ButtonOptions', 'isLocalized'): False,
    ('ButtonOptions', 'displaystate'): True,
    ('ButtonOptions', 'outlineEnabled'): False,
    ('ButtonOptions', 'outlineSize'): 1,
    ('ButtonOptions', 'shadowEnabled'): False,
    ('ButtonOptions', 'shadowOffsetX'): 2.0,
    ('ButtonOptions', 'shadowOffsetY'): -2.0,
    ('CheckBoxOptions', 'selectedState'): True,
    ('CheckBoxOptions', 'displaystate'): True,
    ('TextOptions', 'isLocalized'): False,
    ('TextOptions', 'touchScaleEnable'): False,
    ('TextOptions', 'isCustomSize'): False,
    ('TextOptions', 'outlineEnabled'): False,
    ('TextOptions', 'outlineSize'): 1,
    ('TextOptions', 'shadowEnabled'): False,
    ('TextOptions', 'shadowOffsetX'): 2.0,
    ('TextOptions', 'shadowOffsetY'): -2.0,
    ('TextBMFontOptions', 'isLocalized'): False,
    ('TextFieldOptions', 'isLocalized'): False,
    ('TextFieldOptions', 'passwordEnabled'): False,
    ('TextFieldOptions', 'maxLengthEnabled'): False,
    ('TextFieldOptions', 'isCustomSize'): False,
    ('LoadingBarOptions', 'percent'): 80,
    ('LoadingBarOptions', 'direction'): 0,
    ('SliderOptions', 'percent'): 50,
    ('SliderOptions', 'displaystate'): True,
    ('PanelOptions', 'clipEnabled'): False,
    ('PanelOptions', 'colorType'): 0,
    ('PanelOptions', 'bgColorOpacity'): 255,
    ('PanelOptions', 'backGroundScale9Enabled'): False,
    ('ScrollViewOptions', 'clipEnabled'): False,
    ('ScrollViewOptions', 'colorType'): 0,
    ('ScrollViewOptions', 'bgColorOpacity'): 255,
    ('ScrollViewOptions', 'backGroundScale9Enabled'): False,
    ('ScrollViewOptions', 'bounceEnabled'): False,
    ('ScrollViewOptions', 'scrollbarEnabeld'): True,
    ('ScrollViewOptions', 'scrollbarAutoHide'): True,
    ('ScrollViewOptions', 'scrollbarAutoHideTime'): 0.2,
    ('PageViewOptions', 'clipEnabled'): False,
    ('PageViewOptions', 'colorType'): 0,
    ('PageViewOptions', 'bgColorOpacity'): 255,
    ('PageViewOptions', 'backGroundScale9Enabled'): False,
    ('ListViewOptions', 'clipEnabled'): False,
    ('ListViewOptions', 'colorType'): 0,
    ('ListViewOptions', 'bgColorOpacity'): 255,
    ('ListViewOptions', 'backGroundScale9Enabled'): False,
    ('ListViewOptions', 'bounceEnabled'): False,
    ('ListViewOptions', 'itemMargin'): 0,
    ('PointFrame', 'tween'): True,
    ('ScaleFrame', 'tween'): True,
    ('ColorFrame', 'tween'): True,
    ('TextureFrame', 'tween'): True,
    ('EventFrame', 'tween'): True,
    ('IntFrame', 'tween'): True,
    ('BoolFrame', 'tween'): True,
    ('BoolFrame', 'value'): True,
    ('InnerActionFrame', 'tween'): True,
    ('BlendFrame', 'tween'): True,
    ('EasingData', 'type'): -1,
    ('Sprite3DOptions', 'runAction'): False,
    ('UserCameraOptions', 'fov'): 60.0,
    ('UserCameraOptions', 'nearClip'): 1.0,
    ('UserCameraOptions', 'farClip'): 1000.0,
    ('CSArmatureNodeOption', 'isLoop'): True,
    ('CSArmatureNodeOption', 'isAutoPlay'): True,
    ('ResourceItemData', 'type'): 0,
}


# ===========================================================================
# FlatBuffers 读取
# ===========================================================================
class FlatBufferReader(object):
    def __init__(self, buf):
        self.buf = buf
        self.size = len(buf)

    # -- 基础读取 ----------------------------------------------------------
    def _unpack(self, fmt, pos):
        return struct.unpack_from('<' + fmt, self.buf, pos)[0]

    def u8(self, p):
        return self.buf[p]

    def i8(self, p):
        return self._unpack('b', p)

    def u16(self, p):
        return self._unpack('H', p)

    def i16(self, p):
        return self._unpack('h', p)

    def u32(self, p):
        return self._unpack('I', p)

    def i32(self, p):
        return self._unpack('i', p)

    def f32(self, p):
        return self._unpack('f', p)

    # -- 表结构 ------------------------------------------------------------
    def root(self):
        return self.u32(0)

    def vtable_pos(self, table_pos):
        return table_pos - self.i32(table_pos)

    def field_pos(self, table_pos, field_id):
        vt = self.vtable_pos(table_pos)
        vt_size = self.u16(vt)
        idx = 4 + field_id * 2
        if idx + 2 > vt_size:
            return 0
        off = self.u16(vt + idx)
        return table_pos + off if off else 0

    def indirect(self, pos):
        return pos + self.u32(pos)

    def read_string(self, pos):
        n = self.u32(pos)
        return self.buf[pos + 4:pos + 4 + n].decode('utf-8', 'replace')

    def read_scalar(self, ftype, pos):
        fmt, _ = SCALARS[ftype]
        v = self._unpack(fmt, pos)
        if ftype == 'bool':
            return bool(v)
        return v

    def read_struct(self, name, pos):
        out = {}
        off = 0
        for fname, ftype in STRUCTS[name]:
            _, fsize = SCALARS[ftype]
            off = (off + fsize - 1) // fsize * fsize
            out[fname] = self.read_scalar(ftype, pos + off)
            off += fsize
        return out

    def read_vector(self, elem_type, pos):
        n = self.u32(pos)
        base = pos + 4
        out = []
        if elem_type == 'string':
            for i in range(n):
                out.append(self.read_string(self.indirect(base + i * 4)))
        elif elem_type.startswith('table:'):
            tname = elem_type[6:]
            for i in range(n):
                out.append(self.read_table(tname, self.indirect(base + i * 4)))
        elif elem_type.startswith('struct:'):
            sname = elem_type[7:]
            ssize = struct_size(sname)
            for i in range(n):
                out.append(self.read_struct(sname, base + i * ssize))
        else:
            fmt, fsize = SCALARS[elem_type]
            for i in range(n):
                v = self._unpack(fmt, base + i * fsize)
                out.append(bool(v) if elem_type == 'bool' else v)
        return out

    def read_field(self, table_name, field_name, ftype, pos):
        if ftype == 'string':
            return self.read_string(self.indirect(pos))
        if ftype.startswith('table:'):
            return self.read_table(ftype[6:], self.indirect(pos))
        if ftype.startswith('struct:'):
            return self.read_struct(ftype[7:], pos)
        if ftype.startswith('vector:'):
            # 向量字段存的是指向向量起始位置的 uoffset
            return self.read_vector(ftype[7:], self.indirect(pos))
        return self.read_scalar(ftype, pos)

    def read_table(self, table_name, table_pos, with_defaults=True):
        fields = TABLES.get(table_name)
        if fields is None:
            return {'__unknown_table__': table_name, '__pos__': table_pos}
        out = {}
        for fid, (fname, ftype) in enumerate(fields):
            pos = self.field_pos(table_pos, fid)
            if pos:
                try:
                    out[fname] = self.read_field(table_name, fname, ftype, pos)
                except Exception as exc:  # 容错：字段损坏时保留错误信息
                    out[fname] = '<parse error: %s>' % exc
            elif with_defaults and (table_name, fname) in DEFAULTS:
                out[fname] = DEFAULTS[(table_name, fname)]
        return out


# ===========================================================================
# 格式识别
# ===========================================================================
def detect_format(buf):
    """返回 'flatbuffer' / 'cocoloader' / 'unknown'。"""
    if len(buf) >= 88:
        desc = buf[:32].split(b'\0')[0]
        if desc.startswith(b'CocoStudio'):
            return 'cocoloader'
    if _looks_like_flatbuffer(buf):
        return 'flatbuffer'
    return 'unknown'


def _looks_like_flatbuffer(buf):
    """校验根表第一个字段（version 字符串）是否可读。"""
    if len(buf) < 8:
        return False
    root = struct.unpack_from('<I', buf, 0)[0]
    if root == 0 or root + 4 > len(buf):
        return False
    try:
        vt = root - struct.unpack_from('<i', buf, root)[0]
        if vt < 0 or vt + 4 > len(buf):
            return False
        vt_size = struct.unpack_from('<H', buf, vt)[0]
        if vt_size < 6:
            return False
        off = struct.unpack_from('<H', buf, vt + 4)[0]
        if off == 0:
            return False
        sp = root + off
        sp += struct.unpack_from('<I', buf, sp)[0]   # 字段是 uoffset
        n = struct.unpack_from('<I', buf, sp)[0]
        if n == 0 or n > 32 or sp + 4 + n > len(buf):
            return False
        s = buf[sp + 4:sp + 4 + n]
        return all(32 <= c < 127 for c in s)
    except Exception:
        return False


# ===========================================================================
# CSB（FlatBuffers）解析
# ===========================================================================
def parse_flatbuffer(buf, with_action=False):
    r = FlatBufferReader(buf)
    root = r.root()

    data = {
        'format': 'flatbuffer',
        'version': _read_str_field(r, root, 0) or '',
        'textures': _read_vector_field(r, root, 1, 'string'),
        'texturePngs': _read_vector_field(r, root, 2, 'string'),
        'nodeTree': None,
        'action': None,
        'animationList': None,
    }

    tree_pos = r.field_pos(root, 3)
    if tree_pos:
        data['nodeTree'] = _walk_node_tree(r, r.indirect(tree_pos))

    if with_action:
        act_pos = r.field_pos(root, 4)
        if act_pos:
            data['action'] = r.read_table('NodeAction', r.indirect(act_pos))
        anim_pos = r.field_pos(root, 5)
        if anim_pos:
            data['animationList'] = r.read_vector(
                'table:AnimationInfo', r.indirect(anim_pos))

    return data


def _read_str_field(r, table_pos, fid):
    pos = r.field_pos(table_pos, fid)
    return r.read_string(r.indirect(pos)) if pos else None


def _read_vector_field(r, table_pos, fid, elem_type):
    pos = r.field_pos(table_pos, fid)
    return r.read_vector(elem_type, r.indirect(pos)) if pos else []


def _walk_node_tree(r, tree_pos):
    """递归解析 NodeTree；options.data 的真实类型由 classname 决定。"""
    classname = _read_str_field(r, tree_pos, 0) or ''
    custom = _read_str_field(r, tree_pos, 3) or ''
    effective = custom if custom else classname

    options = {}
    opts_pos = r.field_pos(tree_pos, 2)
    if opts_pos:
        opts_table = r.indirect(opts_pos)
        data_pos = r.field_pos(opts_table, 0)
        if data_pos:
            tname = CLASS_OPTIONS.get(effective, 'WidgetOptions')
            options = r.read_table(tname, r.indirect(data_pos))

    children = []
    ch_pos = r.field_pos(tree_pos, 1)
    if ch_pos:
        vec = r.indirect(ch_pos)
        n = r.u32(vec)
        for i in range(n):
            children.append(_walk_node_tree(r, r.indirect(vec + 4 + i * 4)))

    return {
        'classname': classname,
        'customClassName': custom,
        'effectiveClassname': effective,
        'options': options,
        'children': children,
    }


# ===========================================================================
# 旧版 CocoLoader 格式
# ===========================================================================
COCO_TYPE_CHARS = {'N': 'null', 'F': 'false', 'T': 'true', 'O': 'object',
                   'A': 'array', 'S': 'string', 'V': 'number'}
RAPIDJSON_TYPES = ['null', 'false', 'true', 'object', 'array', 'string', 'number']


class CocoLoader(object):
    HEADER_SIZE = 88  # 32 + 32 + 4*6

    def __init__(self, buf):
        self.raw = buf
        (self.file_desc, self.version, self.data_size, self.compress_size,
         self.object_count, self.attrib_addr, self.node_addr,
         self.string_addr) = struct.unpack_from('<32s32sIIIIII', buf, 0)
        self.file_desc = self.file_desc.split(b'\0')[0].decode('utf-8', 'replace')
        self.version = self.version.split(b'\0')[0].decode('utf-8', 'replace')

        payload = buf[self.HEADER_SIZE:]
        if self.compress_size > 0:
            self.data = zlib.decompress(payload[:self.compress_size])
        else:
            self.data = payload[:self.data_size]

    # -- 基础 --------------------------------------------------------------
    def string_at(self, off):
        base = self.string_addr
        end = self.data.find(b'\0', base + off)
        if end < 0:
            end = len(self.data)
        return self.data[base + off:end].decode('utf-8', 'replace')

    def object_desc(self, index):
        pos = index * 12
        attrib_num = self.data[pos]
        name_off = struct.unpack_from('<I', self.data, pos + 4)[0]
        attrib_arr = struct.unpack_from('<I', self.data, pos + 8)[0]
        return attrib_num, name_off, attrib_arr

    def attrib_desc(self, obj_index, attrib_index):
        _, _, attrib_arr = self.object_desc(obj_index)
        pos = self.attrib_addr + attrib_arr + attrib_index * 8
        type_char = chr(self.data[pos])
        name_off = struct.unpack_from('<I', self.data, pos + 4)[0]
        return type_char, name_off

    def node(self, pos):
        obj_index, attrib_index = struct.unpack_from('<hh', self.data, pos)
        child_num = self.data[pos + 4]
        sz_value = struct.unpack_from('<I', self.data, pos + 8)[0]
        child_array = struct.unpack_from('<I', self.data, pos + 12)[0]
        return obj_index, attrib_index, child_num, sz_value, child_array

    # -- 递归构建 ----------------------------------------------------------
    def build(self, pos):
        obj_index, attrib_index, child_num, sz_value, child_array = self.node(pos)
        value = self.string_at(sz_value)

        if obj_index >= 0:
            if attrib_index >= 0:
                type_char, name_off = self.attrib_desc(obj_index, attrib_index)
                name = self.string_at(name_off)
                typ = COCO_TYPE_CHARS.get(type_char, 'string')
                if typ in ('false', 'true'):
                    typ = 'true' if value and value[0] != '0' else 'false'
                return {'name': name, 'type': typ, 'value': value}
            # 对象节点
            _, name_off, _ = self.object_desc(obj_index)
            name = value if value else self.string_at(name_off)
            return {
                'name': name,
                'type': 'object',
                'children': [self.build(self.node_addr + child_array + i * 16)
                             for i in range(child_num)],
            }

        if attrib_index >= 0:
            # 数组元素
            typ = RAPIDJSON_TYPES[child_num] if child_num < len(RAPIDJSON_TYPES) else 'unknown'
            name = self.string_at(child_array)
            return {'name': name, 'type': typ, 'value': value}

        # 数组
        return {
            'name': value,
            'type': 'array',
            'children': [self.build(self.node_addr + child_array + i * 16)
                         for i in range(child_num)],
        }

    def parse(self):
        return {
            'format': 'cocoloader',
            'fileDesc': self.file_desc,
            'version': self.version,
            'dataSize': self.data_size,
            'compressSize': self.compress_size,
            'objectCount': self.object_count,
            'root': self.build(self.node_addr),
        }


# ===========================================================================
# 节点辅助
# ===========================================================================
def widget_options(node):
    """取出节点承载通用属性的 WidgetOptions 表。"""
    opts = node.get('options') or {}
    for key in WIDGET_OPTION_KEYS:
        if isinstance(opts.get(key), dict):
            return opts[key]
    if 'name' in opts:
        return opts
    return {}


def node_name(node):
    return widget_options(node).get('name') or ''


def iter_nodes(node):
    """深度优先遍历节点树。"""
    if not node:
        return
    yield node
    for child in node.get('children') or []:
        for n in iter_nodes(child):
            yield n


# ===========================================================================
# 输出
# ===========================================================================
def _fmt_num(v):
    if isinstance(v, float):
        return ('%.4f' % v).rstrip('0').rstrip('.') or '0'
    return str(v)


def _node_label(node):
    w = widget_options(node)
    parts = [node.get('effectiveClassname') or node.get('classname') or '?']
    if w.get('name'):
        parts.append('"%s"' % w['name'])
    pos = w.get('position')
    if isinstance(pos, dict):
        parts.append('pos=(%s,%s)' % (_fmt_num(pos.get('x', 0)), _fmt_num(pos.get('y', 0))))
    size = w.get('size')
    if isinstance(size, dict):
        parts.append('size=(%s,%s)' % (_fmt_num(size.get('width', 0)),
                                       _fmt_num(size.get('height', 0))))
    if w.get('visible') is False:
        parts.append('HIDDEN')
    return ' '.join(parts)


def print_tree(node, indent=0, max_depth=None):
    if node is None:
        return
    print('%s%s' % ('  ' * indent, _node_label(node)))
    if max_depth is not None and indent >= max_depth:
        return
    for child in node.get('children') or []:
        print_tree(child, indent + 1, max_depth)


def summarize(data):
    stats = {'format': data.get('format'), 'version': data.get('version'),
             'total': 0, 'classes': {}, 'maxDepth': 0,
             'textures': len(data.get('textures') or [])}

    def walk(node, depth):
        if not node:
            return
        stats['total'] += 1
        stats['maxDepth'] = max(stats['maxDepth'], depth)
        cls = node.get('effectiveClassname') or node.get('classname') or '?'
        stats['classes'][cls] = stats['classes'].get(cls, 0) + 1
        for c in node.get('children') or []:
            walk(c, depth + 1)

    walk(data.get('nodeTree'), 1)
    return stats


def collect_resources(data):
    """收集 csb 引用的图片 / plist / 字体 / 其他资源路径。"""
    images, plists, fonts, others = set(), set(), set(), set()

    def scan_table(tbl):
        if not isinstance(tbl, dict):
            return
        path = tbl.get('path')
        if isinstance(path, str) and path:
            low = path.lower()
            if low.endswith(('.png', '.jpg', '.jpeg')):
                images.add(path)
            elif low.endswith(('.plist', '.json')):
                plists.add(path)
            elif low.endswith(('.ttf', '.fnt', '.otf')):
                fonts.add(path)
            else:
                others.add(path)
        plist = tbl.get('plistFile')
        if isinstance(plist, str) and plist:
            plists.add(plist)

    def walk(node):
        if not node:
            return
        for value in (node.get('options') or {}).values():
            if isinstance(value, dict):
                scan_table(value)
        for c in node.get('children') or []:
            walk(c)

    walk(data.get('nodeTree'))
    for t in data.get('textures') or []:
        plists.add(t)
    return {
        'images': sorted(images),
        'plists': sorted(plists),
        'fonts': sorted(fonts),
        'others': sorted(others),
    }


def find_nodes(node, name):
    return [n for n in iter_nodes(node) if node_name(n) == name]


def find_path(node, path):
    """按 name 路径（a/b/c）定位节点。"""
    cur = node
    for part in [p for p in path.split('/') if p]:
        if cur is None:
            return None
        cur = next((c for c in cur.get('children') or [] if node_name(c) == part), None)
    return cur


# ===========================================================================
# 入口
# ===========================================================================
def load(path, with_action=False):
    with open(path, 'rb') as f:
        buf = f.read()
    fmt = detect_format(buf)
    if fmt == 'flatbuffer':
        return parse_flatbuffer(buf, with_action)
    if fmt == 'cocoloader':
        return CocoLoader(buf).parse()
    raise ValueError('无法识别的 csb 格式（既不是 FlatBuffers 也不是 CocoLoader）')


def main():
    ap = argparse.ArgumentParser(description='解析 Cocos Studio CSB 二进制文件')
    ap.add_argument('target', help='csb 文件或目录')
    ap.add_argument('--json', action='store_true', help='输出完整 JSON')
    ap.add_argument('--summary', action='store_true', help='输出统计摘要')
    ap.add_argument('--find', metavar='NAME', help='按节点 name 查找')
    ap.add_argument('--path', metavar='A/B/C', help='按 name 路径定位节点')
    ap.add_argument('--resources', action='store_true', help='列出引用的资源')
    ap.add_argument('--with-action', action='store_true', help='附带解析动画时间轴')
    ap.add_argument('--depth', type=int, default=None, help='树形输出最大深度')
    ap.add_argument('--batch', action='store_true', help='批量处理目录下所有 .csb')
    ap.add_argument('--out', metavar='FILE', help='将 JSON 写入文件')
    args = ap.parse_args()

    if args.batch or os.path.isdir(args.target):
        files = []
        for root, _, names in os.walk(args.target):
            for n in names:
                if n.lower().endswith('.csb'):
                    files.append(os.path.join(root, n))
        files.sort()
        print('%-52s %6s %5s %8s' % ('file', 'nodes', 'depth', 'textures'))
        for f in files:
            rel = os.path.relpath(f, args.target)
            try:
                s = summarize(load(f))
                print('%-52s %6s %5s %8s' % (rel, s['total'], s['maxDepth'], s['textures']))
            except Exception as exc:
                print('%-52s %6s %5s %8s' % (rel, 'ERR', str(exc)[:40], ''))
        return

    data = load(args.target, args.with_action)

    if args.find:
        hits = find_nodes(data.get('nodeTree'), args.find)
        if not hits:
            print('未找到 name=%s 的节点' % args.find)
            return
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return

    if args.path:
        node = find_path(data.get('nodeTree'), args.path)
        if not node:
            print('未找到路径 %s' % args.path)
            return
        print(json.dumps(node, ensure_ascii=False, indent=2))
        return

    if args.resources:
        print(json.dumps(collect_resources(data), ensure_ascii=False, indent=2))
        return

    if args.summary:
        print(json.dumps(summarize(data), ensure_ascii=False, indent=2))
        return

    if args.json or args.out:
        text = json.dumps(data, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(text)
            print('已写入 %s' % args.out)
        else:
            print(text)
        return

    # 默认：树形文本
    if data.get('format') == 'cocoloader':
        print('format: CocoLoader  version: %s  objects: %s'
              % (data.get('version'), data.get('objectCount')))
        print(json.dumps(data.get('root'), ensure_ascii=False, indent=2))
        return

    print('version: %s' % data.get('version'))
    textures = data.get('textures') or []
    if textures:
        print('textures: %s' % ', '.join(sorted(set(textures))))
    print('---')
    print_tree(data.get('nodeTree'), 0, args.depth)


if __name__ == '__main__':
    main()
