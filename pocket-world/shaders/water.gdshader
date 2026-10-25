shader_type spatial;
render_mode cull_disabled, specular_disabled, diffuse_toon;

// Cartoon water: gentle bobbing waves, a soft colour gradient and drifting foam lines.

uniform vec4 water_color : source_color = vec4(0.3, 0.7, 0.95, 1.0);
uniform vec4 deep_color : source_color = vec4(0.15, 0.45, 0.8, 1.0);
uniform vec4 foam_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float alpha = 0.82;
uniform float wave_height = 0.06;
uniform float foam_scale = 0.35;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	VERTEX.y += sin(world_pos.x * 0.35 + TIME * 1.2) * wave_height
		+ cos(world_pos.z * 0.28 + TIME * 0.9) * wave_height;
}

void fragment() {
	vec2 p = world_pos.xz * foam_scale;
	float blend = sin(p.x * 0.3 + TIME * 0.2) * cos(p.y * 0.25 - TIME * 0.15) * 0.5 + 0.5;
	vec3 col = mix(deep_color.rgb, water_color.rgb, blend);
	float lines = sin(p.x * 1.7 + sin(p.y * 1.3 + TIME) * 1.5 + TIME * 0.8);
	float foam = smoothstep(0.93, 0.98, lines) * (0.5 + 0.5 * sin(p.y * 0.7 + TIME * 0.5));
	ALBEDO = mix(col, foam_color.rgb, foam * 0.8);
	ROUGHNESS = 0.4;
	ALPHA = alpha;
}
