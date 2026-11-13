import bpy,math,random,sys
from pathlib import Path
from mathutils import Vector
random.seed(6217)
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_v6_egg"
OUT.mkdir(exist_ok=True)
SOURCE=ROOT/"three_shots"/"egg"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene
s.frame_end=108
s.rigidbody_world.point_cache.frame_end=108
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720
s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="full" else 65
s.render.fps=24
s.render.image_settings.color_mode="RGB"
s.render.image_settings.file_format="PNG"
s.render.image_settings.compression=15
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.31
# Preserve all original splat geometry/material and physics keyframes. New droplets appear after source frame 48.
yolk=bpy.data.materials.get("Rich wet egg yolk")
white=bpy.data.materials.get("Wet translucent egg white")
shell=bpy.data.materials.get("Eggshell porous off-white")
if not yolk or not white or not shell:
 raise RuntimeError("MISSING SOURCE MATERIALS")
# Blender EEVEE otherwise renders the original highly transmissive albumen as an opaque grey stain.
# Match the original Cycles footage with a pale, translucent wet material.
wbs=white.node_tree.nodes.get("Principled BSDF")
if wbs:
 wbs.inputs["Transmission Weight"].default_value=.06
 wbs.inputs["Alpha"].default_value=.54
 wbs.inputs["Base Color"].default_value=(.78,.80,.75,1)
 wbs.inputs["Roughness"].default_value=.18
 white.surface_render_method='DITHERED'
def key_pos(ob,f,p,scale=None):
 ob.location=p
 ob.keyframe_insert(data_path="location",frame=f)
 if scale is not None:
  ob.scale=scale
  ob.keyframe_insert(data_path="scale",frame=f)

def new_rivulet(name,x,z,material,radius,start,finish,length,curve=0.):
 # A ribbon of variable cross section laid on the brick surface. Local z=0 at top, local -z grows downward.
 verts=[]
 rings=16;side=10
 for j in range(rings):
  t=j/(rings-1)
  w=radius*(.80+.22*math.sin(3*math.pi*t)+.45*t**5)
  if j==rings-1:w*=.36
  for i in range(side):
   ang=2*math.pi*i/side
   verts.append((curve*t*t+w*math.cos(ang),
                 .008*math.sin(ang),
                 -t))
 faces=[]
 for j in range(rings-1):
  for i in range(side):
   a=j*side+i
   b=j*side+(i+1)%side
   faces.append((a,b,b+side,a+side))
 faces.append(tuple(reversed(tuple(range(side)))))
 faces.append(tuple((rings-1)*side+i for i in range(side)))
 mesh=bpy.data.meshes.new(name+" mesh")
 mesh.from_pydata(verts,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh)
 bpy.context.collection.objects.link(ob)
 ob.data.materials.append(material)
 for poly in mesh.polygons:poly.use_smooth=True
 key_pos(ob,start-1,(x,-.217,z),(1,1,.001))
 key_pos(ob,start,(x,-.217,z),(1,1,.004))
 key_pos(ob,finish,(x,-.217,z),(1,1,length))
 key_pos(ob,108,(x,-.217,z),(1,1,length+.013))
 return ob
def ellipsoid(name,material,loc,scale,frame):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
 ob=bpy.context.object;ob.name=name
 ob.data.materials.append(material)
 for poly in ob.data.polygons:poly.use_smooth=True
 key_pos(ob,frame,loc,scale)
 return ob
# 5 clearly growing trails: 3 yolk, 2 transparent albumen. No image-only scale/zoom trick.
trails=[
 (-.147,1.235,.015,53,90,.45,-.018,yolk),
 (-.048,1.205,.021,56,97,.58,.010,yolk),
 (.090,1.243,.014,61,105,.38,-.009,yolk),
 (.174,1.258,.012,64,102,.32,-.017,white),
 (-.192,1.290,.010,59,98,.26,.011,white)]
for i,(x,z,radius,start,finish,length,slant,mat) in enumerate(trails):
 new_rivulet("V6 DRIP / "+str(i),x,z,mat,radius,start,finish,length,slant)
 # Growing wet droplet at the tip, attached to the liquid trail until it falls.
 d=ellipsoid("V6 DRIP TIP / "+str(i),mat,(x,-.226,z),(.012,.018,.022),start)
 for f,fac in ((start-1,.001),(start,.20),(finish,1)):
  dropz=z-length*((f-start)/max(1,finish-start)) if f>=start else z
  dx=slant*((f-start)/max(1,finish-start))**2 if f>=start else 0
  key_pos(d,f,(x+dx,-.226,dropz),
   (radius*.9,radius*.75,radius*(1.4+.4*fac)) if f>=start else (.001,.001,.001))
 key_pos(d,108,(x+slant,-.226,z-length-.013),(radius*.82,radius*.76,radius*1.25))
# Puddle builds from falling egg liquid at base of wall; stays physically still as drop flow tails off.
p=ellipsoid("V6 BASE PUDDLE",yolk,(-.025,-.48,.011),(.001,.001,.003),48)
for f,size in [(48,.001),(60,.042),(75,.14),(91,.245),(108,.30)]:
 key_pos(p,f,(-.025,-.48,.012),(.30*size,.58*size,.013 if size>.02 else .002))
pw=ellipsoid("V6 EGG WHITE PUDDLE",white,(.13,-.52,.008),(.001,.001,.001),52)
for f,size in [(48,.001),(52,.015),(77,.11),(108,.21)]:
 key_pos(pw,f,(.13,-.52,.009),(.23*size,.62*size,.007 if size>.03 else .001))
# More independent droplets fall from the burst, with gravitational acceleration then two small bounces.
for k in range(12):
 t0=51+k*3
 if t0>85:break
 cx=random.uniform(-.21,.20);cy=-random.uniform(.25,.57)
 z0=random.uniform(.78,1.43)
 r=random.uniform(.008,.019)
 mat=yolk if k%3!=0 else white
 b=ellipsoid("V6 DETACHED DROP / %02d"%k,mat,(cx,cy,z0),(.001,.001,.001),t0-1)
 for fr in range(t0,109,3):
  dt=(fr-t0)/24.
  z=z0-.5*8.4*dt*dt
  if z<.028:
   # tiny secondary wobble after contact, no repeated freeze
   z=.028+.035*math.exp(-5*(dt-.40))*abs(math.sin(13*(dt-.40))) if dt<.70 else .028
  xx=cx+.09*dt +.035*math.sin(dt*6+k)
  key_pos(b,fr,(xx,cy-.16*dt,z),(.8*r,.8*r,1.4*r) if fr>=t0 else (.001,.001,.001))
 # cleanup/small drops settle; no discontinuity
# Shell flakes retain original material, scatter with ballistic keyframes. Distinct motion through ~6 sec.
for k in range(9):
 t0=51+6*k
 x0=random.uniform(-.22,.22);y0=-random.uniform(.34,.65);z0=random.uniform(.7,1.27)
 mesh=bpy.data.meshes.new("V6 SHELL FLAKE geo")
 size=random.uniform(.025,.055)
 mesh.from_pydata([(-size,-.005,0),(size*.8,0,.012),(.002,.008,size*.9)],[],[(0,1,2)])
 mesh.update()
 obj=bpy.data.objects.new("V6 SHELL FLAKE %02d"%k,mesh)
 bpy.context.collection.objects.link(obj)
 obj.data.materials.append(shell)
 for frame in range(t0-1,109,4):
  dt=max(0,(frame-t0)/24.)
  z=max(.025,z0-4.9*dt*dt)
  if z==.025 and dt<.65:z+=.045*abs(math.sin(dt*16))
  key_pos(obj,frame,(x0+.22*dt,y0-.20*dt,z),
           (.001,)*3 if frame<t0 else (1,1,1))
  obj.rotation_euler=(dt*5.3,dt*4.7,dt*3.1)
  obj.keyframe_insert(data_path="rotation_euler",frame=frame)
# Camera dolly from the ACTUAL previous shot camera at source frame 48; focuses on the running yolk.
cam=s.camera
s.frame_set(48)
source_pos=cam.location.copy()
source_rot=cam.rotation_euler.copy()
source_lens=cam.data.lens
# Keep original camera position until frame 49 to avoid a location jump.
for fr in (48,49):
 cam.location=source_pos;cam.rotation_euler=source_rot;cam.data.lens=source_lens
 for prop in ("location","rotation_euler"):cam.keyframe_insert(prop,frame=fr)
 cam.data.keyframe_insert(data_path="lens",frame=fr)
def point_cam(f,loc,target,lens):
 cam.location=loc
 cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
 cam.data.lens=lens
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
 cam.data.keyframe_insert(data_path="lens",frame=f)
point_cam(65,(1.4,-4.1,1.61),(0,-.18,1.16),33)
point_cam(84,(1.03,-3.15,1.57),(-.03,-.18,1.08),36)
point_cam(108,(.65,-2.35,1.47),(-.045,-.18,.95),38)
# Save asset: the original *.blend remains untouched.
s.frame_set(1)
save=OUT/"EGG_V6_ANIMATED_AFTERIMPACT.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(save))
print("ASSET_SAVED",save,flush=True)
# The existing shell fragments are simulated in Bullet: warm the whole timeline sequentially.
# Jumping straight to frame 48 or a partial animation render leaves eggshell segments stacked at impact.
if mode=="preview":
 samples={48,49,60,75,90,108}
 for f in range(1,109):
  s.frame_set(f)
  if f not in samples:continue
  s.render.filepath=str(OUT/f"EGG_V6_PREVIEW_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("PREVIEW_FRAME",f,flush=True)
elif mode=="full":
 folder=OUT/"after_frames"
 folder.mkdir(exist_ok=True)
 for f in range(1,109):
  s.frame_set(f)
  if f<49:continue
  s.render.filepath=str(folder/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%10==0 or f==108:print("AFTERMATH_RENDER",f,"/",108,flush=True)
 print("AFTERMATH_60FRAMES_RENDERED",flush=True)
