import bpy, math, random, json
from mathutils import Vector
from pathlib import Path

root = Path(__file__).resolve().parent
out = root / "glass_panel_challenge_v5"
out.mkdir(exist_ok=True)
random.seed(51421)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.cycles.max_bounces=8
scene.cycles.transmission_bounces=8
if hasattr(scene.cycles,'caustics_reflective'): scene.cycles.caustics_reflective=False
if hasattr(scene.cycles,'caustics_refractive'): scene.cycles.caustics_refractive=False
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=70
scene.render.fps=24
scene.frame_start=1
scene.frame_end=36
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.film_transparent=False
scene.world=bpy.data.worlds.new("Soft studio air")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.28,.30,.32,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.35

def mat(name,color,metal=0,rough=.35,trans=0,ior=1.45):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Transmission Weight"].default_value=trans
    p.inputs["IOR"].default_value=ior
    p.inputs["Alpha"].default_value=1.0
    return m

glass=mat("V5 solid silica | Fresnel refraction IOR 1.51",(.96,.99,1),rough=.024,trans=1,ior=1.51)
edge=mat("V5 fracture green glass edges",(.72,.94,.94),rough=.045,trans=1,ior=1.51)
steel=mat("V5 machined chrome steel",(.53,.56,.59),metal=.98,rough=.14)
darkmetal=mat("V5 graphite anodized aluminum",(.20,.24,.25),metal=.73,rough=.30)
rubber=mat("V5 silicone pads",(.07,.075,.075),rough=.82)
concrete=mat("V5 speckled floor",(.34,.35,.35),rough=.81)
backdrop=mat("V5 concrete background",(.24,.26,.27),rough=.84)
# Material roughness variation in large planes: real surfaces aren't flat gradients
for m,scale,bump_strength,dist in [(concrete,140,.24,.015),(backdrop,50,.17,.03)]:
    p=m.node_tree.nodes.get("Principled BSDF")
    noise=m.node_tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=scale
    noise.inputs["Detail"].default_value=3.4
    bump=m.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=bump_strength
    bump.inputs["Distance"].default_value=dist
    m.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"],p.inputs["Normal"])

def cube(name,location,dims,material,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    o=bpy.context.object;o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bev:
        b=o.modifiers.new("Machined micro-bevel", "BEVEL")
        b.width=bev
        b.segments=3
        n=o.modifiers.new("Angle weighted normals","WEIGHTED_NORMAL")
    return o

floor=cube("Concrete studio floor",(0,2,-.13),(13,14,.26),concrete,.035)
wall=cube("Gradual textured rear",(0,6,4),(13,.3,9),backdrop,.03)
# Create two physical shoes with polished steel and rubber liners
for x in (-.65,.65):
    base=cube(f"Support shoe foot {x}",(x,.04,.068),(.42,.70,.12),darkmetal,.026)
    vertical=cube(f"Machined steel clamp body {x}",(x,.04,.36),(.31,.20,.58),darkmetal,.024)
    g1=cube(f"Front silicone pad {x}",(x,-.065,.48),(.255,.015,.16),rubber,.008)
    g2=cube(f"Rear silicone pad {x}",(x,.065,.48),(.255,.015,.16),rubber,.008)
    for z in (.20,.36):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.038,depth=.024,location=(x,-.091,z),rotation=(math.pi/2,0,0))
        bolt=bpy.context.object;bolt.name=f"Steel bolt head {x} {z}"
        bolt.data.materials.append(steel)
        bolt.modifiers.new("Round steel edge","BEVEL").width=.004

W,H,TH=1.72,2.16,.012
CENTER_Z=1.58
# Refractive glass has real front and back faces, beveling, not alpha-blended white cards
pane=cube("Actual tempered glass pane",(0,0,CENTER_Z),(W,TH,H),glass,.003)
pane.modifiers.new("Glass edge normals","WEIGHTED_NORMAL")

def visible(o,f,state):
    o.hide_render=not state
    o.keyframe_insert(data_path="hide_render",frame=f)
    o.hide_viewport=not state
    o.keyframe_insert(data_path="hide_viewport",frame=f)
visible(pane,1,True)
visible(pane,11,True)
visible(pane,12,False)
visible(pane,36,False)

# Irregular Voronoi impact crack: nonuniform center concentration, no square grid.
pts=[]
for i in range(92):
    angle=random.random()*math.tau
    r=(random.random()**1.6)*.72
    if i>46:
        r=.32+random.random()*.83
    x=(r*math.cos(angle)*1.13)+random.gauss(0,.026)
    z=(r*math.sin(angle)*1.18)+random.gauss(0,.025)
    x=max(-W*.49,min(W*.49,x))
    z=max(-H*.49,min(H*.49,z))
    pts.append((x,z))
pts += [(-W/2,-H/2),(-W/2,H/2),(W/2,-H/2),(W/2,H/2)]
outline=[(-W/2,-H/2),(W/2,-H/2),(W/2,H/2),(-W/2,H/2)]

def clip(poly,nx,nz,limit):
    if not poly:return []
    out=[]
    prev=poly[-1];dprev=prev[0]*nx+prev[1]*nz-limit
    for cur in poly:
        dcur=cur[0]*nx+cur[1]*nz-limit
        if (dprev<=0)!=(dcur<=0):
            t=dprev/(dprev-dcur)
            out.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
        if dcur<=0:out.append(cur)
        prev,dprev=cur,dcur
    return out

def new_fragment(i,poly,t):
    cx=sum(x for x,z in poly)/len(poly)
    cz=sum(z for x,z in poly)/len(poly)
    n=len(poly)
    verts=[(x-cx,-t/2,z-cz) for x,z in poly]+[(x-cx,t/2,z-cz) for x,z in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for k in range(n):faces.append((k,(k+1)%n,(k+1)%n+n,k+n))
    mesh=bpy.data.meshes.new("fracture closed mesh")
    mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(f"True glass fragment {i:03d}",mesh)
    bpy.context.collection.objects.link(o)
    mesh.materials.append(glass);mesh.materials.append(edge)
    for face in mesh.polygons:face.material_index=int(face.index>=2)
    o.location=(cx,0,CENTER_Z+cz)
    bev=o.modifiers.new("Microscopic polished glass edge","BEVEL")
    bev.width=.0014
    bev.segments=2
    return o,cx,cz

polys=[]
for i,(sx,sz) in enumerate(pts):
    poly=outline[:]
    for j,(ox,oz) in enumerate(pts):
        if i==j:continue
        nx,nz=ox-sx,oz-sz
        lim=(ox*ox+oz*oz-sx*sx-sz*sz)/2
        poly=clip(poly,nx,nz,lim)
        if len(poly)<3:break
    if len(poly)<3:continue
    a=abs(sum(poly[k][0]*poly[(k+1)%len(poly)][1]-poly[(k+1)%len(poly)][0]*poly[k][1] for k in range(len(poly)))/2)
    if a>.00015:polys.append((poly,a))

for i,(poly,area) in enumerate(polys):
    t=.006+min(.006,.005*math.sqrt(area/.07))
    ob,cx,cz=new_fragment(i,poly,t)
    radius=math.hypot(cx,cz)
    delay=(0 if radius<.26 else (1 if radius<.5 else (2 if radius<.8 else 3)))
    start=12+delay
    visible(ob,1,False)
    visible(ob,start-1,False)
    visible(ob,start,True)
    ob.location=(cx,0,CENTER_Z+cz)
    ob.keyframe_insert(data_path="location",frame=start)
    ob.rotation_euler=(0,0,0)
    ob.keyframe_insert(data_path="rotation_euler",frame=start)
    rad_x=cx/(radius+.02);rad_z=cz/(radius+.02)
    # The central region starts small and explosively fast; the exterior breaks loose later.
    impulse=2.8/(1+3.0*radius)
    vx=rad_x*impulse+random.uniform(-.50,.50)
    vy=3.4/(1+1.9*radius)+random.uniform(.2,.9)
    vz=rad_z*impulse+random.uniform(.4,1.6)
    for f in (start+3,start+7,start+13,36):
        dt=(f-start)/24
        z=max(.03,CENTER_Z+cz+vz*dt-4.9*dt*dt)
        ob.location=(cx+vx*dt,vy*dt,z)
        ob.rotation_euler=(random.uniform(-1,1)*dt*3,random.uniform(-1,1)*dt*4,random.uniform(-1,1)*dt*3)
        ob.keyframe_insert(data_path="location",frame=f)
        ob.keyframe_insert(data_path="rotation_euler",frame=f)

# Visible crack paths a split second prior to disintegration.
crackmat=mat("white hairline fractures",(.7,.91,.96),rough=.1,trans=.55)
for k in range(11):
    start=Vector((0,-.010,CENTER_Z))
    angle=k*math.tau/11+random.uniform(-.13,.13)
    r=0
    for j in range(4):
        r+=random.uniform(.09,.18)
        angle+=random.uniform(-.15,.15)
        end=Vector((r*math.cos(angle),-.010,CENTER_Z+r*math.sin(angle)))
        mid=(start+end)/2
        diff=end-start
        bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.0009,depth=diff.length,location=mid)
        o=bpy.context.object;o.name="Microscopic fracture fissure"
        o.rotation_euler=diff.to_track_quat("Z","Y").to_euler()
        o.data.materials.append(crackmat)
        visible(o,1,False);visible(o,10,False);visible(o,11,True);visible(o,15,False)
        start=end

# A machined steel sphere visibly meets the glass instead of teleporting through it.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.095,location=(0,-1.7,CENTER_Z))
ball=bpy.context.object;ball.name="19 mm equivalent chrome projectile"
ball.data.materials.append(steel)
for p in ball.data.polygons:p.use_smooth=True
for f,y in [(1,-1.65),(7,-.70),(11,-.19),(12,0),(14,.22),(19,.76),(36,1.45)]:
    ball.location=(0,y,CENTER_Z)
    ball.keyframe_insert(data_path="location",frame=f)

# Four realistic photographic softboxes with separate reflection strips.
def light(name,at,power,size,aim,c=(1,1,1)):
    d=bpy.data.lights.new(name,"AREA")
    d.shape="RECTANGLE";d.size=size[0];d.size_y=size[1]
    d.energy=power;d.color=c
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=at
    o.rotation_euler=(Vector(aim)-o.location).to_track_quat("-Z","Y").to_euler()
light("Huge left studio softbox",(-3.5,-3,5),1050,(3.5,5),(0,0,1.6))
light("Thin long glass rim",(-2,2,4),980,(1,5),(0,0,1.5),(.9,.96,1))
light("Warm opposing rim",(3.0,1.8,3.8),1500,(2,4),(0,0,1.5),(1,.94,.86))
light("Front fill softbox",(2,-2,5.5),450,(4,2),(0,0,1.4))
# Camera: glass at eye height, enough angle to see 12 mm edges.
bpy.ops.object.camera_add(location=(2.55,-3.65,2.22))
cam=bpy.context.object;scene.camera=cam
cam.data.lens=48
cam.data.clip_end=100
cam.data.dof.use_dof=True
cam.data.dof.focus_object=pane
cam.data.dof.aperture_fstop=10
for f,pos,target in [(1,(2.9,-4.4,2.35),(0,0,1.50)),
                     (12,(2.55,-3.7,2.22),(0,0,1.53)),
                     (36,(2.35,-3.25,2.10),(0,.25,1.50))]:
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.keyframe_insert(data_path="location",frame=f)
    cam.keyframe_insert(data_path="rotation_euler",frame=f)
scene.frame_set(1)
file=out/"GLASS_V5_ONE_PANE_QUALITY_TEST.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(file))
print("V5_ONE_PANE_READY",file,"FRAGMENTS",len(polys),flush=True)
