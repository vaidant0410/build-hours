#!/usr/bin/env python3
"""Generates every material, prop, core scene and map for Pocket World.

    python3 tools/build_world.py            # write everything
    python3 tools/build_world.py --preview  # also write top-down PNG previews

Maps are plain .tscn files, so after generating you can keep editing them in
the Godot editor (or via the Godot MCP). Re-running this script overwrites them.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from props import ROOT, all_props, look_props, write_core_scenes, write_materials  # noqa: E402
from tscn import Scene, color, num, string, strings, v2, v3, v4, vec4_array, xform  # noqa: E402

from levels import LEVELS  # noqa: E402


def smoothstep(a, b, x):
    if abs(a - b) < 1e-9:
        return a
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def seg_dist(x, z, s):
    ax, az, bx, bz = s
    abx, abz = bx - ax, bz - az
    l2 = max(abx * abx + abz * abz, 0.0001)
    t = min(max(((x - ax) * abx + (z - az) * abz) / l2, 0.0), 1.0)
    return math.hypot(x - (ax + abx * t), z - (az + abz * t))


class TerrainFn:
    """Mirror of Terrain.height_at() in scenes/world/terrain.gd."""

    DEFAULTS = dict(size=160, seed_offset=0.0, base_height=1.0, amplitude=2.0, frequency=0.04,
                    tilt=(0.0, 0.0), border_width=20.0, border_height=18.0, border_sides=(1, 1, 1, 1),
                    flats=(), channels=(), channel_width=6.0, channel_bottom=-1.5, paths=(), path_width=2.2)

    def __init__(self, **kw):
        self.p = dict(self.DEFAULTS)
        self.p.update({k: v for k, v in kw.items() if k in self.DEFAULTS})
        self.extra = {k: v for k, v in kw.items() if k not in self.DEFAULTS}
        self.__dict__.update(self.p)

    def height(self, x, z):
        s = self.seed_offset
        fx, fz = x * self.frequency, z * self.frequency
        n = (math.sin(fx + s) * math.cos(fz * 0.8 + s * 1.3) * 0.55
             + math.sin(fx * 2.1 - fz * 1.7 + s * 2.1) * 0.25
             + math.cos(fx * 3.7 + fz * 2.9 + s * 0.7) * 0.12
             + math.sin(fx * 0.45 + fz * 0.35 + s * 3.1) * 0.6)
        h = self.base_height + n * self.amplitude + self.tilt[0] * x + self.tilt[1] * z
        for fxp, fzp, r, fh in self.flats:
            d = math.hypot(x - fxp, z - fzp)
            w = 1.0 - smoothstep(r * 0.55, r, d)
            h = h + (fh - h) * w
        for c in self.channels:
            d = seg_dist(x, z, c)
            w = 1.0 - smoothstep(self.channel_width * 0.35, self.channel_width, d)
            h = min(h, h + (self.channel_bottom - h) * w)
        half = self.size * 0.5
        bs = self.border_sides
        tx = smoothstep(half - self.border_width, half, abs(x)) * (bs[1] if x > 0 else bs[0])
        tz = smoothstep(half - self.border_width, half, abs(z)) * (bs[3] if z > 0 else bs[2])
        t = max(tx, tz)
        bumps = 0.75 + 0.35 * math.sin(x * 0.13 + s) * math.cos(z * 0.11 - s)
        return h + t * self.border_height * bumps

    def slope(self, x, z):
        dx = self.height(x + 0.5, z) - self.height(x - 0.5, z)
        dz = self.height(x, z + 0.5) - self.height(x, z - 0.5)
        return math.hypot(dx, dz)

    def path_dist(self, x, z):
        return min((seg_dist(x, z, p) for p in self.paths), default=1e9)

    def channel_dist(self, x, z):
        return min((seg_dist(x, z, c) for c in self.channels), default=1e9)

    def node_props(self, sc):
        p = self.p
        out = {
            "script": sc.ext_res("Script", "res://scenes/world/terrain.gd"),
            "size": str(p["size"]),
            "seed_offset": num(p["seed_offset"]),
            "base_height": num(p["base_height"]),
            "amplitude": num(p["amplitude"]),
            "frequency": num(p["frequency"]),
            "tilt": v2(*p["tilt"]),
            "border_width": num(p["border_width"]),
            "border_height": num(p["border_height"]),
            "border_sides": v4(*p["border_sides"]),
            "flats": vec4_array(p["flats"]),
            "channels": vec4_array(p["channels"]),
            "channel_width": num(p["channel_width"]),
            "channel_bottom": num(p["channel_bottom"]),
            "paths": vec4_array(p["paths"]),
            "path_width": num(p["path_width"]),
        }
        for k, v in self.extra.items():
            out[k] = color(v) if isinstance(v, tuple) else num(v)
        return out


def pascal(name):
    return "".join(part.capitalize() for part in name.split("_"))


class Level:
    def __init__(self, map_id, terrain, env, water=None, bounds=None, seed=1):
        self.map_id = map_id
        self.t = TerrainFn(**terrain)
        self.env = env
        self.water = water
        self.water_level = water["level"] if water else -1e9
        half = self.t.size * 0.5 - self.t.border_width * 0.6
        self.bounds = bounds or (-half, half, -half, half)
        self.rng = random.Random(seed)
        self.items = []  # (group, prop, pos, yaw, scale, props)
        self.occupied = []  # (x, z, r)
        self.npcs = []
        self.portals = []
        self.spawns = []
        self.extras = []
        self._counts = {}

    # -- helpers --
    def h(self, x, z):
        return self.t.height(x, z)

    @staticmethod
    def face(x, z, tx, tz):
        """Yaw that points a node's -Z axis (its front) at (tx, tz)."""
        return math.atan2(-(tx - x), -(tz - z))

    @staticmethod
    def face_plus_z(x, z, tx, tz):
        """Yaw that points a node's +Z axis at (tx, tz) (signs read from +Z)."""
        return math.atan2(tx - x, tz - z)

    def is_free(self, x, z, r):
        for ox, oz, orad in self.occupied:
            if (x - ox) ** 2 + (z - oz) ** 2 < (r + orad) ** 2:
                return False
        return True

    def place(self, prop, x, z, yaw=0.0, scale=1.0, y=None, y_off=0.0, group="Decor", r=0.0, props=None):
        if y is None:
            y = self.h(x, z) + y_off
        self.items.append((group, prop, (x, y, z), yaw, scale, props or {}))
        if r > 0:
            self.occupied.append((x, z, r))

    def reserve(self, x, z, r):
        self.occupied.append((x, z, r))

    def scatter(self, props, count, group, r=1.0, scale=(1.0, 1.0), y_off=-0.05, area=None,
                path_gap=1.5, min_h=None, max_h=None, max_slope=0.9, register=True, keep_out=(), tries=40):
        area = area or self.bounds
        min_h = self.water_level + 0.35 if min_h is None else min_h
        placed = 0
        for _ in range(count * tries):
            if placed >= count:
                break
            if isinstance(area[0], tuple):  # ((cx, cz), radius) disc
                (cx, cz), rad = area
                ang, dist = self.rng.random() * math.tau, math.sqrt(self.rng.random()) * rad
                x, z = cx + math.cos(ang) * dist, cz + math.sin(ang) * dist
            else:
                x = self.rng.uniform(area[0], area[1])
                z = self.rng.uniform(area[2], area[3])
            if any(math.hypot(x - kx, z - kz) < kr for kx, kz, kr in keep_out):
                continue
            if path_gap is not None and self.t.path_dist(x, z) < self.t.path_width + path_gap:
                continue
            hh = self.h(x, z)
            if hh < min_h or (max_h is not None and hh > max_h):
                continue
            if self.t.slope(x, z) > max_slope:
                continue
            if register and not self.is_free(x, z, r):
                continue
            prop = self.rng.choice(props) if isinstance(props, (list, tuple)) else props
            s = self.rng.uniform(*scale)
            self.place(prop, x, z, self.rng.random() * math.tau, s, y_off=y_off, group=group, r=r * s if register else 0)
            placed += 1
        return placed

    def ring(self, prop, cx, cz, radius, count, group, start=0.0, face_center=True, skip=(), r=1.0, y_off=0.0, outward=False):
        for i in range(count):
            ang = start + i * math.tau / count
            if any(abs(math.remainder(ang - s, math.tau)) < 0.25 for s in skip):
                continue
            x, z = cx + math.cos(ang) * radius, cz + math.sin(ang) * radius
            yaw = self.face(x, z, cx, cz) if face_center else 0.0
            if outward:
                yaw += math.pi
            self.place(prop, x, z, yaw, group=group, r=r, y_off=y_off)

    def npc(self, data, x, z, y=None):
        if y is None:
            y = self.h(x, z) + 0.15
        self.npcs.append((data, (x, y, z)))
        self.reserve(x, z, 1.2)

    def portal(self, target, spawn, x, z, yaw, color_=(0.55, 0.85, 1.0)):
        self.portals.append((target, spawn, (x, self.h(x, z), z), yaw, color_))
        self.reserve(x, z, 4.0)

    def spawn(self, name, x, z, yaw):
        self.spawns.append((name, (x, self.h(x, z) + 0.2, z), yaw))
        self.reserve(x, z, 2.0)

    def sign(self, x, z, title, lines, face_to):
        yaw = self.face_plus_z(x, z, *face_to)
        self.place("sign_board", x, z, yaw, group="Signs", r=1.0, y_off=-0.05,
                   props={"title": string(title), "lines": strings(lines)})

    # -- output --
    def write(self):
        name = pascal(self.map_id)
        sc = Scene(name, "Node3D", props={})
        sc.nodes[0] += "\n" + "\n".join([
            f"script = {sc.ext_res('Script', 'res://scenes/world/level.gd')}",
            f"map_id = {string(self.map_id)}",
        ])
        e = self.env
        sky_mat = sc.sub_res("ProceduralSkyMaterial", {
            "sky_top_color": color(e["sky_top"]),
            "sky_horizon_color": color(e["sky_horizon"]),
            "sky_curve": "0.12",
            "ground_bottom_color": color(e["ground"]),
            "ground_horizon_color": color(e["sky_horizon"]),
            "sun_angle_max": "20.0",
        })
        sky = sc.sub_res("Sky", {"sky_material": sky_mat})
        env = sc.sub_res("Environment", {
            "background_mode": "2",
            "sky": sky,
            "ambient_light_source": "3",
            "ambient_light_color": color(e.get("ambient", (1, 1, 1))),
            "ambient_light_sky_contribution": "0.5",
            "ambient_light_energy": num(e.get("ambient_energy", 0.75)),
            "tonemap_mode": "0",
            "glow_enabled": "true",
            "glow_intensity": "0.5",
            "glow_bloom": "0.05",
            "glow_hdr_threshold": "1.2",
            "fog_enabled": "true",
            "fog_light_color": color(e["fog"]),
            "fog_density": num(e.get("fog_density", 0.004)),
            "fog_sky_affect": "0.3",
            "adjustment_enabled": "true",
            "adjustment_saturation": num(e.get("saturation", 1.0)),
        })
        sc.node("WorldEnvironment", "WorldEnvironment", props={"environment": env})
        sc.node("Sun", "DirectionalLight3D", props={
            "transform": xform((0, 30, 0), (e.get("sun_pitch", -0.9), e.get("sun_yaw", 0.6), 0)),
            "light_color": color(e.get("sun_color", (1.0, 0.96, 0.88))),
            "light_energy": num(e.get("sun_energy", 1.1)),
            "shadow_enabled": "true",
            "shadow_opacity": "0.75",
            "directional_shadow_max_distance": "90.0",
        })
        sc.node("Terrain", "StaticBody3D", props=self.t.node_props(sc))

        if self.water:
            w = self.water
            mat = sc.sub_res("ShaderMaterial", {
                "render_priority": "0",
                "shader": sc.ext_res("Shader", "res://shaders/water.gdshader"),
                "shader_parameter/water_color": color(w.get("color", (0.3, 0.72, 0.95))),
                "shader_parameter/deep_color": color(w.get("deep", (0.15, 0.48, 0.85))),
                "shader_parameter/foam_color": color((1, 1, 1)),
                "shader_parameter/alpha": num(w.get("alpha", 0.82)),
                "shader_parameter/wave_height": "0.06",
                "shader_parameter/foam_scale": "0.35",
            })
            size = w.get("size", self.t.size - 10)
            plane = sc.sub_res("PlaneMesh", {"material": mat, "size": v2(size, size), "subdivide_width": "96", "subdivide_depth": "96"})
            sc.node("Water", "MeshInstance3D", props={
                "transform": xform((w.get("x", 0), w["level"], w.get("z", 0))),
                "mesh": plane,
                "cast_shadow": "0",
            })

        # Invisible walls so nobody wanders off the edge of the world.
        x0, x1, z0, z1 = self.bounds
        sc.node("Bounds", "StaticBody3D")
        walls = [((x0 - 1, 0, (z0 + z1) / 2), (2, 120, z1 - z0 + 4)), ((x1 + 1, 0, (z0 + z1) / 2), (2, 120, z1 - z0 + 4)),
                 (((x0 + x1) / 2, 0, z0 - 1), (x1 - x0 + 4, 120, 2)), (((x0 + x1) / 2, 0, z1 + 1), (x1 - x0 + 4, 120, 2))]
        for i, (pos, size) in enumerate(walls):
            sc.node(f"Wall{i + 1}", "CollisionShape3D", "Bounds", props={
                "transform": xform(pos),
                "shape": sc.sub_res("BoxShape3D", {"size": v3(*size)}),
            })

        sc.node("Props", "Node3D")
        groups = []
        for group, *_ in self.items:
            if group not in groups:
                groups.append(group)
        for g in groups:
            sc.node(g, "Node3D", "Props")
        for group, prop, pos, yaw, scale, props in self.items:
            self._counts[prop] = self._counts.get(prop, 0) + 1
            p = {"transform": xform(pos, (0, yaw, 0), scale)}
            p.update(props)
            sc.node(f"{pascal(prop)}{self._counts[prop]}", None, f"Props/{group}",
                    instance=sc.ext_res("PackedScene", f"res://assets/props/{prop}.tscn"), props=p)

        sc.node("NPCs", "Node3D")
        for data, pos in self.npcs:
            p = {
                "transform": xform(pos, (0, data.get("yaw", 0.0), 0)),
                "npc_id": string(data["id"]),
                "display_name": string(data["name"]),
                "lines": strings(data["lines"]),
                "repeat_lines": strings(data.get("repeat", [])),
                "wander_radius": num(data.get("wander", 2.5)),
            }
            p.update(look_props(data["look"]))
            sc.node(pascal(data["id"]), None, "NPCs", instance=sc.ext_res("PackedScene", "res://scenes/characters/npc.tscn"), props=p)

        sc.node("Portals", "Node3D")
        for target, spawn, pos, yaw, col in self.portals:
            sc.node(f"To{pascal(target)}", None, "Portals",
                    instance=sc.ext_res("PackedScene", "res://scenes/world/portal.tscn"), props={
                        "transform": xform(pos, (0, yaw, 0)),
                        "target_map": string(target),
                        "target_spawn": string(spawn),
                        "ring_color": color(col),
                    })

        sc.node("Spawns", "Node3D")
        for name_, pos, yaw in self.spawns:
            sc.node(name_, "Marker3D", "Spawns", props={"transform": xform(pos, (0, yaw, 0))})

        for kind, data in self.extras:
            if kind == "snow":
                self._write_snow(sc, data)
            elif kind == "leaves":
                self._write_snow(sc, data)

        default = next(p for n, p, _ in self.spawns if n == "Default")
        sc.node("Player", None, ".", instance=sc.ext_res("PackedScene", "res://scenes/characters/player.tscn"), props={
            "transform": xform(default),
        })
        sc.node("HUD", None, ".", instance=sc.ext_res("PackedScene", "res://scenes/ui/hud.tscn"))
        sc.write(os.path.join(ROOT, f"levels/{self.map_id}.tscn"))

    def _write_snow(self, sc, d):
        mat = sc.sub_res("StandardMaterial3D", {
            "shading_mode": "0",
            "albedo_color": color(d.get("color", (1, 1, 1))),
        })
        mesh = sc.sub_res("SphereMesh", {"material": mat, "radius": num(d.get("size", 0.06)), "height": num(d.get("size", 0.06) * 2), "radial_segments": "6", "rings": "3"})
        sc.node(d.get("name", "Snowfall"), "CPUParticles3D", ".", props={
            "script": sc.ext_res("Script", "res://scenes/world/follow_player.gd"),
            "amount": str(d.get("amount", 500)),
            "lifetime": num(d.get("lifetime", 8.0)),
            "preprocess": "8.0",
            "local_coords": "false",
            "mesh": mesh,
            "emission_shape": "3",
            "emission_box_extents": v3(28, 1, 28),
            "direction": v3(0.3, -1, 0.1),
            "spread": "20.0",
            "gravity": v3(0, d.get("gravity", -1.2), 0),
            "initial_velocity_min": "0.5",
            "initial_velocity_max": "1.5",
            "offset": v3(0, d.get("height", 12), 0),
            "color": color(d.get("color", (1, 1, 1))),
        })


def preview(level, path, scale=3):
    from PIL import Image, ImageDraw

    t = level.t
    half = t.size / 2
    n = int(t.size * scale)
    img = Image.new("RGB", (n, n))
    px = img.load()
    for iy in range(n):
        for ix in range(n):
            x = ix / scale - half
            z = iy / scale - half
            hh = t.height(x, z)
            if hh < level.water_level:
                c = (70, 150, 230)
            elif t.path_dist(x, z) < t.path_width * 0.8:
                c = (205, 168, 115)
            else:
                g = max(0, min(255, int(110 + hh * 7)))
                c = (int(g * 0.6), g, int(g * 0.45))
            px[ix, iy] = c
    d = ImageDraw.Draw(img)

    def to_px(x, z):
        return ((x + half) * scale, (z + half) * scale)

    for group, prop, (x, _, z), *_ in level.items:
        cx, cy = to_px(x, z)
        colr = (20, 90, 30) if "tree" in prop or "bush" in prop else (200, 60, 60) if "house" in prop or "cabin" in prop else (120, 120, 120)
        rad = 3 if "house" in prop or "tree" in prop else 1
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=colr)
    for data, (x, _, z) in level.npcs:
        cx, cy = to_px(x, z)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 0, 200))
        d.text((cx + 6, cy - 6), data["name"], fill=(255, 255, 255))
    for target, _, (x, _, z), *_ in level.portals:
        cx, cy = to_px(x, z)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(0, 255, 255), width=3)
    for name, (x, _, z), _ in level.spawns:
        cx, cy = to_px(x, z)
        d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 0))
    img.save(path)


def main():
    write_materials()
    for prop in all_props():
        prop.write()
    write_core_scenes()
    out_dir = None
    if "--preview" in sys.argv:
        out_dir = sys.argv[sys.argv.index("--preview") + 1] if len(sys.argv) > sys.argv.index("--preview") + 1 else os.path.join(ROOT, "tools/previews")
        os.makedirs(out_dir, exist_ok=True)
    total_npcs = 0
    for build in LEVELS:
        level = build(Level)
        level.write()
        total_npcs += len(level.npcs)
        print(f"{level.map_id}: {len(level.items)} props, {len(level.npcs)} villagers, {len(level.portals)} portals")
        if out_dir:
            preview(level, os.path.join(out_dir, f"{level.map_id}.png"))
    print(f"total villagers: {total_npcs}")


if __name__ == "__main__":
    main()
