import bpy
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v4"
bpy.ops.wm.open_mainfile(filepath=str(out/"GLASS_20_PANEL_CHALLENGE_V4_1.blend"))
s=bpy.context.scene
# Remove the rectangular end wall; it read as a painted CGI backdrop.
rear=bpy.data.objects.get("Rear wall")
if rear:rear.hide_render=True;rear.hide_viewport=True
# A clean smoky charcoal space makes glass edges legible.
w=s.world.node_tree.nodes.get("Background")
w.inputs["Color"].default_value=(.125,.14,.153,1)
w.inputs["Strength"].default_value=.50
# Prior attempt produced screen-space raytracing stipple on stacked panes.
s.eevee.use_raytracing=False
glass=bpy.data.materials["V3 clear thin glass"]
p=glass.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=(.80,.89,.91,1)
p.inputs["Roughness"].default_value=.075
p.inputs["Transmission Weight"].default_value=0.0
p.inputs["Alpha"].default_value=.14
glass.surface_render_method="BLENDED"
edge=bpy.data.materials["V3 glass fracture edge glints"]
p=edge.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=(.40,.52,.55,1)
p.inputs["Roughness"].default_value=.14
p.inputs["Transmission Weight"].default_value=0.0
p.inputs["Alpha"].default_value=.38
edge.surface_render_method="BLENDED"
# Moderated softboxes: overexposure destroyed surface differentiation.
for ob in bpy.data.objects:
    if ob.type=="LIGHT" and ob.data.type=="AREA":
        ob.data.energy*=.50
s.camera.data.lens=34
ball=bpy.data.objects.get("STEEL BALL | decelerating")
if ball:
    s.camera.data.dof.use_dof=True
    s.camera.data.dof.focus_object=ball
    s.camera.data.dof.aperture_fstop=9
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"GLASS_20_PANEL_CHALLENGE_V4_2.blend"))
print("V4_2_READY",flush=True)
