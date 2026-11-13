import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v1"
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261113
rng=random.Random(SEED)
PANELS=20
DIST=1.65
PANEL_W=1.85
PANEL_H=2.18
PANEL_Z=1.48
FPS=24
FRAMES=192
START=57
E0=112.0
assert bpy.app.version >= (5,2,0), bpy.app.version
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials:
    if d.users==0:bpy.data.materials.remove(d)

def mat(name,c,metal=0,rough=.3,trans=0,alpha=1,emission=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Transmission Weight"].default_value=trans
    p.inputs["Alpha"].default_value=alpha
    if emission:
        p.inputs["Emission Color"].default_value=(*c,1)
        p.inputs["Emission Strength"].default_value=emission
    return m

glass=mat("Tempered glass | cyan-tinted transmissive",(.58,.86,.94),rough=.11,trans=.05,alpha=.34)
glass.surface_render_method="BLENDED"
glass_edge=mat("Fresh glass fracture facets",(.19,.70,.82),rough=.16,trans=.28,alpha=.97)
steel=mat("Machined steel | steel sphere",(.67,.71,.75),metal=1,rough=.18)
metal=mat("Brushed aluminium brackets",(.29,.39,.46),metal=.86,rough=.26)
rubber=mat("Industrial rubber | projectile pouch",(.16,.12,.10),rough=.75)
wood=mat("Polished dark hardwood",(.24,.13,.068),rough=.55)
floor=mat("Deep graphite laboratory concrete",(.062,.085,.10),rough=.62)
back=mat("Blue-dark stage environment",(.018,.036,.053),rough=.8)
strip=mat("Cold cyan running light",(.18,.72,1),rough=.24,emission=7.5)
hot=mat("Warm laboratory highlights",(.99,.67,.38),rough=.2,emission=2.0)
crack_mat=mat("White glass stressed cracks",(.79,.94,1),rough=.26,emission=.65)

def cube(name,loc,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new("Clean bevel highlights","BEVEL")
        m.width=bevel
        m.segments=2
        n=o.modifiers.new("Weighted normal","WEIGHTED_NORMAL")
    return o

def cylinder_between(name,a,b,radius,material,vertices=14):
    direction=Vector(b)-Vector(a)
    mid=(Vector(a)+Vector(b))/2
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=direction.length,location=mid)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
    o.data.materials.append(material)
    return o

ground=cube("Ground | catch falling glass",(0,11,-.07),(9.0,58.0,.14),floor,.03)
bpy.context.view_layer.objects.active=ground
bpy.ops.rigidbody.object_add(type="PASSIVE")
ground.rigid_body.friction=.58
ground.rigid_body.restitution=.16
cube("Rear wall",(0,34.5,3.7),(9,.3,7.4),back)
for side in [-1,1]:
    x=side*2.65
    cube("Runway rail",(x,11,.035),(.10,57,.06),metal,.02)
    cube("LED runway stripe",(x,11,.086),(.04,57,.018),strip)
    for y in range(-7,34,7):
        cube("Recessed indicator",(x,y,.2),(.06,.48,.2),hot,.012)

# Relatively compact 20-pane 50m-like testing corridor.
energy=E0
events=[]
for idx in range(PANELS):
    cost=4.0 + .28*idx + rng.uniform(-.28,.28)
    f=START+3*idx+round(.16*idx*idx)
    passed=energy>=cost
    if passed:energy-=cost
    events.append(dict(number=idx+1,frame=f,y=idx*DIST,required_energy=round(cost,3),energy_after=round(energy,3),broken=bool(passed)))
BROKEN=sum(e["broken"] for e in events)
FIRST_STOP=next((e for e in events if not e["broken"]),None)
assert 12 <= BROKEN < PANELS,(BROKEN,events)
print("GLASS_ENERGY_MODEL",E0,"BROKEN",BROKEN,"STOP",FIRST_STOP,flush=True)

def visibility(o, frame, visible):
    o.hide_render=not visible
    o.keyframe_insert(data_path="hide_render",frame=frame)
    o.hide_viewport=not visible
    o.keyframe_insert(data_path="hide_viewport",frame=frame)

def polygon_shard(name,xzpoints,cy,material):
    # Thin closed prism with bevel-like material on the fracture edge.
    n=len(xzpoints)
    verts=[(x,cy-.011,z+PANEL_Z) for x,z in xzpoints]+[(x,cy+.011,z+PANEL_Z) for x,z in xzpoints]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for k in range(n):
        t=(k+1)%n
        faces.append((k,t,t+n,k+n))
    mesh=bpy.data.meshes.new(name+" geometry")
    mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(material)
    mesh.materials.append(glass_edge)
    for face in mesh.polygons:
        face.material_index=1 if face.index>=2 else 0
    return ob

def dist_to_edge(theta):
    dx,dz=math.cos(theta),math.sin(theta)
    return min((PANEL_W*.5)/(abs(dx)+1e-9),(PANEL_H*.5)/(abs(dz)+1e-9))

SHARD_COUNT=0
for event in events:
    idx=event["number"]-1
    y=event["y"]
    f=event["frame"]
    # Each panel keeps its clean intact outline until the actual contact frame.
    pane=cube(f"Glass sheet {idx+1:02d} | intact",(0,y,PANEL_Z),(PANEL_W,.026,PANEL_H),glass,.005)
    if event["broken"]:
        visibility(pane,1,True)
        visibility(pane,f-1,True)
        visibility(pane,f,False)
        visibility(pane,FRAMES,False)
    # Metallic holders are NOT a border; impact can shatter entire glass pane.
    for side in [-1,1]:
        x=side*(PANEL_W*.5+.085)
        cube(f"Pane stand {idx+1:02d}",(x,y,.77),(.037,.09,1.54),metal,.009)
        cube(f"Pane clamp {idx+1:02d}",(x-side*.045,y,PANEL_Z-PANEL_H*.31),(.10,.10,.065),metal,.009)
        cube(f"Pane upper clamp {idx+1:02d}",(x-side*.045,y,PANEL_Z+PANEL_H*.40),(.10,.10,.065),metal,.009)
    if not event["broken"]:
        if idx==BROKEN:
            # Spider cracks on the stopping plate: no fake full shatter.
            for ray in range(11):
                a=ray*math.tau/11+.13
                p1=(.07*math.cos(a),y-.025,PANEL_Z+.07*math.sin(a))
                p2=(.48*math.cos(a+.06),y-.025,PANEL_Z+.47*math.sin(a+.06))
                crack=cylinder_between(f"STOP cracked radial {ray}",p1,p2,.0024,crack_mat,8)
                visibility(crack,1,False)
                visibility(crack,f-1,False)
                visibility(crack,f,True)
            print("STOP_PANE_CRACKED",idx+1)
        continue

    # Independent irregular tiles fracture into manageable glass fragments;
    # no enormous wedge is permitted to dominate the camera.
    nx,nz=6,6
    dx=PANEL_W/nx;dz=PANEL_H/nz
    points={}
    for ix in range(nx+1):
        for iz in range(nz+1):
            x=-PANEL_W/2+ix*dx
            z=-PANEL_H/2+iz*dz
            if 0<ix<nx and 0<iz<nz:
                x+=rng.uniform(-.09,.09)*dx
                z+=rng.uniform(-.13,.13)*dz
            points[(ix,iz)]=(x,z)
    part_num=0
    for ix in range(nx):
        for iz in range(nz):
            quad=[points[(ix,iz)],points[(ix+1,iz)],points[(ix+1,iz+1)],points[(ix,iz+1)]]
            # Smaller triangles in the actual steel-ball strike zone.
            if 2<=ix<=3 and 2<=iz<=3:
                center=(sum(p[0] for p in quad)/4,sum(p[1] for p in quad)/4)
                polys=[[center,quad[0],quad[1]],[center,quad[1],quad[2]],
                       [center,quad[2],quad[3]],[center,quad[3],quad[0]]]
            else:
                polys=[quad]
            for poly in polys:
                name=f"Pane {idx+1:02d} fragment {part_num:02d}"
                part_num+=1
                ob=polygon_shard(name,poly,y,glass)
                bpy.context.view_layer.objects.active=ob
                bpy.ops.object.select_all(action="DESELECT")
                ob.select_set(True)
                bpy.ops.rigidbody.object_add(type="ACTIVE")
                ob.rigid_body.collision_shape='CONVEX_HULL'
                ob.rigid_body.mass=.032+rng.uniform(.002,.027)
                ob.rigid_body.friction=.46
                ob.rigid_body.restitution=.18
                ob.rigid_body.collision_margin=.002
                ob.rigid_body.linear_damping=.08
                ob.rigid_body.angular_damping=.14
                ob.rigid_body.kinematic=True
                ob.rigid_body.keyframe_insert(data_path="kinematic",frame=1)
                ob.rigid_body.keyframe_insert(data_path="kinematic",frame=f)
                ob.location=(0,0,0)
                ob.keyframe_insert(data_path="location",frame=f)
                visibility(ob,1,False)
                visibility(ob,f-1,False)
                visibility(ob,f,True)
                cx=sum(p[0] for p in poly)/len(poly)
                cz=sum(p[1] for p in poly)/len(poly)
                dxr,dzr=cx/(PANEL_W/2),cz/(PANEL_H/2)
                bx=dxr*(.09+rng.random()*.10)+rng.uniform(-.025,.025)
                bz=dzr*(.07+rng.random()*.11)+rng.uniform(-.017,.025)
                by=.14+rng.uniform(.05,.16)
                ob.location=(bx,by,bz)
                ob.keyframe_insert(data_path="location",frame=f+1)
                ob.rotation_euler=(rng.uniform(-.26,.26),rng.uniform(-.29,.29),rng.uniform(-.22,.22))
                ob.keyframe_insert(data_path="rotation_euler",frame=f+1)
                ob.rigid_body.kinematic=False
                ob.rigid_body.keyframe_insert(data_path="kinematic",frame=f+2)
                SHARD_COUNT+=1

# Steel ball is keyed along progressively slower hit intervals.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.105,location=(0,-8.5,PANEL_Z))
ball=bpy.context.object;ball.name="STEEL BALL | decelerating"
ball.data.materials.append(steel)
for p in ball.data.polygons:p.use_smooth=True
ball_points=[(1,-8.5,PANEL_Z),(48,-8.5,PANEL_Z)]
ball_points += [(e["frame"],e["y"]-.05,PANEL_Z) for e in events if e["broken"]]
if FIRST_STOP:
    ff=FIRST_STOP["frame"]
    yy=FIRST_STOP["y"]
    ball_points += [(ff,yy-.13,PANEL_Z),(ff+4,yy-.72,PANEL_Z-.10),(ff+12,yy-1.65,PANEL_Z-.70),
                    (ff+21,yy-1.8,.20),(FRAMES,yy-1.9,.105)]
for f,y,z in ball_points:
    ball.location=(0,y,z)
    ball.keyframe_insert(data_path="location",frame=f)
    ball.rotation_euler=(f*.08,f*.035,f*.11)
    ball.keyframe_insert(data_path="rotation_euler",frame=f)
def smooth_keyframes(ob, mode='LINEAR'):
    act=ob.animation_data.action
    if hasattr(act, 'fcurves'):
        curves=act.fcurves
    else:
        curves=[]
        for layer in act.layers:
            for st in layer.strips:
                for slot in act.slots:
                    try:
                        bag=st.channelbag(slot)
                        if bag:curves.extend(list(bag.fcurves))
                    except Exception:pass
    for fc in curves:
        for pt in fc.keyframe_points:pt.interpolation=mode
smooth_keyframes(ball, 'LINEAR')

# Launcher: restrained slingshot with real forks, not an ornamental spring.
cylinder_between("Slingshot hardwood handle",(0,-9.3,.30),(0,-9.3,1.21),.077,wood,16)
for side in [-1,1]:
    cylinder_between(f"Slingshot branch {side}",(0,-9.3,1.18),(side*.31,-9.3,1.69),.055,wood,12)
    cylinder_between(f"Slingshot strap {side}",(side*.31,-9.3,1.69),(0,-9.03,1.5),.011,rubber,8)

# Atmosphere: dark testing studio, colored edge light shows transparency.
world=bpy.data.worlds.new("Midnight studio ambient")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.09,.145,.23,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.38

def light(name,typ,loc,color,power,target,size=5):
    datab=bpy.data.lights.new(name,typ)
    datab.energy=power
    datab.color=color
    ob=bpy.data.objects.new(name,datab)
    bpy.context.collection.objects.link(ob)
    ob.location=loc
    if typ=="AREA":
        datab.shape='DISK';datab.size=size
        ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    return ob
light("Long cyan rim", "AREA",(3,8,6),(.3,.83,1),2200,(0,10,1.5),12)
light("Warm strike accent", "AREA",(-4,21,5),(1,.68,.43),1450,(0,17,1.4),14)
light("Long cool fill", "AREA",(-2,-8,7),(.67,.80,1),1650,(0,0,1.5),16)

# Single 3D scene, continuous animated camera with a calm lead-in and trailing follow.
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(3,-12,2.5))
cam=bpy.context.object
cam.name="Single continuity tracking camera"
scene.camera=cam
cam.data.lens=28
cam.data.clip_end=230
def ckey(f,position,target):
    cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=f)
    cam.keyframe_insert(data_path='rotation_euler',frame=f)
ckey(1,(3.2,-11.8,2.95),(0,11,1.45))
ckey(33,(3.2,-11.8,2.95),(0,11,1.45))
ckey(46,(1.75,-11.0,2.17),(0,-5,1.48))
ckey(49,(1.34,-11.4,1.94),(0,-4.3,1.48))
for e in events:
    if not e["broken"]:break
    f=e["frame"]
    pos=(1.42,e["y"]-4.35,2.07)
    target=(0,e["y"]+4.0,1.47)
    ckey(f,pos,target)
if FIRST_STOP:
    f=FIRST_STOP["frame"]
    y=FIRST_STOP["y"]
    ckey(f,(1.52,y-4.75,2.06),(0,y+.2,1.42))
    ckey(FRAMES,(1.52,y-4.75,2.06),(0,y+.2,1.42))
smooth_keyframes(cam, 'BEZIER')

scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.fps=FPS
scene.frame_start=1;scene.frame_end=FRAMES
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
try:
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
except Exception:pass
if not scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
scene.rigidbody_world.substeps_per_frame=18
scene.rigidbody_world.solver_iterations=12
scene.rigidbody_world.point_cache.frame_start=1
scene.rigidbody_world.point_cache.frame_end=FRAMES
scene.render.filepath=str(OUT/"frames"/"frame_0001.png")
scene.frame_set(1)
saved=OUT/"GLASS_20_PANEL_CHALLENGE_V1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
meta=dict(seed=SEED,total=PANELS,broken=BROKEN,remaining=PANELS-BROKEN,stop_pane=FIRST_STOP["number"] if FIRST_STOP else None,
    frames=FRAMES,fps=FPS,resolution=[720,1280],break_events=events,shards=SHARD_COUNT,scene=saved.name,
    note="Stylized kinetic-energy attenuation for ball; released glass shards use Blender rigid-body dynamics, not fully coupled fracture.")
(OUT/"physics_results.json").write_text(json.dumps(meta,indent=2),encoding="utf8")
print("SCENE_READY",saved,"BROKEN",BROKEN,"SHARDS",SHARD_COUNT,flush=True)
