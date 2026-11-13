import bpy,math,random,sys
from pathlib import Path
from mathutils import Vector
random.seed(915)
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v9_egg"
OUT.mkdir(parents=True,exist_ok=True)
src=R/"cinematic_50m_v8"/"egg_50M_V8_LAUNCH.blend"
mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
bpy.ops.wm.open_mainfile(filepath=str(src))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720
sc.render.resolution_y=1280
sc.render.resolution_percentage=100 if mode=="full" else 65
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.render.image_settings.compression=14
sc.render.fps=24
sc.render.use_motion_blur=True
sc.render.motion_blur_shutter=.37
cam=bpy.data.objects["CINEMA CAMERA"]
ball=bpy.data.objects["POLISHED STEEL SHOT"]
rig=bpy.data.objects["SHOT POUCH / rig"]
bands={side:bpy.data.objects["TENSIONED LATEX / "+side] for side in ("LEFT","RIGHT")}
for textname in ("Small lens legend","Top score in lens"):
 o=bpy.data.objects.get(textname)
 if o:o.hide_render=True
# Visually grounded roughness for the projectile, rather than a plain white plastic surface.
mat=ball.data.materials[0]
bs=mat.node_tree.nodes.get("Principled BSDF")
if bs:
 bs.inputs["Base Color"].default_value=(.87,.825,.715,1.)
 bs.inputs["Metallic"].default_value=0.
 bs.inputs["Roughness"].default_value=.21
 bs.inputs["Coat Weight"].default_value=.36
 bs.inputs["Coat Roughness"].default_value=.115
 bs.inputs["Subsurface Weight"].default_value=.045
 nodes=mat.node_tree.nodes
 tex=nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=72.
 tex.inputs["Detail"].default_value=2.0;tex.inputs["Roughness"].default_value=.7
 bump=nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.045
 bump.inputs["Distance"].default_value=.008
 mat.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
 mat.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
# Existing concrete is flat. Subtle micro-roughness catches grazing highlights.
floor=bpy.data.objects.get("Concrete walkway")
if floor:
 for m in floor.data.materials:
  if not m or not m.use_nodes:continue
  bs=m.node_tree.nodes.get("Principled BSDF")
  if not bs:continue
  tx=m.node_tree.nodes.new("ShaderNodeTexNoise")
  tx.inputs["Scale"].default_value=185
  tx.inputs["Detail"].default_value=2.4
  bump=m.node_tree.nodes.new("ShaderNodeBump")
  bump.inputs["Strength"].default_value=.17
  bump.inputs["Distance"].default_value=.012
  m.node_tree.links.new(tx.outputs["Fac"],bump.inputs["Height"])
  m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
# Preserve stonework while slightly increasing surface relief, not more particles.
for m in bpy.data.materials:
 if not m or not m.use_nodes:continue
 if "brick" not in m.name.lower():continue
 bs=m.node_tree.nodes.get("Principled BSDF")
 if not bs:continue
 tx=m.node_tree.nodes.new("ShaderNodeTexNoise")
 tx.inputs["Scale"].default_value=92
 tx.inputs["Detail"].default_value=3.0
 bump=m.node_tree.nodes.new("ShaderNodeBump")
 bump.inputs["Strength"].default_value=.21
 bump.inputs["Distance"].default_value=.014
 m.node_tree.links.new(tx.outputs["Fac"],bump.inputs["Height"])
 m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
# Small static roadside grit creates grounded optical motion parallax.
stone=bpy.data.materials.new("V9 scattered exposed aggregate")
stone.diffuse_color=(.22,.225,.215,1)
stone.use_nodes=True
st=stone.node_tree.nodes.get("Principled BSDF")
st.inputs["Base Color"].default_value=(.22,.23,.22,1)
st.inputs["Roughness"].default_value=.89
for i in range(145):
 y=random.uniform(-47,-.8)
 x=random.uniform(-3.0,3.0)
 rad=random.uniform(.014,.043)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rad,location=(x,y,.014))
 o=bpy.context.object
 o.name="V9 realistic floor aggregate %03d"%i
 o.scale=(1.3,.65,.22)
 o.rotation_euler=(random.random(),random.random(),random.random()*math.pi)
 o.data.materials.append(stone)
# Strongly directional grazing edge light for the near flight.
ld=bpy.data.lights.new("V9 projectile edge separation","AREA")
ld.energy=780
ld.shape="RECTANGLE";ld.size=7;ld.size_y=14
light=bpy.data.objects.new("V9 projectile edge separation",ld)
bpy.context.collection.objects.link(light)
light.location=(-3,-25,5)
light.rotation_euler=(Vector((0,-23,1.6))-light.location).to_track_quat("-Z","Y").to_euler()
# Real 50m flight and a sharp elastic recoil, not camera-screen VFX.
for ob in (ball,rig,cam,*bands.values()):ob.animation_data_clear()
cam.data.animation_data_clear()
def put(ob,frame,pos):
 ob.location=pos;ob.keyframe_insert(data_path="location",frame=frame)
draw=[(1,-49.57),(12,-49.68),(22,-50.16),(35,-50.70),(43,-50.87),(48,-50.87),
      (49,-49.93),(50,-49.06),(51,-49.35),(52,-49.50),(54,-49.59),(57,-49.56),(96,-49.56)]
for f,y in draw:
 put(rig,f,(0,y,1.79))
 for side,sign in (("LEFT",-1),("RIGHT",1)):
  b=bands[side]
  anchor=Vector((sign*.32,-49.33,2.01))
  endpoint=Vector((sign*.205,y-.078,1.808))
  v=endpoint-anchor
  b.location=(anchor+endpoint)*.5
  b.rotation_mode="QUATERNION"
  b.rotation_quaternion=v.to_track_quat("Z","Y")
  b.scale=(.065,.025,v.length)
  for prop in ("location","rotation_quaternion","scale"):b.keyframe_insert(data_path=prop,frame=f)
# Acceleration from f48 onward, terminal +y approach to brick wall.
pkey=[(1,-49.57,1.79),(12,-49.68,1.79),(22,-50.16,1.79),(35,-50.70,1.79),
 (43,-50.87,1.79),(48,-50.87,1.79),(49,-49.93,1.786),(50,-48.60,1.772),
 (51,-47.30,1.764),(52,-46.0,1.751)]
for f in range(53,97):
 q=(f-52)/44
 pkey.append((f,-46.+45.69*q,1.751-(1.751-1.28)*q))
for f,y,z in pkey:
 put(ball,f,(0,y,z))
 ball.rotation_euler=(.012*max(0,f-49),.005*max(0,f-49),.002*max(0,f-49))
 ball.keyframe_insert(data_path="rotation_euler",frame=f)
def ball_at(f):
 for ff,y,z in pkey:
  if ff==f:return y,z
 return -.31,1.28
def cam_pose(f,location,target,lens):
 cam.location=location
 cam.rotation_euler=(Vector(target)-Vector(location)).to_track_quat("-Z","Y").to_euler()
 cam.data.lens=lens
 cam.keyframe_insert("location",frame=f)
 cam.keyframe_insert("rotation_euler",frame=f)
 cam.data.keyframe_insert(data_path="lens",frame=f)
# Shot 1: high-tension over-shoulder aim, visible snap.
for f,xyz,tgt,lens in [
 (1,(.1,-51.75,1.97),(0,-49.55,1.74),35),
 (12,(.28,-51.92,2.07),(0,-49.64,1.75),37),
 (21,(.68,-52.17,2.16),(0,-49.92,1.73),41),
 (35,(.74,-52.22,2.15),(0,-50.17,1.75),45),
 (48,(.74,-52.22,2.15),(0,-50.17,1.75),45),
 (49,(.74,-52.22,2.15),(0,-50.17,1.75),45),
 (52,(.72,-52.20,2.12),(0,-49.6,1.73),43),
 (58,(.46,-51.70,1.91),(0,-42.0,1.67),32)]:
 cam_pose(f,xyz,tgt,lens)
# Shot 2: flight tracking camera moves in world space, deliberately slower than the ball at the end.
for f in range(59,86):
 y,z=ball_at(f)
 t=(f-59)/26.
 trail=2.3+9.8*t*t
 cameray=y-trail
 location=(1.25+.15*t,cameray,1.87-.20*t)
 cam_pose(f,location,(0,y+1.4,z-.05),32+5*t)
# Shot 3: target-side viewpoint; the ball crosses the last meters into the wall.
for f in range(86,97):
 y,z=ball_at(f)
 location=(2.70,-9.60,1.74)
 # Camera position fixed; its pan tracks the projectile without optical zoom.
 cam_pose(f,location,(0,y+.15,z-.03),42)
# Use deliberate direct cut between shot 1/2 and shot 2/3.
# Preserve linear world-space trajectory.
for o in [ball,cam,rig,*bands.values()]:
 if not o.animation_data:continue
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   if strip.type!="KEYFRAME":continue
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for kp in curve.keyframe_points:
      if o==cam and kp.co.x in (58,85):kp.interpolation="CONSTANT"
      elif kp.co.x>=48:kp.interpolation="LINEAR"
sc.frame_set(48);start=ball.matrix_world.translation.copy()
sc.frame_set(96);end=ball.matrix_world.translation.copy()
d=(end-start).length
assert 50.4<d<50.8,d
print("V9_50M_ACTUAL_DISTANCE",round(d,3),flush=True)
sc.frame_set(1)
asset=OUT/"EGG_50M_V9_SPEED_AND_SURFACE.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print("V9_ASSET_READY",asset,flush=True)
if mode=="preview":
 frames=[43,48,49,50,51,52,56,60,66,74,82,85,86,90,94,96]
 for f in range(1,97):
  sc.frame_set(f)
  if f not in frames:continue
  sc.render.filepath=str(OUT/f"V9_EGG_LAUNCH_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("V9_LAUNCH_PREVIEW",f,flush=True)
elif mode=="full":
 frame_dir=OUT/"launch_frames"
 frame_dir.mkdir(exist_ok=True)
 for f in range(1,97):
  sc.frame_set(f)
  sc.render.filepath=str(frame_dir/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%12==0:print("V9_LAUNCH_FULL",f,flush=True)
