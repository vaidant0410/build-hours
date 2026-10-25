class_name PropBaker
## Merges the many primitive pieces of a prop (a flower patch is 18 meshes) into
## one mesh with vertex colours, so each prop costs one draw call (plus its outline)
## instead of dozens. Props are authored as separate pieces so they stay easy to
## edit; baking only happens at runtime. Emissive pieces keep their own material,
## and pieces under scripted pivots (windmill blades, campfire flames) are left
## alone so they keep animating.

const VC_MATERIAL := preload("res://assets/materials/toon_vertex_color.tres")

static var _cache := {}


static func bake_children(root: Node) -> void:
	for group in root.get_children():
		for inst in group.get_children():
			if inst is Node3D and inst.scene_file_path != "":
				bake(inst)


static func bake(inst: Node3D) -> void:
	var pieces := _pieces(inst)
	if pieces.size() < 2:
		return
	var path := inst.scene_file_path
	if not _cache.has(path):
		_cache[path] = _build_mesh(inst, pieces)
	for mi in pieces:
		mi.free()
	var merged := MeshInstance3D.new()
	merged.name = "BakedMesh"
	merged.mesh = _cache[path]
	inst.add_child(merged)


static func _pieces(inst: Node3D) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	for node in inst.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null or mi.owner != inst or _under_script(mi, inst):
			continue
		out.append(mi)
	return out


static func _under_script(node: Node, root: Node) -> bool:
	var n := node.get_parent()
	while n and n != root:
		if n.get_script() != null:
			return true
		n = n.get_parent()
	return false


static func _local_transform(node: Node3D, root: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY
	var n: Node = node
	while n and n != root:
		t = (n as Node3D).transform * t
		n = n.get_parent()
	return t


static func _build_mesh(inst: Node3D, pieces: Array[MeshInstance3D]) -> ArrayMesh:
	# One bucket for every plain toon piece (coloured per vertex), plus one per
	# emissive or otherwise special material.
	var buckets := {}
	for mi in pieces:
		var mat := mi.get_surface_override_material(0)
		if mat == null:
			mat = mi.material_override
		if mat == null:
			mat = mi.mesh.surface_get_material(0)
		var std := mat as StandardMaterial3D
		var plain := std != null and not std.emission_enabled and std.transparency == BaseMaterial3D.TRANSPARENCY_DISABLED
		var key: Variant = "vc" if plain else mat
		if not buckets.has(key):
			buckets[key] = {"verts": PackedVector3Array(), "normals": PackedVector3Array(),
				"colors": PackedColorArray(), "indices": PackedInt32Array(), "material": mat}
		var xf := _local_transform(mi, inst)
		var nbasis := xf.basis.inverse().transposed()
		var col := std.albedo_color if std else Color.WHITE
		# Packed arrays are values in GDScript, so work on locals and store them back.
		var bv: PackedVector3Array = buckets[key].verts
		var bn: PackedVector3Array = buckets[key].normals
		var bc: PackedColorArray = buckets[key].colors
		var bi: PackedInt32Array = buckets[key].indices
		for s in mi.mesh.get_surface_count():
			var arrays := mi.mesh.surface_get_arrays(s)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var base := bv.size()
			for i in verts.size():
				bv.append(xf * verts[i])
				bn.append((nbasis * normals[i]).normalized() if normals.size() > i else Vector3.UP)
				bc.append(col)
			if indices.is_empty():
				for i in verts.size():
					bi.append(base + i)
			else:
				for idx in indices:
					bi.append(base + idx)
		buckets[key].verts = bv
		buckets[key].normals = bn
		buckets[key].colors = bc
		buckets[key].indices = bi

	var mesh := ArrayMesh.new()
	for key in buckets:
		var b: Dictionary = buckets[key]
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = b.verts
		arrays[Mesh.ARRAY_NORMAL] = b.normals
		arrays[Mesh.ARRAY_COLOR] = b.colors
		arrays[Mesh.ARRAY_INDEX] = b.indices
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		mesh.surface_set_material(mesh.get_surface_count() - 1, VC_MATERIAL if key is String else b.material)
	return mesh
