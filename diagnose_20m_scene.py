import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v2"/"egg_launch_v2.blend"))
s=bpy.context.scene
for ob in bpy.data.objects:
 if ob.type in ("MESH","CURVE","EMPTY","CAMERA"):
  print("OBJ",ob.name,"LOC",tuple(round(a,2) for a in ob.location),"DIM",tuple(round(a,2) for a in ob.dimensions),"PARENT",ob.parent.name if ob.parent else "-",flush=True)
for f in (1,30,34,35,41,46,48):
 s.frame_set(f)
 print("KEY",f,"BALL",tuple(round(a,2) for a in bpy.data.objects["POLISHED STEEL SHOT"].matrix_world.translation),"CAM",tuple(round(a,2) for a in s.camera.matrix_world.translation),flush=True)
