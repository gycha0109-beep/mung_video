import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v2"
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261114
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

glass=mat("V2 tempered clear glass",(.69,.90,.96),rough=.095,trans=.07,alpha=.24)
glass.surface_render_method="BLENDED"
glass_edge=mat("V2 broken glass bright edge facets",(.34,.88,.98),rough=.12,trans=.08,alpha=.91)
steel=mat("Machined steel | steel sphere",(.67,.71,.75),metal=1,rough=.18)
metal=mat("Brushed aluminium brackets",(.29,.39,.46),metal=.86,rough=.26)
rubber=mat("Industrial rubber | projectile pouch",(.16,.12,.10),rough=.75)
wood=mat("Polished dark hardwood",(.24,.13,.068),rough=.55)
floor=mat("Deep graphite laboratory concrete",(.062,.085,.10),rough=.62)
back=mat("Blue-dark stage environment",(.018,.036,.053),rough=.8)
strip=mat("Cold cyan running light",(.18,.72,1),rough=.24,emission=7.5)
hot=mat("Warm laboratory highlights",(.99,.67,.38),rough=.2,emission=2.0)
crack_mat=mat("V2 irregular glass stress fracture",(.80,.96,1),rough=.30,emission=.35)

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
            for ray in range(9):
                angle=ray*math.tau/9+rng.uniform(-.11,.11)
                dist=.07
                start=(.025*math.cos(angle),y-.025,PANEL_Z+.025*math.sin(angle))
                for step in range(3):
                    angle+=rng.uniform(-.21,.21)
                    target_dist=dist+rng.uniform(.10,.21)
                    endpoint=(target_dist*math.cos(angle),y-.026,PANEL_Z+target_dist*math.sin(angle))
                    crack=cylinder_between(f"V2 STOP jagged radial {ray} segment {step}",start,endpoint,.0018,crack_mat,6)
                    visibility(crack,1,False);visibility(crack,f-1,False);visibility(crack,f,True)
                    start=endpoint;dist=target_dist
            print("STOP_PANE_CRACKED",idx+1)
        continue

    # V2: Voronoi fracture, bounded at the physical pane outline.
    # A deterministic cellular crack network replaces V1's square tile grid.
    def clip_halfplane(poly,nx,nz,limit):
        if not poly:return []
        out=[]
        prev=poly[-1]
        dprev=prev[0]*nx+prev[1]*nz-limit
        for cur in poly:
            dcur=cur[0]*nx+cur[1]*nz-limit
            inside_prev=dprev<=1e-8;inside_cur=dcur<=1e-8
            if inside_prev != inside_cur:
                t=dprev/(dprev-dcur)
                out.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
            if inside_cur:out.append(cur)
            prev,dprev=cur,dcur
        return out
    points=[]
    nx,nz=7,8
    for ix in range(nx):
        for iz in range(nz):
            x=(-.5+(ix+.5)/nx)*PANEL_W
            z=(-.5+(iz+.5)/nz)*PANEL_H
            dx=PANEL_W/nx;dz=PANEL_H/nz
            x+=rng.uniform(-.43,.43)*dx
            z+=rng.uniform(-.43,.43)*dz
            points.append((x,z))
    for j in range(10):
        r=.12+.29*math.sqrt(rng.random())
        a=rng.random()*math.tau
        points.append((r*math.cos(a),r*math.sin(a)))
    all_polys=[]
    outline=[(-PANEL_W/2,-PANEL_H/2),(PANEL_W/2,-PANEL_H/2),
             (PANEL_W/2,PANEL_H/2),(-PANEL_W/2,PANEL_H/2)]
    for index,(sx,sz) in enumerate(points):
        poly=outline[:]
        for j,(ox,oz) in enumerate(points):
            if index==j:continue
            nx, nz = ox-sx, oz-sz
            limit=(ox*ox+oz*oz-sx*sx-sz*sz)/2.
            poly=clip_halfplane(poly,nx,nz,limit)
            if len(poly)<3:break
        if len(poly)<3:continue
        # Remove nearly duplicated polygon corners.
        clean=[]
        for px,pz in poly:
            if not clean or math.hypot(px-clean[-1][0],pz-clean[-1][1])>1e-5:
                clean.append((px,pz))
        if len(clean)>=3:
            area=abs(sum(clean[k][0]*clean[(k+1)%len(clean)][1]-
                         clean[(k+1)%len(clean)][0]*clean[k][1] for k in range(len(clean)))/2)
            if area>.00015:all_polys.append(clean)
    print("V2_FRACTURE",idx+1,"CELL_COUNT",len(all_polys),flush=True)
    for part_num,poly in enumerate(all_polys):
        name=f"V2 pane {idx+1:02d} irregular shard {part_num:03d}"
        ob=polygon_shard(name,poly,y,glass)
        bpy.context.view_layer.objects.active=ob
        ob.select_set(True)
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        ob.select_set(False)
        ob.rigid_body.collision_shape='CONVEX_HULL'
        ob.rigid_body.mass=.018+rng.uniform(.006,.040)
        ob.rigid_body.friction=.52
        ob.rigid_body.restitution=.13
        ob.rigid_body.collision_margin=.002
        ob.rigid_body.linear_damping=.14
        ob.rigid_body.angular_damping=.20
        ob.rigid_body.kinematic=True
        ob.rigid_body.keyframe_insert(data_path="kinematic",frame=1)
        cx=sum(p[0] for p in poly)/len(poly)
        cz=sum(p[1] for p in poly)/len(poly)
        dist=math.hypot(cx,cz)
        # Near the impact: brisk shock; far from it: mostly gravity.
        shock=1.0/(1+2.8*dist)
        delay=0 if dist<.45 else (1 if dist<.75 else 2)
        hit=f+delay
        ob.rigid_body.keyframe_insert(data_path="kinematic",frame=hit)
        ob.location=(0,0,0)
        ob.keyframe_insert(data_path="location",frame=hit)
        visibility(ob,1,False)
        visibility(ob,hit-1,False)
        visibility(ob,hit,True)
        # Impulse is only a few centimetres in the first frame, keeping
        # impact visually localized rather than an artificial full-wall blast.
        bx=(cx/(dist+.01))*(.012+.080*shock)+rng.uniform(-.014,.014)
        bz=(cz/(dist+.01))*(.015+.065*shock)+rng.uniform(-.013,.010)
        by=(.035+.115*shock)+rng.uniform(.002,.019)
        ob.location=(bx,by,bz)
        ob.keyframe_insert(data_path="location",frame=hit+1)
        ob.rotation_euler=(rng.uniform(-.17,.17),rng.uniform(-.20,.20),rng.uniform(-.11,.11))
        ob.keyframe_insert(data_path="rotation_euler",frame=hit+1)
        ob.rigid_body.kinematic=False
        ob.rigid_body.keyframe_insert(data_path="kinematic",frame=hit+2)
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
cam.data.lens=30
cam.data.clip_end=230
def ckey(f,position,target):
    cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=f)
    cam.keyframe_insert(data_path='rotation_euler',frame=f)
ckey(1,(3.2,-11.8,2.95),(0,11,1.45))
ckey(33,(3.2,-11.8,2.95),(0,11,1.45))
ckey(46,(1.75,-11.0,2.17),(0,-5,1.48))
ckey(49,(1.85,-11.7,2.11),(0,-4.3,1.48))
for e in events:
    if not e["broken"]:break
    f=e["frame"]
    pos=(2.12,e["y"]-6.75,2.23)
    target=(0,e["y"]+2.7,1.44)
    ckey(f,pos,target)
if FIRST_STOP:
    f=FIRST_STOP["frame"]
    y=FIRST_STOP["y"]
    ckey(f,(2.18,y-7.0,2.23),(0,y+.2,1.42))
    ckey(FRAMES,(2.18,y-7.0,2.23),(0,y+.2,1.42))
smooth_keyframes(cam, 'BEZIER')

scene.render.engine="BLENDER_EEVEE"
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
scene.rigidbody_world.substeps_per_frame=16
scene.rigidbody_world.solver_iterations=12
scene.rigidbody_world.point_cache.frame_start=1
scene.rigidbody_world.point_cache.frame_end=FRAMES
scene.render.filepath=str(OUT/"frames"/"frame_0001.png")
scene.frame_set(1)
saved=OUT/"GLASS_20_PANEL_CHALLENGE_V2.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
meta=dict(seed=SEED,total=PANELS,broken=BROKEN,remaining=PANELS-BROKEN,stop_pane=FIRST_STOP["number"] if FIRST_STOP else None,
    frames=FRAMES,fps=FPS,resolution=[720,1280],break_events=events,shards=SHARD_COUNT,scene=saved.name,
    note="V2 irregular Voronoi-style pre-fracture; simplified stylized energy attenuation for ball; rigid-body shards are released on contact, not a fully coupled fracture solver.")
(OUT/"physics_results.json").write_text(json.dumps(meta,indent=2),encoding="utf8")
print("SCENE_READY",saved,"BROKEN",BROKEN,"SHARDS",SHARD_COUNT,flush=True)
