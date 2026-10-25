@tool
class_name Terrain
extends StaticBody3D
## Procedural cartoon terrain: rolling hills, a mountain rim around the edge,
## flattened areas for towns, carved channels and painted dirt paths.
## The mesh and collision are rebuilt whenever a parameter changes in the editor.
##
## NOTE: tools/build_world.py mirrors height_at() so it can place props on the
## ground. If you change the formula here, change it there too.

@export var size := 160:
	set(v): size = v; _queue_build()
@export var seed_offset := 0.0:
	set(v): seed_offset = v; _queue_build()
@export var base_height := 1.0:
	set(v): base_height = v; _queue_build()
@export var amplitude := 2.0:
	set(v): amplitude = v; _queue_build()
@export var frequency := 0.04:
	set(v): frequency = v; _queue_build()
## Height change per metre along X and Z (tilts the whole map, e.g. toward the sea).
@export var tilt := Vector2.ZERO:
	set(v): tilt = v; _queue_build()
@export var border_width := 20.0:
	set(v): border_width = v; _queue_build()
@export var border_height := 18.0:
	set(v): border_height = v; _queue_build()
## How strongly each edge rises into mountains: (west, east, north, south). 0 = open edge (e.g. the sea).
@export var border_sides := Vector4(1, 1, 1, 1):
	set(v): border_sides = v; _queue_build()
## Flattened discs: (x, z, radius, height).
@export var flats: Array[Vector4] = []:
	set(v): flats = v; _queue_build()
## Carved channels (rivers / lake beds) as segments: (x1, z1, x2, z2).
@export var channels: Array[Vector4] = []:
	set(v): channels = v; _queue_build()
@export var channel_width := 6.0:
	set(v): channel_width = v; _queue_build()
@export var channel_bottom := -1.5:
	set(v): channel_bottom = v; _queue_build()
## Painted dirt paths as segments: (x1, z1, x2, z2).
@export var paths: Array[Vector4] = []:
	set(v): paths = v; _queue_build()
@export var path_width := 2.2:
	set(v): path_width = v; _queue_build()

@export_group("Colors")
@export var grass_color := Color(0.49, 0.78, 0.36):
	set(v): grass_color = v; _queue_build()
@export var grass_alt_color := Color(0.4, 0.7, 0.32):
	set(v): grass_alt_color = v; _queue_build()
@export var rock_color := Color(0.6, 0.56, 0.52):
	set(v): rock_color = v; _queue_build()
@export var sand_color := Color(0.95, 0.87, 0.6):
	set(v): sand_color = v; _queue_build()
@export var path_color := Color(0.82, 0.66, 0.45):
	set(v): path_color = v; _queue_build()
@export var snow_color := Color(0.96, 0.97, 1.0):
	set(v): snow_color = v; _queue_build()
@export var sand_height := 0.4:
	set(v): sand_height = v; _queue_build()
@export var snow_height := 14.0:
	set(v): snow_height = v; _queue_build()
@export var rock_slope := 0.35:
	set(v): rock_slope = v; _queue_build()

var _build_queued := false


func _ready() -> void:
	_build()


func _queue_build() -> void:
	if not is_inside_tree() or _build_queued:
		return
	_build_queued = true
	_build.call_deferred()


func height_at(x: float, z: float) -> float:
	var s := seed_offset
	var fx := x * frequency
	var fz := z * frequency
	var n := sin(fx + s) * cos(fz * 0.8 + s * 1.3) * 0.55 \
		+ sin(fx * 2.1 - fz * 1.7 + s * 2.1) * 0.25 \
		+ cos(fx * 3.7 + fz * 2.9 + s * 0.7) * 0.12 \
		+ sin(fx * 0.45 + fz * 0.35 + s * 3.1) * 0.6
	var h := base_height + n * amplitude + tilt.x * x + tilt.y * z

	for f in flats:
		var d := Vector2(x - f.x, z - f.y).length()
		var w := 1.0 - smoothstep(f.z * 0.55, f.z, d)
		h = lerpf(h, f.w, w)

	for c in channels:
		var d := _segment_distance(x, z, c)
		var w := 1.0 - smoothstep(channel_width * 0.35, channel_width, d)
		h = minf(h, lerpf(h, channel_bottom, w))

	var half := size * 0.5
	var tx := smoothstep(half - border_width, half, absf(x)) * (border_sides.y if x > 0.0 else border_sides.x)
	var tz := smoothstep(half - border_width, half, absf(z)) * (border_sides.w if z > 0.0 else border_sides.z)
	var t := maxf(tx, tz)
	var bumps := 0.75 + 0.35 * sin(x * 0.13 + s) * cos(z * 0.11 - s)
	return h + t * border_height * bumps


func path_amount(x: float, z: float) -> float:
	var amount := 0.0
	for p in paths:
		var d := _segment_distance(x, z, p)
		amount = maxf(amount, 1.0 - smoothstep(path_width * 0.6, path_width, d))
	return amount


func _segment_distance(x: float, z: float, seg: Vector4) -> float:
	var a := Vector2(seg.x, seg.y)
	var b := Vector2(seg.z, seg.w)
	var p := Vector2(x, z)
	var ab := b - a
	var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
	return p.distance_to(a + ab * t)


func _build() -> void:
	_build_queued = false
	for child in get_children():
		if child.has_meta("generated"):
			child.free()

	var n := size + 1
	var half := size * 0.5
	var heights := PackedFloat32Array()
	heights.resize(n * n)
	for iz in n:
		for ix in n:
			heights[iz * n + ix] = height_at(ix - half, iz - half)

	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	verts.resize(n * n)
	normals.resize(n * n)
	colors.resize(n * n)
	for iz in n:
		for ix in n:
			var i := iz * n + ix
			var x := ix - half
			var z := iz - half
			var h := heights[i]
			var hl := heights[iz * n + maxi(ix - 1, 0)]
			var hr := heights[iz * n + mini(ix + 1, n - 1)]
			var hd := heights[maxi(iz - 1, 0) * n + ix]
			var hu := heights[mini(iz + 1, n - 1) * n + ix]
			var normal := Vector3(hl - hr, 2.0, hd - hu).normalized()
			verts[i] = Vector3(x, h, z)
			normals[i] = normal
			colors[i] = _color_at(x, z, h, normal)

	var indices := PackedInt32Array()
	indices.resize(size * size * 6)
	var k := 0
	for iz in size:
		for ix in size:
			var a := iz * n + ix
			var b := a + 1
			var c := a + n
			var d := c + 1
			indices[k] = a; indices[k + 1] = b; indices[k + 2] = c
			indices[k + 3] = b; indices[k + 4] = d; indices[k + 5] = c
			k += 6

	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)

	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.vertex_color_is_srgb = true
	mat.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
	mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	mat.roughness = 1.0
	mesh.surface_set_material(0, mat)

	var mi := MeshInstance3D.new()
	mi.name = "TerrainMesh"
	mi.mesh = mesh
	mi.set_meta("generated", true)
	add_child(mi)

	var shape := HeightMapShape3D.new()
	shape.map_width = n
	shape.map_depth = n
	shape.map_data = heights
	var col := CollisionShape3D.new()
	col.name = "TerrainCollision"
	col.shape = shape
	col.set_meta("generated", true)
	add_child(col)


func _color_at(x: float, z: float, h: float, normal: Vector3) -> Color:
	# Soft, blotchy grass variation so the ground doesn't look flat.
	var blotch := sin(x * 0.21 + seed_offset) * cos(z * 0.17 - seed_offset) + sin((x + z) * 0.07) * 0.5
	var col := grass_color.lerp(grass_alt_color, smoothstep(-0.2, 0.6, blotch))
	col = col.lerp(path_color, path_amount(x, z))
	col = col.lerp(sand_color, 1.0 - smoothstep(sand_height, sand_height + 0.6, h))
	col = col.lerp(rock_color, smoothstep(rock_slope, rock_slope + 0.12, 1.0 - normal.y))
	col = col.lerp(snow_color, smoothstep(snow_height, snow_height + 1.5, h))
	return col
