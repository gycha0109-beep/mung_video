import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
KIND=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "egg"
scene_path=ROOT/"slingshot_pouch_mechanics_v3.blend"
output=ROOT/"three_shots"/KIND/"launch"
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene=bpy.context.scene
scene.frame_start=1;scene.frame_end=58
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.fps=24
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
ball=bpy.data.objects["POLISHED STEEL SHOT"]
mat=bpy.data.materials.new(KIND+" projectile finish")
mat.use_nodes=True
bsdf=mat.node_tree.nodes.get("Principled BSDF")
if KIND=="egg":
    bsdf.inputs["Base Color"].default_value=(.83,.70,.51,1)
    bsdf.inputs["Roughness"].default_value=.51
    bsdf.inputs["Metallic"].default_value=0
    n=mat.node_tree.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value=74
    n.inputs["Detail"].default_value=3
    bump=mat.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.18
    bump.inputs["Distance"].default_value=.002
    mat.node_tree.links.new(n.outputs["Fac"],bump.inputs["Height"])
    mat.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    # Thin egg, widest at the broad end; mesh deformation in place.
    for vertex in ball.data.vertices:
        z=vertex.co.z/.142
        wid=1+.10*z-.08*z*z
        vertex.co.x*=.82*wid
        vertex.co.y*=.85*wid
        vertex.co.z*=1.20
    bpy.data.objects["Top score in lens"].data.body="SHOT 01   /   EGG"
elif KIND=="billiard":
    bsdf.inputs["Base Color"].default_value=(.012,.012,.016,1)
    bsdf.inputs["Roughness"].default_value=.13
    bsdf.inputs["Coat Weight"].default_value=.68
    bsdf.inputs["Coat Roughness"].default_value=.085
    # An embedded white disk plus numeral on the front-facing black ball.
    white=bpy.data.materials.new("Billiard ivory number 8 field")
    white.diffuse_color=(.93,.88,.73,1);white.use_nodes=True
    white.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.93,.88,.73,1)
    white.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.26
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,radius=.049)
    patch=bpy.context.object;patch.name="8 ball white medallion"
    patch.parent=ball
    patch.location=(0,-.138,0)
    patch.scale=(1,.15,1)
    patch.data.materials.append(white)
    ink=bpy.data.materials.new("8 ball numeral ink")
    ink.diffuse_color=(.012,.012,.018,1);ink.use_nodes=True
    ink.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.018,.018,.025,1)
    curve=bpy.data.curves.new("number-eight","FONT")
    curve.body="8";curve.size=.075;curve.align_x="CENTER";curve.align_y="CENTER"
    number=bpy.data.objects.new("White circle black eight",curve)
    bpy.context.collection.objects.link(number)
    number.parent=ball;number.location=(0,-.147,0)
    number.rotation_euler=(math.pi/2,0,0)
    number.data.materials.append(ink)
    bpy.data.objects["Top score in lens"].data.body="SHOT 03   /   8 BALL"
elif KIND=="steel":
    bsdf.inputs["Base Color"].default_value=(.33,.38,.42,1)
    bsdf.inputs["Metallic"].default_value=.93
    bsdf.inputs["Roughness"].default_value=.18
    bpy.data.objects["Top score in lens"].data.body="SHOT 02   /   STEEL"
else:raise RuntimeError(KIND)
ball.data.materials.clear();ball.data.materials.append(mat)
# Pouch is parented to its own rig and has no hard dependency on projectile geometry.
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(output/(KIND+"_launch.blend")))
scene.render.filepath=str(output/"frame_")
print("LAUNCH_SCENE_READY",KIND,scene.frame_end,flush=True)
if KIND=="preview":
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("LAUNCH_FRAMES_COMPLETE",KIND,flush=True)
