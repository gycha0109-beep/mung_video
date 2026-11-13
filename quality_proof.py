import bpy,math,random,sys,os
from mathutils import Vector
from math import sin,cos,pi
from pathlib import Path
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
ROOT.mkdir(parents=True,exist_ok=True)
MODE=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
random.seed(44018)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
S=bpy.context.scene
S.render.engine="BLENDER_EEVEE"
S.render.resolution_x=1080;S.render.resolution_y=1920
S.render.resolution_percentage=52 if MODE=="preview" else 70
S.render.fps=24;S.frame_start=1;S.frame_end=192
S.render.image_settings.file_format="PNG";S.render.image_settings.color_mode="RGB"
S.render.image_settings.compression=22
S.view_settings.view_transform="AgX";S.view_settings.look="AgX - Medium High Contrast"
S.render.film_transparent=False
world=bpy.data.worlds.new("Bright cloudy outdoor ambience")
S.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.34,.46,.58,1)
bg.inputs["Strength"].default_value=.66
environment_path=ROOT/"outdoor.exr"
if environment_path.exists():
 env=world.node_tree.nodes.new("ShaderNodeTexEnvironment")
 env.image=bpy.data.images.load(str(environment_path))
 world.node_tree.links.new(env.outputs["Color"],bg.inputs["Color"])
 bg.inputs["Strength"].default_value=.39
 print("HDRI_ACTIVE",environment_path,flush=True)
def shader(name,color,met=0,rough=.6,scale=None,bump=.0,color2=None):
 m=bpy.data.materials.new(name);m.use_nodes=True
 nodes=m.node_tree.nodes;links=m.node_tree.links
 b=nodes.get("Principled BSDF")
 b.inputs["Base Color"].default_value=(*color,1)
 b.inputs["Metallic"].default_value=met;b.inputs["Roughness"].default_value=rough
 if scale:
  tex=nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=scale
  tex.inputs["Detail"].default_value=5.0
  tex.inputs["Roughness"].default_value=.68
  roughnoise=nodes.new("ShaderNodeTexNoise");roughnoise.inputs["Scale"].default_value=scale*9
  roughnoise.inputs["Detail"].default_value=3
  cr=nodes.new("ShaderNodeValToRGB")
  cr.color_ramp.elements[0].position=.21
  cr.color_ramp.elements[0].color=(*(tuple(c*.68 for c in color)),1)
  cr.color_ramp.elements[1].position=.78
  cr.color_ramp.elements[1].color=(*(color2 if color2 else tuple(min(1,c*1.17) for c in color)),1)
  links.new(tex.outputs["Fac"],cr.inputs["Fac"]);links.new(cr.outputs["Color"],b.inputs["Base Color"])
  if bump:
   bm=nodes.new("ShaderNodeBump");bm.inputs["Strength"].default_value=.30;bm.inputs["Distance"].default_value=bump
   fine=nodes.new("ShaderNodeMath");fine.operation="MULTIPLY_ADD";fine.inputs[1].default_value=.7;fine.inputs[2].default_value=.0
   links.new(roughnoise.outputs["Fac"],fine.inputs[0]);links.new(fine.outputs[0],bm.inputs["Height"])
   links.new(bm.outputs["Normal"],b.inputs["Normal"])
   rr=nodes.new("ShaderNodeMapRange");rr.inputs["From Min"].default_value=.14;rr.inputs["From Max"].default_value=.88
   rr.inputs["To Min"].default_value=max(.15,rough-.14);rr.inputs["To Max"].default_value=min(1,rough+.12)
   links.new(tex.outputs["Fac"],rr.inputs["Value"]);links.new(rr.outputs["Result"],b.inputs["Roughness"])
 return m
brickmats=[
 shader("Fired clay rough / charcoal",(.31,.107,.071),rough=.88,scale=33,bump=.018),
 shader("Fired clay warm terracotta",(.47,.20,.135),rough=.88,scale=39,bump=.018),
 shader("Weathered red brick",(.34,.13,.091),rough=.90,scale=32,bump=.022),
 shader("Old kiln orange brick",(.51,.205,.13),rough=.84,scale=30,bump=.024),
 shader("Old mortar marked reddish brown",(.38,.145,.105),rough=.90,scale=47,bump=.021)]
photo_dir=ROOT/"brick_faces"
if photo_dir.exists():
 photographic=[]
 for ix in (6,8,9,10):
  f=photo_dir/("brick_%02d.jpg"%ix)
  if not f.exists():continue
  m=shader("Photographed kiln-fired brick "+str(ix),(.42,.16,.11),rough=.85,scale=61,bump=.015)
  im=m.node_tree.nodes.new("ShaderNodeTexImage")
  im.image=bpy.data.images.load(str(f));im.interpolation="Linear"
  im.image.pack()
  b=m.node_tree.nodes.get("Principled BSDF")
  m.node_tree.links.new(im.outputs["Color"],b.inputs["Base Color"])
  photographic.append(m)
 if photographic:
  brickmats=photographic
  print("PHOTOGRAPHIC_DIFFUSE_MATERIALS",len(brickmats),flush=True)
normal_path=ROOT/"brick_nor.png"
if normal_path.exists():
 tex_image=bpy.data.images.load(str(normal_path));tex_image.colorspace_settings.name="Non-Color"
 for index,mt in enumerate(brickmats):
  n=mt.node_tree.nodes;l=mt.node_tree.links
  im=n.new("ShaderNodeTexImage");im.image=tex_image;im.interpolation="Linear"
  im.extension="REPEAT"
  normal=n.new("ShaderNodeNormalMap");normal.inputs["Strength"].default_value=.23
  l.new(im.outputs["Color"],normal.inputs["Color"])
  b=next((x for x in n if x.bl_idname=="ShaderNodeBump"),None)
  if b:l.new(normal.outputs["Normal"],b.inputs["Normal"])
 print("PHOTOGRAPHIC_NORMAL_MAP_ACTIVE",normal_path,flush=True)
mortar=shader("Cement / sand pores",(.28,.28,.26),rough=.92,scale=38,bump=.015)
dirt=shader("Natural roadside gravel",(.18,.185,.165),rough=.96,scale=38,bump=.018)
paving=shader("Dusty concrete tarmac",(.28,.31,.30),rough=.89,scale=110,bump=.009)
oak=shader("Rugged carved hickory wood",(.19,.085,.035),rough=.50,scale=11,bump=.013)
grip=shader("Tanned worn leather",(.105,.042,.024),rough=.75,scale=48,bump=.004)
rubber=shader("Elastic dark rubber",(.020,.022,.023),rough=.68,scale=76,bump=.001)
polished=shader("Forged brushed stainless steel",(.34,.40,.43),met=.92,rough=.17,scale=98,bump=.001)
darksteel=shader("Oxidised steel fasteners",(.056,.068,.073),met=.78,rough=.33,scale=85,bump=.002)
darker=shader("Damaged clay core",(.23,.095,.064),rough=.95,scale=70,bump=.022)
armglove=shader("Worn suede gloves",(.22,.125,.076),rough=.87,scale=47,bump=.006)
leatherrib=shader("Glove stitching",(.48,.32,.18),rough=.85,scale=40,bump=.001)
sky=shader("Blue grey distance",(.24,.34,.43),rough=1)
def bevel(o,w=.012,seg=3):
 mod=o.modifiers.new("Real chamfered edge","BEVEL");mod.width=w;mod.segments=seg;mod.affect="EDGES"
 o.modifiers.new("Weighted normal","WEIGHTED_NORMAL")
def box(name,loc,dim,mat,bev=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=name;o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat)
 if bev:bevel(o,bev)
 return o
def sphere(name,loc,r,mat,ico=False):
 if ico:bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=loc)
 else:bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,radius=r,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 if not ico:
  for f in o.data.polygons:f.use_smooth=True
 return o
def beam(name,a,b,rad,mat,nverts=20):
 d=Vector(b)-Vector(a)
 mid=(Vector(a)+Vector(b))*.5
 bpy.ops.mesh.primitive_cylinder_add(vertices=nverts,radius=rad,depth=d.length,location=mid)
 o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
 o.data.materials.append(mat);bevel(o,rad*.32,3)
 return o
def animate(o,prop,keys):
 for frame,v in keys:
  setattr(o,prop,v);o.keyframe_insert(data_path=prop,frame=frame)
def interp(o):
 if not o.animation_data or not o.animation_data.action:return
 for l in o.animation_data.action.layers:
  for st in l.strips:
   if st.type!="KEYFRAME":continue
   for cb in st.channelbags:
    for fc in cb.fcurves:
     for k in fc.keyframe_points:
      k.interpolation="BEZIER"
      k.handle_left_type="AUTO_CLAMPED";k.handle_right_type="AUTO_CLAMPED"
def visible(o,start=1,end=192):
 if start>1:
  o.hide_render=True;o.keyframe_insert("hide_render",frame=start-1)
 o.hide_render=False;o.keyframe_insert("hide_render",frame=start)
 o.hide_render=False;o.keyframe_insert("hide_render",frame=end)
 if end<192:
  o.hide_render=True;o.keyframe_insert("hide_render",frame=end+1)
def line_between(o,frame,a,b,width,depth):
 d=Vector(b)-Vector(a);o.location=(Vector(a)+Vector(b))*.5
 o.rotation_mode="QUATERNION";o.rotation_quaternion=d.to_track_quat("Z","Y")
 o.scale=(width,depth,d.length)
 for p in ("location","rotation_quaternion","scale"):o.keyframe_insert(p,frame=frame)
# Outdoor scene with shadow-catching ground.
ground=box("Full courtyard ground",(0,-7,-.29),(80,80,.36),dirt,.035)
walk=box("Concrete walkway",(0,-5,-.084),(9.5,17,.10),paving,.045)
for i in range(245):
 x=random.uniform(-4.8,4.8);y=random.uniform(-13,2)
 if abs(x)<.8 and y< -8:continue
 r=random.uniform(.012,.052)
 ob=sphere("Small natural gravel %03d"%i,(x,y,-.018+r*.24),r,random.choice([mortar,dirt,darker]),True)
 ob.scale.z=random.uniform(.15,.42)
# wall support architecture
box("Stone pillar left",(-3.64,.32,1.74),(.42,.66,3.8),mortar,.058)
box("Stone pillar right",(3.64,.32,1.74),(.42,.66,3.8),mortar,.058)
box("Foundation lip",(0,.33,.03),(7.3,.65,.18),mortar,.022)
box("Wall top coping",(0,.20,3.63),(7.45,.58,.27),mortar,.065)
# behind-wall structure has a real black depth recess visible when center collapses.
# No solid wall behind the masonry: removed bricks reveal a genuine through-hole.
cols,rows=18,15
BW=.397;BH=.229
impact_z=1.63
to_break=[]
for j in range(rows):
 for i in range(cols):
  x=(i-(cols-1)/2)*BW + (.18 if j%2 else 0)
  z=.20+j*BH
  if abs(x)>3.42:continue
  y=-.035+random.uniform(-.009,.009)
  dw=BW-random.uniform(.015,.025)
  dh=BH-random.uniform(.013,.021)
  mat=random.choice(brickmats)
  brick=box("Hand-laid worn masonry %02d %02d"%(j,i),(x,y,z),(dw,.30,dh),mat,.016)
  brick.rotation_euler=(random.uniform(-.012,.012),random.uniform(-.005,.005),random.uniform(-.006,.006))
  breakout= (abs(x)<.81 and abs(z-impact_z)<.62)
  if breakout:
   visible(brick,1,96)
   to_break.append((x,y,z,dw,dh,mat))
# Texture details in intact brickwork: dark chips and mortar on edges.
for k in range(110):
 x=random.uniform(-3.23,3.23);z=random.uniform(.20,3.48)
 if abs(x)<1.1 and abs(z-impact_z)<.91:continue
 if random.random()<.44:
  ob=box("Weathered chipped enamel %03d"%k,(x,-.194,z),(.023,.003,random.uniform(.006,.055)),darker,.002)
  ob.rotation_euler[1]=random.uniform(-.5,.5)
# Impact damage: fracture bricks into shaped clay chunks with persistent void.
for ii,(x,y,z,dw,dh,mat) in enumerate(to_break):
 for sx in range(3):
  for sz in range(2):
   xx=x+(sx-1)*dw/3
   zz=z+(sz-.5)*dh/2
   shard=box("FRACTURED BRICK SHARD %02d-%d-%d"%(ii,sx,sz),
      (xx,y,zz),(dw/3-.005,.27,dh/2-.007),
      random.choice([mat,darker]),.006)
   visible(shard,97,192)
   travel=(Vector((xx,0,zz))-Vector((0,0,impact_z)))
   lateral=Vector((travel.x*.44+random.uniform(-.5,.5),
         random.uniform(.6,2.8),random.uniform(.30,1.9)))
   base=Vector((xx,y,zz))
   target=base+lateral*.30
   target2=base+lateral*.82+Vector((0,0,-.55))
   target3=base+lateral*1.33+Vector((0,0,-2.8))
   target4=Vector((target3.x,target3.y,max(-.008,target3.z)))
   for f,pos in [(97,base),(101,target),(119,target2),(145,target3),(170,target4),(192,target4)]:
    shard.location=pos
    shard.keyframe_insert("location",frame=f)
   spin=Vector((random.uniform(-4,4),random.uniform(-5,5),random.uniform(-4,4)))
   animate(shard,"rotation_euler",[(97,(0,0,0)),(119,tuple(spin*.5)),(145,tuple(spin)),(170,tuple(spin*1.18)),(192,tuple(spin*1.18))])
   interp(shard)
# secondary fine grit physically originates from contact ring, not unrelated visual particles
for k in range(95):
 theta=random.random()*2*pi
 radial=random.random()**.5*.82
 x=cos(theta)*radial;z=impact_z+sin(theta)*radial
 r=random.uniform(.010,.036)
 flake=sphere("Clay splinter %03d"%k,(x,-.18,z),r,random.choice([darker,brickmats[0],brickmats[1]]),True)
 flake.scale=Vector((random.uniform(.4,1),random.uniform(.5,1.6),random.uniform(.2,.55)))
 visible(flake,97,192)
 v=Vector((random.uniform(-2.5,2.5),random.uniform(-1.2,3.6),random.uniform(.2,3.5)))
 start=Vector((x,-.18,z));endpos=start+v*.72+Vector((0,0,-1.7))
 endpos.z=max(.015,endpos.z)
 animate(flake,"location",[(97,start),(103,start+v*.11),(120,start+v*.43+Vector((0,0,-.26))),(150,endpos),(192,endpos)])
 animate(flake,"rotation_euler",[(97,(0,0,0)),(150,(random.uniform(-7,7),random.uniform(-7,7),random.uniform(-7,7)))])
 interp(flake)
# Thin luminous dust shafts: colored clay fine particles, not opaque white orbs.
dustcolors=[shader("Dust #"+str(k),(.40+k*.018,.29+k*.016,.22+k*.01),rough=1) for k in range(4)]
for k in range(70):
 direction=Vector((random.uniform(-1.0,1.0),random.uniform(-1.0,.8),random.uniform(-.25,.75)))
 size=random.uniform(.007,.024)
 speck=sphere("Microscopic brick powder %03d"%k,(0,-.19,impact_z),size,random.choice(dustcolors),True)
 visible(speck,97,145)
 animate(speck,"location",[(97,(0,-.19,impact_z)),(103,tuple(direction*.2+Vector((0,-.19,impact_z)))),(125,tuple(direction*1.2+Vector((0,-.19,impact_z)))),
 (145,tuple(direction*1.75+Vector((0,-.19,impact_z-.65))))])
 animate(speck,"scale",[(97,(.2,.2,.2)),(104,(1,1,1)),(145,(.01,.01,.01))])
# Slingshot body: shaped solid wood Y, leather hand grip, fastening bands and rivets.
fork_y=-9.30
branch_z=1.52
peak_z=2.01
fork_l=Vector((-.32,fork_y-.02,peak_z))
fork_r=Vector((.32,fork_y-.02,peak_z))
central=Vector((0,fork_y,branch_z))
handlebase=Vector((0,fork_y,.72))
beam("Carved wooden slingshot handle",handlebase,central,.094,oak,20)
for side,p in (("LEFT",fork_l),("RIGHT",fork_r)):
 beam("Solid oak Y arm "+side,central,p,.067,oak,20)
 # Leather loop anchor with bronze steel rivet
 sphere("Forged elastic anchor "+side,p,.069,darksteel)
 beam("Brushed elastic cap "+side,p+Vector((0,-.027,-.08)),p+Vector((0,-.027,.045)),.049,polished)
for j in range(13):
 z=.94+j*.026
 band=beam("Wrapped leather handle grip %02d"%j,(0,fork_y,z),(0,fork_y,z+.018),.102,grip)
# Approximate visible forearm glove gripping handle on right lower edge.
palm=sphere("Right hand with leather glove",(.45,-9.83,.81),.135,armglove)
palm.scale=(.82,.88,1.15)
for j in range(4):
 a=-.05+j*.093
 f=beam("Protective glove fingers %d"%j,(a,-9.58,1.22),(a+.035,-9.26,1.14),.045,armglove,12)
beam("Wrist of shooter",(.45,-9.88,.81),(.70,-10.4,.29),.11,armglove)
# Sling bands extend and contract on drawing. They're flattened broad latex straps.
pouch=sphere("Stitched leather projectile cup",(0,-9.55,1.79),.16,grip)
pouch.scale=(1.13,.29,.67)
for f, pos in [(1,(0,-9.49,1.79)),(48,(0,-10.18,1.79)),(53,(0,-9.49,1.79)),(192,(0,-9.49,1.79))]:
 pouch.location=pos;pouch.keyframe_insert("location",frame=f)
interp(pouch)
for title,tip in (("LEFT",fork_l),("RIGHT",fork_r)):
 bpy.ops.mesh.primitive_cube_add(size=1)
 band=bpy.context.object;band.name="Elastic band straps "+title
 band.data.materials.append(rubber)
 band.rotation_mode="QUATERNION"
 for f,back in [(1,-9.49),(48,-10.18),(53,-9.49),(192,-9.49)]:
  target=Vector((-.11 if title=="LEFT" else .11,back,1.79))
  line_between(band,f,tip,target,.057,.022)
# Smooth sphere with brushed steel and brushed reflections.
ball=sphere("POLISHED STEEL SHOT", (0,-9.49,1.79),.142,polished)
S.render.image_settings.color_mode="RGBA"
# Visually exact muzzle position, then motion for 2 seconds, then contact.
positions=[(1,(0,-9.49,1.79)),(48,(0,-10.18,1.79)),(51,(0,-9.43,1.81)),
           (67,(0,-6.63,1.76)),(82,(0,-3.47,1.69)),(94,(0,-.78,impact_z)),(96,(0,-.29,impact_z)),
           (99,(0,.07,impact_z)),(106,(0,.63,impact_z-.075)),(116,(0,1.32,impact_z-.36)),(136,(0,2.15,.42)),
           (160,(0,2.54,.15)),(192,(0,2.54,.15))]
animate(ball,"location",positions);interp(ball)
# Cinematic first-person tracking camera; follows and freezes one meter from wall.
data=bpy.data.cameras.new("Dynamic POV / collision witness")
camera=bpy.data.objects.new("CINEMA CAMERA",data);bpy.context.collection.objects.link(camera);S.camera=camera
camera.data.clip_start=.012;camera.data.clip_end=250
camera.data.sensor_fit="AUTO"
def cam(fr,loc,target,lens):
 camera.location=loc
 camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
 camera.keyframe_insert("location",frame=fr);camera.keyframe_insert("rotation_euler",frame=fr)
 camera.data.lens=lens;camera.data.keyframe_insert("lens",frame=fr)
cam(1,(0,-11.1,1.87),(0,-5.5,1.73),30)
cam(46,(0,-11.17,1.86),(0,-5.5,1.73),30)
cam(51,(0,-10.60,1.85),(0,-5.3,1.7),28)
cam(73,(.24,-5.15,1.81),(0,-1.15,1.65),25)
cam(88,(.36,-2.37,1.81),(0,-.2,1.63),22)
cam(94,(.39,-1.32,1.86),(0,-.12,impact_z),22)
cam(96,(.39,-1.32,1.86),(0,-.12,impact_z),22)
cam(97,(.36,-1.37,1.85),(0,-.12,impact_z),22)
cam(100,(.42,-1.35,1.87),(0,-.12,impact_z),22)
cam(104,(.39,-1.32,1.86),(0,-.12,impact_z),22)
cam(192,(.39,-1.32,1.86),(0,-.12,impact_z),22)
interp(camera)
# Outdoor sunlight with clean bounce fill and edge separation, not flat gray.
def sunlight(name,loc,power,size,color,point):
 bpy.ops.object.light_add(type="AREA",location=loc)
 ob=bpy.context.object;ob.name=name;ob.data.energy=power
 ob.data.shape="RECTANGLE";ob.data.size=size[0];ob.data.size_y=size[1]
 ob.data.color=color
 ob.rotation_euler=(Vector(point)-ob.location).to_track_quat("-Z","Y").to_euler()
 return ob
sunlight("Sun reflected from courtyard",(-4,-7,9),1500,(7,7),(1,.82,.68),(0,-2,1.5))
sunlight("Sky huge area softbox",(2,1,7),830,(10,6),(.65,.81,1),(0,-2,1.5))
sunlight("Side metallic specular highlight",(3,-9,3.7),700,(2,5),(.96,.96,1),(0,-7,1.8))
bpy.ops.object.light_add(type="SUN",location=(-2,-3,8))
s=bpy.context.object;s.name="Late afternoon sunlight";s.data.energy=1.65;s.data.angle=.115
s.rotation_euler=(.48,-.38,.28)
# Add title as restrained diegetic screen-space (not blocking impact).
font_path=Path("C:/Windows/Fonts/bahnschrift.ttf")
font=bpy.data.fonts.load(str(font_path)) if font_path.exists() else None
hud=shader("Lens HUD ivory",(.86,.92,.89),rough=.5)
hud.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value=(.66,.78,.72,1)
hud.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value=.55
def title(text,name,y,size):
 c=bpy.data.curves.new(name,"FONT");c.body=text;c.size=size;c.align_x="CENTER";c.extrude=.0006
 if font:c.font=font
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o)
 o.parent=camera;o.location=(0,y,-5.8);o.data.materials.append(hud);return o
title("SHOT 02   /   STEEL","Top score in lens",3.02,.24)
title("10M   |   8.0 SEC   |   PHYSICS TEST","Small lens legend",2.64,.12)
# Keep no extra outlines and no fake victory text.
S.frame_set(1)
out=ROOT/"slingshot_quality_proof_v2.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print("PROJECT_CREATED",out,len(bpy.data.objects),"objects",len(to_break),"breaking bricks",flush=True)
if MODE=="preview":
 for frame in (1,45,78,94,100,125,176):
  S.frame_set(frame)
  S.render.filepath=str(ROOT/("test_%03d.png"%frame))
  bpy.ops.render.render(write_still=True)
  print("FRAME_TEST_OK",frame,flush=True)
elif MODE=="hero":
 S.render.resolution_percentage=82
 for frame in (1,94,125,176):
  S.frame_set(frame)
  S.render.filepath=str(ROOT/("hero_%03d.png"%frame))
  bpy.ops.render.render(write_still=True)
  print("HERO_RENDER_OK",frame,flush=True)
elif MODE=="video":
 S.render.filepath=str(ROOT/"frames"/"frame_")
 (ROOT/"frames").mkdir(exist_ok=True)
 bpy.ops.render.render(animation=True)
 print("RENDER_192_FRAMES_DONE",flush=True)
