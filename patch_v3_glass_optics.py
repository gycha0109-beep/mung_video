import bpy
from pathlib import Path
root=Path(r"C:\Users\hun\Documents\mung_video\glass_panel_challenge_v3")
path=root/"GLASS_20_PANEL_CHALLENGE_V3.blend"
bpy.ops.wm.open_mainfile(filepath=str(path))
m=bpy.data.materials.get("V3 clear thin glass")
assert m is not None
m.surface_render_method="BLENDED"
p=m.node_tree.nodes.get("Principled BSDF")
p.inputs["Alpha"].default_value=.23
p.inputs["Transmission Weight"].default_value=.28
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print("OPTICS_PATCH_OK",m.name,m.surface_render_method,flush=True)
