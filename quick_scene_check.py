import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v2"/"egg_launch_v2.blend"))
s=bpy.context.scene
for ob in bpy.data.objects:
 if any(x in ob.name.lower() for x in ("wall", "floor", "walkway", "wooden", "oak", "elastic", "band", "pouch", "steel shot", "camera", "foundation", "light")):
  if ob.type not in ('MESH','EMPTY','CAMERA','LIGHT'):continue
  if any(x in ob.name.lower() for x in ('clay','fractured')):continue
  print(ob.name,ob.type,tuple(round(v,3) for v in ob.location),tuple(round(v,2) for v in ob.dimensions),flush=True)
