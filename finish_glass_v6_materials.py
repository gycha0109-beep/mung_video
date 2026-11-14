import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v6"
bpy.ops.wm.open_mainfile(filepath=str(O/"GLASS_V6_LAUNCH_AND_ONE_PANE.blend"))
s=bpy.context.scene
s.view_settings.exposure=-.38
# Less plastic sheen on elastics. Set lower base-color, reduced dielectric glint.
latex=bpy.data.materials["V6 flat latex rubber bands"]
p=latex.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=(.015,.014,.012,1)
p.inputs["Roughness"].default_value=.95
try:p.inputs["IOR Level"].default_value=.12
except Exception:pass
wood=bpy.data.materials["V6 solid walnut grip layered grain"]
p=wood.node_tree.nodes.get("Principled BSDF")
noise=wood.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=6.5
noise.inputs["Detail"].default_value=4
ramp=wood.node_tree.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.12
ramp.color_ramp.elements[0].color=(.125,.052,.025,1)
ramp.color_ramp.elements[1].position=.83
ramp.color_ramp.elements[1].color=(.30,.16,.072,1)
wood.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
wood.node_tree.links.new(ramp.outputs["Color"],p.inputs["Base Color"])
# Shift the camera's depth-of-field gently from the launcher to the glass.
cam=s.camera
cam.data.dof.use_dof=True
cam.data.dof.aperture_fstop=8.0
for f,d in [(1,3.40),(23,3.30),(29,3.3),(34,3.9),(40,4.25),(43,4.48),(84,4.30)]:
    cam.data.dof.focus_distance=d
    cam.data.dof.keyframe_insert(data_path="focus_distance",frame=f)
s.frame_set(1)
dest=O/"GLASS_V6_QUALITY_FINAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print("V6_FINAL_SCENE_READY",dest,flush=True)
