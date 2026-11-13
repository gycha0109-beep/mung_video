import bpy
from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
bpy.ops.wm.open_mainfile(filepath=str(r/"steel_impact_aftermath_4sec.blend"))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE";s.render.resolution_percentage=65
s.render.resolution_x=720;s.render.resolution_y=1280
s.render.image_settings.file_format="PNG"
for f in range(1,18):
 s.frame_set(f)
deps=bpy.context.evaluated_depsgraph_get()
ball=bpy.data.objects["PHYSICS STEEL PROJECTILE"]
print("BALL"," ".join("%.3f"%v for v in ball.evaluated_get(deps).matrix_world.translation),flush=True)
s.render.filepath=str(r/"STEEL_17_MANUAL_SIM.png")
bpy.ops.render.render(write_still=True)
print("COMPLETE",flush=True)
