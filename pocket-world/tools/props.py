"""Cartoon material palette, prop library and core character/UI scenes."""
import math
import os

from tscn import Resource, Scene, color, num, string, v3, xform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT_DIR = "res://assets/materials"
PROP_DIR = "res://assets/props"

# name: (rgb, outline, emission)
PALETTE = {
    "wood": ((0.56, 0.36, 0.22), True, 0),
    "wood_dark": ((0.38, 0.24, 0.15), True, 0),
    "wood_light": ((0.84, 0.64, 0.42), True, 0),
    "leaf": ((0.38, 0.73, 0.3), True, 0),
    "leaf_light": ((0.56, 0.84, 0.36), True, 0),
    "leaf_dark": ((0.22, 0.55, 0.3), True, 0),
    "leaf_autumn": ((0.98, 0.62, 0.25), True, 0),
    "pine": ((0.17, 0.48, 0.34), True, 0),
    "palm": ((0.32, 0.72, 0.32), True, 0),
    "grass": ((0.45, 0.76, 0.32), False, 0),
    "snow": ((0.95, 0.97, 1.0), True, 0),
    "ice": ((0.72, 0.9, 1.0), True, 0),
    "stone": ((0.66, 0.65, 0.68), True, 0),
    "stone_dark": ((0.47, 0.47, 0.52), True, 0),
    "wall_cream": ((0.99, 0.93, 0.8), True, 0),
    "wall_pink": ((0.99, 0.8, 0.8), True, 0),
    "wall_mint": ((0.8, 0.95, 0.86), True, 0),
    "wall_sky": ((0.82, 0.9, 1.0), True, 0),
    "wall_butter": ((1.0, 0.92, 0.6), True, 0),
    "roof_red": ((0.9, 0.34, 0.3), True, 0),
    "roof_blue": ((0.33, 0.52, 0.88), True, 0),
    "roof_teal": ((0.2, 0.66, 0.62), True, 0),
    "roof_orange": ((0.96, 0.6, 0.25), True, 0),
    "roof_purple": ((0.62, 0.42, 0.82), True, 0),
    "roof_dark": ((0.35, 0.28, 0.32), True, 0),
    "window": ((0.6, 0.85, 1.0), True, 0.15),
    "door": ((0.62, 0.36, 0.2), True, 0),
    "white": ((0.97, 0.97, 0.97), True, 0),
    "red": ((0.92, 0.26, 0.26), True, 0),
    "yellow": ((1.0, 0.85, 0.3), True, 0),
    "orange": ((1.0, 0.56, 0.16), True, 0),
    "pink": ((1.0, 0.6, 0.72), True, 0),
    "purple": ((0.68, 0.48, 0.9), True, 0),
    "blue": ((0.35, 0.6, 0.95), True, 0),
    "black": ((0.12, 0.11, 0.13), False, 0),
    "metal": ((0.25, 0.25, 0.3), True, 0),
    "mushroom_red": ((0.92, 0.24, 0.24), True, 0),
    "mushroom_blue": ((0.4, 0.55, 0.95), True, 0),
    "mushroom_stem": ((0.98, 0.94, 0.84), True, 0),
    "sand": ((0.96, 0.88, 0.62), True, 0),
    "coconut": ((0.45, 0.3, 0.18), True, 0),
    "water_still": ((0.42, 0.74, 0.96), False, 0.1),
    "glow_yellow": ((1.0, 0.9, 0.5), False, 2.5),
    "glow_white": ((1.0, 1.0, 1.0), False, 2.0),
    "fire": ((1.0, 0.55, 0.15), False, 3.0),
    "fire_core": ((1.0, 0.9, 0.4), False, 3.0),
    "crystal": ((0.55, 0.9, 1.0), True, 0.8),
    "crystal_pink": ((1.0, 0.65, 0.9), True, 0.8),
    "hay": ((0.96, 0.82, 0.42), True, 0),
    "pumpkin": ((1.0, 0.55, 0.15), True, 0),
    "carrot": ((1.0, 0.5, 0.1), False, 0),
}


def mat(name):
    return f"{MAT_DIR}/{name}.tres"


def write_materials():
    out = Resource("StandardMaterial3D", {
        "cull_mode": "1",
        "shading_mode": "0",
        "albedo_color": color((0.13, 0.1, 0.14)),
        "grow": "true",
        "grow_amount": "0.022",
    })
    out.write(os.path.join(ROOT, "assets/materials/outline.tres"))
    for name, (rgb, outline, emission) in PALETTE.items():
        r = Resource("StandardMaterial3D")
        props = {}
        if outline:
            props["next_pass"] = r.ext_res("Material", mat("outline"))
        props["albedo_color"] = color(rgb)
        props["roughness"] = "1.0"
        props["diffuse_mode"] = "3"
        props["specular_mode"] = "2"
        if emission:
            props["emission_enabled"] = "true"
            props["emission"] = color(rgb)
            props["emission_energy_multiplier"] = num(emission)
        r.props = props
        r.write(os.path.join(ROOT, f"assets/materials/{name}.tres"))


# --- mesh / shape specs ----------------------------------------------------

def sphere(r, seg=16, rings=8, hemi=False):
    p = {"radius": num(r), "height": num(r if hemi else r * 2), "radial_segments": str(seg), "rings": str(rings)}
    if hemi:
        p["is_hemisphere"] = "true"
    return ("SphereMesh", p)


def cyl(top, bottom, h, seg=12):
    return ("CylinderMesh", {"top_radius": num(top), "bottom_radius": num(bottom), "height": num(h), "radial_segments": str(seg), "rings": "1"})


def box(x, y, z):
    return ("BoxMesh", {"size": v3(x, y, z)})


def capsule(r, h):
    return ("CapsuleMesh", {"radius": num(r), "height": num(h), "radial_segments": "12", "rings": "4"})


def prism(x, y, z):
    return ("PrismMesh", {"size": v3(x, y, z)})


def torus(inner, outer):
    return ("TorusMesh", {"inner_radius": num(inner), "outer_radius": num(outer), "rings": "32", "ring_segments": "12"})


def shape_cyl(r, h):
    return ("CylinderShape3D", {"radius": num(r), "height": num(h)})


def shape_box(x, y, z):
    return ("BoxShape3D", {"size": v3(x, y, z)})


def shape_sphere(r):
    return ("SphereShape3D", {"radius": num(r)})


def shape_capsule(r, h):
    return ("CapsuleShape3D", {"radius": num(r), "height": num(h)})


class Prop:
    def __init__(self, name, script=None, script_props=None):
        self.name = name
        self.parts = []  # (parent, mesh, material, pos, rot, scale)
        self.shapes = []  # (shape, pos, rot)
        self.pivots = []  # (name, parent, pos, rot, script, props)
        self.extras = []  # (name, type, parent, props)
        self.script = script
        self.script_props = script_props or {}

    def mesh(self, mesh, material, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent="."):
        self.parts.append((parent, mesh, material, pos, rot, scale))
        return self

    def shape(self, shape, pos=(0, 0, 0), rot=(0, 0, 0)):
        self.shapes.append((shape, pos, rot))
        return self

    def pivot(self, name, pos=(0, 0, 0), rot=(0, 0, 0), script=None, props=None, parent="."):
        self.pivots.append((name, parent, pos, rot, script, props or {}))
        return name

    def extra(self, name, type_, props, parent="."):
        self.extras.append((name, type_, parent, props))

    def write(self):
        root_type = "StaticBody3D" if self.shapes else "Node3D"
        sc = Scene(self.name, root_type)
        if self.script:
            root_props = {"script": sc.ext_res("Script", self.script)}
            root_props.update(self.script_props)
            sc.nodes[0] += "".join(f"\n{k} = {v}" for k, v in root_props.items())
        for i, (shape, pos, rot) in enumerate(self.shapes):
            sc.node(f"Collision{i + 1}", "CollisionShape3D", ".", props={
                "transform": xform(pos, rot),
                "shape": sc.sub_res(*shape),
            })
        for name, parent, pos, rot, script, props in self.pivots:
            p = {"transform": xform(pos, rot)}
            if script:
                p["script"] = sc.ext_res("Script", script)
            p.update(props)
            sc.node(name, "Node3D", parent, props=p)
        for i, (parent, mesh, material, pos, rot, scale) in enumerate(self.parts):
            sc.node(f"Mesh{i + 1}", "MeshInstance3D", parent, props={
                "transform": xform(pos, rot, scale),
                "mesh": sc.sub_res(*mesh),
                "surface_material_override/0": sc.ext_res("StandardMaterial3D", mat(material)),
            })
        for name, type_, parent, props in self.extras:
            sc.node(name, type_, parent, props=props)
        sc.write(os.path.join(ROOT, f"assets/props/{self.name}.tscn"))


# --- prop library ----------------------------------------------------------

def tree_round(name, leaf, fruit=None):
    p = Prop(name)
    p.mesh(cyl(0.17, 0.26, 2.3, 10), "wood", (0, 1.15, 0))
    p.mesh(sphere(1.35), leaf, (0, 3.0, 0))
    p.mesh(sphere(0.95), leaf, (0.85, 2.55, 0.3))
    p.mesh(sphere(0.9), leaf, (-0.75, 2.65, -0.35))
    p.mesh(sphere(0.8), leaf, (0.1, 3.75, 0.45))
    if fruit:
        for a in range(5):
            ang = a * 1.3
            p.mesh(sphere(0.13, 10, 5), fruit, (math.cos(ang) * 1.25, 2.5 + (a % 3) * 0.4, math.sin(ang) * 1.25))
    p.shape(shape_cyl(0.3, 2.4), (0, 1.2, 0))
    return p


def tree_pine(name, snowy=False):
    p = Prop(name)
    p.mesh(cyl(0.14, 0.2, 1.3, 8), "wood_dark", (0, 0.65, 0))
    tiers = [(1.4, 1.9, 1.85), (1.08, 1.6, 2.9), (0.75, 1.3, 3.85)]
    for r, h, y in tiers:
        p.mesh(cyl(0.0, r, h, 10), "pine", (0, y, 0))
        if snowy:
            p.mesh(cyl(0.0, r * 0.56, h * 0.46, 10), "snow", (0, y + h * 0.28, 0))
    p.shape(shape_cyl(0.32, 2.4), (0, 1.2, 0))
    return p


def tree_palm():
    p = Prop("tree_palm")
    x = 0.0
    tilt = 0.0
    y = 0.0
    for i in range(6):
        r = 0.2 - i * 0.012
        x += 0.12 * i
        tilt -= 0.05
        p.mesh(cyl(r - 0.01, r, 0.95, 8), "wood_light" if i % 2 else "wood", (x, y + 0.45, 0), (0, 0, tilt))
        y += 0.9
    top = (x + 0.15, y + 0.05, 0)
    for i in range(7):
        ang = i * math.tau / 7
        dx, dz = math.cos(ang), math.sin(ang)
        p.mesh(box(0.55, 0.06, 2.3), "palm", (top[0] + dx * 1.05, top[1] - 0.35, top[2] + dz * 1.05), (0.35, math.atan2(dx, dz), 0))
    for i in range(3):
        ang = i * math.tau / 3 + 0.4
        p.mesh(sphere(0.17, 10, 6), "coconut", (top[0] + math.cos(ang) * 0.25, top[1] - 0.3, math.sin(ang) * 0.25))
    p.mesh(sphere(0.35, 12, 6), "palm", top, (0, 0, 0), (1, 0.5, 1))
    p.shape(shape_cyl(0.3, 4.5), (0.5, 2.25, 0))
    return p


def bush(name, leaf, berries=None):
    p = Prop(name)
    p.mesh(sphere(0.62), leaf, (0, 0.45, 0))
    p.mesh(sphere(0.48), leaf, (0.52, 0.33, 0.12))
    p.mesh(sphere(0.46), leaf, (-0.48, 0.32, -0.1))
    p.mesh(sphere(0.4), leaf, (0.05, 0.3, 0.5))
    if berries:
        for a in range(6):
            ang = a * 1.05
            p.mesh(sphere(0.08, 8, 4), berries, (math.cos(ang) * 0.62, 0.5 + (a % 2) * 0.2, math.sin(ang) * 0.62))
    p.shape(shape_sphere(0.6), (0, 0.4, 0))
    return p


def flowers(name, petal):
    p = Prop(name)
    spots = [(0, 0), (0.35, 0.2), (-0.3, 0.25), (0.15, -0.35), (-0.25, -0.2), (0.45, -0.15)]
    for i, (x, z) in enumerate(spots):
        h = 0.28 + (i % 3) * 0.06
        p.mesh(cyl(0.018, 0.018, h, 5), "leaf", (x, h / 2, z))
        p.mesh(sphere(0.09, 8, 4), petal, (x, h + 0.02, z), (0, 0, 0), (1, 0.55, 1))
        p.mesh(sphere(0.04, 6, 3), "yellow", (x, h + 0.06, z))
    return p


def grass_tuft():
    p = Prop("grass_tuft")
    for i, (x, z, h, t) in enumerate([(0, 0, 0.45, 0), (0.12, 0.05, 0.35, 0.3), (-0.1, 0.06, 0.38, -0.3), (0.02, -0.1, 0.3, 0.2)]):
        p.mesh(cyl(0.0, 0.06, h, 4), "grass", (x, h / 2, z), (t * 0.5, i, t))
    return p


def rock(name, snowy=False):
    p = Prop(name)
    p.mesh(sphere(1.0, 7, 4), "stone", (0, 0.25, 0), (0, 0, 0), (1.25, 0.75, 1.0))
    p.mesh(sphere(0.55, 6, 3), "stone_dark", (0.75, 0.1, 0.4), (0, 0.6, 0), (1.1, 0.7, 1.0))
    if snowy:
        p.mesh(sphere(0.92, 7, 3, True), "snow", (0, 0.55, 0), (0, 0, 0), (1.2, 0.45, 0.95))
    p.shape(shape_sphere(0.85), (0, 0.15, 0))
    return p


def mushroom(name, cap):
    p = Prop(name)
    p.mesh(cyl(0.32, 0.45, 1.4, 12), "mushroom_stem", (0, 0.7, 0))
    p.mesh(sphere(1.15, 18, 9, True), cap, (0, 1.25, 0), (0, 0, 0), (1, 0.75, 1))
    for i in range(7):
        ang = i * math.tau / 7
        rr = 0.75 if i % 2 else 0.5
        y = 1.25 + math.sqrt(max(1.15 ** 2 - rr ** 2, 0)) * 0.75
        p.mesh(sphere(0.14, 8, 4), "white", (math.cos(ang) * rr, y, math.sin(ang) * rr), (0, 0, 0), (1, 0.45, 1))
    p.mesh(sphere(0.18, 8, 4), "white", (0, 1.25 + 1.15 * 0.75, 0), (0, 0, 0), (1, 0.45, 1))
    p.shape(shape_cyl(0.45, 1.6), (0, 0.8, 0))
    return p


def house(name, wall, roof, tall=False):
    p = Prop(name)
    h = 5.0 if tall else 3.0
    p.mesh(box(4.4, 1.6, 4.4), "stone", (0, -0.65, 0))
    p.mesh(box(4, h, 4), wall, (0, h / 2, 0))
    p.mesh(prism(4.7, 1.9, 4.7), roof, (0, h + 0.95, 0))
    p.mesh(box(0.55, 1.3, 0.55), "stone_dark", (1.15, h + 1.2, 0.8))
    p.mesh(box(1.05, 1.75, 0.12), "door", (0, 0.875, -2.02))
    p.mesh(sphere(0.07, 8, 4), "yellow", (0.32, 0.9, -2.1))
    p.mesh(box(1.5, 0.22, 0.7), "stone", (0, 0.11, -2.35))
    rows = [1.9, 3.7] if tall else [1.9]
    for y in rows:
        for x in (-1.25, 1.25):
            if y == 1.9 and abs(x) < 1:
                continue
            p.mesh(box(0.85, 0.85, 0.1), "window", (x, y, -2.02))
            p.mesh(box(1.0, 0.12, 0.14), "white", (x, y - 0.48, -2.04))
        for side in (-1, 1):
            p.mesh(box(0.1, 0.85, 0.85), "window", (2.02 * side, y, 0))
    if tall:
        p.mesh(box(0.85, 0.85, 0.1), "window", (0, 3.7, -2.02))
    # Window box with flowers under the front windows.
    for x in (-1.25, 1.25):
        p.mesh(box(0.95, 0.22, 0.25), "wood", (x, 1.32, -2.12))
        for dx in (-0.25, 0, 0.25):
            p.mesh(sphere(0.1, 8, 4), "pink" if dx else "yellow", (x + dx, 1.5, -2.12))
    p.shape(shape_box(4, h, 4), (0, h / 2, 0))
    p.shape(shape_box(4.4, 1.8, 4.4), (0, h + 0.8, 0))
    return p


def market_stall(name, stripe):
    p = Prop(name)
    for x in (-1.3, 1.3):
        for z in (-0.8, 0.8):
            p.mesh(cyl(0.07, 0.07, 2.4, 6), "wood", (x, 1.2, z))
    p.mesh(box(2.8, 0.9, 1.0), "wood_light", (0, 0.45, -0.3))
    for i in range(6):
        x = -1.25 + i * 0.5
        p.mesh(box(0.5, 0.06, 2.0), stripe if i % 2 == 0 else "white", (x, 2.55, 0), (0.25, 0, 0))
    for i, f in enumerate(["red", "orange", "yellow", "leaf_light", "pink"]):
        p.mesh(sphere(0.14, 8, 4), f, (-1.0 + i * 0.5, 1.0, -0.45))
    p.shape(shape_box(2.8, 1.0, 1.0), (0, 0.5, -0.3))
    return p


def fountain():
    p = Prop("fountain")
    p.mesh(cyl(2.6, 2.75, 0.7, 24), "stone", (0, 0.35, 0))
    p.mesh(cyl(2.25, 2.25, 0.1, 24), "water_still", (0, 0.68, 0))
    p.mesh(cyl(0.3, 0.42, 1.8, 12), "stone", (0, 1.4, 0))
    p.mesh(cyl(1.0, 0.5, 0.35, 16), "stone", (0, 2.3, 0))
    p.mesh(cyl(0.85, 0.85, 0.06, 16), "water_still", (0, 2.46, 0))
    p.mesh(sphere(0.3, 12, 6), "water_still", (0, 2.75, 0), (0, 0, 0), (1, 1.4, 1))
    for i in range(6):
        ang = i * math.tau / 6
        p.mesh(sphere(0.12, 8, 4), "water_still", (math.cos(ang) * 1.3, 1.4, math.sin(ang) * 1.3))
    p.shape(shape_cyl(2.7, 0.9), (0, 0.45, 0))
    p.shape(shape_cyl(0.5, 2.6), (0, 1.3, 0))
    return p


def lamp_post():
    p = Prop("lamp_post")
    p.mesh(cyl(0.12, 0.18, 0.3, 8), "metal", (0, 0.15, 0))
    p.mesh(cyl(0.06, 0.06, 3.0, 6), "metal", (0, 1.6, 0))
    p.mesh(sphere(0.26, 12, 6), "glow_yellow", (0, 3.25, 0))
    p.mesh(cyl(0.0, 0.32, 0.25, 8), "metal", (0, 3.6, 0))
    p.shape(shape_cyl(0.15, 3.2), (0, 1.6, 0))
    return p


def fence():
    p = Prop("fence")
    for x in (-1.0, 1.0):
        p.mesh(box(0.16, 1.0, 0.16), "wood_light", (x, 0.5, 0))
        p.mesh(prism(0.16, 0.14, 0.16), "wood_light", (x, 1.07, 0))
    for y in (0.4, 0.75):
        p.mesh(box(2.2, 0.12, 0.08), "wood_light", (0, y, 0))
    p.shape(shape_box(2.2, 1.0, 0.2), (0, 0.5, 0))
    return p


def bench():
    p = Prop("bench")
    p.mesh(box(1.7, 0.1, 0.55), "wood", (0, 0.45, 0))
    p.mesh(box(1.7, 0.45, 0.08), "wood", (0, 0.78, 0.25), (-0.15, 0, 0))
    for x in (-0.7, 0.7):
        p.mesh(box(0.1, 0.45, 0.5), "metal", (x, 0.22, 0))
    p.shape(shape_box(1.7, 0.9, 0.6), (0, 0.45, 0))
    return p


def well():
    p = Prop("well")
    p.mesh(cyl(0.95, 1.0, 0.9, 16), "stone", (0, 0.45, 0))
    p.mesh(cyl(0.75, 0.75, 0.05, 16), "water_still", (0, 0.8, 0))
    for x in (-0.85, 0.85):
        p.mesh(box(0.14, 1.9, 0.14), "wood", (x, 1.3, 0))
    p.mesh(prism(2.2, 0.8, 1.6), "roof_red", (0, 2.55, 0))
    p.mesh(cyl(0.08, 0.08, 1.6, 6), "wood_dark", (0, 1.75, 0), (0, 0, math.pi / 2))
    p.mesh(cyl(0.18, 0.15, 0.3, 8), "wood", (0, 1.35, 0))
    p.shape(shape_cyl(1.0, 1.0), (0, 0.5, 0))
    return p


def crate():
    p = Prop("crate")
    p.mesh(box(0.8, 0.8, 0.8), "wood_light", (0, 0.4, 0))
    for y in (0.08, 0.72):
        p.mesh(box(0.84, 0.12, 0.84), "wood", (0, y, 0))
    p.shape(shape_box(0.8, 0.8, 0.8), (0, 0.4, 0))
    return p


def barrel():
    p = Prop("barrel")
    p.mesh(cyl(0.36, 0.36, 1.0, 12), "wood", (0, 0.5, 0))
    p.mesh(cyl(0.42, 0.42, 0.5, 12), "wood", (0, 0.5, 0))
    for y in (0.15, 0.85):
        p.mesh(cyl(0.4, 0.4, 0.07, 12), "metal", (0, y, 0))
    p.shape(shape_cyl(0.42, 1.0), (0, 0.5, 0))
    return p


def sign_board():
    p = Prop("sign_board", "res://scenes/world/sign.gd")
    p.mesh(box(0.16, 1.5, 0.16), "wood", (0, 0.75, 0))
    p.mesh(box(1.5, 0.8, 0.1), "wood_light", (0, 1.4, 0))
    p.mesh(box(1.6, 0.1, 0.14), "wood", (0, 1.83, 0))
    p.extra("Text", "Label3D", {
        "transform": xform((0, 1.4, 0.06)),
        "pixel_size": "0.004",
        "modulate": color((0.3, 0.18, 0.1)),
        "outline_size": "0",
        "font_size": "40",
        "text": string("Sign"),
        "autowrap_mode": "3",
        "width": "330.0",
    })
    p.shape(shape_box(1.5, 1.9, 0.3), (0, 0.95, 0))
    return p


def log_cabin():
    p = Prop("log_cabin")
    p.mesh(box(5.4, 1.4, 4.4), "stone", (0, -0.6, 0))
    for i in range(7):
        y = 0.22 + i * 0.42
        for side in (-1, 1):
            p.mesh(cyl(0.22, 0.22, 5.4, 8), "wood" if i % 2 else "wood_dark", (0, y, 2.0 * side), (0, 0, math.pi / 2))
            p.mesh(cyl(0.22, 0.22, 4.4, 8), "wood_dark" if i % 2 else "wood", (2.5 * side, y + 0.21, 0), (math.pi / 2, 0, 0))
    p.mesh(prism(6.0, 2.0, 5.0), "roof_dark", (0, 4.0, 0), (0, math.pi / 2, 0), (0.95, 1, 1.2))
    p.mesh(box(1.1, 1.8, 0.15), "door", (0, 0.9, -2.2))
    p.mesh(box(0.9, 0.8, 0.12), "window", (-1.5, 1.6, -2.2))
    p.mesh(box(0.9, 0.8, 0.12), "window", (1.5, 1.6, -2.2))
    p.mesh(box(0.6, 1.6, 0.6), "stone_dark", (-1.8, 4.2, 1.0))
    p.shape(shape_box(5.2, 3.2, 4.4), (0, 1.6, 0))
    p.shape(shape_box(5.6, 1.8, 4.8), (0, 4.0, 0))
    return p


def campfire():
    p = Prop("campfire")
    for i in range(8):
        ang = i * math.tau / 8
        p.mesh(sphere(0.2, 7, 4), "stone_dark", (math.cos(ang) * 0.7, 0.1, math.sin(ang) * 0.7), (0, ang, 0), (1.2, 0.8, 1))
    p.mesh(cyl(0.1, 0.1, 1.2, 6), "wood", (0, 0.15, 0), (0, 0.5, math.pi / 2))
    p.mesh(cyl(0.1, 0.1, 1.2, 6), "wood", (0, 0.2, 0), (0, -0.7, math.pi / 2))
    flames = p.pivot("Flames", (0, 0.2, 0), script="res://scenes/world/spinner.gd", props={"axis": v3(0, 1, 0), "speed": "2.0"})
    p.mesh(cyl(0.0, 0.4, 1.0, 6), "fire", (0, 0.45, 0), parent=flames)
    p.mesh(cyl(0.0, 0.22, 0.7, 6), "fire_core", (0.1, 0.4, 0.05), parent=flames)
    p.mesh(cyl(0.0, 0.18, 0.6, 6), "fire", (-0.2, 0.3, -0.1), parent=flames)
    p.extra("Light", "OmniLight3D", {
        "transform": xform((0, 1.0, 0)),
        "light_color": color((1.0, 0.6, 0.3)),
        "light_energy": "2.0",
        "omni_range": "7.0",
    })
    p.shape(shape_cyl(0.8, 0.4), (0, 0.2, 0))
    return p


def log_fallen():
    p = Prop("log_fallen")
    p.mesh(cyl(0.38, 0.38, 3.2, 10), "wood", (0, 0.36, 0), (0, 0, math.pi / 2))
    for side in (-1, 1):
        p.mesh(cyl(0.3, 0.3, 0.02, 10), "wood_light", (1.61 * side, 0.36, 0), (0, 0, math.pi / 2))
    p.mesh(sphere(0.18, 8, 4), "leaf", (0.5, 0.7, 0.1), (0, 0, 0), (1.4, 0.6, 1))
    p.shape(shape_cyl(0.38, 3.2), (0, 0.36, 0), (0, 0, math.pi / 2))
    return p


def stump():
    p = Prop("stump")
    p.mesh(cyl(0.45, 0.55, 0.6, 10), "wood", (0, 0.3, 0))
    p.mesh(cyl(0.44, 0.44, 0.02, 10), "wood_light", (0, 0.61, 0))
    p.shape(shape_cyl(0.55, 0.6), (0, 0.3, 0))
    return p


def bridge():
    p = Prop("bridge")
    for i in range(14):
        z = -6.5 + i
        p.mesh(box(3.0, 0.2, 0.9), "wood_light" if i % 2 else "wood", (0, 0, z))
    for x in (-1.45, 1.45):
        for z in (-6.5, -2.2, 2.2, 6.5):
            p.mesh(box(0.18, 1.2, 0.18), "wood_dark", (x, 0.5, z))
        p.mesh(box(0.12, 0.12, 13.2), "wood", (x, 1.0, 0))
    p.shape(shape_box(3.0, 0.3, 14), (0, 0, 0))
    for x in (-1.45, 1.45):
        p.shape(shape_box(0.2, 1.2, 13.2), (x, 0.6, 0))
    return p


def lighthouse():
    p = Prop("lighthouse")
    p.mesh(cyl(2.4, 2.6, 1.0, 16), "stone", (0, 0.5, 0))
    for i in range(5):
        r0 = 1.8 - i * 0.16
        p.mesh(cyl(r0 - 0.16, r0, 2.0, 16), "red" if i % 2 == 0 else "white", (0, 2.0 + i * 2.0, 0))
    p.mesh(cyl(1.5, 1.5, 0.2, 16), "metal", (0, 11.1, 0))
    p.mesh(cyl(0.85, 0.85, 1.3, 12), "glow_yellow", (0, 11.85, 0))
    p.mesh(cyl(0.0, 1.1, 1.0, 12), "red", (0, 13.0, 0))
    p.mesh(sphere(0.15, 8, 4), "metal", (0, 13.55, 0))
    p.mesh(box(0.9, 1.6, 0.12), "door", (0, 1.8, -1.79))
    p.extra("Beam", "OmniLight3D", {
        "transform": xform((0, 11.9, 0)),
        "light_color": color((1.0, 0.9, 0.6)),
        "light_energy": "3.0",
        "omni_range": "16.0",
    })
    p.shape(shape_cyl(2.5, 1.0), (0, 0.5, 0))
    p.shape(shape_cyl(1.8, 11.0), (0, 6.0, 0))
    return p


def dock():
    p = Prop("dock")
    for i in range(16):
        z = i * 1.0
        p.mesh(box(3.2, 0.2, 0.92), "wood_light" if i % 2 else "wood", (0, 0, z))
    for z in (0.5, 5.0, 10.0, 15.0):
        for x in (-1.5, 1.5):
            p.mesh(cyl(0.16, 0.16, 3.0, 8), "wood_dark", (x, -1.2, z))
    p.mesh(cyl(0.2, 0.2, 0.9, 8), "wood_dark", (1.5, 0.45, 15.0))
    p.mesh(torus(0.25, 0.4), "red", (1.65, 0.6, 14.0), (0, 0, math.pi / 2))
    p.shape(shape_box(3.2, 0.3, 16), (0, 0, 7.5))
    return p


def umbrella(name, canopy):
    p = Prop(name)
    p.mesh(cyl(0.04, 0.04, 2.4, 6), "white", (0, 1.2, 0))
    p.mesh(cyl(0.0, 1.5, 0.55, 8), canopy, (0, 2.35, 0))
    p.mesh(sphere(0.08, 6, 3), "white", (0, 2.65, 0))
    p.mesh(box(1.0, 0.03, 1.9), canopy, (0.9, 0.02, 0.3), (0, 0.2, 0))
    p.mesh(box(1.0, 0.032, 0.3), "white", (0.9, 0.025, 0.3), (0, 0.2, 0))
    p.shape(shape_cyl(0.1, 2.4), (0, 1.2, 0))
    return p


def rowboat():
    p = Prop("rowboat")
    p.mesh(sphere(1.0, 14, 7, True), "wood", (0, 0.55, 0), (math.pi, 0, 0), (0.85, 0.6, 2.0))
    p.mesh(box(1.5, 0.08, 0.35), "wood_light", (0, 0.45, 0.5))
    p.mesh(box(1.5, 0.08, 0.35), "wood_light", (0, 0.45, -0.6))
    p.mesh(cyl(0.04, 0.04, 2.2, 5), "wood_dark", (0.6, 0.6, 0), (0.3, 0, 1.2))
    p.shape(shape_box(1.6, 0.7, 3.6), (0, 0.3, 0))
    return p


def beach_ball():
    p = Prop("beach_ball")
    p.mesh(sphere(0.35, 12, 6), "white", (0, 0.35, 0))
    p.mesh(sphere(0.355, 12, 6), "red", (0, 0.35, 0), (0, 0, 0), (0.35, 1, 1))
    p.mesh(sphere(0.355, 12, 6), "blue", (0, 0.35, 0), (0, 0, 0), (1, 1, 0.35))
    return p


def starfish(name, colr):
    p = Prop(name)
    for i in range(5):
        ang = i * math.tau / 5
        p.mesh(sphere(0.12, 6, 3), colr, (math.cos(ang) * 0.12, 0.03, math.sin(ang) * 0.12), (0, -ang, 0), (1.8, 0.35, 0.7))
    return p


def sandcastle():
    p = Prop("sandcastle")
    p.mesh(box(1.4, 0.6, 1.4), "sand", (0, 0.3, 0))
    for x in (-0.6, 0.6):
        for z in (-0.6, 0.6):
            p.mesh(cyl(0.22, 0.25, 0.9, 8), "sand", (x, 0.45, z))
            p.mesh(cyl(0.0, 0.25, 0.3, 8), "sand", (x, 1.05, z))
    p.mesh(cyl(0.3, 0.35, 1.2, 8), "sand", (0, 0.6, 0))
    p.mesh(box(0.02, 0.3, 0.25), "red", (0, 1.5, 0.12))
    p.mesh(cyl(0.015, 0.015, 0.5, 4), "wood", (0, 1.4, 0))
    p.shape(shape_box(1.4, 1.0, 1.4), (0, 0.5, 0))
    return p


def igloo():
    p = Prop("igloo")
    p.mesh(sphere(2.3, 20, 10, True), "snow", (0, 0, 0))
    p.mesh(cyl(0.85, 0.85, 1.8, 14), "snow", (0, 0.5, -2.1), (math.pi / 2, 0, 0))
    p.mesh(cyl(0.6, 0.6, 0.05, 14), "black", (0, 0.55, -3.01), (math.pi / 2, 0, 0))
    for i in range(3):
        y = 0.6 + i * 0.6
        r = math.sqrt(2.3 ** 2 - y ** 2)
        p.mesh(torus(r - 0.02, r + 0.04), "ice", (0, y, 0))
    p.shape(shape_cyl(2.2, 2.0), (0, 1.0, 0))
    p.shape(shape_box(1.7, 1.4, 1.8), (0, 0.6, -2.1))
    return p


def snowman():
    p = Prop("snowman")
    p.mesh(sphere(0.62, 14, 7), "snow", (0, 0.55, 0))
    p.mesh(sphere(0.45, 14, 7), "snow", (0, 1.35, 0))
    p.mesh(sphere(0.33, 14, 7), "snow", (0, 1.95, 0))
    p.mesh(cyl(0.0, 0.06, 0.35, 6), "carrot", (0, 1.95, -0.45), (-math.pi / 2, 0, 0))
    for x in (-0.11, 0.11):
        p.mesh(sphere(0.04, 6, 3), "black", (x, 2.05, -0.29))
    for y in (1.2, 1.4, 1.6):
        p.mesh(sphere(0.045, 6, 3), "black", (0, y, -math.sqrt(max(0.45 ** 2 - (y - 1.35) ** 2, 0)) - 0.01))
    for side in (-1, 1):
        p.mesh(cyl(0.03, 0.03, 0.9, 5), "wood_dark", (0.6 * side, 1.5, 0), (0, 0, -0.9 * side))
    p.mesh(cyl(0.38, 0.38, 0.04, 12), "black", (0, 2.22, 0))
    p.mesh(cyl(0.22, 0.22, 0.38, 12), "black", (0, 2.42, 0))
    p.mesh(cyl(0.48, 0.48, 0.12, 12), "red", (0, 1.68, 0), (0, 0, 0), (1, 1, 1))
    p.shape(shape_cyl(0.6, 2.4), (0, 1.2, 0))
    return p


def crystal(name, colr):
    p = Prop(name)
    for (x, z, h, rx, rz) in [(0, 0, 2.2, 0, 0), (0.45, 0.2, 1.4, 0.2, -0.35), (-0.4, 0.15, 1.2, -0.15, 0.4), (0.1, -0.45, 1.0, -0.35, 0)]:
        p.mesh(cyl(0.0, 0.32, h * 0.35, 6), colr, (x, h * 0.85, z), (rx, 0, rz))
        p.mesh(cyl(0.32, 0.32, h * 0.7, 6), colr, (x, h * 0.35, z), (rx, 0, rz))
    p.shape(shape_cyl(0.6, 2.0), (0, 1.0, 0))
    return p


def sled():
    p = Prop("sled")
    p.mesh(box(0.7, 0.08, 1.4), "red", (0, 0.3, 0))
    for x in (-0.3, 0.3):
        p.mesh(box(0.05, 0.05, 1.6), "metal", (x, 0.05, 0))
        p.mesh(box(0.05, 0.25, 0.05), "metal", (x, 0.17, 0.5))
        p.mesh(box(0.05, 0.25, 0.05), "metal", (x, 0.17, -0.5))
    return p


def cloud(name, scale):
    p = Prop(name)
    for (x, y, z, r) in [(0, 0, 0, 2.2), (2.2, -0.4, 0.3, 1.6), (-2.1, -0.5, -0.2, 1.7), (0.8, 0.9, -0.3, 1.4), (-0.9, 0.6, 0.6, 1.3)]:
        p.mesh(sphere(r * scale, 14, 7), "white", (x * scale, y * scale, z * scale))
    return p


def tent():
    p = Prop("tent")
    p.mesh(prism(2.6, 1.9, 3.0), "orange", (0, 0.95, 0))
    p.mesh(prism(1.0, 1.1, 0.05), "wood_dark", (0, 0.55, -1.51))
    p.shape(shape_box(2.2, 1.6, 3.0), (0, 0.8, 0))
    return p


def pumpkin():
    p = Prop("pumpkin")
    for i in range(6):
        ang = i * math.tau / 6
        p.mesh(sphere(0.3, 10, 6), "pumpkin", (math.cos(ang) * 0.12, 0.28, math.sin(ang) * 0.12), (0, -ang, 0), (0.75, 0.9, 1.1))
    p.mesh(cyl(0.04, 0.06, 0.2, 5), "leaf_dark", (0, 0.6, 0), (0.2, 0, 0.1))
    return p


def hay_bale():
    p = Prop("hay_bale")
    p.mesh(cyl(0.6, 0.6, 1.1, 14), "hay", (0, 0.6, 0), (0, 0, math.pi / 2))
    p.mesh(cyl(0.61, 0.61, 0.08, 14), "wood_light", (0.3, 0.6, 0), (0, 0, math.pi / 2))
    p.mesh(cyl(0.61, 0.61, 0.08, 14), "wood_light", (-0.3, 0.6, 0), (0, 0, math.pi / 2))
    p.shape(shape_cyl(0.6, 1.1), (0, 0.6, 0), (0, 0, math.pi / 2))
    return p


def windmill():
    p = Prop("windmill")
    p.mesh(box(4.2, 1.2, 4.2), "stone", (0, -0.5, 0))
    p.mesh(cyl(1.6, 2.2, 7.0, 10), "wall_cream", (0, 3.5, 0))
    p.mesh(cyl(0.0, 2.1, 2.4, 10), "roof_red", (0, 8.2, 0))
    p.mesh(box(1.1, 1.9, 0.15), "door", (0, 0.95, -2.12), (0.08, 0, 0))
    p.mesh(box(0.7, 0.7, 0.12), "window", (0, 4.5, -1.86), (0.08, 0, 0))
    hub = p.pivot("Blades", (0, 6.6, -2.0), script="res://scenes/world/spinner.gd", props={"axis": v3(0, 0, 1), "speed": "0.8"})
    p.mesh(cyl(0.35, 0.35, 0.4, 10), "wood_dark", (0, 0, 0), (math.pi / 2, 0, 0), parent=hub)
    for i in range(4):
        ang = i * math.pi / 2
        dx, dy = math.cos(ang), math.sin(ang)
        p.mesh(box(0.18, 4.6, 0.1), "wood", (dx * 2.3, dy * 2.3, -0.2), (0, 0, ang - math.pi / 2), parent=hub)
        p.mesh(box(1.0, 3.6, 0.05), "white", (dx * 2.6 + dy * 0.55, dy * 2.6 - dx * 0.55, -0.25), (0, 0, ang - math.pi / 2), parent=hub)
    p.shape(shape_cyl(2.1, 7.0), (0, 3.5, 0))
    return p


def mountain(name, snowy):
    p = Prop(name)
    p.mesh(cyl(0.0, 12.0, 22.0, 9), "stone_dark", (0, 11.0, 0))
    p.mesh(cyl(0.0, 8.0, 15.0, 9), "stone", (5.0, 7.5, 3.0))
    if snowy:
        p.mesh(cyl(0.0, 4.4, 8.0, 9), "snow", (0, 18.05, 0))
        p.mesh(cyl(0.0, 2.8, 5.2, 9), "snow", (5.0, 12.45, 3.0))
    return p


def ice_sheet():
    p = Prop("ice_sheet")
    p.mesh(cyl(1.0, 1.0, 0.1, 32), "ice", (0, 0, 0))
    p.shape(shape_cyl(1.0, 0.1), (0, 0, 0))
    return p


def all_props():
    return [
        tree_round("tree_round", "leaf"),
        tree_round("tree_round_light", "leaf_light"),
        tree_round("tree_apple", "leaf", fruit="red"),
        tree_round("tree_autumn", "leaf_autumn"),
        tree_pine("tree_pine"),
        tree_pine("tree_pine_snow", snowy=True),
        tree_palm(),
        bush("bush", "leaf_dark"),
        bush("bush_berries", "leaf", berries="purple"),
        bush("bush_snow", "snow"),
        flowers("flowers_pink", "pink"),
        flowers("flowers_yellow", "yellow"),
        flowers("flowers_purple", "purple"),
        flowers("flowers_white", "white"),
        grass_tuft(),
        rock("rock"),
        rock("rock_snow", snowy=True),
        mushroom("mushroom_red", "mushroom_red"),
        mushroom("mushroom_blue", "mushroom_blue"),
        house("house_red", "wall_cream", "roof_red"),
        house("house_blue", "wall_sky", "roof_blue"),
        house("house_teal", "wall_mint", "roof_teal"),
        house("house_orange", "wall_butter", "roof_orange"),
        house("house_purple", "wall_pink", "roof_purple"),
        house("house_tall_red", "wall_pink", "roof_red", tall=True),
        house("house_tall_blue", "wall_cream", "roof_blue", tall=True),
        market_stall("market_stall_red", "red"),
        market_stall("market_stall_blue", "blue"),
        fountain(),
        lamp_post(),
        fence(),
        bench(),
        well(),
        crate(),
        barrel(),
        sign_board(),
        log_cabin(),
        campfire(),
        log_fallen(),
        stump(),
        bridge(),
        lighthouse(),
        dock(),
        umbrella("umbrella_red", "red"),
        umbrella("umbrella_blue", "blue"),
        umbrella("umbrella_yellow", "yellow"),
        rowboat(),
        beach_ball(),
        starfish("starfish_orange", "orange"),
        starfish("starfish_pink", "pink"),
        sandcastle(),
        igloo(),
        snowman(),
        crystal("crystal_blue", "crystal"),
        crystal("crystal_pink", "crystal_pink"),
        sled(),
        cloud("cloud", 1.0),
        cloud("cloud_big", 1.6),
        tent(),
        pumpkin(),
        hay_bale(),
        windmill(),
        mountain("mountain", False),
        mountain("mountain_snow", True),
        ice_sheet(),
    ]


# --- core scenes -----------------------------------------------------------

PLAYER_LOOK = {
    "skin_color": (1.0, 0.84, 0.7),
    "shirt_color": (1.0, 0.78, 0.25),
    "pants_color": (0.3, 0.45, 0.85),
    "shoe_color": (0.9, 0.3, 0.3),
    "hair_color": (0.45, 0.28, 0.15),
    "hat": 1,
    "hat_color": (0.95, 0.33, 0.3),
}


def look_props(look):
    out = {}
    for k, v in look.items():
        if isinstance(v, tuple):
            out[k] = color(v)
        elif isinstance(v, bool):
            out[k] = "true" if v else "false"
        else:
            out[k] = str(v)
    return out


def write_core_scenes():
    # Player
    sc = Scene("Player", "CharacterBody3D")
    sc.nodes[0] += "\n" + "\n".join([
        f"script = {sc.ext_res('Script', 'res://scenes/characters/player.gd')}",
        "floor_max_angle = 0.87",
        "floor_snap_length = 0.4",
    ])
    sc.node("Collision", "CollisionShape3D", props={
        "transform": xform((0, 0.85, 0)),
        "shape": sc.sub_res(*shape_capsule(0.35, 1.7)),
    })
    model_props = {"script": sc.ext_res("Script", "res://scenes/characters/character_model.gd")}
    model_props.update(look_props(PLAYER_LOOK))
    sc.node("Model", "Node3D", props=model_props)
    sc.node("CameraYaw", "Node3D")
    sc.node("CameraPitch", "Node3D", "CameraYaw", props={"transform": xform((0, 0, 0), (-0.32, 0, 0))})
    sc.node("SpringArm", "SpringArm3D", "CameraYaw/CameraPitch", props={
        "shape": sc.sub_res(*shape_sphere(0.3)),
        "spring_length": "7.5",
        "margin": "0.2",
    })
    sc.node("Camera", "Camera3D", "CameraYaw/CameraPitch/SpringArm", props={
        "transform": xform((0, 0, 7.5)),
        "current": "true",
        "fov": "60.0",
        "far": "600.0",
    })
    sc.write(os.path.join(ROOT, "scenes/characters/player.tscn"))

    # NPC
    sc = Scene("NPC", "CharacterBody3D")
    sc.nodes[0] += f"\nscript = {sc.ext_res('Script', 'res://scenes/characters/npc.gd')}"
    sc.node("Collision", "CollisionShape3D", props={
        "transform": xform((0, 0.85, 0)),
        "shape": sc.sub_res(*shape_capsule(0.35, 1.7)),
    })
    sc.node("Model", "Node3D", props={"script": sc.ext_res("Script", "res://scenes/characters/character_model.gd")})
    sc.node("NameTag", "Label3D", props={
        "transform": xform((0, 2.25, 0)),
        "billboard": "1",
        "no_depth_test": "true",
        "pixel_size": "0.004",
        "font_size": "48",
        "outline_size": "14",
        "modulate": color((1, 1, 1)),
        "outline_modulate": color((0.2, 0.12, 0.25)),
        "text": string("Villager"),
    })
    sc.node("NewMarker", "Label3D", props={
        "transform": xform((0, 2.7, 0)),
        "billboard": "1",
        "pixel_size": "0.006",
        "font_size": "96",
        "outline_size": "20",
        "modulate": color((1, 0.85, 0.2)),
        "outline_modulate": color((0.45, 0.2, 0.05)),
        "text": string("!"),
    })
    sc.write(os.path.join(ROOT, "scenes/characters/npc.tscn"))

    # Portal
    sc = Scene("Portal", "Area3D")
    sc.nodes[0] += f"\nscript = {sc.ext_res('Script', 'res://scenes/world/portal.gd')}"
    sc.node("Collision", "CollisionShape3D", props={
        "transform": xform((0, 2.0, 0)),
        "shape": sc.sub_res(*shape_box(2.6, 3.4, 1.4)),
    })
    sc.node("Base", "MeshInstance3D", props={
        "transform": xform((0, 0.1, 0)),
        "mesh": sc.sub_res(*cyl(1.6, 1.8, 0.4, 20)),
        "surface_material_override/0": sc.ext_res("StandardMaterial3D", mat("stone")),
    })
    sc.node("Ring", "MeshInstance3D", props={
        "transform": xform((0, 2.3, 0), (math.pi / 2, 0, 0)),
        "mesh": sc.sub_res(*torus(1.55, 1.95)),
    })
    sc.node("Swirl", "Node3D", props={"transform": xform((0, 2.3, 0))})
    sc.node("Disk", "MeshInstance3D", "Swirl", props={
        "transform": xform((0, 0, 0), (math.pi / 2, 0, 0)),
        "mesh": sc.sub_res(*cyl(1.56, 1.56, 0.04, 28)),
    })
    for i in range(6):
        ang = i * math.tau / 6
        sc.node(f"Sparkle{i + 1}", "MeshInstance3D", "Swirl", props={
            "transform": xform((math.cos(ang) * 1.1, math.sin(ang) * 1.1, 0)),
            "mesh": sc.sub_res(*sphere(0.1, 8, 4)),
            "surface_material_override/0": sc.ext_res("StandardMaterial3D", mat("glow_white")),
        })
    sc.node("Label", "Label3D", props={
        "transform": xform((0, 4.4, 0)),
        "billboard": "1",
        "pixel_size": "0.006",
        "font_size": "64",
        "outline_size": "18",
        "outline_modulate": color((0.15, 0.1, 0.25)),
        "text": string("To ..."),
    })
    sc.node("Glow", "OmniLight3D", props={
        "transform": xform((0, 2.3, 0)),
        "light_color": color((0.6, 0.85, 1.0)),
        "light_energy": "1.5",
        "omni_range": "6.0",
    })
    sc.write(os.path.join(ROOT, "scenes/world/portal.tscn"))

    # HUD
    sc = Scene("HUD", "CanvasLayer")
    sc.nodes[0] += f"\nscript = {sc.ext_res('Script', 'res://scenes/ui/hud.gd')}"
    sc.write(os.path.join(ROOT, "scenes/ui/hud.tscn"))
