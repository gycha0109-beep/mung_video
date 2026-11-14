import bpy
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v4"
bpy.ops.wm.open_mainfile(filepath=str(out/"GLASS_20_PANEL_CHALLENGE_V4_2.blend"))
s=bpy.context.scene
ground=bpy.data.objects.get("Ground | catch falling glass")
if ground:
    ground.scale.x*=3
    ground.scale.y*=3
# Far plates should be almost clear; avoid endless opaque plastic cards.
glass=bpy.data.materials["V3 clear thin glass"]
front=glass.copy()
front.name="V4.3 complete plate thin silica"
pn=front.node_tree.nodes.get("Principled BSDF")
pn.inputs["Alpha"].default_value=.065
pn.inputs["Roughness"].default_value=.046
pn.inputs["Base Color"].default_value=(.86,.91,.93,1)
front.surface_render_method="BLENDED"
# Splinters get a little more visible at glancing angles, but stay thin.
pieces=glass.copy()
pieces.name="V4.3 separated flying fragments"
p=pieces.node_tree.nodes.get("Principled BSDF")
p.inputs["Alpha"].default_value=.25
p.inputs["Roughness"].default_value=.075
p.inputs["Base Color"].default_value=(.71,.80,.83,1)
pieces.surface_render_method="BLENDED"
for o in bpy.data.objects:
    if o.type!="MESH" or len(o.data.materials)<1:continue
    if o.name.startswith("Glass sheet"):
        o.data.materials[0]=front
    if " irregular shard " in o.name:
        o.data.materials[0]=pieces
# The environment should not end in a clear horizon cutoff.
s.frame_set(1)
dest=out/"GLASS_20_PANEL_CHALLENGE_V4_FINAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print("V4_FINAL_SCENE",dest,flush=True)
