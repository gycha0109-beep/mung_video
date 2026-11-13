import bpy
from pathlib import Path
R=Path.home()/"Downloads"/"slingshot_quality_proof"
bpy.ops.wm.open_mainfile(filepath=str(R/"three_shots"/"billiard"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"))
s=bpy.context.scene
c=s.camera
out=["CAM "+c.name+" "+str(tuple(round(x,3) for x in c.location))+" "+str(c.data.lens)]
out+=["OBJ "+o.name+" type="+o.type+" rigid="+str(o.rigid_body.type if o.rigid_body else None) for o in s.objects if any(k in o.name.lower() for k in ("ball","projectile","billiard","cue"))]
for f in range(1,109):
 s.frame_set(f)
 if f not in [1,7,10,12,13,14,18,21,26,32,38,48,49,55,62,75,90,108]:continue
 out.append("FRAME "+str(f))
 for o in s.objects:
  if any(k in o.name.lower() for k in ("ball","projectile","billiard","cue")):
   p=o.matrix_world.translation
   out.append(o.name+" "+str(tuple(round(a,3) for a in p))+" render="+str(o.hide_render))
(R/"cinematic_50m_v8"/"billiard_motion_report.txt").write_text("\n".join(out),encoding="utf8")
print("REPORT_READY",flush=True)
