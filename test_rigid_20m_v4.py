import bpy,sys,math
from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"
mode=sys.argv[sys.argv.index("--")+1]
path=(root/"physics_proof_v1"/"PHYSICAL_IMPACT_DEMO.blend") if mode in ("original","extend") else (root/"cinematic_20m_v4"/"steel_impact_aftermath_4sec.blend")
bpy.ops.wm.open_mainfile(filepath=str(path))
s=bpy.context.scene
rbw=s.rigidbody_world
print("STATUS",mode,"range",rbw.point_cache.frame_start,rbw.point_cache.frame_end,"baked",rbw.point_cache.is_baked,flush=True)
if mode=="extend":rbw.point_cache.frame_end=108
ball=bpy.data.objects["PHYSICS STEEL PROJECTILE"]
frags=[o for o in bpy.data.objects if "PHYSICS fracture" in o.name]
start=frags[0].location.copy()
for frame in range(1,25):
 s.frame_set(frame)
 if frame in (1,12,13,14,17,20,24):
  deps=bpy.context.evaluated_depsgraph_get()
  pos=ball.evaluated_get(deps).matrix_world.translation
  p=frags[0].evaluated_get(deps).matrix_world.translation
  active=sum((o.evaluated_get(deps).matrix_world.translation-o.location).length>.05 for o in frags)
  print("FRAME",frame,"BALL",tuple(round(v,3) for v in pos),"FIRST",tuple(round(v,3) for v in p),"MOVED",active,flush=True)
