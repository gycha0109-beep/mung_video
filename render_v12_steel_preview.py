import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cinematic_50m_v12_steel"
OUT.mkdir(exist_ok=True)
SRC = ROOT / "cinematic_50m_v11_extension" / "steel" / "STEEL_V11_50M_SINGLE_SCENE.blend"
FRAME = 94
assert SRC.exists(), SRC
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene = bpy.context.scene
scene.frame_set(FRAME)
camera = scene.camera
assert camera, "Original V11 camera not found"
cam_matrix = [[round(float(v), 8) for v in row] for row in camera.matrix_world]
cam_lens = float(camera.data.lens)
original_resolution = (scene.render.resolution_x, scene.render.resolution_y)

def material(name, color, metallic=0, roughness=.65):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    return m, p

def noise_bump(m, p, scale, strength, distance):
    n = m.node_tree.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 5.0
    n.inputs["Roughness"].default_value = .68
    b = m.node_tree.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = distance
    m.node_tree.links.new(n.outputs["Fac"], b.inputs["Height"])
    m.node_tree.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return n

brick, bp = material("V12 | Fired clay brick PBR", (.31, .105, .067), roughness=.84)
co = brick.node_tree.nodes.new("ShaderNodeTexNoise")
co.inputs["Scale"].default_value = 8.4
co.inputs["Detail"].default_value = 5.0
co.inputs["Roughness"].default_value = .78
ramp = brick.node_tree.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .18
ramp.color_ramp.elements[0].color = (.055, .025, .019, 1)
ramp.color_ramp.elements[1].position = .78
ramp.color_ramp.elements[1].color = (.31, .125, .071, 1)
brick.node_tree.links.new(co.outputs["Fac"], ramp.inputs["Fac"])
variation = brick.node_tree.nodes.new("ShaderNodeObjectInfo")
scale_var = brick.node_tree.nodes.new("ShaderNodeMapRange")
scale_var.inputs["To Min"].default_value = .57
scale_var.inputs["To Max"].default_value = 1.0
brick.node_tree.links.new(variation.outputs["Random"], scale_var.inputs["Value"])
mix = brick.node_tree.nodes.new("ShaderNodeMixRGB")
mix.blend_type = "MULTIPLY"
mix.inputs[0].default_value = .32
brick.node_tree.links.new(ramp.outputs["Color"], mix.inputs[1])
brick.node_tree.links.new(scale_var.outputs["Result"], mix.inputs[2])
brick.node_tree.links.new(mix.outputs["Color"], bp.inputs["Base Color"])
noise_bump(brick, bp, 115, .30, .022)
rough = brick.node_tree.nodes.new("ShaderNodeMapRange")
rough.inputs["From Min"].default_value = 0
rough.inputs["From Max"].default_value = 1
rough.inputs["To Min"].default_value = .67
rough.inputs["To Max"].default_value = .94
brick.node_tree.links.new(co.outputs["Fac"], rough.inputs["Value"])
brick.node_tree.links.new(rough.outputs["Result"], bp.inputs["Roughness"])

mortar, mp = material("V12 | Mineral mortar PBR", (.36, .35, .30), roughness=.94)
noise_bump(mortar, mp, 85, .28, .018)

steel, sp = material("V12 | Precision steel micro-scratches", (.63, .68, .72), metallic=1, roughness=.17)
noise_bump(steel, sp, 320, .10, .0007)

ground, gp = material("V12 | Weathered compacted ground", (.25, .225, .19), roughness=.89)
gn = ground.node_tree.nodes.new("ShaderNodeTexNoise")
gn.inputs["Scale"].default_value = 38
gn.inputs["Detail"].default_value = 4
gr = ground.node_tree.nodes.new("ShaderNodeValToRGB")
gr.color_ramp.elements[0].color = (.055, .062, .065, 1)
gr.color_ramp.elements[1].color = (.205, .210, .207, 1)
ground.node_tree.links.new(gn.outputs["Fac"], gr.inputs["Fac"])
ground.node_tree.links.new(gr.outputs["Color"], gp.inputs["Base Color"])
noise_bump(ground, gp, 95, .24, .012)

counts = {"brick":0, "mortar":0, "steel":0, "ground":0}
for o in scene.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    low = o.name.lower()
    mat = None
    if low.startswith("hand-laid worn masonry") or low.startswith("v11 falling original masonry"):
        mat = brick
        counts["brick"] += 1
        if not any(m.type == 'BEVEL' for m in o.modifiers):
            mod = o.modifiers.new("V12 chipped edge catchlight", "BEVEL")
            mod.width = .007
            mod.segments = 2
            mod.affect = 'EDGES'
    elif "mortar" in low or "grout" in low:
        mat = mortar
        counts["mortar"] += 1
    elif "v11 steel projectile" in low:
        mat = steel
        counts["steel"] += 1
    elif any(x in low for x in ("ground", "terrain", "earth", "dirt", "floor", "asphalt", "concrete walkway", "courtyard")) and not any(x in low for x in ("launcher","slingshot","wooden")):
        mat = ground
        counts["ground"] += 1
    if mat is not None and o.data is not None:
        o.data.materials.clear()
        o.data.materials.append(mat)

def area(name, xyz, target, watts, size, rgb):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = watts
    data.shape = 'DISK'
    data.size = size
    data.color = rgb
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = xyz
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

area("V12 | Large soft sunlight", (-3.5, -3.5, 7.5), (0, -.20, 1.33), 370, 6.5, (1, .88, .76))
area("V12 | Cool sky bounce", (4.5, -1.8, 4.5), (0, -.20, 1.33), 140, 8.0, (.69, .81, 1))

scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception as exc:
    print("COLOR_VIEW_FALLBACK", exc)
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.get_devices()
    prefs.compute_device_type = "CUDA"
    for device in prefs.devices:
        device.use = device.type == 'CUDA'
    scene.cycles.device = 'GPU' if any(d.type == 'CUDA' for d in prefs.devices) else 'CPU'
except Exception as exc:
    print("GPU_FALLBACK", exc)
    scene.cycles.device = 'CPU'

scene.frame_set(FRAME)
assert max(abs(float(camera.matrix_world[i][j])-cam_matrix[i][j]) for i in range(4) for j in range(4)) < 1e-6
assert float(camera.data.lens) == cam_lens
assert counts["steel"] > 0 and counts["brick"] > 0, counts
scene.render.filepath = str(OUT / "STEEL_V12_FRAME_094.png")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "STEEL_V12_CINEMATIC_PREVIEW.blend"))
(OUT / "V12_RENDER_INFO.json").write_text(json.dumps({
 "source": str(SRC.relative_to(ROOT)), "frame": FRAME,
 "camera_matrix": cam_matrix, "camera_lens": cam_lens,
 "original_resolution": original_resolution,
 "render": "Cycles", "samples": scene.cycles.samples,
 "materials": counts, "device": scene.cycles.device
}, indent=2), encoding="utf-8")
bpy.ops.render.render(write_still=True)
print("V12_RENDER_DONE", scene.render.filepath, counts, flush=True)
