import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v7"
O.mkdir(exist_ok=True)
rng=random.Random(2026111511)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.render.engine="CYCLES"
S.cycles.samples=48
S.cycles.use_denoising=True
S.cycles.max_bounces=8
S.cycles.transmission_bounces=8
S.render.resolution_x=720
S.render.resolution_y=1280
S.render.resolution_percentage=100
S.render.fps=24
S.frame_start=1
S.frame_end=84
S.render.image_settings.file_format="PNG"
S.render.image_settings.color_mode="RGB"
S.view_settings.view_transform="AgX"
S.view_settings.look="AgX - Medium High Contrast"
S.view_settings.exposure=-.12
S.render.film_transparent=False
W,H,T,Z=1.85,2.23,.010,1.66
HIT=38

def mat(name,color,metal=0,rough=.33,trans=0,ior=1.45):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Transmission Weight"].default_value=trans
    p.inputs["IOR"].default_value=ior
    return m

glass=mat("V7 | annealed clear glass face IOR 1.51",(.97,.99,1),rough=.018,trans=1,ior=1.51)
glassedge=mat("V7 | exposed dark aqua fracture edge",(.63,.84,.84),rough=.046,trans=.92,ior=1.51)
steel=mat("V7 | polished alloy projectile",(.56,.59,.61),metal=.98,rough=.10)
support=mat("V7 | blackened machined alloy",(.083,.093,.10),metal=.57,rough=.44)
rubber=mat("V7 | matte rubber isolation strips",(.044,.047,.045),rough=.78)
floor=mat("V7 | photostudio rough concrete",(.15,.165,.17),rough=.83)
wall=mat("V7 | soft neutral concrete backdrop",(.095,.105,.115),rough=.88)
boltmat=mat("V7 | titanium fasteners",(.41,.45,.46),metal=.88,rough=.18)
for m,scale,strength,dist in [(floor,175,.22,.008),(wall,85,.14,.015)]:
    nodes=m.node_tree.nodes
    p=nodes.get("Principled BSDF")
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=scale
    noise.inputs["Detail"].default_value=3.3
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=strength
    bump.inputs["Distance"].default_value=dist
    m.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"],p.inputs["Normal"])

def cube(name,pos,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Manufacturer edge radii","BEVEL")
        mod.width=bevel
        mod.segments=3
        mod.affect="EDGES"
        o.modifiers.new("Weighted manufacturing normals","WEIGHTED_NORMAL")
    return o

def cylinder(name,pos,radius,depth,material,vertices=32,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=pos)
    obj=bpy.context.object
    obj.name=name
    if rot:obj.rotation_euler=rot
    obj.data.materials.append(material)
    bevel=obj.modifiers.new("Smooth machined edges","BEVEL")
    bevel.width=.003
    bevel.segments=3
    return obj

ground=cube("Real textured studio floor",(0,.8,-.105),(10,12,.21),floor,.035)
bpy.context.view_layer.objects.active=ground
bpy.ops.rigidbody.object_add(type="PASSIVE")
ground.rigid_body.friction=.65
ground.rigid_body.restitution=.12
cube("Deep studio wall",(0,5.4,3.2),(10,.18,7),wall,.016)
for side in (-1,1):
    x=side*(W/2+.09)
    cube("Extruded vertical support "+str(side),(x,0,1.35),(.075,.13,2.7),support,.016)
    cube("Weighted floor anchor "+str(side),(x,-.10,.11),(.34,.68,.22),support,.024)
    for z in (.74,1.80,2.38):
        cube("Clamp steel top "+str(side)+" "+str(z),(x-side*.042,-.045,z),(.19,.105,.14),support,.011)
        cube("Clamp rubber face "+str(side)+" "+str(z),(x-side*.102,-.012,z),(.062,.024,.108),rubber,.007)
        for q in (-1,1):
            cylinder("Clamp hex bolt "+str(side)+" "+str(z)+" "+str(q),
                     (x+q*.055,-.103,z),.022,.026,boltmat,6,(math.pi/2,0,0))

pane=cube("Whole unbroken 10mm glazing",(0,0,Z),(W,T,H),glass,.002)
def hide(o,frame,on):
    o.hide_render=on
    o.keyframe_insert(data_path="hide_render",frame=frame)

hide(pane,1,False)
hide(pane,HIT-1,False)
hide(pane,HIT,True)
hide(pane,84,True)

# Interlocking radial-and-circumferential crack network:
# unlike Voronoi cells, each branch originates at the central projectile impact.
SECTORS=21
RINGS=[0,.105,.225,.39,.61,.88,1.18,1.92]
base_angle=rng.uniform(-.11,.11)
angles=[base_angle + j*math.tau/SECTORS + rng.uniform(-.10,.10) for j in range(SECTORS)]
nodes={}
for rid,r in enumerate(RINGS):
    for j in range(SECTORS):
        if rid==0:
            nodes[rid,j]=(0.0,0.0)
            continue
        a=angles[j]+rng.uniform(-.08,.08)
        rad=r*(1+rng.uniform(-.17,.17)) if rid<len(RINGS)-1 else 1.92
        nodes[rid,j]=(rad*math.cos(a),rad*math.sin(a))

def clip_axis(poly,axis,limit,is_upper):
    if not poly:return []
    out=[]
    def inside(v):return v[axis]<=limit+1e-8 if is_upper else v[axis]>=limit-1e-8
    def val(v):return v[axis]-limit
    prev=poly[-1]
    for cur in poly:
        a,b=inside(prev),inside(cur)
        if a!=b:
            delta=val(cur)-val(prev)
            t=(-val(prev)/delta) if abs(delta)>1e-10 else 0
            out.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
        if b:out.append(cur)
        prev=cur
    return out

def panel_clip(poly):
    for axis,limit,upper in [(0,-W/2,False),(0,W/2,True),(1,-H/2,False),(1,H/2,True)]:
        poly=clip_axis(poly,axis,limit,upper)
        if len(poly)<3:return []
    clean=[]
    for v in poly:
        if not clean or math.dist(v,clean[-1])>1e-5:clean.append(v)
    if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-5:clean.pop()
    return clean

def poly_area(points):
    return abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points))))*.5

def fracture_mesh(name,poly):
    # True 3D closed prisms with consistent front/back normals, colored only at the cuts.
    cx=sum(a for a,b in poly)/len(poly)
    cz=sum(b for a,b in poly)/len(poly)
    n=len(poly)
    verts=[(x-cx,-T/2,z-cz) for x,z in poly]+[(x-cx,T/2,z-cz) for x,z in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for k in range(n):faces.append((k,(k+1)%n,(k+1)%n+n,k+n))
    mesh=bpy.data.meshes.new("Watertight fragment")
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(glass)
    mesh.materials.append(glassedge)
    mesh.update()
    for face in mesh.polygons:face.material_index=int(face.index>=2)
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.location=(cx,0,Z+cz)
    mod=ob.modifiers.new("Polished cut bevel","BEVEL")
    mod.width=.0009
    mod.segments=2
    return ob,cx,cz

parts=[]
for k in range(len(RINGS)-1):
    for j in range(SECTORS):
        nxt=(j+1)%SECTORS
        if k==0: poly=[nodes[0,j],nodes[1,j],nodes[1,nxt]]
        else: poly=[nodes[k,j],nodes[k+1,j],nodes[k+1,nxt],nodes[k,nxt]]
        poly=panel_clip(poly)
        if len(poly)>=3 and poly_area(poly)>.00012:
            parts.append((k,j,poly,poly_area(poly)))
print("CUSTOM_RADIAL_FRACTURE",len(parts),flush=True)
for i,(ring,j,poly,area) in enumerate(parts):
    ob,cx,cz=fracture_mesh(f"V7 physical radial fragment {i:03d}",poly)
    rad=math.hypot(cx,cz)
    delay=(0 if rad<.18 else (1 if rad<.38 else (2 if rad<.68 else (4 if rad<1.02 else 6))))
    release=HIT+delay
    hide(ob,1,True)
    hide(ob,HIT-1,True)
    hide(ob,HIT,False)
    # Animated rigid body before fracture becomes a true physics object afterward.
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active=ob
    bpy.ops.rigidbody.object_add(type="ACTIVE")
    ob.rigid_body.collision_shape="CONVEX_HULL"
    ob.rigid_body.mass=max(.005,area*T*1100)
    ob.rigid_body.collision_margin=.001
    ob.rigid_body.friction=.56
    ob.rigid_body.restitution=.10
    ob.rigid_body.linear_damping=.15
    ob.rigid_body.angular_damping=.21
    ob.rigid_body.use_margin=True
    ob.rigid_body.kinematic=True
    ob.rigid_body.keyframe_insert(data_path="kinematic",frame=1)
    ob.rigid_body.keyframe_insert(data_path="kinematic",frame=release)
    initial=Vector((cx,0,Z+cz))
    ob.location=initial
    ob.keyframe_insert(data_path="location",frame=release)
    # Impact impulse spread: force is strongest near the bullet and delayed
    # for the heavy outside sheet pieces.
    shock=1/(1+3*rad)
    speed=(.07+.20*shock)*rng.uniform(.72,1.22)
    outward=Vector((cx/(rad+.04),0,cz/(rad+.04)))
    ob.location=initial+Vector((outward.x*speed, .10+.24*shock, outward.z*speed+.04))
    ob.keyframe_insert(data_path="location",frame=release+2)
    ob.rotation_euler=(rng.uniform(-.10,.10),rng.uniform(-.12,.12),rng.uniform(-.05,.05))
    ob.keyframe_insert(data_path="rotation_euler",frame=release+2)
    ob.rigid_body.kinematic=False
    ob.rigid_body.keyframe_insert(data_path="kinematic",frame=release+3)

# Fine shards at the epicenter fly before the broad material separates.
tiny=mat("V7 crystalline small chip",(.83,.93,.95),rough=.09,trans=.80,ior=1.51)
for i in range(135):
    a=rng.random()*math.tau
    radius=.02+(.22*math.sqrt(rng.random()))
    x,z=radius*math.cos(a),radius*math.sin(a)
    size=rng.uniform(.003,.016)
    verts=[(-size,-.003,-size*.25),(size*.63,-.003,-size*.61),
           (0,-.003,size),(size*.05,.003,0)]
    faces=[(0,2,1),(0,1,3),(1,2,3),(2,0,3)]
    mesh=bpy.data.meshes.new("chip mesh")
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(tiny)
    ob=bpy.data.objects.new(f"Micro glass dust {i:03d}",mesh)
    bpy.context.collection.objects.link(ob)
    hide(ob,1,True)
    hide(ob,HIT-2,True)
    hide(ob,HIT-1,False)
    spin=[rng.uniform(-7,7) for _ in range(3)]
    vx=rng.uniform(.7,2.8)*x/(radius+.05)
    vy=rng.uniform(1,3.5)
    vz=rng.uniform(.4,1.7)+z/(radius+.05)
    for fr in (HIT-1,HIT+2,HIT+6,HIT+15,HIT+28,84):
        t=max(0,(fr-HIT+1)/24)
        ob.location=(x+vx*t,vy*t,Z+z+vz*t-4.9*t*t)
        ob.rotation_euler=tuple(v*t for v in spin)
        ob.keyframe_insert(data_path="location",frame=fr)
        ob.keyframe_insert(data_path="rotation_euler",frame=fr)

# Radial cracks at the moment before the first material moves.
crack=mat("V7 subtle photographic crack highlights",(.42,.60,.62),rough=.08,trans=.28)
def filament(name,a,b,radius):
    direction=Vector(b)-Vector(a)
    if direction.length<.0001:return
    bpy.ops.mesh.primitive_cylinder_add(vertices=5,radius=radius,depth=direction.length,location=(Vector(a)+Vector(b))/2)
    ob=bpy.context.object;ob.name=name
    ob.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
    ob.data.materials.append(crack)
    hide(ob,1,True);hide(ob,HIT-3,True);hide(ob,HIT-2,False);hide(ob,HIT+3,True)
for j in range(13):
    theta=math.tau*j/13+rng.uniform(-.10,.10)
    last=Vector((0,-.011,Z))
    r=0
    for seg in range(4):
        r+=rng.uniform(.055,.11)
        theta+=rng.uniform(-.11,.11)
        end=Vector((math.cos(theta)*r,-.011,Z+math.sin(theta)*r))
        filament("Fissure "+str(j)+" "+str(seg),last,end,.00065)
        last=end

# Smooth machined bearing steel, driven in and then deflected toward the floor.
bpy.ops.mesh.primitive_uv_sphere_add(segments=80,ring_count=40,radius=.10,location=(0,-3.25,Z))
ball=bpy.context.object
ball.name="V7 one-piece steel projectile"
ball.data.materials.append(steel)
for face in ball.data.polygons:face.use_smooth=True
bpoints=[(1,-3.42,Z),(13,-2.65,Z),(25,-1.25,Z),(34,-.43,Z),
         (38,-.07,Z),(41,.26,Z),(45,.71,Z-.04),(53,1.52,Z-.24),
         (62,2.3,.79),(70,2.84,.17),(75,3.08,.27),(81,3.31,.105),(84,3.48,.105)]
for fr,y,z in bpoints:
    ball.location=(0,y,z)
    ball.rotation_euler=(fr*.11,fr*.07,fr*.12)
    ball.keyframe_insert(data_path="location",frame=fr)
    ball.keyframe_insert(data_path="rotation_euler",frame=fr)

world=bpy.data.worlds.new("Poly Haven studio HDRI reflection rig")
S.world=world
world.use_nodes=True
nodes=world.node_tree.nodes
nodes.clear()
tex=nodes.new("ShaderNodeTexEnvironment")
tex.image=bpy.data.images.load(str(O/"assets"/"studio_small_09_1k.exr"),check_existing=True)
bg=nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value=.37
out=nodes.new("ShaderNodeOutputWorld")
world.node_tree.links.new(tex.outputs["Color"],bg.inputs["Color"])
world.node_tree.links.new(bg.outputs["Background"],out.inputs["Surface"])
def area(name,loc,energy,size,target,color):
    d=bpy.data.lights.new(name,"AREA")
    d.energy=energy;d.shape="RECTANGLE"
    d.size=size[0];d.size_y=size[1];d.color=color
    o=bpy.data.objects.new(name,d)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
area("Wide softbox main",(-3.7,-2.4,5.3),900,(3.0,5.0),(0,0,Z),(1,.96,.91))
area("Tall edge reflection",(3.0,1.8,4.2),880,(1.3,5.2),(0,0,Z),(.87,.96,1))
area("Overhead high reflection",(-1.0,1.6,5.2),550,(3.5,1.2),(0,0,Z),(1,1,1))
area("Camera side fill",(1.0,-4.2,3.5),220,(2.0,3),(0,0,Z),(1,1,1))

bpy.ops.object.camera_add(location=(2.76,-4.45,2.40))
cam=bpy.context.object
S.camera=cam
cam.data.lens=52
cam.data.clip_end=100
cam.data.dof.use_dof=True
cam.data.dof.focus_object=pane
cam.data.dof.aperture_fstop=10
def camera_key(fr,pos,target):
    cam.location=Vector(pos)
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.keyframe_insert(data_path="location",frame=fr)
    cam.keyframe_insert(data_path="rotation_euler",frame=fr)
camera_key(1,(2.84,-4.90,2.52),(0,0,1.59))
camera_key(35,(2.71,-4.47,2.38),(0,0,1.61))
camera_key(HIT,(2.63,-4.31,2.33),(0,.09,1.60))
camera_key(84,(2.48,-4.24,2.31),(0,.38,1.57))

if S.rigidbody_world:
    S.rigidbody_world.substeps_per_frame=18
    S.rigidbody_world.solver_iterations=12
    S.rigidbody_world.point_cache.frame_start=1
    S.rigidbody_world.point_cache.frame_end=84
S.frame_set(1)
saved=O/"V7_ONE_PANE_PHYSICS_MASTER.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
info={"frames":84,"fps":24,"resolution":[720,1280],"impact_frame":HIT,
      "glass_panels":1,"rigid_body_fragments":len(parts),"micro_shards":135,
      "fracture_shape":"radial spiderweb with branching concentric cells",
      "method":"native Blender active rigidbody with animated kinematic release, real glass transmission and studio HDRI"}
(O/"scene_info.json").write_text(json.dumps(info,indent=2),encoding="utf8")
print("V7_SCENE_READY",saved,"PHYSICS_PIECES",len(parts),flush=True)
