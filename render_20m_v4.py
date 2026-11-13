import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_20m_v4"
OUT.mkdir(exist_ok=True)
kind=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "egg"
mode=sys.argv[sys.argv.index("--")+2] if "--" in sys.argv and len(sys.argv)>sys.argv.index("--")+2 else "preview"
path=ROOT/"cinematic_v2"/f"{kind}_launch_v2.blend"
bpy.ops.wm.open_mainfile(filepath=str(path))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720
sc.render.resolution_y=1280
sc.render.resolution_percentage=100 if mode=="full" else 66
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.render.image_settings.compression=16
sc.render.use_motion_blur=True
sc.render.motion_blur_shutter=.38
sc.frame_start=1
sc.frame_end=96
cam=bpy.data.objects["CINEMA CAMERA"]
ball=bpy.data.objects["POLISHED STEEL SHOT"]
rig=bpy.data.objects["SHOT POUCH / rig"]
bands={side:bpy.data.objects["TENSIONED LATEX / "+side] for side in ("LEFT","RIGHT")}
# Move the physical slingshot 10m away from the original wall, instead of faking distance in editing.
shift=-10.
for o in bpy.data.objects:
 if o.name in (
 "Carved wooden slingshot handle","Solid oak Y arm LEFT","Solid oak Y arm RIGHT",
 "Forged elastic anchor LEFT","Forged elastic anchor RIGHT",
 "Brushed elastic cap LEFT","Brushed elastic cap RIGHT","Side metallic specular highlight"):
  o.location.y+=shift
floor=bpy.data.objects.get("Concrete walkway")
if floor:
 floor.location.y=-10.
 floor.dimensions.y=31.
for obj in (cam,ball,rig,*bands.values()):obj.animation_data_clear()
cam.data.animation_data_clear()
def put(obj,frame,xyz):
 obj.location=xyz
 obj.keyframe_insert(data_path="location",frame=frame)
draw=[
 (1,-19.57),(12,-19.68),(22,-20.16),(35,-20.70),
 (43,-20.87),(48,-20.87),(49,-20.59),(50,-20.08),
 (51,-19.57),(52,-19.43),(54,-19.58),(60,-19.55),(96,-19.55)]
for f,y in draw:
 put(rig,f,(0,y,1.79))
 for side,sgn in (("LEFT",-1),("RIGHT",1)):
  b=bands[side]
  start=Vector((sgn*.32,-19.33,2.01))
  end=Vector((sgn*.205,y-.078,1.808))
  diff=end-start
  b.location=(start+end)/2
  b.rotation_mode='QUATERNION'
  b.rotation_quaternion=diff.to_track_quat('Z','Y')
  b.scale=(.065,.025,diff.length)
  for prop in ("location","rotation_quaternion","scale"):b.keyframe_insert(data_path=prop,frame=f)
# Original projectile seats correctly in the leather pouch until 2 seconds.
flight=[
 (1,-19.57,1.79),(12,-19.68,1.79),(22,-20.16,1.79),
 (35,-20.70,1.79),(43,-20.87,1.79),(48,-20.87,1.79),
 (49,-20.59,1.79),(50,-19.68,1.77),(51,-19.06,1.75),
 (52,-18.53,1.73),(54,-17.67,1.71),(58,-15.93,1.67),
 (62,-14.20,1.63),(70,-10.72,1.55),(78,-7.23,1.48),
 (86,-3.74,1.40),(91,-1.56,1.34),(94,-.61,1.30),
 (95,-.42,1.29),(96,-.31,1.28)]
for f,y,z in flight:put(ball,f,(0,y,z))
def camera(f,xyz,focus,lens):
 cam.location=xyz
 cam.rotation_euler=(Vector(focus)-Vector(xyz)).to_track_quat('-Z','Y').to_euler()
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
 cam.data.lens=lens
 cam.data.keyframe_insert(data_path="lens",frame=f)
# Same composition/movement pattern as the previous aim shot, with shooter moved backward.
camera(1,(.10,-21.75,1.97),(0,-19.55,1.74),35)
camera(12,(.28,-21.92,2.07),(0,-19.64,1.75),37)
camera(21,(.68,-22.17,2.16),(0,-19.92,1.73),41)
camera(35,(.74,-22.22,2.15),(0,-20.17,1.75),45)
camera(48,(.74,-22.22,2.15),(0,-20.17,1.75),45)
camera(49,(.74,-22.22,2.15),(0,-20.17,1.75),45)
camera(52,(.74,-22.22,2.15),(0,-20.17,1.75),45)
# Clean cut to a moving side-follow camera, showing the wall approach with real parallax.
camera(53,(1.40,-20.30,1.93),(0,-18.10,1.72),36)
camera(62,(1.25,-16.30,1.86),(0,-14.20,1.63),33)
camera(72,(1.45,-11.65,1.81),(0,-9.85,1.53),32)
camera(82,(1.70,-7.17,1.75),(0,-5.48,1.43),31)
camera(90,(1.85,-3.53,1.70),(0,-1.98,1.35),32)
camera(96,(1.85,-2.45,1.68),(0,-.31,1.28),36)
# Key frames on camera hold the aim still immediately before release.
def interpolations(obj,frm,to,how):
 if not obj.animation_data:return
 for layer in obj.animation_data.action.layers:
  for strip in layer.strips:
   if strip.type!="KEYFRAME":continue
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for kp in fc.keyframe_points:
      if frm <= kp.co.x <= to:kp.interpolation=how
interpolations(ball,48,96,'LINEAR')
interpolations(cam,53,96,'LINEAR')
interpolations(cam,52,52,'CONSTANT')
sc.frame_set(1)
saved=OUT/f"{kind}_20m_launch.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
print("SAVED_REAL_DISTANCE",kind,"from",-20.87,"to",-0.31,"meters",flush=True)
if mode=="preview":
 for frame in (1,24,40,48,50,53,62,74,86,95):
  sc.frame_set(frame)
  sc.render.filepath=str(OUT/f"{kind}_preview_{frame:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("PREVIEW",kind,frame,flush=True)
elif mode=="full":
 folder=OUT/kind/"launch"
 folder.mkdir(parents=True,exist_ok=True)
 sc.render.filepath=str(folder/"frame_")
 bpy.ops.render.render(animation=True)
 print("LAUNCH_20M_COMPLETE",kind,flush=True)
