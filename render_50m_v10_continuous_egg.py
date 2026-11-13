import bpy,sys,random,math
from pathlib import Path
from mathutils import Vector
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v10_egg"
OUT.mkdir(parents=True,exist_ok=True)
mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
bpy.ops.wm.open_mainfile(filepath=str(R/"cinematic_50m_v9t_egg"/"EGG_50M_V9T_TRACKLOCK.blend"))
sc=bpy.context.scene
sc.frame_start=1;sc.frame_end=192
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720;sc.render.resolution_y=1280
sc.render.resolution_percentage=100 if mode=="full" else 65
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.render.image_settings.compression=15
sc.render.use_motion_blur=False
camera=sc.camera
ball=bpy.data.objects["POLISHED STEEL SHOT"]
# Root cause: 13 leather rings were placed at -9.3m, directly in the flight path,
# instead of being attached to the handle at -49.3m.
wrong=[o for o in list(sc.objects) if o.name.startswith("Wrapped leather handle grip")]
for o in wrong:bpy.data.objects.remove(o,do_unlink=True)
print("REMOVED_WRONG_LEATHER_GRIPS",len(wrong),flush=True)
camera.animation_data_clear()
camera.data.animation_data_clear()
camera.data.dof.use_dof=False
# One single camera follows ball until 5m before the wall, then literally stops
# and keeps its last exact transform. No cut or change of lens.
for f in range(1,193):
 sf=min(f,96)
 sc.frame_set(sf)
 if f<=91 or f==92 or f==192:
  if f<=91:
   y,z=ball.matrix_world.translation.y,ball.matrix_world.translation.z
   loc=Vector((.36,y-2.48,z+.26))
   target=Vector((0,y+.02,z))
  else:
   sc.frame_set(91)
   y,z=ball.matrix_world.translation.y,ball.matrix_world.translation.z
   loc=Vector((.36,y-2.48,z+.26))
   target=Vector((0,y+.02,z))
  camera.location=loc
  camera.rotation_euler=(target-loc).to_track_quat("-Z","Y").to_euler()
  camera.data.lens=37.
  camera.keyframe_insert(data_path="location",frame=f)
  camera.keyframe_insert(data_path="rotation_euler",frame=f)
  camera.data.keyframe_insert(data_path="lens",frame=f)
sc.frame_set(91)
stop_ball_y=ball.matrix_world.translation.y
stop_camera_y=camera.location.y
assert -6.4 < stop_ball_y < -4.4,(stop_ball_y,stop_camera_y)
print("CAMERA_FREEZE",91,"BALL_DISTANCE",round(abs(stop_ball_y),2),"CAMERA_Y",round(stop_camera_y,2),flush=True)
# Hide original intact egg only after wall contact. No new projectile appears.
for f,hidden in [(1,False),(96,False),(97,True),(192,True)]:
 ball.hide_render=hidden
 ball.keyframe_insert(data_path="hide_render",frame=f)
# Keep the same wall, same sky and same lighting for all 192 frames.
# Append ONLY material effects, not walls, floor, sky or cameras.
source=R/"cinematic_50m_v9_egg"/"EGG_50M_V9_FORCEFUL_IMPACT.blend"
with bpy.data.libraries.load(str(source),link=False) as (from_data,to_data):
 names=[n for n in from_data.objects if n.startswith("V9 ORIGINAL IMPACT FORCE")
        or n.startswith("V9 viscous raised center")
        or n.startswith("V9 wet perimeter dispersion")
        or n.startswith("V9 cohesive impact spread")]
 to_data.objects=names
effects=[]
for o in to_data.objects:
 if o is None:continue
 sc.collection.objects.link(o)
 effects.append(o)
 o.hide_render=False
 if o.animation_data and o.animation_data.action:
  # The existing impact was authored at frame 13. It now starts at global frame 97.
  act=o.animation_data.action.copy()
  o.animation_data.action=act
  for layer in act.layers:
   for strip in layer.strips:
    if strip.type!="KEYFRAME":continue
    for bag in strip.channelbags:
     for curve in bag.fcurves:
      for kp in curve.keyframe_points:
       kp.co.x+=84.
       kp.handle_left.x+=84.
       kp.handle_right.x+=84.
      curve.update()
print("SINGLE_SCENE_EGG_SPLASH_EFFECTS",len(effects),flush=True)
# Organic shells: single real wall, geometry appears at first contact and falls,
# without switching the camera or replacing the wall mid-video.
shellmat=bpy.data.materials.get("V10 eggshell cream")
if shellmat is None:
 shellmat=bpy.data.materials.new("V10 eggshell cream")
 shellmat.diffuse_color=(.78,.75,.68,1)
 shellmat.use_nodes=True
 p=shellmat.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(.82,.79,.73,1)
 p.inputs["Roughness"].default_value=.55
rand=random.Random(661)
for j in range(13):
 ang=2*math.pi*j/13+.1
 speed=.8+rand.uniform(-.25,.32)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
 o=bpy.context.object
 o.name="V10 original shell fragments %02d"%j
 o.data.materials.append(shellmat)
 rad=.035+rand.uniform(.005,.016)
 for fr in [1,96,97,99,103,108,118,132,192]:
  dt=max(0,(fr-97)/24)
  x=.10*math.sin(ang)+speed*dt*math.cos(ang)*.5
  y=-.305-.10*dt-speed*dt*math.sin(ang)*.15
  z=max(.045,1.35+(.95+rand.uniform(-.16,.16))*dt-4.905*dt*dt)
  o.location=(x,y,z)
  t=max(.001,1. if fr>=97 else .001)
  o.scale=(rad*t*.7,rad*t*.85,rad*t*.35)
  o.rotation_euler=(j+dt*8,j*.31+dt*7,j*.21+dt*6)
  for prop in ("location","scale","rotation_euler"):
   o.keyframe_insert(data_path=prop,frame=fr)
# Freeze camera mathematically: after 91 every frame must have identical transform.
sc.frame_set(91);p1=camera.matrix_world.copy()
sc.frame_set(192);p2=camera.matrix_world.copy()
assert all(abs(p1[i][j]-p2[i][j])<1e-5 for i in range(4) for j in range(4))
sc.frame_set(1)
asset=OUT/"EGG_V10_SINGLE_SCENE_50M.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print("SINGLE_SCENE_VALIDATED",asset,flush=True)
if mode=="preview":
 for f in [1,48,74,90,91,92,94,96,97,99,102,112,144,192]:
  sc.frame_set(f)
  sc.render.filepath=str(OUT/f"V10_CHECK_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("V10_PREVIEW_FRAME",f,flush=True)
elif mode=="full":
 folder=OUT/"frames"
 folder.mkdir(exist_ok=True)
 for f in range(1,193):
  sc.frame_set(f)
  sc.render.filepath=str(folder/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%24==0:print("V10_FRAME",f,"of 192",flush=True)
