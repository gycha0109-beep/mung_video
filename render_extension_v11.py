import bpy,math,random,sys
from pathlib import Path
from mathutils import Vector
R=Path.home()/"Downloads"/"slingshot_quality_proof"
kind=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "steel"
mode=sys.argv[sys.argv.index("--")+2] if "--" in sys.argv and len(sys.argv)>sys.argv.index("--")+2 else "preview"
assert kind in ("steel","billiard","watermelon","cannon"),kind
OUT=R/"cinematic_50m_v11_extension"/kind
OUT.mkdir(parents=True,exist_ok=True)
random.seed(1027+len(kind))
bpy.ops.wm.open_mainfile(filepath=str(R/"cinematic_50m_v10_egg"/"EGG_V10_SINGLE_SCENE_50M.blend"))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE";s.render.resolution_x=720;s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="full" else 65
s.render.image_settings.file_format="PNG";s.render.image_settings.color_mode="RGB";s.render.image_settings.compression=14
s.render.use_motion_blur=False;s.frame_start=1;s.frame_end=192;s.render.fps=24
camera=s.camera
source=bpy.data.objects["POLISHED STEEL SHOT"]
# V10 egg effects never appear in the other material shots.
for o in list(s.objects):
 if (o.name.startswith("V9 ") or o.name.startswith("V10 original shell fragments")
     or o.name.startswith("Clay splinter") or o.name.startswith("Microscopic brick powder")):
  bpy.data.objects.remove(o,do_unlink=True)
# V10 previously keyed some original wall bricks to disappear for the egg.
# All materials must begin with an intact wall; only material-specific damage is allowed.
for o in s.objects:
 if o.name.startswith("Hand-laid worn masonry"):
  o.animation_data_clear()
  o.hide_render=False
# Position reference from the exact V10 50m tracked flight.
pkeys={}
for f in range(1,97):
 s.frame_set(f)
 loc=source.matrix_world.translation.copy()
 pkeys[f]=Vector(loc)
source_name=source.name
bpy.data.objects.remove(source,do_unlink=True)
# Build or retrieve the projectile from the *actual* prior Blender asset.
if kind in ("steel","billiard"):
 src=R/"cinematic_50m_v8"/f"{kind}_50M_V8_LAUNCH.blend"
 with bpy.data.libraries.load(str(src),link=False) as (a,b):
  names=["POLISHED STEEL SHOT"]
  if kind=="billiard":names+=["8 ball white medallion","White circle black eight"]
  b.objects=[n for n in names if n in a.objects]
 parts={o.name:o for o in b.objects if o}
 for o in parts.values():
  if o.name not in s.objects:s.collection.objects.link(o)
 projectile=parts["POLISHED STEEL SHOT"]
 projectile.name="V11 "+kind.upper()+" projectile"
 projectile.animation_data_clear()
 projectile.hide_render=False
 projectile.scale=(1,1,1)
 if kind=="billiard":
  for n in ("8 ball white medallion","White circle black eight"):
   if n in parts:
    ob=parts[n]
    ob.hide_render=False
    ob.animation_data_clear()
    ob.parent=projectile
else:
 # Watermelon or cannonball 3D sphere; no egg geometry reuse.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,radius=1)
 projectile=bpy.context.object
 projectile.name="V11 "+kind.upper()+" projectile"
 if kind=="watermelon":
  projectile.scale=(.20,.20,.20)
  m=bpy.data.materials.new("V11 deep green watermelon stripes")
  m.use_nodes=True
  nodes=m.node_tree.nodes
  p=nodes.get("Principled BSDF")
  p.inputs["Roughness"].default_value=.27
  p.inputs["Coat Weight"].default_value=.5
  tex=nodes.new("ShaderNodeTexWave");tex.wave_type="BANDS";tex.bands_direction="X";tex.inputs["Scale"].default_value=8
  tex.inputs["Distortion"].default_value=.65;tex.inputs["Detail"].default_value=2
  col=nodes.new("ShaderNodeValToRGB")
  col.color_ramp.elements[0].position=.32
  col.color_ramp.elements[0].color=(.008,.055,.018,1)
  col.color_ramp.elements[1].position=.68
  col.color_ramp.elements[1].color=(.095,.24,.052,1)
  m.node_tree.links.new(tex.outputs["Color"],col.inputs["Fac"])
  m.node_tree.links.new(col.outputs["Color"],p.inputs["Base Color"])
  projectile.data.materials.append(m)
 else:
  projectile.scale=(.23,.23,.23)
  m=bpy.data.materials.new("V11 cannonball forged iron")
  m.use_nodes=True
  p=m.node_tree.nodes.get("Principled BSDF")
  p.inputs["Metallic"].default_value=.85;p.inputs["Roughness"].default_value=.39
  p.inputs["Base Color"].default_value=(.085,.091,.093,1)
  projectile.data.materials.append(m)
 for face in projectile.data.polygons:face.use_smooth=True
def keypose(o,f,loc,rotation=None,scale=None):
 o.location=loc;o.keyframe_insert(data_path="location",frame=f)
 if rotation is not None:
  o.rotation_euler=rotation;o.keyframe_insert(data_path="rotation_euler",frame=f)
 if scale is not None:
  o.scale=scale;o.keyframe_insert(data_path="scale",frame=f)
# The imported 8-ball graphic has the original parent relationship and is never hidden.
for f in range(1,193):
 if f<=96:
  pos=pkeys[f].copy()
 elif kind in ("steel","cannon"):
  t=(f-96)/24.
  pos=Vector((.018*t,-.31+13*t,1.28-.50*t-.4*t*t))
 elif kind=="billiard":
  t=(f-96)/24.
  # rebound backward from the wall, then settles on the floor.
  pos=Vector((.11*t,-.31-3.9*t, max(.16,1.28+1.3*t-4.905*t*t)))
 else:
  pos=Vector((0,-.31,1.28))
 keypose(projectile,f,pos)
 if kind=="billiard":
  projectile.rotation_euler=((max(0,f-48))*.085,0,(max(0,f-48))*.024)
  projectile.keyframe_insert(data_path="rotation_euler",frame=f)
# A real (not clipped) single-scene object may only switch visibility at actual impact.
if kind=="watermelon":
 for f,hide in [(1,False),(96,False),(97,True),(192,True)]:
  projectile.hide_render=hide;projectile.keyframe_insert(data_path="hide_render",frame=f)
# Steel and cannon: displace real bricks from the *same* wall when projectile hits.
def brick_damage(energy):
 candidates=[]
 for b in list(s.objects):
  if not b.name.startswith("Hand-laid worn masonry"):continue
  v=b.location
  rr=math.hypot(v.x,(v.z-1.33)*1.04)
  if rr<.56*energy:candidates.append((rr,b))
 candidates.sort(key=lambda x:x[0])
 print("V11_BRICKS_HIT",kind,len(candidates),flush=True)
 for j,(_,b) in enumerate(candidates):
  for f,hide in [(1,False),(96,False),(97,True),(192,True)]:
   b.hide_render=hide;b.keyframe_insert(data_path="hide_render",frame=f)
  clone=b.copy();clone.data=b.data.copy();clone.name="V11 falling original masonry %02d"%j
  s.collection.objects.link(clone)
  clone.animation_data_clear()
  clone.hide_render=False
  orig=b.location.copy()
  phase=(j*2.399)+random.uniform(-.16,.16)
  speed=(1.4+random.random()*1.9)*energy
  for f in (1,96,97,99,103,109,120,144,192):
   t=max(0,(f-97)/24)
   if f<97:scale=(.001,)*3
   else:scale=(1,1,1)
   x=orig.x+math.sin(phase)*speed*t*.8
   y=orig.y-speed*t*.7-.06*t
   z=max(.115,orig.z+(1.0+.09*math.sin(j*2.1))*t-4.905*t*t)
   keypose(clone,f,(x,y,z),(t*3.3,0,t*5),scale)
# Wall is one structure; no external collision scene splice.
if kind in ("steel","cannon"):brick_damage(1.0 if kind=="steel" else 1.55)
# Billiard: visible point impact and ricochet, no wall demolition.
if kind=="billiard":
 m=bpy.data.materials.new("V11 black ball wall scuff")
 m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(.06,.04,.035,1)
 p.inputs["Roughness"].default_value=.88
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1)
 o=bpy.context.object
 o.name="V11 billiard impact scuff"
 o.data.materials.append(m)
 for f,scale in [(1,.001),(96,.001),(97,.04),(99,.13),(102,.12),(192,.12)]:
  keypose(o,f,(0,-.210,1.33),scale=(scale,scale*.035,scale))
if kind=="watermelon":
 # Fruit body opens into pulpy rind sections at contact, and wet red interior remains.
 rind=projectile.data.materials[0]
 flesh=bpy.data.materials.new("V11 red watermelon flesh")
 flesh.use_nodes=True
 p=flesh.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(.75,.028,.048,1)
 p.inputs["Roughness"].default_value=.34
 p.inputs["Subsurface Weight"].default_value=.13
 for j in range(14):
  a=j*2*math.pi/14
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
  o=bpy.context.object
  o.name="V11 watermelon rupture segment %02d"%j
  o.data.materials.append(rind if j%3 else flesh)
  for f in (1,96,97,99,103,110,124,144,192):
   t=max(0,(f-97)/24)
   radial=(.12+1.3*t)
   x=radial*math.cos(a)
   y=-.34-1.4*t+(.012*math.sin(j*.9))
   z=max(.03,1.32+radial*.50*math.sin(a)+1.1*t-4.905*t*t)
   sca=(.001,)*3 if f<=96 else (.15,.17,.09)
   keypose(o,f,(x,y,z),(t*4+j*.1,t*2,j*.3),sca)
 # The wet red body appears as an attached deformation; no separate background.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=36,ring_count=24,radius=1)
 o=bpy.context.object;o.name="V11 watermelon fleshy impact"
 o.data.materials.append(flesh)
 for f,sz in ((1,.001),(96,.001),(97,.13),(99,.30),(104,.50),(116,.43),(192,.37)):
  keypose(o,f,(0,-.24,1.32),scale=(sz,sz*.12,sz*.80))
# Cannon prototype: cannon on the same 50m ground, separate launch model.
if kind=="cannon":
 for o in list(s.objects):
  if ("slingshot" in o.name.lower() or "pouch" in o.name.lower()
      or "Y arm" in o.name or "latex" in o.name.lower()
      or "elastic" in o.name.lower() or "wooden" in o.name.lower()):
   o.hide_render=True
 # tube aligned with forward flight axis +Y, positioned at original launcher.
 m=bpy.data.materials.new("V11 cannon cold cast iron")
 m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(.06,.07,.08,1)
 p.inputs["Metallic"].default_value=.83;p.inputs["Roughness"].default_value=.38
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.33,depth=2.4,location=(0,-52.05,1.53))
 barrel=bpy.context.object;barrel.name="V11 cannon barrel"
 barrel.rotation_euler=(math.pi/2,0,0)
 # A hollow thick-walled steel barrel, not a capped solid cylinder.
 n=48;v=[];faces=[]
 for radius,z in ((.33,-1.2),(.33,1.2),(.23,-1.2),(.23,1.2)):
  for i in range(n):
   a=2*math.pi*i/n
   v.append((radius*math.cos(a),radius*math.sin(a),z))
 for i in range(n):
  j=(i+1)%n
  faces.extend(((i,j,n+j,n+i),
                (2*n+i,3*n+i,3*n+j,2*n+j),
                (i,2*n+i,2*n+j,j),
                (n+i,n+j,3*n+j,3*n+i)))
 mesh=bpy.data.meshes.new("V11 hollow cannon bore")
 mesh.from_pydata(v,[],faces);mesh.update()
 barrel.data=mesh
 barrel.data.materials.append(m)
 for face in barrel.data.polygons:face.use_smooth=True
 for f,y in ((1,-52.05),(45,-52.05),(48,-52.05),(49,-52.40),(53,-52.28),(61,-52.05),(192,-52.05)):
  keypose(barrel,f,(0,y,1.53))
 # wheel pair
 for x in (-.55,.55):
  bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=.48,depth=.17,location=(x,-52.2,.50))
  w=bpy.context.object;w.name="V11 cannon carriage wheel "+str(x)
  w.rotation_euler=(0,math.pi/2,0)
  w.data.materials.append(m)
# Cannon start: look past the carriage and smoothly join V10 projectile tracking.
if kind=="cannon":
 positions={};rotations={}
 for f in range(1,193):
  s.frame_set(f)
  positions[f]=camera.location.copy()
  rotations[f]=camera.rotation_euler.copy()
 camera.animation_data_clear()
 for f in range(1,193):
  if f<=48:
   y,z=pkeys[f].y,pkeys[f].z
   loc=Vector((1.47,y-4.15,z+.81))
   target=Vector((0,y+1.9,z-.13))
   rot=(target-loc).to_track_quat("-Z","Y").to_euler()
  elif f<63:
   t=(f-48)/15.
   y,z=pkeys[f].y,pkeys[f].z
   side=Vector((1.47,y-4.15,z+.81))
   target=Vector((0,y+1.9,z-.13))
   loc=side.lerp(positions[f],t)
   rot=(target-loc).to_track_quat("-Z","Y").to_euler()
   rot=rot.to_quaternion().slerp(rotations[f].to_quaternion(),t).to_euler()
  else:
   loc=positions[f];rot=rotations[f]
  camera.location=loc
  camera.rotation_euler=rot
  camera.keyframe_insert("location",frame=f)
  camera.keyframe_insert("rotation_euler",frame=f)
 glow=bpy.data.materials.new("V11 cannon muzzle orange glow")
 glow.use_nodes=True
 g=glow.node_tree.nodes.get("Principled BSDF")
 g.inputs["Base Color"].default_value=(1.0,.23,.015,1)
 g.inputs["Emission Color"].default_value=(1.0,.17,.015,1)
 g.inputs["Emission Strength"].default_value=14
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1)
 fx=bpy.context.object
 fx.name="V11 muzzle ignition flash"
 fx.data.materials.append(glow)
 for f,a in ((1,.001),(48,.001),(49,.48),(50,.66),(51,.34),(53,.001),(192,.001)):
  keypose(fx,f,(0,-50.84,1.53),scale=(a,a*.67,a))
# Camera follows the V10 shot without changes: last follow-frame 91 at about 5.5m.
s.frame_set(91);a=camera.matrix_world.copy()
s.frame_set(192);b=camera.matrix_world.copy()
assert all(abs(a[i][j]-b[i][j])<1e-5 for i in range(4) for j in range(4))
sc=s
sc.frame_set(1)
scene_path=OUT/f"{kind.upper()}_V11_50M_SINGLE_SCENE.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(scene_path))
print("V11_SCENE_READY",kind,scene_path,flush=True)
frames=[1,44,48,56,74,90,94,96,97,101,108,130,174,192]
if mode=="preview":
 for f in frames:
  sc.frame_set(f)
  sc.render.filepath=str(OUT/f"PREVIEW_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("V11_PREVIEW",kind,f,flush=True)
elif mode=="full":
 d=OUT/"frames";d.mkdir(exist_ok=True)
 for f in range(1,193):
  sc.frame_set(f)
  target=d/f"frame_{f:04d}.png"
  if target.exists() and target.stat().st_size>12000:
   continue
  sc.render.filepath=str(target)
  bpy.ops.render.render(write_still=True)
  if f%24==0:print("V11_RENDER",kind,f,"/192",flush=True)
