import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
target=R/"glass_panel_challenge_v7"/"V7_ONE_PANE_PHYSICS_MASTER.blend"
bpy.ops.wm.open_mainfile(filepath=str(target))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(target))
for im in bpy.data.images:
    if "studio_small_09" in im.name:
        assert im.packed_file is not None,"HDRI not packed"
        print("PACKED_HDRI",im.name,len(im.packed_file.data),flush=True)
print("V7_PROJECT_PORTABLE",target,flush=True)
