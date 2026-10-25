"""Tiny writer for Godot 4 text scenes (.tscn) and resources (.tres)."""
import math
import os


def num(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    s = ("%.4f" % x).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def v2(x, y):
    return f"Vector2({num(x)}, {num(y)})"


def v3(x, y, z):
    return f"Vector3({num(x)}, {num(y)}, {num(z)})"


def v4(x, y, z, w):
    return f"Vector4({num(x)}, {num(y)}, {num(z)}, {num(w)})"


def color(c):
    r, g, b = c[:3]
    a = c[3] if len(c) > 3 else 1.0
    return f"Color({num(r)}, {num(g)}, {num(b)}, {num(a)})"


def string(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strings(items):
    return "PackedStringArray(" + ", ".join(string(s) for s in items) + ")"


def vec4_array(items):
    return "Array[Vector4]([" + ", ".join(v4(*i) for i in items) + "])"


def _matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def basis(rot=(0, 0, 0), scale=(1, 1, 1)):
    """Rows of Basis.from_euler(rot) (YXZ order) scaled per axis."""
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    rx, ry, rz = rot
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    mx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    my = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    mz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    r = _matmul(_matmul(my, mx), mz)
    return [[r[i][j] * scale[j] for j in range(3)] for i in range(3)]


def xform(pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    b = basis(rot, scale)
    vals = [b[i][j] for i in range(3) for j in range(3)] + list(pos)
    return "Transform3D(" + ", ".join(num(v) for v in vals) + ")"


class Doc:
    """Collects ext/sub resources and nodes, then serialises them."""

    def __init__(self):
        self.ext = []  # (type, path, id)
        self.sub = []  # (type, id, props)
        self._ext_ids = {}
        self._sub_ids = {}
        self.body = []

    def ext_res(self, type_, path):
        if path not in self._ext_ids:
            rid = f"{len(self.ext) + 1}_{os.path.splitext(os.path.basename(path))[0][:12]}"
            self.ext.append((type_, path, rid))
            self._ext_ids[path] = rid
        return f'ExtResource("{self._ext_ids[path]}")'

    def sub_res(self, type_, props):
        key = (type_, tuple(sorted(props.items())))
        if key not in self._sub_ids:
            rid = f"{type_}_{len(self.sub) + 1}"
            self.sub.append((type_, rid, props))
            self._sub_ids[key] = rid
        return f'SubResource("{self._sub_ids[key]}")'

    def _header_and_resources(self, header):
        out = [header, ""]
        for type_, path, rid in self.ext:
            out.append(f'[ext_resource type="{type_}" path="{path}" id="{rid}"]')
        if self.ext:
            out.append("")
        for type_, rid, props in self.sub:
            out.append(f'[sub_resource type="{type_}" id="{rid}"]')
            for k, v in props.items():
                out.append(f"{k} = {v}")
            out.append("")
        return out

    def save(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)


class Scene(Doc):
    def __init__(self, root_name, root_type=None, root_instance=None, props=None):
        super().__init__()
        self.nodes = []
        self.node(root_name, root_type, None, root_instance, props)

    def node(self, name, type_=None, parent=".", instance=None, props=None, groups=None):
        head = f'[node name="{name}"'
        if type_:
            head += f' type="{type_}"'
        if parent is not None:
            head += f' parent="{parent}"'
        if instance:
            head += f" instance={instance}"
        if groups:
            head += " groups=[" + ", ".join(string(g) for g in groups) + "]"
        head += "]"
        lines = [head]
        for k, v in (props or {}).items():
            lines.append(f"{k} = {v}")
        self.nodes.append("\n".join(lines))
        return name

    def write(self, path):
        steps = len(self.ext) + len(self.sub) + 1
        out = self._header_and_resources(f"[gd_scene load_steps={steps} format=3]")
        out.append("\n\n".join(self.nodes))
        self.save(path, "\n".join(out) + "\n")


class Resource(Doc):
    def __init__(self, type_, props=None):
        super().__init__()
        self.type = type_
        self.props = props or {}

    def write(self, path):
        steps = len(self.ext) + len(self.sub) + 1
        header = f'[gd_resource type="{self.type}" load_steps={steps} format=3]'
        if steps == 1:
            header = f'[gd_resource type="{self.type}" format=3]'
        out = self._header_and_resources(header)
        out.append("[resource]")
        for k, v in self.props.items():
            out.append(f"{k} = {v}")
        self.save(path, "\n".join(out) + "\n")
