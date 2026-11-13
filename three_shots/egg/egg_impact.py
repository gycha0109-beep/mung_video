import bpy, math, random, sys, os
from pathlib import Path
from mathutils import Vector, noise
from math import pi, sin, cos
from mathutils import Quaternion
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"three_shots"/"egg"/"impact"
OUT.mkdir(exist_ok=True)
MODE=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
random.seed(20261111)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for mat in tuple(bpy.data.materials):
    if mat.users==0: bpy.data.materials.remove(mat)
scene=bpy.context.scene
scene.render.engine='CYCLES'
try:
    cp=bpy.context.preferences.addons["cycles"].preferences
    cp.compute_device_type="CUDA"
    cp.get_devices()
    for device in cp.devices: device.use=(device.type=="CUDA")
    scene.cycles.device="GPU"
    print("CUDA_GPU_ENABLED",[(d.name,d.use) for d in cp.devices],flush=True)
except Exception as exc:
    scene.cycles.device="CPU"
    print("FALLBACK_CPU",repr(exc),flush=True)
scene.cycles.samples = 14 if MODE=="preview" else 24
scene.cycles.use_denoising=True
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=68 if MODE=="preview" else 100
scene.render.fps=24
scene.frame_start=1
scene.frame_end=48
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.film_transparent=False
scene.render.image_settings.compression=28
scene.camera=None
scene.gravity=(0,0,-9.81)
scene.render.threads_mode="FIXED"
scene.render.threads=8
world=bpy.data.worlds.new("HDRI overcast blue sky")
scene.world=world
world.use_nodes=True
w=world.node_tree
bg=w.nodes.get("Background")
env_path=ROOT/"outdoor.exr"
if env_path.exists():
    tex=w.nodes.new("ShaderNodeTexEnvironment")
    tex.image=bpy.data.images.load(str(env_path))
    w.links.new(tex.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value=.32
else:
    bg.inputs["Color"].default_value=(.27,.36,.47,1)
    bg.inputs["Strength"].default_value=.9

def mat_physical(name, base, rough=.82, metallic=0, noise_scale=4, bump=.075):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    n=mat.node_tree.nodes
    l=mat.node_tree.links
    b=n.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*base,1)
    b.inputs["Roughness"].default_value=rough
    b.inputs["Metallic"].default_value=metallic
    tex=n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=noise_scale
    tex.inputs["Detail"].default_value=4
    tex.inputs["Roughness"].default_value=.67
    ramp=n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.25
    ramp.color_ramp.elements[0].color=(*(c*.72 for c in base),1)
    ramp.color_ramp.elements[1].position=.72
    ramp.color_ramp.elements[1].color=(*(min(1,c*1.21) for c in base),1)
    l.new(tex.outputs["Fac"],ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"],b.inputs["Base Color"])
    fine=n.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value=noise_scale*24
    fine.inputs["Detail"].default_value=3
    bn=n.new("ShaderNodeBump")
    bn.inputs["Strength"].default_value=.32
    bn.inputs["Distance"].default_value=bump
    l.new(fine.outputs["Fac"],bn.inputs["Height"])
    l.new(bn.outputs["Normal"],b.inputs["Normal"])
    return mat
brick_mats=[]
tile_dir=ROOT/"physics_proof_v1"/"wall_tiles"
tile_ids=[0,2,5,8,10]
for idx in tile_ids:
    mt=bpy.data.materials.new("PHOTOGRAMMETRY BRICK %02d"%idx)
    mt.use_nodes=True
    n=mt.node_tree.nodes
    l=mt.node_tree.links
    b=n.get("Principled BSDF")
    b.inputs["Roughness"].default_value=.88
    uv=n.new("ShaderNodeTexCoord")
    color=n.new("ShaderNodeTexImage")
    color.image=bpy.data.images.load(str(tile_dir/("%02d_color.png"%idx)))
    color.image.pack()
    color.extension="EXTEND"
    l.new(uv.outputs["UV"],color.inputs["Vector"])
    l.new(color.outputs["Color"],b.inputs["Base Color"])
    rough=n.new("ShaderNodeTexImage")
    rough.image=bpy.data.images.load(str(tile_dir/("%02d_rough.png"%idx)))
    rough.image.colorspace_settings.name="Non-Color"
    rough.image.pack()
    rough.extension="EXTEND"
    l.new(uv.outputs["UV"],rough.inputs["Vector"])
    mix=n.new("ShaderNodeMixRGB")
    mix.blend_type='MIX'
    mix.inputs[0].default_value=.35
    mix.inputs[1].default_value=(.85,.85,.85,1)
    l.new(rough.outputs["Color"],mix.inputs[2])
    l.new(mix.outputs["Color"],b.inputs["Roughness"])
    norm=n.new("ShaderNodeTexImage")
    norm.image=bpy.data.images.load(str(tile_dir/("%02d_normal.png"%idx)))
    norm.image.colorspace_settings.name="Non-Color"
    norm.image.pack()
    norm.extension="EXTEND"
    l.new(uv.outputs["UV"],norm.inputs["Vector"])
    normal=n.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value=.78
    l.new(norm.outputs["Color"],normal.inputs["Color"])
    l.new(normal.outputs["Normal"],b.inputs["Normal"])
    brick_mats.append(mt)
core=mat_physical("Broken reddish terracotta gritty core",(.31,.115,.061),.97,0,27,.018)
mortar=mat_physical("Uneven mortar cement",(.35,.342,.30),.96,0,52,.01)
concrete=mat_physical("Weathered concrete pores",(.29,.29,.275),.89,0,37,.008)
steel=mat_physical("Used stainless ball micro-scratches",(.24,.28,.31),.23,.92,38,.0008)
steel_b=steel.node_tree.nodes.get("Principled BSDF")
steel_b.inputs["Coat Weight"].default_value=.22
steel_b.inputs["Coat Roughness"].default_value=.13

def box(name, xyz, dims, mat, bevel=.006):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    obj=bpy.context.object
    obj.name=name
    obj.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new("Chipped rounded edges","BEVEL")
        mod.width=bevel
        mod.segments=3
        obj.modifiers.new("Weighted normal","WEIGHTED_NORMAL")
    return obj

def face_brick_uv(ob,dimx,dimz):
    # Image tile covers each brick front/back face; not six default cube atlas islands.
    me=ob.data
    uv=me.uv_layers.active or me.uv_layers.new(name="Brick-face")
    if len(me.materials)==1:me.materials.append(core)
    for face in me.polygons:
        if abs(face.normal.y)>.5:
            face.material_index=0
            for li in face.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv=(v.x/dimx+.5,v.z/dimz+.5)
        else:
            face.material_index=1
            for li in face.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv=(v.y/D+.5,v.z/dimz+.5)

def rigid(ob, passive=False, mass=2.5, friction=.72, bounce=.05, start_sleep=False):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active=ob
    bpy.ops.rigidbody.object_add(type='PASSIVE' if passive else 'ACTIVE')
    rb=ob.rigid_body
    rb.friction=friction
    rb.restitution=bounce
    rb.collision_shape='BOX' if passive else 'CONVEX_HULL'
    rb.use_margin=True
    rb.collision_margin=.0012
    if not passive:
        rb.mass=mass
        rb.linear_damping=.075
        rb.angular_damping=.09
        rb.use_deactivation=True
        rb.use_start_deactivated=start_sleep
    return ob

# Ground and back studio background are collision and visible set pieces.
floor=box("CONCRETE FLOOR", (0,0,-.13),(28,29,.25), concrete,.008)
rigid(floor,passive=True,friction=.83)
# The back of the wall remains open so fragments travel naturally into open space.
# Wall bricks laid with staggered joints.
NW=12
NH=10
BW=.445
BH=.225
D=.28
GAPX=.011
GAPZ=.011
W=NW*BW
rows=list(range(NH))
fragments=[]
active_bricks=[]
passive_bricks=[]
impactrow=5
impactcol=(NW-1)/2
impactz=.125+(impactrow+.5)*BH
def polygon_area_centroid(poly):
    cross=0; cx=0; cz=0
    for i,(x,z) in enumerate(poly):
        x2,z2=poly[(i+1)%len(poly)]
        a=x*z2-x2*z
        cross+=a;cx+=(x+x2)*a;cz+=(z+z2)*a
    if abs(cross)<1.e-7:
        return (sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly))
    return cx/(3*cross),cz/(3*cross)
def cut_half(poly,nx,nz,const):
    out=[]
    for i,A in enumerate(poly):
        B=poly[(i+1)%len(poly)]
        fa=nx*A[0]+nz*A[1]-const
        fb=nx*B[0]+nz*B[1]-const
        if fa<=0:out.append(A)
        if (fa<=0)!=(fb<=0):
            t=fa/(fa-fb)
            out.append((A[0]+(B[0]-A[0])*t, A[1]+(B[1]-A[1])*t))
    return out
def voronoi_cells(w,h, count):
    seeds=[(random.uniform(-w*.37,w*.37),random.uniform(-h*.36,h*.36)) for _ in range(count)]
    out=[]
    for idx,(px,pz) in enumerate(seeds):
        poly=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
        for j,(ox,oz) in enumerate(seeds):
            if j==idx:continue
            nx=ox-px;nz=oz-pz
            cons=((ox*ox+oz*oz)-(px*px+pz*pz))*.5
            poly=cut_half(poly,nx,nz,cons)
            if len(poly)<3:break
        if len(poly)>=3:out.append(poly)
    return out
def chunk(name, at, poly, depth, material, mat_inner):
    cx,cz=polygon_area_centroid(poly)
    # Each independent irregular convex cell is its own active physical object.
    verts=[]
    n=len(poly)
    for fy in (-depth/2,depth/2):
        for x,z in poly:
            verts.append((x-cx,fy,z-cz))
    faces=[tuple(reversed(list(range(n)))),tuple(range(n,n*2))]
    face_mats=[0,0]
    for j in range(n):
        k=(j+1)%n
        faces.append((j,k,k+n,j+n))
        face_mats.append(1)
    me=bpy.data.meshes.new(name+"-mesh")
    me.from_pydata(verts,[],faces)
    me.validate()
    me.update()
    uv=me.uv_layers.new(name="Face mapping")
    for fi,polyface in enumerate(me.polygons):
        for loop in polyface.loop_indices:
            vi=me.loops[loop].vertex_index
            v=me.vertices[vi].co
            if fi in (0,1):
                uv.data[loop].uv=((v.x+cx)/BW+.5,(v.z+cz)/BH+.5)
            else:
                uv.data[loop].uv=(v.y/D+.5,v.z/BH+.5)
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    ob.location=(at[0]+cx,at[1],at[2]+cz)
    me.materials.append(material)
    me.materials.append(mat_inner)
    for f,ind in zip(me.polygons,face_mats):
        f.material_index=ind
        f.use_smooth=False
    mod=ob.modifiers.new("Fractured crisp edge bevel","BEVEL")
    mod.width=.004
    mod.segments=2
    ob.modifiers.new("Normal smoothing","WEIGHTED_NORMAL")
    return ob

for row in range(NH):
    for col in range(NW):
        ox=(col-(NW-1)/2)*BW + (.5*BW if row%2 else 0)
        oz=.115+row*BH
        if abs(ox)>W/2-.10:continue
        xx=ox+random.uniform(-.0025,.0025)
        yy=random.uniform(-.004,.004)
        zz=oz+random.uniform(-.0015,.0015)
        mat=random.choice(brick_mats)
        dx=BW-GAPX-random.uniform(0,.004)
        dz=BH-GAPZ-random.uniform(0,.003)
        distance=math.sqrt((xx/.76)**2+((zz-impactz)/.52)**2)
        near=False
        fracture=False
        if fracture:
            cells=voronoi_cells(dx,dz,random.choice([4,5,6]))
            for i,cell in enumerate(cells):
                ob=chunk("PHYSICS fracture %d %d %d"%(row,col,i),(xx,yy,zz),cell,D,mat,core)
                rigid(ob,mass=0.65,friction=.79,bounce=.018,start_sleep=True)
                fragments.append(ob)
        elif near:
            ob=box("PHYSICS whole displaced brick %d %d"%(row,col),(xx,yy,zz),(dx,D,dz),mat,.006)
            face_brick_uv(ob,dx,dz)
            ob.rotation_euler=(random.uniform(-.01,.01),0,random.uniform(-.01,.01))
            rigid(ob,mass=2.8,friction=.84,bounce=.024,start_sleep=True)
            active_bricks.append(ob)
        else:
            ob=box("STATIC surrounding wall %d %d"%(row,col),(xx,yy,zz),(dx,D,dz),mat,.007)
            face_brick_uv(ob,dx,dz)
            rigid(ob,passive=True,friction=.92,bounce=.015)
            passive_bricks.append(ob)
# Concrete footing strip holds bottom bricks.
ledge=box("Wall concrete footing",(0,0,-.002),(W+.35,.48,.12),mortar,.013)
rigid(ledge,passive=True)
# Spheres: actual dynamic collision; 0->near target move animated then Bullet takes over.
bpy.ops.mesh.primitive_uv_sphere_add(segments=72,ring_count=48,radius=.155,location=(-.31,-3.1,impactz+.14))
ball=bpy.context.object
ball.name="PHYSICS EGG SHELL BEFORE IMPACT"
eggshell=mat_physical("Eggshell porous off-white",(.78,.72,.58),.49,0,64,.0012)
ball.data.materials.append(eggshell)
for vert in ball.data.vertices:
    z=vert.co.z/.155
    width=1+.12*z-.09*z*z
    vert.co.x*=.81*width
    vert.co.y*=.81*width
    vert.co.z*=1.22
for frame,hidden in ((1,False),(13,False),(14,True),(48,True)):
    ball.hide_render=hidden
    ball.keyframe_insert(data_path="hide_render",frame=frame)
for f in ball.data.polygons:f.use_smooth=True
rigid(ball,mass=.11,friction=.2,bounce=.02,start_sleep=False)
ball.rigid_body.collision_shape='SPHERE'
ball.rigid_body.use_margin=True
ball.rigid_body.collision_margin=.001
for frame,y in [(1,-3.1),(8,-1.42),(11,-.69),(12,-.445),(13,-.31)]:
    ball.location=(-.31 + .31*(frame-1)/12,y,impactz+.14-.14*(frame-1)/12)
    ball.keyframe_insert(data_path="location",frame=frame)
for frame,value in ((1,True),(12,True),(13,False)):
    ball.rigid_body.kinematic=value
    ball.rigid_body.keyframe_insert(data_path='kinematic',frame=frame)

# Egg ruptures on contact. Breakage is timed, but each shell segment receives real rigid-body motion.
# Fluid surfaces are a controllable stylized effect, not a Navier-Stokes simulation.
inner=mat_physical("Eggshell inner cream",(.63,.56,.43),.77,0,25,.0006)
yolk=bpy.data.materials.new("Rich wet egg yolk")
yolk.use_nodes=True
yb=yolk.node_tree.nodes["Principled BSDF"]
yb.inputs["Base Color"].default_value=(.89,.49,.014,1)
yb.inputs["Roughness"].default_value=.13
yb.inputs["Coat Weight"].default_value=.54
yb.inputs["Coat Roughness"].default_value=.12
eggwhite=bpy.data.materials.new("Wet translucent egg white")
eggwhite.use_nodes=True
wb=eggwhite.node_tree.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value=(.92,.94,.89,1)
wb.inputs["Roughness"].default_value=.12
wb.inputs["Transmission Weight"].default_value=.88
wb.inputs["IOR"].default_value=1.335
shard_count=0
center=Vector((0,-.31,impactz))
for band in range(3):
    for sect in range(12):
        theta1=.15+band*(math.pi-.3)/3
        theta2=.15+(band+1)*(math.pi-.3)/3
        phi1=2*math.pi*sect/12
        phi2=2*math.pi*(sect+1)/12
        radius=.128
        def xy(theta,phi,rr):
            return (rr*math.sin(theta)*math.cos(phi),
                rr*math.sin(theta)*math.sin(phi),rr*math.cos(theta))
        pts=[xy(t,p,r) for r in (radius,radius-.005)
             for t,p in ((theta1,phi1),(theta1,phi2),(theta2,phi2),(theta2,phi1))]
        m=bpy.data.meshes.new("ceramic shell piece")
        m.from_pydata(pts,[],[(0,1,2,3),(4,7,6,5),(0,4,5,1),
                               (1,5,6,2),(2,6,7,3),(3,7,4,0)])
        m.update()
        ob=bpy.data.objects.new("PHYSICAL EGG SHELL %02d %02d"%(band,sect),m)
        bpy.context.collection.objects.link(ob)
        m.materials.append(eggshell);m.materials.append(inner)
        for face in m.polygons:face.material_index=1 if face.index else 0
        ob.location=center
        rigid(ob,mass=.007,friction=.4,bounce=.15)
        ob.rigid_body.collision_shape='CONVEX_HULL'
        for f,loc in ((1,center),(13,center),
                      (14,center+Vector((math.cos(phi1)*.021,-.044-math.sin(theta1)*.016,
                                         math.cos(theta1)*.025)))):
            ob.location=loc
            ob.keyframe_insert(data_path="location",frame=f)
        for f,on in ((1,True),(14,True),(15,False)):
            ob.rigid_body.kinematic=on
            ob.rigid_body.keyframe_insert(data_path="kinematic",frame=f)
        for f,hide in ((1,True),(13,True),(14,False),(48,False)):
            ob.hide_render=hide
            ob.keyframe_insert(data_path="hide_render",frame=f)
        ob.rotation_euler[2]=random.uniform(-.25,.25)
        shard_count+=1

# Wall-facing wet fluid lobes grow against the front of the brick surface.
def blob(name,x,z,rx,rz,mat,appear=14):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=26,ring_count=16,radius=1,location=(x,-.195,z))
    ob=bpy.context.object
    ob.name=name
    ob.data.materials.append(mat)
    for f in ob.data.polygons:f.use_smooth=True
    for frame,scale in ((1,(.0001,.0001,.0001)),
                        (appear,(.001,.001,.001)),
                        (appear+3,(rx*.84,.018,rz*.75)),
                        (appear+9,(rx,.014,rz)),
                        (48,(rx,.013,rz*1.16))):
        ob.scale=scale
        ob.keyframe_insert(data_path="scale",frame=frame)
    return ob

blob("Egg white sticky spread central",-.02,impactz,.24,.18,eggwhite)
blob("Egg yolk vivid central",.022,impactz-.014,.16,.135,yolk)
for k in range(7):
    angle=2*math.pi*k/7+random.uniform(-.12,.12)
    dx=.25*math.cos(angle)
    dz=.20*math.sin(angle)
    blob("Egg white perimeter wet %02d"%k,dx,impactz+dz,
         random.uniform(.025,.055),random.uniform(.017,.04),eggwhite,appear=15+k%3)
for k in range(6):
    x=random.uniform(-.16,.14)
    z=impactz+random.uniform(-.12,.11)
    ob=blob("Egg yolk sticky drip %02d"%k,x,z,.019,.045,yolk,appear=15+k%4)
    for f,zval in ((1,z),(17,z),(32,z-random.uniform(.12,.25)),(48,z-random.uniform(.2,.37))):
        ob.location.z=zval
        ob.keyframe_insert(data_path="location",frame=f)

# Physical droplets also collide with the wall / floor, distinct from deforming wet splats.
for k in range(16):
    theta=random.uniform(0,2*math.pi)
    rr=random.uniform(.018,.047)
    m=yolk if k%4 else eggwhite
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=rr,
        location=(random.uniform(-.09,.09),-.34,impactz+random.uniform(-.10,.10)))
    ob=bpy.context.object
    ob.name="DYNAMIC egg droplet %02d"%k
    ob.data.materials.append(m)
    rigid(ob,mass=.004,friction=.21,bounce=.07)
    ob.rigid_body.collision_shape='SPHERE'
    orig=ob.location.copy()
    step=Vector((math.cos(theta)*.05,-random.uniform(.08,.16),
                 math.sin(theta)*.055))
    for f,loc in ((1,orig),(13,orig),(14,orig+step)):
        ob.location=loc
        ob.keyframe_insert(data_path="location",frame=f)
    for f,on in ((1,True),(14,True),(15,False)):
        ob.rigid_body.kinematic=on
        ob.rigid_body.keyframe_insert(data_path="kinematic",frame=f)
    for f,hide in ((1,True),(13,True),(14,False),(48,False)):
        ob.hide_render=hide
        ob.keyframe_insert(data_path="hide_render",frame=f)
print("PHYSICALLY_SIMULATED_EGG_SHELLS",shard_count,"DROPLETS",16,flush=True)

# Strong physics solver to ensure bullet contact and settling.
rbw=scene.rigidbody_world
rbw.substeps_per_frame=100
rbw.solver_iterations=25
rbw.point_cache.frame_start=1
rbw.point_cache.frame_end=48
# Camera: slight oblique witness, bullet entering at left of the frame.
camera_data=bpy.data.cameras.new("Cinematic close impact lens")
camera=bpy.data.objects.new("CINEMATIC CAMERA",camera_data)
bpy.context.collection.objects.link(camera)
scene.camera=camera
camera.location=(1.65,-5.1,1.69)
look=Vector((-.08,-.16,impactz))
camera.rotation_euler=(look-Vector(camera.location)).to_track_quat('-Z','Y').to_euler()
camera.data.lens=31
camera.data.clip_start=.01
camera.data.clip_end=120
# A motivated reverse-angle cut at impact exposes the physically moving fragments.
front_loc=camera.location.copy()
front_rot=camera.rotation_euler.copy()
for f in (1,14):
    camera.location=front_loc
    camera.rotation_euler=front_rot
    camera.data.lens=31
    camera.keyframe_insert(data_path="location",frame=f)
    camera.keyframe_insert(data_path="rotation_euler",frame=f)
    camera.data.keyframe_insert(data_path="lens",frame=f)
back_loc=front_loc.copy()
back_target=Vector((-.08,-.16,impactz))
back_rot=(back_target-back_loc).to_track_quat('-Z','Y').to_euler()
for f in (15,48):
    camera.location=back_loc
    camera.rotation_euler=back_rot
    camera.data.lens=31
    camera.keyframe_insert(data_path="location",frame=f)
    camera.keyframe_insert(data_path="rotation_euler",frame=f)
    camera.data.keyframe_insert(data_path="lens",frame=f)
# Soft outdoor rays, cool skylight and low-angle side accent.
def area(name,loc,power,size_x,size_y,color,target):
    dat=bpy.data.lights.new(name,"AREA")
    obj=bpy.data.objects.new(name,dat)
    bpy.context.collection.objects.link(obj)
    obj.location=loc
    dat.energy=power
    dat.shape="RECTANGLE"
    dat.size=size_x
    dat.size_y=size_y
    dat.color=color
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
area("Warm courtyard reflected light",(-3.7,-3.8,6),640,6,5,(1,.87,.74),(0,0,1.5))
area("Wide cool environment fill",(2.4,-1.5,6),460,7,4,(.73,.86,1),(0,0,1))
area("Thin crisp specular rim",(-1.2,1,3.6),330,3,4,(1,.97,.90),(0,0,1.5))
bpy.ops.object.light_add(type='SUN',location=(-2,-3,6))
sun=bpy.context.object
sun.name="Pale afternoon sun"
sun.data.energy=.95
sun.data.angle=.14
sun.rotation_euler=(.53,-.43,.26)
# Dust is a softly textured volumetric medium (no fake bright particle spheres).
volmat=bpy.data.materials.new("Low density scattered clay dust")
volmat.use_nodes=True
nodes=volmat.node_tree.nodes
nodes.clear()
out=nodes.new("ShaderNodeOutputMaterial")
v=nodes.new("ShaderNodeVolumePrincipled")
v.inputs["Color"].default_value=(.49,.32,.22,1)
v.inputs["Density"].default_value=0
v.inputs["Anisotropy"].default_value=.38
volmat.node_tree.links.new(v.outputs["Volume"],out.inputs["Volume"])
dust=box("CINEMATIC DUST / post-impact",(0,.48,impactz), (1.95,.95,1.38),volmat,0)
for frame,density in ((1,0),(12,0),(16,0),(19,0),(26,0),(36,0),(48,0)):
    v.inputs["Density"].default_value=density
    v.inputs["Density"].keyframe_insert(data_path="default_value",frame=frame)
# Readable close evidence and frame logs.
if MODE=="preview":
    scene.render.resolution_percentage=65
    scene.cycles.samples=12
else:
    scene.render.resolution_percentage=100
    scene.cycles.samples=24
scene.frame_set(1)
blend=OUT/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print("SAVED_SCENE",blend,"RIGID_BODIES",len(fragments)+len(active_bricks)+len(passive_bricks)+4,
      "FRACTURE_PIECES",len(fragments),"ACTIVE_BRICKS",len(active_bricks),flush=True)
# Sequential frame evaluation to ensure physics runs and to record non-keyframed velocities.
logs=[]
for frame in range(1,49):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    if frame in (1,12,14,17,20,24,32,40,48):
        def wpos(ob):
            p=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
            return tuple(round(v,4) for v in p)
        pball=wpos(ball)
        mov=[]
        for ob in fragments+active_bricks:
            p=wpos(ob)
            orig=ob.location
            d=math.sqrt(sum((p[k]-orig[k])**2 for k in range(3)))
            if d>.04:mov.append(round(d,3))
        logs.append((frame,pball,len(mov),round(max(mov) if mov else 0,3)))
        print("PHYSICS_SAMPLE",frame,pball,"MOVED",len(mov),"MAX_SHIFT",round(max(mov) if mov else 0,3),flush=True)
logpath=OUT/"physics_samples.txt"
logpath.write_text("\n".join(str(line) for line in logs),encoding="utf-8")
if MODE=="preview":
    frames=[1,12,17,22,32,44]
    preview=OUT/"preview"
    preview.mkdir(exist_ok=True)
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath=str(preview/("proof_%03d.png"%f))
        bpy.ops.render.render(write_still=True)
        print("PREVIEW_RENDERED",f,flush=True)
elif MODE=="video":
    frames=OUT/"frames"
    frames.mkdir(exist_ok=True)
    scene.render.filepath=str(frames/"frame_")
    bpy.ops.render.render(animation=True)
    print("VIDEO_RENDER_DONE",flush=True)
