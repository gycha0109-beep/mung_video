import bpy,sys,math
from pathlib import Path
from mathutils import Vector
root=Path.home()/"Downloads"/"slingshot_quality_proof"
kind=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "steel"
mode=sys.argv[sys.argv.index("--")+2] if "--" in sys.argv and len(sys.argv)>sys.argv.index("--")+2 else "preview"
source=(root/"slingshot_pouch_mechanics_v3.blend") if kind=="steel" else (root/"three_shots"/kind/"launch"/(kind+"_launch.blend"))
out=root/"cinematic_v2"
(out/kind/"launch_frames").mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720;s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="video" else 75
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.fps=24
s.frame_start=1;s.frame_end=46
s.render.image_settings.compression=15
cam=bpy.data.objects["CINEMA CAMERA"]
ball=bpy.data.objects["POLISHED STEEL SHOT"]
rig=bpy.data.objects["SHOT POUCH / rig"]
bands=[bpy.data.objects["TENSIONED LATEX / LEFT"],bpy.data.objects["TENSIONED LATEX / RIGHT"]]
for o in [cam,ball,rig]+bands:o.animation_data_clear()
cam.data.animation_data_clear()
# Explicit physical displacement: 1.3 m pull and high-speed launch.
pouch=[
(1,-9.57),(6,-9.60),(10,-9.73),(14,-10.07),
(18,-10.46),(22,-10.72),(27,-10.87),(30,-10.87),
(31,-10.82),(32,-9.99),(33,-9.50),(34,-9.38),
(36,-9.62),(39,-9.55),(46,-9.55)]
def put_location(o,f,v):
 o.location=v;o.keyframe_insert(data_path="location",frame=f)
for f,y in pouch:
 put_location(rig,f,(0,y,1.79))
 for name,sgn in (("LEFT",-1),("RIGHT",1)):
  band=bpy.data.objects["TENSIONED LATEX / "+name]
  tip=Vector((sgn*.32,-9.33,2.01))
  target=Vector((sgn*.205,y-.078,1.808))
  delta=target-tip
  band.location=(tip+target)/2
  band.rotation_mode="QUATERNION"
  band.rotation_quaternion=delta.to_track_quat("Z","Y")
  band.scale=(.065,.025,delta.length)
  for prop in ("location","rotation_quaternion","scale"):
   band.keyframe_insert(prop,frame=f)
ball_path=[
(1,-9.57,1.79),(6,-9.60,1.79),(10,-9.73,1.79),
(14,-10.07,1.79),(18,-10.46,1.79),(22,-10.72,1.79),
(27,-10.87,1.79),(30,-10.87,1.79),
(31,-10.82,1.79),
(32,-9.92,1.79),(33,-8.66,1.79),(34,-7.25,1.79),
(35,-5.90,1.78),(36,-5.05,1.77),(37,-4.49,1.76),
(38,-4.04,1.75),(39,-3.68,1.74),(40,-3.38,1.73),
(41,-3.08,1.72),(46,-1.2,1.68)]
for f,y,z in ball_path:put_location(ball,f,(0,y,z))
# Cinematic motivation: see rubber stretch from a fixed frame, then cut to a pursuit camera.
def camera_pose(f,loc,target,lens):
 cam.location=loc
 cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
 cam.keyframe_insert("location",frame=f)
 cam.keyframe_insert("rotation_euler",frame=f)
 cam.data.lens=lens;cam.data.keyframe_insert("lens",frame=f)
camera_pose(1,(.10,-11.75,1.97),(0,-9.55,1.74),35)
camera_pose(12,(.28,-11.92,2.07),(0,-9.64,1.75),37)
camera_pose(21,(.68,-12.17,2.16),(0,-9.92,1.73),41)
camera_pose(30,(.74,-12.22,2.15),(0,-10.13,1.75),45)
camera_pose(31,(.74,-12.22,2.15),(0,-10.13,1.75),45)
camera_pose(32,(.74,-12.22,2.15),(0,-10.13,1.75),45)
camera_pose(33,(.74,-12.22,2.15),(0,-10.13,1.75),45)
camera_pose(34,(.74,-12.22,2.15),(0,-10.13,1.75),45)
# A whip cut from the stationary shooter to a low side pursuit camera.
camera_pose(35,(1.04,-7.65,2.03),(0,-5.90,1.78),38)
camera_pose(37,(1.04,-6.30,1.96),(0,-4.49,1.76),34)
camera_pose(39,(1.15,-5.38,1.89),(0,-3.68,1.74),32)
camera_pose(41,(1.26,-4.57,1.85),(0,-3.08,1.72),30)
camera_pose(46,(1.42,-2.95,1.78),(0,-1.2,1.68),28)
# No interpolation through the camera cut.
for o in (cam,):
 ad=o.animation_data
 for layer in ad.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for kp in fc.keyframe_points:
      if kp.co.x==34:kp.interpolation='CONSTANT'
# Stepped camera shoot side angles are intentional, moving pre-release has smooth easing.
def change_tangents(obj,start,end,method):
 ad=obj.animation_data
 if not ad:return
 for layer in ad.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for kp in fc.keyframe_points:
      if start<=kp.co.x<=end:kp.interpolation=method
change_tangents(ball,31,46,"LINEAR")
change_tangents(rig,30,39,"BEZIER")
change_tangents(cam,35,46,"LINEAR")
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.32
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/(kind+"_launch_v2.blend")))
print("NEW_CAMERA_RIG_AND_PHYSICAL_PULL",kind,flush=True)
if mode=="preview":
 for f in (1,14,22,30,32,33,34,35,37,41):
  s.frame_set(f)
  s.render.filepath=str(out/kind/("check_%03d.png"%f))
  bpy.ops.render.render(write_still=True)
  print("PREVIEW_FRAME",kind,f,flush=True)
elif mode=="video":
 s.frame_end=41
 s.render.filepath=str(out/kind/"launch_frames"/"frame_")
 bpy.ops.render.render(animation=True)
 print("RENDERED_NEW_LAUNCH",kind,flush=True)
