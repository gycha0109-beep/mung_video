import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v6"
O.mkdir(exist_ok=True)
SRC=R/"glass_panel_challenge_v5"/"GLASS_V5_ONE_PANE_QUALITY_TEST.blend"
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s=bpy.context.scene
rng=random.Random(61114)
HIT=43
N=84
s.frame_start=1
s.frame_end=N
s.render.fps=24
s.render.resolution_x=720
s.render.resolution_y=1280
s.render.resolution_percentage=100
s.render.engine="CYCLES"
s.cycles.samples=48
s.cycles.use_denoising=True
s.cycles.max_bounces=8
s.cycles.transmission_bounces=8
s.render.image_settings.file_format="PNG"

def pmat(name,color,metal=0,rough=.4,trans=0,ior=1.45):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Transmission Weight"].default_value=trans
    p.inputs["IOR"].default_value=ior
    return mat

wood=pmat("V6 solid walnut grip layered grain",(.23,.105,.046),rough=.45)
p=wood.node_tree.nodes.get("Principled BSDF")
noise=wood.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=16
noise.inputs["Detail"].default_value=3.6
bump=wood.node_tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.13
bump.inputs["Distance"].default_value=.004
wood.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
wood.node_tree.links.new(bump.outputs["Normal"],p.inputs["Normal"])
lat=pmat("V6 flat latex rubber bands",(.075,.058,.046),rough=.65)
leather=pmat("V6 dark stitched pouch leather",(.10,.053,.026),rough=.75)
steel=bpy.data.materials["V5 machined chrome steel"]
alum=bpy.data.materials["V5 graphite anodized aluminum"]
glass=bpy.data.materials["V5 solid silica | Fresnel refraction IOR 1.51"]
gp=glass.node_tree.nodes.get("Principled BSDF")
gp.inputs["Roughness"].default_value=.035
gp.inputs["Base Color"].default_value=(.91,.96,.96,1)
fragglass=glass.copy()
fragglass.name="V6 thinner shattered silica"
fnp=fragglass.node_tree.nodes.get("Principled BSDF")
fnp.inputs["Roughness"].default_value=.045
fnp.inputs["Base Color"].default_value=(.79,.94,.95,1)
pouchZ=1.54
forkY=-4.05
# Original projectile and fracture geometry are preserved, but the object visibility
# and motion are rebuilt so that the outer pane remains present during impact.
ball=bpy.data.objects["19 mm equivalent chrome projectile"]
ball.animation_data_clear()
def key_visible(o,f,vis):
    o.hide_render=not vis
    o.keyframe_insert(data_path="hide_render",frame=f)
    o.hide_viewport=not vis
    o.keyframe_insert(data_path="hide_viewport",frame=f)

for f,y in [(1,-4.34),(11,-4.44),(23,-5.35),(29,-5.35),
            (31,-4.23),(34,-3.38),(40,-1.02),(43,-.065),
            (46,.36),(52,1.16),(64,2.50),(84,3.85)]:
    ball.location=(0,y,pouchZ)
    ball.keyframe_insert(data_path="location",frame=f)
# Keep the shiny ball visible rather than disappearing into the test pane.
pane=bpy.data.objects["Actual tempered glass pane"]
pane.animation_data_clear()
key_visible(pane,1,True)
key_visible(pane,HIT-1,True)
key_visible(pane,HIT,False)
key_visible(pane,N,False)
# Rebuild every glass fragment with a deterministic impulse and gravity, not
# frame-by-frame independent random rotations.
fragments=sorted([o for o in bpy.data.objects if o.name.startswith("True glass fragment")],key=lambda x:x.name)
for o in fragments:
    o.animation_data_clear()
    o.data.materials[0]=fragglass
    cx,_,czw=o.location
    localz=czw-1.58
    rad=math.hypot(cx,localz)
    central=rad<.24
    delay=0 if central else (1 if rad<.49 else (3 if rad<.78 else 5))
    release=HIT+delay
    key_visible(o,1,False)
    key_visible(o,HIT-1,False)
    key_visible(o,HIT,True)
    key_visible(o,N,True)
    # By showing all fragments while the intact pane is hidden, the glass no
    # longer pops out as a blank rectangle for the delayed outer shards.
    o.location=(cx,0,czw)
    o.rotation_euler=(0,0,0)
    o.keyframe_insert(data_path="location",frame=HIT)
    o.keyframe_insert(data_path="rotation_euler",frame=HIT)
    o.keyframe_insert(data_path="location",frame=release)
    o.keyframe_insert(data_path="rotation_euler",frame=release)
    poly=o.data.polygons[0]
    area=max(.001,abs(poly.area))
    area_factor=max(.65,min(1.65,(.014/area)**.24))
    ang=math.atan2(localz,cx)
    radial=(2.0/(1+2.7*rad))*area_factor
    vx=math.cos(ang)*radial+rng.uniform(-.29,.29)
    vy=(3.4/(1+1.7*rad))*area_factor+rng.uniform(.06,.45)
    vz=math.sin(ang)*radial+.48+rng.uniform(-.12,.35)
    rx,ry,rz=(rng.uniform(-5,5),rng.uniform(-5,5),rng.uniform(-5,5))
    damp=(.65+.35*rng.random())
    for fr in range(release+1,N+1,2):
        t=(fr-release)/24
        z=czw+vz*t-4.905*t*t
        if z<.025:
            z=.025 + (.07*math.exp(-4*max(0,t-.5)))*abs(math.sin(13*t))
        o.location=(cx+vx*t*damp,vy*t*damp,z)
        o.rotation_euler=(rx*t,ry*t,rz*t)
        o.keyframe_insert(data_path="location",frame=fr)
        o.keyframe_insert(data_path="rotation_euler",frame=fr)
# Fracture lines appear 2 frames before full break and fade once fragments fly.
for o in bpy.data.objects:
    if o.name=="Microscopic fracture fissure":
        o.animation_data_clear()
        key_visible(o,1,False)
        key_visible(o,HIT-3,False)
        key_visible(o,HIT-2,True)
        key_visible(o,HIT+5,False)
# Additional fine glass chips: small 3D micro-triangles concentrated on impact.
def chip_mesh(idx,center,t=.003):
    x,y,z=center
    size=rng.uniform(.004,.020)
    d=rng.uniform(.002,.006)
    local=[(-size*.52,-d/2,-size*.15),(size*.72,-d/2,-size*.30),
           (-size*.11,-d/2,size*.80),(-size*.52,d/2,-size*.15),
           (size*.72,d/2,-size*.30),(-size*.11,d/2,size*.80)]
    faces=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
    mesh=bpy.data.meshes.new("v6 microchip geometry")
    mesh.from_pydata(local,[],faces)
    mesh.materials.append(fragglass)
    ob=bpy.data.objects.new(f"V6 real 3D microchip {idx:03d}",mesh)
    bpy.context.collection.objects.link(ob)
    ob.location=(x,y,z)
    return ob
for i in range(185):
    theta=rng.uniform(-math.pi,math.pi)
    rad=.018+(.22*math.sqrt(rng.random()))
    cx=math.cos(theta)*rad
    cz=math.sin(theta)*rad
    o=chip_mesh(i,(cx,0,1.58+cz))
    key_visible(o,1,False)
    key_visible(o,HIT-1,False)
    key_visible(o,HIT,True)
    key_visible(o,N,True)
    vx=cx/(rad+.015)*rng.uniform(1.8,3.9)
    vz=cz/(rad+.015)*rng.uniform(.2,1.6)+rng.uniform(.35,1.4)
    vy=rng.uniform(2.1,5.7)
    spin=(rng.uniform(-6,6),rng.uniform(-7,7),rng.uniform(-7,7))
    for f in range(HIT,N+1,3):
        t=max(0,(f-HIT)/24)
        z=max(.025,1.58+cz+vz*t-4.9*t*t)
        o.location=(cx+vx*t,vy*t,z)
        o.rotation_euler=(spin[0]*t,spin[1]*t,spin[2]*t)
        o.keyframe_insert(data_path="location",frame=f)
        o.keyframe_insert(data_path="rotation_euler",frame=f)
# Slingshot hardwood Y-branch is constructed as smoothly tapered swept tubes.
def branch(name,points,radii,material,sides=18):
    verts=[];faces=[]
    for i,pt in enumerate(points):
        at=Vector(pt)
        direction=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
        direction.normalize()
        side=direction.cross(Vector((0,1,0))).normalized()
        up=direction.cross(side).normalized()
        for j in range(sides):
            ang=j*math.tau/sides
            v=at+radii[i]*(side*math.cos(ang)+up*math.sin(ang))
            verts.append(tuple(v))
    faces.append(tuple(range(sides-1,-1,-1)))
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    last=(len(points)-1)*sides
    faces.append(tuple(range(last,last+sides)))
    mesh=bpy.data.meshes.new(name+" solid timber")
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material)
    for face in mesh.polygons:face.use_smooth=True
    bevel=obj.modifiers.new("subtle rounded grain bevel","BEVEL")
    bevel.width=.006
    bevel.segments=2
    return obj
branch("Carved continuous walnut grip",
       [(0,forkY,.76),(0,forkY,.90),(.012,forkY,1.05),(.005,forkY,1.21),
        (0,forkY,1.34)],[.072,.080,.075,.067,.060],wood)
for side in (-1,1):
    branch(f"Curved real hardwood fork {side}",
       [(0,forkY,1.29),(side*.085,forkY,1.42),(side*.17,forkY,1.55),
        (side*.242,forkY,1.68),(side*.278,forkY,1.78)],
       [.058,.054,.049,.044,.038],wood)
# Pouch is double layered leather, held by two actual broad flat elastics.
bpy.ops.mesh.primitive_cube_add(size=1)
pouch=bpy.context.object
pouch.name="V6 stitched leather pouch and fold"
pouch.dimensions=(.26,.05,.17)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
pouch.data.materials.append(leather)
b=pouch.modifiers.new("soft leather roundness","BEVEL")
b.width=.028;b.segments=4
for f,y in [(1,-4.34),(11,-4.44),(23,-5.35),(29,-5.35),(31,-4.23),
            (34,-4.07),(37,-4.18),(43,-4.11),(84,-4.11)]:
    pouch.location=(0,y,pouchZ)
    pouch.keyframe_insert(data_path="location",frame=f)
for side in (-1,1):
    fork=Vector((side*.278,forkY,1.78))
    bpy.ops.mesh.primitive_cube_add(size=1)
    band=bpy.context.object
    band.name=f"V6 actual flat elastic {side}"
    band.data.materials.append(lat)
    for f,y in [(1,-4.34),(11,-4.44),(23,-5.35),(29,-5.35),(31,-4.23),
                (34,-4.07),(37,-4.18),(43,-4.11),(84,-4.11)]:
        end=Vector((side*.105,y,pouchZ))
        v=end-fork
        band.location=(fork+end)/2
        band.rotation_euler=v.to_track_quat("Z","Y").to_euler()
        band.scale=(.052,.011,v.length)
        band.keyframe_insert(data_path="location",frame=f)
        band.keyframe_insert(data_path="rotation_euler",frame=f)
        band.keyframe_insert(data_path="scale",frame=f)
    # Narrow suede edge on the wooden fork cap.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=fork)
    cap=bpy.context.object
    cap.name=f"V6 hardwood fork cap {side}"
    cap.scale=(.042,.044,.050)
    cap.data.materials.append(wood)
# Contour-grip wrapping: shallow overlapping tactile raised leather strips.
for i in range(9):
    z=.84+i*.048
    bpy.ops.mesh.primitive_torus_add(major_segments=22,minor_segments=6,
            location=(0,forkY,z),major_radius=.071,minor_radius=.0028)
    ob=bpy.context.object
    ob.name=f"V6 grip embossed leather ring {i}"
    ob.data.materials.append(leather)

# Set dressing: dark grey textured studio, steel markers, black track on concrete.
floor=bpy.data.objects.get("Concrete studio floor")
if floor:
    floor.scale.y=1.65
    mat=floor.data.materials[0]
    node=mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value=(.19,.205,.207,1)
wall=bpy.data.objects.get("Gradual textured rear")
if wall:
    node=wall.data.materials[0].node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value=(.16,.17,.18,1)
for ob in bpy.data.objects:
    if ob.type=="LIGHT":
        ob.data.energy*=.78
# Camera tracks one continuous physical 3D scene from loaded pouch into impact.
cam=s.camera
cam.animation_data_clear()
cam.data.lens=43
cam.data.dof.use_dof=False
def camera_frame(f,pos,aim):
    cam.location=Vector(pos)
    cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.keyframe_insert(data_path="location",frame=f)
    cam.keyframe_insert(data_path="rotation_euler",frame=f)
camera_frame(1,(1.52,-7.32,2.14),(0,-4.25,1.45))
camera_frame(23,(1.6,-7.30,2.17),(0,-4.66,1.47))
camera_frame(29,(1.6,-7.30,2.17),(0,-4.66,1.47))
camera_frame(34,(2.35,-6.10,2.23),(0,-2.45,1.53))
camera_frame(40,(2.63,-4.21,2.28),(0,-.34,1.56))
camera_frame(43,(2.48,-3.66,2.20),(0,0,1.53))
camera_frame(84,(2.33,-3.50,2.08),(0,.34,1.53))
# Subtle overall light adjustment, no glowing special effects.
scene_bg=s.world.node_tree.nodes.get("Background")
scene_bg.inputs["Strength"].default_value=.40
s.frame_set(1)
target=O/"GLASS_V6_LAUNCH_AND_ONE_PANE.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
(O/"scene_meta.json").write_text(json.dumps({
    "frames":N,"fps":24,"resolution":[720,1280],"impact_frame":HIT,
    "fragments":len(fragments),"microchips":185,"scope":"full slingshot-to-one-pane shot",
    "note":"Art-directable ballistic keyframes, not measured fracture mechanics",
},indent=2),encoding="utf8")
print("V6_SCENE_READY",target,"original_fragments",len(fragments),"microchips",185,flush=True)
