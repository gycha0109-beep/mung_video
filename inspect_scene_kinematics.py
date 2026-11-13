import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path.home()/"Downloads"/"slingshot_quality_proof"/"three_shots"/"egg"/"launch"/"egg_launch.blend"))
s=bpy.context.scene
print("SCENE",s.frame_start,s.frame_end,s.render.resolution_x,s.render.resolution_y,flush=True)
print("CAM",s.camera.name,s.camera.data.lens,flush=True)
for ob in bpy.data.objects:
 if any(x in ob.name.lower() for x in ["pouch","band","camera","shot","rubber","slingshot","frame","arm","string","cup"]):
  print("OBJECT",ob.name,ob.type, "parent",ob.parent.name if ob.parent else "NONE",flush=True)
for f in [1,12,24,30,36,42,46,48,49,50,51,52,53,54,58,62,67,73,82,88,94]:
 s.frame_set(f)
 ob=bpy.data.objects["POLISHED STEEL SHOT"]
 cam=s.camera
 rig=bpy.data.objects["SHOT POUCH / rig"]
 print("FRAME",f,"BALL",tuple(round(v,3) for v in ob.matrix_world.translation),"POUCH",tuple(round(v,3) for v in rig.matrix_world.translation),"CAM",tuple(round(v,3) for v in cam.matrix_world.translation),"LENS",cam.data.lens,flush=True)
