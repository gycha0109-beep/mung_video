import bpy,sys
from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
kind=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=str(root/f"{kind}_20m_launch.blend"))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720;sc.render.resolution_y=1280
sc.render.resolution_percentage=100
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
folder=root/kind/"launch";folder.mkdir(parents=True,exist_ok=True)
for f in range(1,97):
 p=folder/("frame_%04d.png"%f)
 if p.exists() and p.stat().st_size>20000:
  continue
 sc.frame_set(f)
 sc.render.filepath=str(p)
 bpy.ops.render.render(write_still=True)
 print("RENDERED_RESUME",kind,f,flush=True)
print("LAUNCH_20M_COMPLETE",kind,flush=True)
