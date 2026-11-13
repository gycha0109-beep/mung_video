import bpy
from pathlib import Path
R=Path.home()/"Downloads"/"slingshot_quality_proof"
res=[]
files=[("launch",R/"cinematic_50m_v9t_egg"/"EGG_50M_V9T_TRACKLOCK.blend"),("impact",R/"cinematic_50m_v9_egg"/"EGG_50M_V9_FORCEFUL_IMPACT.blend")]
for title,path in files:
 bpy.ops.wm.open_mainfile(filepath=str(path))
 s=bpy.context.scene
 res.append("===== "+title+" =====")
 res.append("CAM "+s.camera.name+" "+str(tuple(round(v,3) for v in s.camera.location)))
 for o in s.objects:
  if o.type not in ("MESH","FONT","CURVE","EMPTY"):continue
  loc=o.matrix_world.translation
  dim=o.dimensions
  if title=="launch" and not (-14<loc.y<4 or "steel shot" in o.name.lower() or "y arm" in o.name.lower()):continue
  res.append("%s [%s] xyz(%.3f,%.3f,%.3f) dims(%.2f,%.2f,%.2f) hide=%s rigid=%s" % (
   o.name,o.type,loc.x,loc.y,loc.z,dim.x,dim.y,dim.z,o.hide_render,o.rigid_body.type if o.rigid_body else "-"))
 s.frame_set(96 if title=="launch" else 13)
 res.append("FRAME "+str(s.frame_current))
 for o in s.objects:
  if "egg" in o.name.lower() or "shot" in o.name.lower() or "projectile" in o.name.lower():
   loc=o.matrix_world.translation
   res.append("PROJ "+o.name+" "+str(tuple(round(v,3) for v in loc)))
out=R/"v10_join_scene_report.txt"
out.write_text("\n".join(res),encoding="utf8")
print("REPORT",out,flush=True)
