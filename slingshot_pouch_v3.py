import bpy, math, sys
from mathutils import Vector
from pathlib import Path

ROOT = Path.home() / "Downloads" / "slingshot_quality_proof"
SOURCE = ROOT / "slingshot_quality_proof_v2.blend"
OUT_BLEND = ROOT / "slingshot_pouch_mechanics_v3.blend"
MODE = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "preview"

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 192
scene.render.fps = 24
scene.render.resolution_x, scene.render.resolution_y = 1080, 1920
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'

steel = bpy.data.objects["POLISHED STEEL SHOT"]
camera = bpy.data.objects["CINEMA CAMERA"]
leather = bpy.data.materials["Tanned worn leather"]
latex = bpy.data.materials["Elastic dark rubber"]
metal = bpy.data.materials["Oxidised steel fasteners"]
threadmat = bpy.data.materials.get("Glove stitching")
if threadmat is None:
    threadmat = bpy.data.materials.new("Pouch golden stitching")
    threadmat.diffuse_color = (.53,.34,.17,1)

for name in ("Stitched leather projectile cup", "Elastic band straps LEFT", "Elastic band straps RIGHT"):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# The ball is nested in the concave U-shaped pouch rather than floating on it.
# Y+ points toward the target, and the shooter sees the leather cradle from Y-.
rig = bpy.data.objects.new("SHOT POUCH / rig", None)
bpy.context.collection.objects.link(rig)
rig.empty_display_type = 'SPHERE'
rig.empty_display_size = .065

def pose(obj, prop, keys):
    for f, v in keys:
        setattr(obj, prop, v)
        obj.keyframe_insert(data_path=prop, frame=f)

def make_mesh(name, verts, faces, material):
    me = bpy.data.meshes.new(name + " geometry")
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = rig
    for face in me.polygons:
        face.use_smooth = True
    bevel = obj.modifiers.new("Soft-cut leather edges", "BEVEL")
    bevel.width = .003
    bevel.segments = 2
    obj.modifiers.new("Natural edge normals", "WEIGHTED_NORMAL")
    return obj

# A curved, thick, lower-half leather saddle; exposed center of projectile remains steel.
N = 44
INNER = .111
OUTER = .189
thickness = .018
verts = []
for layer in range(2):
    for k in range(N + 1):
        theta = math.pi - .13 + (math.pi + .26) * k / N
        for radius in (INNER, OUTER):
            t = (radius - INNER) / (OUTER - INNER)
            y = -.129 + .056 * t + (thickness if layer else 0)
            verts.append((radius * math.cos(theta), y, radius * math.sin(theta)))
faces = []
for k in range(N):
    i = 2*k
    j = 2*(N+1) + i
    faces.extend([(i, i+1, i+3, i+2),
                  (j+2,j+3,j+1,j),
                  (i,i+2,j+2,j),
                  (i+1,j+1,j+3,i+3)])
faces.extend([(0,2*(N+1),2*(N+1)+1,1),
              (2*N,2*N+1,4*(N+1)-1,4*(N+1)-2)])
cradle = make_mesh("REAL LEATHER CUP - steel ball cradle", verts, faces, leather)

def child_ball(name, local, radius, mat, scales=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = rig
    obj.location = local
    obj.scale = scales
    for poly in obj.data.polygons: poly.use_smooth = True
    return obj

for side, sign in (("LEFT",-1),("RIGHT",1)):
    child_ball("Pouch leather reinforced loop " + side,
               (sign*.202,-.077,.015), .036, leather, (.82,.52,1.3))
    child_ball("Pouch metal eyelet " + side,
               (sign*.206,-.103,.019), .013, metal, (.85,.55,.85))

# A narrow stitching line along the outer leather, built as geometric thread.
def leather_stitch():
    c = bpy.data.curves.new("Pouch stitched contour", 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 2
    c.bevel_depth = .0028
    c.bevel_resolution = 2
    poly = c.splines.new('POLY')
    poly.points.add(38)
    for k, pt in enumerate(poly.points):
        theta = math.pi + .13 + (math.pi - .26)*k/38
        rad = .165
        u = (rad-INNER)/(OUTER-INNER)
        y = -.131 + .056*u - .004
        pt.co = (rad*math.cos(theta), y, rad*math.sin(theta), 1)
    obj = bpy.data.objects.new("Visible saddle stitching", c)
    bpy.context.collection.objects.link(obj)
    obj.parent = rig
    obj.data.materials.append(threadmat)
leather_stitch()

# Dynamic stretched latex ribbons actually terminate on the pouch eyelets.
tips = {"LEFT":Vector((-.32,-9.33,2.01)),
        "RIGHT":Vector(( .32,-9.33,2.01))}
bands = {}
for side in ("LEFT","RIGHT"):
    bpy.ops.mesh.primitive_cube_add(size=1)
    band = bpy.context.object
    band.name = "TENSIONED LATEX / " + side
    band.data.materials.append(latex)
    band.rotation_mode = 'QUATERNION'
    bevel = band.modifiers.new("Rounded flexible strap", 'BEVEL')
    bevel.width = .18
    bevel.segments = 3
    bands[side] = band

pull = [
    (1,-9.71),(12,-9.78),(30,-10.08),(42,-10.24),(48,-10.26),
    (49,-10.05),(50,-9.69),(51,-9.48),(53,-9.64),
    (56,-9.53),(60,-9.59),(70,-9.59),(192,-9.59)
]
pouch_positions = [(f,(0,y,1.79)) for f,y in pull]
pose(rig, "location", pouch_positions)
for side, band in bands.items():
    x = -.205 if side=="LEFT" else .205
    start = tips[side]
    for f,y in pull:
        target = Vector((x,y-.078,1.808))
        d = target-start
        band.location = (start+target)*.5
        band.rotation_quaternion = d.to_track_quat('Z','Y')
        band.scale = (.065,.025,d.length)
        for prop in ("location","rotation_quaternion","scale"):
            band.keyframe_insert(data_path=prop, frame=f)

# The ball remains held until the release, then travels independently.
steel.animation_data_clear()
steel_flight = [
    (1,(0,-9.71,1.79)),
    (12,(0,-9.78,1.79)),
    (30,(0,-10.08,1.79)),
    (42,(0,-10.24,1.79)),
    (48,(0,-10.26,1.79)),
    (49,(0,-10.00,1.80)),
    (50,(0,-9.69,1.81)),
    (51,(0,-9.43,1.81)),
    (67,(0,-6.63,1.76)),
    (82,(0,-3.47,1.69)),
    (94,(0,-.78,1.63)),
    (96,(0,-.29,1.63)),
    (99,(0,.07,1.63)),
    (106,(0,.63,1.555)),
    (116,(0,1.32,1.27)),
    (136,(0,2.15,.42)),
    (160,(0,2.54,.15)),
    (192,(0,2.54,.15))
]
pose(steel, "location", steel_flight)

# Adjust the opening POV so a correctly seated ball is visible while drawing.
for f,y in ((1,-11.23),(12,-11.27),(30,-11.47),(42,-11.62),(46,-11.67),(48,-11.67)):
    camera.location = (0,y,1.87)
    camera.rotation_euler = (Vector((0,-5.5,1.73))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert(data_path="location", frame=f)
    camera.keyframe_insert(data_path="rotation_euler", frame=f)

# Keep the follow camera BEHIND the projectile throughout its flight.
# Prior camera path overtook the ball at frame 67, hiding it completely.
for f, pos, aim in (
    (51,(0,-10.60,1.85),(0,-9.43,1.81)),
    (67,(0,-7.85,1.86),(0,-6.63,1.76)),
    (73,(.12,-6.45,1.85),(0,-5.44,1.73)),
    (82,(.22,-4.65,1.84),(0,-3.47,1.69)),
    (88,(.31,-3.10,1.84),(0,-1.98,1.64)),
    (94,(.39,-1.32,1.86),(0,-.12,1.63)),
):
    camera.location=pos
    camera.rotation_euler=(Vector(aim)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert('location',frame=f)
    camera.keyframe_insert('rotation_euler',frame=f)

# No movement magic: linearly interpolate through release for predictable physical staging.
def set_linear(obj, from_frame):
    ad = obj.animation_data
    if not ad or not ad.action: return
    action = ad.action
    if hasattr(action, "layers") and len(action.layers):
        for layer in action.layers:
            for strip in layer.strips:
                if strip.type != 'KEYFRAME': continue
                for channelbag in strip.channelbags:
                    for curve in channelbag.fcurves:
                        for kp in curve.keyframe_points:
                            if kp.co.x >= from_frame: kp.interpolation = 'LINEAR'
set_linear(steel, 48)

# QA checks ensure the cradle and projectile are colocated until firing.
for f in (1,12,30,42,48):
    scene.frame_set(f)
    if (steel.matrix_world.translation-rig.matrix_world.translation).length > .001:
        raise RuntimeError("BALL_NOT_SEATED frame=" + str(f))
scene.frame_set(67)
if steel.location.y < -7 or rig.location.y > -8:
    raise RuntimeError("RELEASE_OR_RETENTION_NOT_VALID")

scene.frame_start, scene.frame_end = 1, 192
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
print("PATCH_V3_SAVED", OUT_BLEND, "OBJECTS", len(bpy.data.objects), flush=True)

if MODE == "preview":
    preview = ROOT / "pouch_v3_preview"
    preview.mkdir(exist_ok=True)
    scene.render.resolution_percentage = 55
    for frame in (1,30,48,51,67):
        scene.frame_set(frame)
        scene.render.filepath = str(preview / ("stage_%03d.png" % frame))
        bpy.ops.render.render(write_still=True)
        print("PREVIEW_OK", frame, flush=True)
elif MODE == "video":
    frames = ROOT / "frames_pouch_v3"
    frames.mkdir(exist_ok=True)
    scene.render.resolution_percentage = 70
    scene.render.filepath = str(frames / "frame_")
    bpy.ops.render.render(animation=True)
    print("VIDEO_FRAMES_V3_DONE", flush=True)
