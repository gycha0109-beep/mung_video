import bpy,sys,math
from pathlib import Path
from mathutils import Vector
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v8"
OUT.mkdir(exist_ok=True)
kind=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "egg"
mode=sys.argv[sys.argv.index("--")+2] if "--" in sys.argv and len(sys.argv)>sys.argv.index("--")+2 else "preview"
source=R/"cinematic_v2"/f"{kind}_launch_v2.blend"
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720
s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="full" else 66
s.render.fps=24
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.image_settings.compression=15
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.29
s.frame_start=1
s.frame_end=96
cam=bpy.data.objects["CINEMA CAMERA"]
legend=bpy.data.objects.get("Small lens legend")
if legend and legend.type=="FONT":legend.data.body="50M   /   PULL   /   RELEASE"
ball=bpy.data.objects["POLISHED STEEL SHOT"]
rig=bpy.data.objects["SHOT POUCH / rig"]
bands={side:bpy.data.objects["TENSIONED LATEX / "+side] for side in ("LEFT","RIGHT")}
# 50.56m from f48 y=-50.87 to f96 y=-0.31. Real world units, NO 2D footage stretching.
shift=-40.
for o in s.objects:
 if o.name in ("Carved wooden slingshot handle","Solid oak Y arm LEFT","Solid oak Y arm RIGHT",
               "Forged elastic anchor LEFT","Forged elastic anchor RIGHT",
               "Brushed elastic cap LEFT","Brushed elastic cap RIGHT","Side metallic specular highlight"):
  o.location.y+=shift
floor=bpy.data.objects.get("Concrete walkway")
if floor:
 floor.location.y=-26.
 floor.dimensions.y=112.
# Physical walkway seams every 5m make spatial motion visible; avoid fake speed-line overlays.
mat=bpy.data.materials.new("V8 road expansion joints natural concrete")
mat.diffuse_color=(.18,.195,.20,1)
mat.use_nodes=True
bs=mat.node_tree.nodes.get("Principled BSDF")
if bs:bs.inputs["Base Color"].default_value=(.18,.185,.19,1);bs.inputs["Roughness"].default_value=.89
for yy in range(-45,0,5):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,yy,.007))
 o=bpy.context.object;o.name=f"V8 pavement seam at {yy}m"
 o.dimensions=(7.1,.034,.011)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat)
# Clear material design: preserve source silhouette; enhance how it reads during high speed.
materials=[m for m in ball.data.materials if m and m.use_nodes]
for m in materials:
 p=m.node_tree.nodes.get("Principled BSDF")
 if not p:continue
 if kind=="egg":
  p.inputs["Base Color"].default_value=(.89,.855,.75,1)
  p.inputs["Roughness"].default_value=.18
  p.inputs["Coat Weight"].default_value=.28
  p.inputs["Coat Roughness"].default_value=.13
 elif kind=="steel":
  p.inputs["Metallic"].default_value=.95
  p.inputs["Roughness"].default_value=.115
  p.inputs["Coat Weight"].default_value=.26
  p.inputs["Coat Roughness"].default_value=.07
 elif kind=="billiard":
  p.inputs["Roughness"].default_value=.12
  p.inputs["Coat Weight"].default_value=.71
  p.inputs["Coat Roughness"].default_value=.055
# Wide photo-style specular light, strongest on the nearer half of flight.
ld=bpy.data.lights.new("V8 corridor softbox",type="AREA")
ld.energy=1100
ld.shape="RECTANGLE"
ld.size=12
ld.size_y=23
ob=bpy.data.objects.new("V8 corridor softbox",ld)
bpy.context.collection.objects.link(ob)
ob.location=(5,-26,9)
ob.rotation_euler=(Vector((0,-22,1.3))-ob.location).to_track_quat("-Z","Y").to_euler()
for obj in (cam,ball,rig,*bands.values()):obj.animation_data_clear()
cam.data.animation_data_clear()
def put(ob,f,loc):
 ob.location=loc;ob.keyframe_insert(data_path="location",frame=f)
# Pouch stays at the actual slingshot, and elastic endpoints use the same shifted anchor.
draw=[(1,-49.57),(12,-49.68),(22,-50.16),(35,-50.70),
      (43,-50.87),(48,-50.87),(49,-50.59),(50,-50.08),
      (51,-49.57),(52,-49.43),(54,-49.58),(60,-49.55),(96,-49.55)]
for f,y in draw:
 put(rig,f,(0,y,1.79))
 for side,sign in (("LEFT",-1),("RIGHT",1)):
  b=bands[side]
  a=Vector((sign*.32,-49.33,2.01))
  e=Vector((sign*.205,y-.078,1.808))
  diff=e-a
  b.location=(a+e)/2
  b.rotation_mode="QUATERNION"
  b.rotation_quaternion=diff.to_track_quat("Z","Y")
  b.scale=(.065,.025,diff.length)
  for prop in ("location","rotation_quaternion","scale"):
   b.keyframe_insert(data_path=prop,frame=f)
def projectile(f):
 if f<=48:
  keys=[(1,-49.57,1.79),(12,-49.68,1.79),(22,-50.16,1.79),(35,-50.70,1.79),(43,-50.87,1.79),(48,-50.87,1.79)]
  for a,b in zip(keys,keys[1:]):
   if a[0]<=f<=b[0]:
    q=(f-a[0])/(b[0]-a[0])
    return (a[1]*(1-q)+b[1]*q,a[2]*(1-q)+b[2]*q)
 if f==49:return (-50.59,1.79)
 if f>=96:return (-.31,1.28)
 # Cover the full 50m over 1.96s; short acceleration burst then consistent velocity.
 t=(f-49)/47
 progress=t**1.10
 yy=-50.59+50.28*progress
 zz=1.79-.51*progress
 return yy,zz
for f in range(1,97):
 yy,zz=projectile(f)
 put(ball,f,(0,yy,zz))
 # rolling mark on 8ball for visibly rotating graphic; egg minimal tumble, steel stable glint.
 if kind=="billiard":
  ball.rotation_euler=(f-49)*.065 if f>=49 else 0,0,(f-49)*.018 if f>=49 else 0
 elif kind=="egg":
  ball.rotation_euler=(f-49)*.004 if f>=49 else 0,0,(f-49)*.004 if f>=49 else 0
 elif kind=="steel":
  ball.rotation_euler=(0,0,(f-49)*.055 if f>=49 else 0)
 ball.keyframe_insert(data_path="rotation_euler",frame=f)
def camera(f,loc,target,lens):
 cam.location=loc
 cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
 cam.data.lens=lens
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
 cam.data.keyframe_insert(data_path="lens",frame=f)
# Stage 1: identical-size slingshot shot with 50m geometry behind, clear launch.
camera(1,(.10,-51.75,1.97),(0,-49.55,1.74),35)
camera(12,(.28,-51.92,2.07),(0,-49.64,1.75),37)
camera(21,(.68,-52.17,2.16),(0,-49.92,1.73),41)
camera(35,(.74,-52.22,2.15),(0,-50.17,1.75),45)
for f in [48,49,50,51,52]:
 camera(f,(.74,-52.22,2.15),(0,-50.17,1.75),45)
# Stage 2a: slower than projectile chase. Ball overtakes and shrinks as wall rushes closer.
for f in range(53,71):
 t=(f-53)/17
 y=-51.3+9.0*t
 focus_y,focus_z=projectile(f)
 # Don't attach camera at a constant interval behind the ball.
 camera(f,(1.07+0.18*t,y,2.05-.16*t),
        (0,focus_y+.12,focus_z-.12),36+2*t)
# Stage 2b: FIXED near the wall. Projectile approaches, rapidly grows and sweeps past the camera.
# No physically impossible chasing: only lens direction rotates as real object passes.
static_pos=Vector((2.85,-6.45,1.91))
for f in range(71,97):
 yy,zz=projectile(f)
 aim_y=yy+.12
 camera(f,static_pos,(0,aim_y,zz-.03),43)
# Set hard camera cuts only at intended shot transitions, smooth true motion otherwise.
for ob in [cam,ball,rig,*bands.values()]:
 if not ob.animation_data:continue
 for layer in ob.animation_data.action.layers:
  for strip in layer.strips:
   if strip.type!="KEYFRAME":continue
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:
      if ob==cam and key.co.x in (52,70):key.interpolation="CONSTANT"
      elif key.co.x>=49:key.interpolation="LINEAR"
# 50.56 meters: explicit validation, frames cannot snap back to 20m.
s.frame_set(48)
p1=ball.matrix_world.translation.copy()
s.frame_set(96)
p2=ball.matrix_world.translation.copy()
distance=(p2-p1).length
assert 50.4<=distance<=50.8,("WRONG_FLIGHT_DISTANCE",distance)
print("50M_REAL_DISTANCE",kind,round(distance,3),"units",flush=True)
s.frame_set(1)
sav=OUT/f"{kind}_50M_V8_LAUNCH.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(sav))
print("SCENE_SAVED",sav,flush=True)
if mode=="preview":
 frames=[1,24,48,53,58,64,70,71,78,86,92,95]
 for f in frames:
  s.frame_set(f)
  s.render.filepath=str(OUT/f"{kind}_PREVIEW_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("PREVIEW",kind,f,flush=True)
elif mode=="full":
 folder=OUT/kind/"launch"
 folder.mkdir(parents=True,exist_ok=True)
 for f in range(1,97):
  s.frame_set(f)
  s.render.filepath=str(folder/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%12==0:print("LAUNCH_RENDER",kind,f,flush=True)
