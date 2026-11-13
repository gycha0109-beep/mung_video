import bpy,math,random,sys
from pathlib import Path
from mathutils import Vector
random.seed(7727)
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_v7_egg"
OUT.mkdir(exist_ok=True)
SOURCE=ROOT/"three_shots"/"egg"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
MODE=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sc=bpy.context.scene
sc.frame_end=108
sc.rigidbody_world.point_cache.frame_end=108
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720
sc.render.resolution_y=1280
sc.render.resolution_percentage=100 if MODE=="full" else 65
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.render.image_settings.compression=14
sc.render.use_motion_blur=True
sc.render.motion_blur_shutter=.28
WHITE=bpy.data.materials["Wet translucent egg white"]
YOLK=bpy.data.materials["Rich wet egg yolk"]
SHELL=bpy.data.materials["Eggshell porous off-white"]
# The source material is too opaque and resembles a painted white disk.
bs=WHITE.node_tree.nodes.get("Principled BSDF")
if bs:
 bs.inputs["Base Color"].default_value=(.87,.88,.80,1)
 bs.inputs["Roughness"].default_value=.12
 bs.inputs["Transmission Weight"].default_value=.24
 bs.inputs["Alpha"].default_value=.32
 WHITE.surface_render_method="DITHERED"
ys=YOLK.node_tree.nodes.get("Principled BSDF")
if ys:
 ys.inputs["Base Color"].default_value=(.91,.47,.012,1)
 ys.inputs["Roughness"].default_value=.13
 ys.inputs["Coat Weight"].default_value=.42
 ys.inputs["Coat Roughness"].default_value=.07
# Compact surface sheen. This is a keyframed physical-looking illustration, not a fluid solver.
def mesh_object(name,verts,faces,material):
 me=bpy.data.meshes.new(name+" mesh")
 me.from_pydata(verts,[],faces)
 me.update()
 ob=bpy.data.objects.new(name,me)
 bpy.context.collection.objects.link(ob)
 ob.data.materials.append(material)
 for p in me.polygons:p.use_smooth=True
 return ob
def set_transform(ob,fr,loc=None,scale=None,rot=None):
 if loc is not None:
  ob.location=loc;ob.keyframe_insert(data_path="location",frame=fr)
 if scale is not None:
  ob.scale=scale;ob.keyframe_insert(data_path="scale",frame=fr)
 if rot is not None:
  ob.rotation_euler=rot;ob.keyframe_insert(data_path="rotation_euler",frame=fr)
def sphere(name,mat,loc=(0,0,0),size=1):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
 ob=bpy.context.object;ob.name=name
 ob.data.materials.append(mat)
 for p in ob.data.polygons:p.use_smooth=True
 ob.scale=(size,)*3
 return ob
def stream(name,mat,x,z,depth,length,start,end,width,slope):
 # Tapered, irregular wet trail; attached to the original wall splash at the top.
 verts=[];faces=[];nr,ns=24,8
 for j in range(nr):
  t=j/(nr-1)
  xx=slope*t*t +.003*math.sin(5*math.pi*t)
  rr=width*(1-.45*t+.08*math.sin(7*math.pi*t))
  for k in range(ns):
   a=2*math.pi*k/ns
   verts.append((xx+rr*math.cos(a), .004*math.sin(a), -length*t))
 for j in range(nr-1):
  for k in range(ns):
   i=j*ns+k
   faces.append((i,j*ns+(k+1)%ns,(j+1)*ns+(k+1)%ns,(j+1)*ns+k))
 faces.append(tuple(range(ns-1,-1,-1)))
 faces.append(tuple((nr-1)*ns+i for i in range(ns)))
 ob=mesh_object(name,verts,faces,mat)
 for fr,s in [(48,.001),(start-1,.001),(start,.008),(end,1.),(108,1.0)]:
  set_transform(ob,fr,(x,depth,z),(1,1,s))
 return ob
def wet_patch(name,mat,x,y,impact,r_x,r_y,seed=4):
 # Uneven shallow wet footprint, only appears when falling liquid reaches the ground.
 rg=random.Random(seed)
 n=28
 verts=[(0,0,.011)]
 for i in range(n):
  a=2*math.pi*i/n
  wave=.88+.14*math.sin(4*a+seed)+.065*math.sin(7*a+seed*.7)+rg.uniform(-.04,.04)
  verts.append((math.cos(a)*r_x*wave,math.sin(a)*r_y*wave,.011+.002*rg.random()))
 faces=[(0,i+1,(i+1)%n+1) for i in range(n)]
 ob=mesh_object(name,verts,faces,mat)
 for f,scal in [(48,.001),(impact-1,.001),(impact,.09),(impact+3,.48),(impact+10,.93),(108,1.)]:
  set_transform(ob,f,(x,y,0),(scal,scal,1))
 return ob
def ballistic_blob(name,mat,start,x,y,z,r,vx,vy,vz=0.,splash=True):
 ob=sphere(name,mat)
 gravity=9.81
 tt=(vz+math.sqrt(vz*vz+2*gravity*(z-r)))/gravity
 hit=start+math.ceil(tt*24)
 xx=x+vx*tt; yy=y+vy*tt
 for f in range(48,109):
  if f<start:
   # Keep clean start, invisible by scale.
   if f in (48,start-1):set_transform(ob,f,(x,y,z),(.001,.001,.001))
   continue
  t=(f-start)/24
  if f<hit:
   zz=z+vz*t-.5*gravity*t*t
   vel=max(.0,-vz+gravity*t)
   set_transform(ob,f,(x+vx*t,y+vy*t,max(r,zz)),(r*.88,r*.83,r*(1.2+min(.95,vel/7))))
  elif f<=hit+7:
   dt=(f-hit)/7
   set_transform(ob,f,(xx,yy,r*.26), (r*(1+1.7*dt),r*(1+1.5*dt),max(.002,r*(.26-.21*dt))))
  elif f==108:
   set_transform(ob,f,(xx,yy,.011),(r*2.7,r*2.4,.003))
 if splash:
  wet_patch(name+" - deposited liquid",mat,xx,yy,hit,r*3.7,r*3.25,seed=len(name))
  # Small offshoots exist only after the parent hits the ground.
  rg=random.Random(len(name)*431)
  for i in range(5):
   a=2*math.pi*i/5+.2*rg.random()
   scale=r*(.19+.12*rg.random())
   sub=sphere(name+" - splashlet "+str(i),mat)
   radius=scale
   dst=.10+.08*rg.random()
   for fr in [48,hit-1,hit,hit+3,hit+6,hit+9,108]:
    if fr<hit:set_transform(sub,fr,(xx,yy,.015),(.001,.001,.001));continue
    dt=(fr-hit)/24
    px=xx+math.cos(a)*dst*min(1,dt/.29)
    py=yy+math.sin(a)*dst*min(1,dt/.29)
    h=max(.014,.015+1.8*dt-4.9*dt*dt)
    set_transform(sub,fr,(px,py,h),(radius,radius,radius*1.2) if fr<hit+9 else (radius*1.6,radius*1.6,.002))
 print("CHAIN_CONTACT",name,"start",start,"ground",hit,"xy",round(xx,3),round(yy,3),flush=True)
 return hit
# There is a real source splash at f48. All V7 action is anchored to its center.
stream("V7 primary run",YOLK,-.055,1.265,-.219,.39,53,64,.009,.007)
stream("V7 second run",YOLK,.093,1.222,-.220,.36,61,76,.007,-.006)
stream("V7 albumen thin run",WHITE,-.164,1.325,-.218,.30,56,71,.006,.014)
# A pair of visible, causally ordered drops, falling under 9.81 m/s^2.
h1=ballistic_blob("V7 MAIN YOLK FALL",YOLK,64,-.048,-.258,.87,.030,-.19,-.44,-.12)
h2=ballistic_blob("V7 SECOND YOLK FALL",YOLK,76,.086,-.264,.86,.023,.25,-.49,-.1)
# Smaller translucent drip, delayed from the pale part of the splash.
h3=ballistic_blob("V7 ALBUMEN FALL",WHITE,72,-.148,-.25,1.03,.019,-.10,-.37,-.1)
# A connected eggshell segment hangs at the upper-right splash edge, releases and tumbles.
def shell_shard(name,sz):
 verts=[(0,0,.016),(-.85*sz,-.25*sz,-.012),(-.8*sz,.43*sz,-.011),(-.19*sz,.87*sz,0),
        (.81*sz,.59*sz,-.013),(1.01*sz,-.35*sz,-.02),(.19*sz,-.91*sz,-.008)]
 faces=[]
 for j in range(1,7):
  faces.append((0,j,j%6+1))
 ob=mesh_object(name,verts,faces,SHELL)
 # Make double-sided curved flake. More plausible than flat white square triangles.
 solid=ob.modifiers.new("thin shell thickness","SOLIDIFY")
 solid.thickness=.0027
 return ob
sh=shell_shard("V7 primary falling shell",.082)
xs,ys,zs=.20,-.279,1.275
for fr in [48,51,54,57,60,63,66,69,72,78,90,108]:
 if fr<51:
  set_transform(sh,fr,(xs,ys,zs),(.001,)*3,(0,0,0))
 elif fr<=54:
  set_transform(sh,fr,(xs,ys,zs),(1,1,1),(0,.1,.2))
 elif fr<=69:
  t=(fr-54)/24
  z=max(.023,zs-.5*9.81*t*t)
  set_transform(sh,fr,(xs+.11*t,ys-.18*t,z),(1,1,1),(.2+7*t,.1+9*t,.2+5*t))
 else:
  d=(fr-69)/24
  zz=.025+max(0,.14*(1-d/.36)) * abs(math.sin(14*d)) if fr<78 else .023
  set_transform(sh,fr,(xs+.07+d*.10,ys-.12-d*.10,zz),(1,1,1),(4.6+d*2.5,5.7+d*3.,3.3+d*.8))
# Small chips are created at shell-to-floor contact, not inserted randomly throughout the shot.
for j in range(7):
 rg=random.Random(400+j)
 start=69+j%2
 chip=shell_shard("V7 secondary shell chip %02d"%j,.022+rg.random()*.020)
 a=rg.random()*2*math.pi
 sx,sy=.27,-.40
 vx,vy=.32*math.cos(a),.37*math.sin(a)
 for fr in [48,start-1,start,start+3,start+6,start+10,108]:
  if fr<start:
   set_transform(chip,fr,(sx,sy,.02),(.001,)*3,(0,0,0));continue
  t=(fr-start)/24
  z=max(.02,.045+1.0*t-4.9*t*t)
  set_transform(chip,fr,(sx+vx*t,sy+vy*t,z),(1,1,1),(t*9+j,t*7+j*.5,t*13+j))
# Camera observes the first event, then tilts DOWN to the ground collision.
cam=sc.camera
sc.frame_set(48)
p=cam.location.copy();rot=cam.rotation_euler.copy();lens=cam.data.lens
for f in [48,49]:
 cam.location=p;cam.rotation_euler=rot;cam.data.lens=lens
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
 cam.data.keyframe_insert(data_path="lens",frame=f)
def camera(f,pos,target,lens):
 cam.location=pos
 cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat("-Z","Y").to_euler()
 cam.data.lens=lens
 cam.keyframe_insert(data_path="location",frame=f)
 cam.keyframe_insert(data_path="rotation_euler",frame=f)
 cam.data.keyframe_insert(data_path="lens",frame=f)
camera(60,(1.31,-4.07,1.57),(-.02,-.20,1.20),33.5)
camera(74,(1.01,-3.36,1.43),(.01,-.30,.96),34.)
camera(87,(.85,-3.04,1.20),(.04,-.42,.58),34.)
camera(108,(.91,-3.22,1.26),(.01,-.38,.76),33.)
sc.frame_set(1)
asset=OUT/"EGG_V7_CAUSAL_CHAIN.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print("ASSET_SAVED",asset,"IMPACTS",h1,h2,h3,flush=True)
if MODE=="preview":
 sample={49,60,69,77,86,96,108}
 for f in range(1,109):
  sc.frame_set(f)
  if f not in sample:continue
  sc.render.filepath=str(OUT/f"EGG_V7_PREVIEW_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("PREVIEW_FRAME",f,flush=True)
elif MODE=="full":
 directory=OUT/"after_frames"
 directory.mkdir(exist_ok=True)
 for f in range(1,109):
  sc.frame_set(f)
  if f<49:continue
  sc.render.filepath=str(directory/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%10==0 or f==108:print("RENDERED",f,"/ 108",flush=True)
 print("FULL_60_FRAMES_COMPLETE",flush=True)
