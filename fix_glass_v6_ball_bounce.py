import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v6"
path=O/"GLASS_V6_QUALITY_FINAL.blend"
bpy.ops.wm.open_mainfile(filepath=str(path))
ball=bpy.data.objects["19 mm equivalent chrome projectile"]
ball.animation_data_clear()
points=[
(1,-4.34,1.54),(11,-4.44,1.54),(23,-5.35,1.54),(29,-5.35,1.54),
(31,-4.23,1.54),(34,-3.38,1.54),(40,-1.02,1.54),(43,-.065,1.54),
(46,.36,1.52),(52,1.16,1.40),(57,1.65,1.12),(61,1.95,.70),
(64,2.17,.14),(67,2.30,.30),(70,2.44,.29),(73,2.58,.15),
(78,2.74,.100),(84,3.03,.095)]
for f,y,z in points:
    ball.location=(0,y,z)
    ball.keyframe_insert(data_path="location",frame=f)
    ball.rotation_euler=(f*.08,f*.07,f*.11)
    ball.keyframe_insert(data_path="rotation_euler",frame=f)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print("V6_BALL_GRAVITY_FIXED",path,flush=True)
