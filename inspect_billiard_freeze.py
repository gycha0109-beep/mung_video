import bpy
from pathlib import Path
p=Path.home()/"Downloads"/"slingshot_quality_proof"/"three_shots"/"billiard"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.open_mainfile(filepath=str(p))
s=bpy.context.scene
o=bpy.data.objects["PHYSICS 8 BALL"]
w=s.rigidbody_world
print("CACHE",w.point_cache.frame_start,w.point_cache.frame_end,w.point_cache.is_baked,"SCENE",s.frame_start,s.frame_end,flush=True)
print("RB",o.rigid_body.type,o.rigid_body.kinematic,o.rigid_body.enabled,o.rigid_body.friction,o.rigid_body.restitution,flush=True)
for f in [1,10,13,24,38,47,48,49,50,55,65]:
 s.frame_set(f)
 print("STATE",f,"WORLD",tuple(round(v,3) for v in o.matrix_world.translation),"LOCAL",tuple(round(v,3) for v in o.location),"KIN",o.rigid_body.kinematic,"ENA",o.rigid_body.enabled,flush=True)
