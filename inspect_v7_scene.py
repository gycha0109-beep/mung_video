import bpy,json,math
from pathlib import Path
src=Path.home()/"Downloads"/"slingshot_quality_proof"/"three_shots"/"egg"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.open_mainfile(filepath=str(src))
s=bpy.context.scene
lines=[]
lines.append("SCENE frame %d-%d camera %s"%(s.frame_start,s.frame_end,s.camera.name))
for f in [13,24,38,48,60,84,108]:
 s.frame_set(f)
 c=s.camera
 lines.append("FRAME %d CAM pos %s rot %s lens %.2f"%(f,list(map(lambda x:round(x,3),c.matrix_world.translation)),list(map(lambda x:round(x,3),c.rotation_euler)),c.data.lens))
 for o in s.objects:
  if any(t in o.name.lower() for t in ["yolk","white","shell","fragment","puddle","splat","egg","liquid","brick","ground"]):
   if f==48:
    loc=o.matrix_world.translation
    lines.append("OBJ %-42s %-5s pos=(%.3f,%.3f,%.3f) dim=%s hide=%s RIGID=%s"%(o.name,o.type,loc.x,loc.y,loc.z,tuple(round(x,3) for x in o.dimensions),o.hide_render,o.rigid_body.type if o.rigid_body else None))
lines.append("ALL OBJECTS NAMES:")
lines.extend([o.name for o in s.objects])
out=src.parent.parent.parent.parent/"cinematic_v6_egg"/"v7_scene_report.txt"
out.write_text("\n".join(lines),encoding="utf-8")
print("REPORT_WRITTEN",out)
