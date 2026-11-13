from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"
src=(root/"physical_impact_proof.py").read_text(encoding="utf-8")
def replace(s,a,b):
    assert s.count(a)==1,(a[:80],s.count(a))
    return s.replace(a,b)
def make(kind):
    t=src
    t=replace(t,'OUT=ROOT/"physics_proof_v1"',f'OUT=ROOT/"three_shots"/"{kind}"/"impact"')
    t=replace(t,'tile_dir=OUT/"wall_tiles"','tile_dir=ROOT/"physics_proof_v1"/"wall_tiles"')
    t=replace(t,'scene.cycles.samples = 20 if MODE=="preview" else 30','scene.cycles.samples = 14 if MODE=="preview" else 24')
    t=replace(t,'scene.cycles.samples=30','scene.cycles.samples=24')
    t=replace(t,'scene.cycles.samples=14','scene.cycles.samples=12')
    if kind=='billiard':
        t=replace(t,'near=distance<1.4','near=distance<.58')
        t=replace(t,'fracture=distance<.88','fracture=distance<.24')
        t=replace(t,'rigid(ball,mass=42,friction=.16,bounce=.21,start_sleep=False)',
          'rigid(ball,mass=.35,friction=.12,bounce=.78,start_sleep=False)')
        t=replace(t,'for frame,y in [(1,-3.1),(8,-1.42),(11,-.69),(12,-.445),(13,-.20)]:',
          'for frame,y in [(1,-3.1),(8,-1.42),(11,-.69),(12,-.445),(13,-.306)]:')
        t=replace(t,'ball.name="PHYSICS STEEL PROJECTILE"','ball.name="PHYSICS 8 BALL"')
        t=replace(t,'ball.data.materials.append(steel)',
          '''eight=bpy.data.materials.new("Glossy real billiard black phenolic resin")
eight.use_nodes=True
b=eight.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value=(.012,.012,.019,1)
b.inputs["Roughness"].default_value=.13
b.inputs["Coat Weight"].default_value=.56
b.inputs["Coat Roughness"].default_value=.06
ball.data.materials.append(eight)
white=bpy.data.materials.new("8 Ball white spot")
white.diffuse_color=(.96,.93,.86,1);white.use_nodes=True
white.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.96,.93,.86,1)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,radius=.051)
spot=bpy.context.object
spot.name="Ivory number roundel"
spot.parent=ball;spot.location=(0,-.137,0);spot.scale=(1,.15,1)
spot.data.materials.append(white)
digits=bpy.data.materials.new("8 ink")
digits.diffuse_color=(.01,.01,.01,1)
digits.use_nodes=True
digits.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.01,.01,.01,1)
cv=bpy.data.curves.new("Eight numeral","FONT")
cv.body="8";cv.size=.079;cv.align_x="CENTER";cv.align_y="CENTER"
number=bpy.data.objects.new("8 numbered billiard",cv)
bpy.context.collection.objects.link(number)
number.parent=ball;number.location=(0,-.147,0)
number.rotation_euler=(math.pi/2,0,0);number.data.materials.append(digits)''')
        t=replace(t,'back_loc=Vector((1.30,3.55,1.85))',
          'back_loc=front_loc.copy()')
        t=replace(t,'back_target=Vector((0,.36,impactz-.07))',
          'back_target=Vector((-.08,-.16,impactz))')
        t=replace(t,'camera.data.lens=28','camera.data.lens=31')
        t=replace(t,'for frame,density in ((1,0),(12,0),(16,0),(19,.065),(26,.072),(36,.047),(48,.026)):',
          'for frame,density in ((1,0),(12,0),(16,0),(19,.003),(26,.002),(36,.001),(48,0)):')
        # Hidden rigid collider supports convincing bounce even when the fractured mesh has small gaps.
        anchor='''# Strong physics solver to ensure bullet contact and settling.'''
        insert='''# Physically rigid center contact surface for billiard rebound, invisible in render.
bounce_wall=box("REBOUND WALL collision", (0,-.005,impactz), (1.15,.29,.92),mortar,0)
bounce_wall.hide_render=True
rigid(bounce_wall,passive=True,friction=.36,bounce=.62)
'''
        t=replace(t,anchor,insert+anchor)
    if kind=='egg':
        t=replace(t,'near=distance<1.4','near=False')
        t=replace(t,'fracture=distance<.88','fracture=False')
        t=replace(t,'rigid(ball,mass=42,friction=.16,bounce=.21,start_sleep=False)',
          'rigid(ball,mass=.11,friction=.2,bounce=.02,start_sleep=False)')
        t=replace(t,'for frame,y in [(1,-3.1),(8,-1.42),(11,-.69),(12,-.445),(13,-.20)]:',
          'for frame,y in [(1,-3.1),(8,-1.42),(11,-.69),(12,-.445),(13,-.31)]:')
        t=replace(t,'ball.name="PHYSICS STEEL PROJECTILE"','ball.name="PHYSICS EGG SHELL BEFORE IMPACT"')
        t=replace(t,'ball.data.materials.append(steel)',
          '''eggshell=mat_physical("Eggshell porous off-white",(.78,.72,.58),.49,0,64,.0012)
ball.data.materials.append(eggshell)
for vert in ball.data.vertices:
    z=vert.co.z/.155
    width=1+.12*z-.09*z*z
    vert.co.x*=.81*width
    vert.co.y*=.81*width
    vert.co.z*=1.22
for frame,hidden in ((1,False),(13,False),(14,True),(48,True)):
    ball.hide_render=hidden
    ball.keyframe_insert(data_path="hide_render",frame=frame)''')
        t=replace(t,'back_loc=Vector((1.30,3.55,1.85))','back_loc=front_loc.copy()')
        t=replace(t,'back_target=Vector((0,.36,impactz-.07))','back_target=Vector((-.08,-.16,impactz))')
        t=replace(t,'camera.data.lens=28','camera.data.lens=31')
        t=replace(t,'for frame,density in ((1,0),(12,0),(16,0),(19,.065),(26,.072),(36,.047),(48,.026)):',
          'for frame,density in ((1,0),(12,0),(16,0),(19,0),(26,0),(36,0),(48,0)):')
        anchor='''# Strong physics solver to ensure bullet contact and settling.'''
        insert= r'''
# Egg ruptures on contact. Breakage is timed, but each shell segment receives real rigid-body motion.
# Fluid surfaces are a controllable stylized effect, not a Navier-Stokes simulation.
inner=mat_physical("Eggshell inner cream",(.63,.56,.43),.77,0,25,.0006)
yolk=bpy.data.materials.new("Rich wet egg yolk")
yolk.use_nodes=True
yb=yolk.node_tree.nodes["Principled BSDF"]
yb.inputs["Base Color"].default_value=(.88,.32,.014,1)
yb.inputs["Roughness"].default_value=.13
yb.inputs["Coat Weight"].default_value=.54
yb.inputs["Coat Roughness"].default_value=.12
eggwhite=bpy.data.materials.new("Wet translucent egg white")
eggwhite.use_nodes=True
wb=eggwhite.node_tree.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value=(.85,.91,.80,1)
wb.inputs["Roughness"].default_value=.12
wb.inputs["Transmission Weight"].default_value=.58
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
                      (14,center+Vector((math.cos(phi1)*.038,-.105-math.sin(theta1)*.025,
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
for k in range(10):
    angle=2*math.pi*k/10+random.uniform(-.12,.12)
    dx=.25*math.cos(angle)
    dz=.20*math.sin(angle)
    blob("Egg white perimeter wet %02d"%k,dx,impactz+dz,
         random.uniform(.045,.095),random.uniform(.024,.068),eggwhite,appear=15+k%3)
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
'''
        t=replace(t,anchor,insert+'\n'+anchor)
    target=root/"three_shots"/kind
    target.mkdir(parents=True,exist_ok=True)
    dest=target/(kind+"_impact.py")
    dest.write_text(t,encoding="utf-8")
    compile(t,str(dest),'exec')
    print("GENERATED",kind,len(t),dest)
for kind in ("egg","billiard"):make(kind)
