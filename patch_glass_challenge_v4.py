import bpy, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
src=root/"glass_panel_challenge_v3"/"GLASS_20_PANEL_CHALLENGE_V3.blend"
out=root/"glass_panel_challenge_v4"
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene
data=json.loads((root/"glass_panel_challenge_v3"/"physics_results.json").read_text(encoding="utf8"))
events=data["break_events"]
ball=bpy.data.objects["STEEL BALL | decelerating"]
camera=scene.camera
ball.animation_data_clear()
camera.animation_data_clear()

# The bead sits inside a movable pouch before the elastic release.
points=[(1,-9.13,1.48),(9,-9.13,1.48),(32,-10.75,1.48),
        (42,-10.75,1.48),(46,-10.75,1.48),(48,-9.18,1.48)]
points.extend((e["frame"],e["y"]-.05,1.48) for e in events if e["broken"])
stop=next(e for e in events if not e["broken"])
points.extend([(stop["frame"],stop["y"]-.13,1.48),(stop["frame"]+4,stop["y"]-.72,1.38),
               (stop["frame"]+12,stop["y"]-1.65,.78),
               (stop["frame"]+21,stop["y"]-1.8,.20),(192,stop["y"]-1.9,.105)])
for f,y,z in points:
    ball.location=(0,y,z)
    ball.keyframe_insert(data_path="location",frame=f)
    ball.rotation_euler=(f*.08,f*.035,f*.11)
    ball.keyframe_insert(data_path="rotation_euler",frame=f)

# The old fixed rubber bands misrepresented the launcher.
for obj in list(bpy.data.objects):
    if obj.name.startswith("Slingshot strap "):
        bpy.data.objects.remove(obj,do_unlink=True)
rubber=bpy.data.materials["Industrial rubber | projectile pouch"]
wood=bpy.data.materials["Polished dark hardwood"]

def make_band(side):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.011,depth=1)
    obj=bpy.context.object
    obj.name=f"V4 animated elastic band {side}"
    obj.data.materials.append(rubber)
    fork=Vector((side*.31,-9.3,1.69))
    for f,y in [(1,-9.13),(9,-9.13),(32,-10.75),(42,-10.75),(46,-10.75),
                (48,-9.17),(50,-9.31),(53,-9.15),(57,-9.20),(192,-9.20)]:
        pouch=Vector((side*.08,y,1.48))
        direction=pouch-fork
        obj.location=(fork+pouch)*.5
        obj.rotation_euler=direction.to_track_quat("Z","Y").to_euler()
        obj.scale=(1,1,direction.length)
        obj.keyframe_insert(data_path="location",frame=f)
        obj.keyframe_insert(data_path="rotation_euler",frame=f)
        obj.keyframe_insert(data_path="scale",frame=f)

for side in [-1,1]:make_band(side)
bpy.ops.mesh.primitive_cube_add(size=1)
pouch=bpy.context.object
pouch.name="V4 leather pouch | loaded, drawn, released"
pouch.dimensions=(.25,.065,.17)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
pouch.data.materials.append(rubber)
bevel=pouch.modifiers.new("Soft leather edges","BEVEL");bevel.width=.027;bevel.segments=3
for f,y in [(1,-9.13),(9,-9.13),(32,-10.75),(42,-10.75),(46,-10.75),
            (48,-9.17),(50,-9.31),(53,-9.15),(57,-9.20),(192,-9.20)]:
    pouch.location=(0,y,1.48)
    pouch.keyframe_insert(data_path="location",frame=f)

# Show the draw, brief tension hold and release before following the shot.
def camkey(frame,pos,tar):
    camera.location=pos
    camera.rotation_euler=(Vector(tar)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.keyframe_insert(data_path="location",frame=frame)
    camera.keyframe_insert(data_path="rotation_euler",frame=frame)
camkey(1,(1.5,-12.6,2.14),(0,-9.55,1.45))
camkey(10,(1.5,-12.6,2.14),(0,-9.55,1.45))
camkey(32,(1.55,-12.85,2.19),(0,-10,1.45))
camkey(42,(1.55,-12.85,2.19),(0,-10,1.45))
camkey(46,(1.54,-12.8,2.17),(0,-8.5,1.48))
camkey(55,(2.1,-7.05,2.2),(0,1.5,1.47))
for e in events:
    if not e["broken"]:break
    camkey(e["frame"],(2.12,e["y"]-6.75,2.23),(0,e["y"]+2.7,1.44))
camkey(stop["frame"],(2.18,stop["y"]-7.0,2.23),(0,stop["y"]+.2,1.42))
camkey(192,(2.18,stop["y"]-7.0,2.23),(0,stop["y"]+.2,1.42))

# Neutral studio, not a neon, stylised video game arena.
for ob in bpy.data.objects:
    if ob.name.startswith("LED runway stripe") or ob.name.startswith("Recessed indicator"):
        ob.hide_render=True
        ob.hide_viewport=True
mats={
 "Deep graphite laboratory concrete":(.25,.255,.26),
 "Blue-dark stage environment":(.19,.205,.215),
 "Brushed aluminium brackets":(.38,.38,.39),
 "V3 clear thin glass":(.89,.94,.96),
 "V3 glass fracture edge glints":(.73,.79,.82),
 "V3 stress fissures":(.75,.78,.81),
}
for name,c in mats.items():
    mat=bpy.data.materials.get(name)
    if mat:
        node=mat.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value=(*c,1)
        if name=="V3 clear thin glass":
            node.inputs["Roughness"].default_value=.025
            node.inputs["Transmission Weight"].default_value=.78
            node.inputs["Alpha"].default_value=.11
        elif name=="V3 glass fracture edge glints":
            node.inputs["Alpha"].default_value=.62
        elif name=="V3 stress fissures":
            node.inputs["Emission Strength"].default_value=0.0
world=scene.world
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.35,.37,.39,1)
bg.inputs["Strength"].default_value=.65
for ob in bpy.data.objects:
    if ob.type=="LIGHT":
        if ob.data.type=="AREA":
            ob.data.color=(1.0,.98,.95)
            ob.data.energy*=.7
try:
    scene.eevee.use_raytracing=True
    scene.eevee.taa_render_samples=48
except Exception as e:
    print("RAYTRACE_WARNING",e)
scene.render.resolution_percentage=100
scene.frame_set(1)
target=out/"GLASS_20_PANEL_CHALLENGE_V4_PREVIEW.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("V4_PREVIEW_SCENE_READY",target,flush=True)
