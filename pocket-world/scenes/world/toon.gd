class_name Toon
## Shared cartoon material helpers: flat toon shading plus an inverted-hull outline.

const OUTLINE := preload("res://assets/materials/outline.tres")

static var _cache := {}


static func material(color: Color, outline := true, emission := 0.0) -> StandardMaterial3D:
	var key := "%s|%s|%s" % [color.to_html(), outline, emission]
	if _cache.has(key):
		return _cache[key]
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
	mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	mat.roughness = 1.0
	if emission > 0.0:
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = emission
	if outline:
		mat.next_pass = OUTLINE
	_cache[key] = mat
	return mat
