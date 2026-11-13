import bpy,math,random,sys
from pathlib import Path
from mathutils import Vector
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v9_egg"
OUT.mkdir(exist_ok=True)
src=R/"cinematic_50m_v8"/"egg_V8_IMPACT_STATIC.blend"
mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
bpy.ops.wm.open_mainfile(filepath=str(src))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720
s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="full" else 65
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.image_settings.compression=14
s.render.fps=24
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.25
s.frame_start=1
s.frame_end=108
if s.rigidbody_world:s.rigidbody_world.point_cache.frame_end=108
# Original planar circles look like stickers. Remove them, NOT the rigid shells/drops.
for o in s.objects:
 if o.name in ("Egg white sticky spread central","Egg yolk vivid central") or o.name.startswith("Egg white perimeter wet") or o.name.startswith("Egg yolk sticky drip"):
  o.hide_render=True
# Impact stays in fixed WIDE perspective. No camera animation, no optical zoom.
cam=s.camera
cam.animation_data_clear()
cam.data.animation_data_clear()
def surface_mat(name,col,alpha,rough=.14):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*col,1)
 m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*col,1)
 bs.inputs["Roughness"].default_value=rough
 bs.inputs["Metallic"].default_value=0
 bs.inputs["Coat Weight"].default_value=.52
 bs.inputs["Coat Roughness"].default_value=.06
 bs.inputs["Subsurface Weight"].default_value=.07
 bs.inputs["Alpha"].default_value=alpha
 m.surface_render_method="DITHERED"
 tx=m.node_tree.nodes.new("ShaderNodeTexNoise")
 tx.inputs["Scale"].default_value=32
 tx.inputs["Detail"].default_value=3
 bump=m.node_tree.nodes.new("ShaderNodeBump")
 bump.inputs["Strength"].default_value=.105
 bump.inputs["Distance"].default_value=.012
 m.node_tree.links.new(tx.outputs["Fac"],bump.inputs["Height"])
 m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
 return m
white=surface_mat("V9 albumen wet variable-height",(0.76,0.73,0.62),.48,.13)
yellow=surface_mat("V9 yolk deep amber",(0.90,0.41,0.01),.98,.12)
clear=surface_mat("V9 thin translucent edge",(0.68,0.70,0.65),.21,.08)
# Jagged, broad cohesive splash: one continuous liquid reaction, not more flying fragments.
def splash(name,material,cx,cz,rx,rz,seed,frequency=8):
 rng=random.Random(seed)
 n=96
 verts=[(cx,-.245,cz)]
 radii=[]
 for j in range(n):
  a=2*math.pi*j/n
  r=(1+.075*math.sin(3*a+seed)+.050*math.sin(7*a+.7)
      +.034*math.sin(11*a+seed)+rng.uniform(-.009,.009))
  radii.append(r)
  verts.append((cx+rx*r*math.cos(a),-.237,cz+rz*r*math.sin(a)))
 faces=[(0,j+1,1+(j+1)%n) for j in range(n)]
 me=bpy.data.meshes.new(name+" mesh")
 me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me)
 bpy.context.collection.objects.link(ob)
 ob.data.materials.append(material)
 solid=ob.modifiers.new("Wet raised uneven edge","SOLIDIFY")
 solid.thickness=.013
 return ob
outer=splash("V9 ORIGINAL IMPACT FORCE / wide albumen",white,-.012,1.36,.62,.52,1209,9)
inner=splash("V9 ORIGINAL IMPACT FORCE / yolk",yellow,.022,1.333,.33,.32,661,7)
edge=splash("V9 wet perimeter dispersion",clear,0,1.358,.76,.64,120,14)
# Back layer at y=-.228; subtle halo, not separate white circles.
edge.location.y=.015
def key(ob,f,sca):
 ob.scale=(sca,sca,sca)
 ob.keyframe_insert("scale",frame=f)
for ob in (edge,outer,inner):
 for f,v in [(1,.001),(12,.001),(13,.09),(14,.42),(16,.90),(18,1.04),(23,.99),(48,1.),(108,1.)]:
  key(ob,f,v)
# Physically attached branching arms: squeezed liquid spreading radially from impact center.
# Each ribbon begins within the central pool, tapers, and reaches its full extent over a few frames.
def finger(name,ang,l,r,material,phase,seed):
 rng=random.Random(seed)
 cx=.012;cz=1.34
 rings=14;ns=7
 verts=[];faces=[]
 for i in range(rings):
  u=i/(rings-1)
  rr=r*(1-.45*u)*(1+.08*math.sin(u*4*math.pi))
  x=cx+l*u*math.cos(ang)
  z=cz+l*u*math.sin(ang)
  for k in range(ns):
   t=2*math.pi*k/ns
   verts.append((x+rr*math.sin(t)*math.sin(ang+math.pi/2),
                 -.255+.008*math.cos(t),
                 z+rr*math.sin(t)*math.cos(ang+math.pi/2)))
 for i in range(rings-1):
  for k in range(ns):
   a=i*ns+k
   b=i*ns+(k+1)%ns
   faces.append((a,b,b+ns,a+ns))
 me=bpy.data.meshes.new(name+" geometry")
 me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 ob.data.materials.append(material)
 for f,v in [(1,.001),(12,.001),(phase,.003),(phase+2,.58),(phase+5,1),(108,1)]:
  # scale in x/z, preserve wall depth
  ob.scale=(v,1,v)
  ob.keyframe_insert("scale",frame=f)
 return ob
for i,(angle,length) in enumerate([(2.2,.58),(3.9,.58),(5.2,.60)]):
 finger("V9 cohesive impact spread %02d"%i,angle,length,.016,
        yellow if i==0 else white,14+(i%3),909+i)
# Wet center has convex relief, 3D thick rather than a flat decal.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=1,location=(.014,-.255,1.327))
bulge=bpy.context.object
bulge.name="V9 viscous raised center"
bulge.data.materials.append(yellow)
for p in bulge.data.polygons:p.use_smooth=True
for f,scale in [(1,.001),(12,.001),(13,.003),(15,.12),(19,.18),(108,.155)]:
 bulge.scale=(scale,scale*.18,scale*.86)
 bulge.keyframe_insert("scale",frame=f)
# Replace the cheap flat brick lighting with more directional side relief.
ld=bpy.data.lights.new("V9 face grazing key",type="AREA")
ld.energy=1200
ld.shape="RECTANGLE";ld.size=6;ld.size_y=10
ob=bpy.data.objects.new("V9 face grazing key",ld)
bpy.context.collection.objects.link(ob)
ob.location=(-3.8,-3.1,4.8)
ob.rotation_euler=(Vector((0,-.18,1.35))-ob.location).to_track_quat("-Z","Y").to_euler()
for m in bpy.data.materials:
 if not m or not m.use_nodes or "brick" not in m.name.lower():continue
 bs=m.node_tree.nodes.get("Principled BSDF")
 if not bs:continue
 tx=m.node_tree.nodes.new("ShaderNodeTexNoise")
 tx.inputs["Scale"].default_value=115
 bump=m.node_tree.nodes.new("ShaderNodeBump")
 bump.inputs["Strength"].default_value=.16
 bump.inputs["Distance"].default_value=.009
 m.node_tree.links.new(tx.outputs["Fac"],bump.inputs["Height"])
 m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
s.frame_set(1)
asset=OUT/"EGG_50M_V9_FORCEFUL_IMPACT.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
print("V9_IMPACT_SAVED",asset,flush=True)
if mode=="preview":
 frames={12,13,14,16,18,22,34,48,72,108}
 for f in range(1,109):
  s.frame_set(f)
  if f not in frames:continue
  s.render.filepath=str(OUT/f"V9_EGG_IMPACT_{f:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("V9_IMPACT_PREVIEW",f,flush=True)
elif mode=="full":
 folder=OUT/"impact_frames";folder.mkdir(exist_ok=True)
 for f in range(1,109):
  s.frame_set(f)
  if f<13:continue
  s.render.filepath=str(folder/f"frame_{f:04d}.png")
  bpy.ops.render.render(write_still=True)
  if f%12==0:print("V9_IMPACT_FULL",f,flush=True)
