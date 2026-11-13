import bpy,sys
from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
kind=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=str(root/f"{kind}_impact_aftermath_4sec.blend"))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720;sc.render.resolution_y=1280
sc.render.resolution_percentage=100
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.rigidbody_world.point_cache.frame_end=108
folder=root/kind/"impact"
folder.mkdir(parents=True,exist_ok=True)
for frame in range(1,109):
 sc.frame_set(frame)
 dest=folder/("frame_%04d.png"%frame)
 if dest.exists() and dest.stat().st_size>20000:continue
 sc.render.filepath=str(dest)
 bpy.ops.render.render(write_still=True)
 print("IMPACT_RESUME",kind,frame,flush=True)
print("IMPACT_4SEC_FINISHED",kind,flush=True)
