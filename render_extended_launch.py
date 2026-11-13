import bpy,sys
from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"
kind=sys.argv[sys.argv.index("--")+1]
folder=root/"three_shots"/kind/"launch"
project=folder/(kind+"_launch.blend")
bpy.ops.wm.open_mainfile(filepath=str(project))
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.fps=24
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=str(folder/"frame_")
scene.frame_start=59
scene.frame_end=82
scene.frame_set(59)
bpy.ops.wm.save_as_mainfile(filepath=str(root/"extended_v1"/(kind+"_flight_extended.blend")))
print("EXTENSION_RENDER_STARTED",kind,flush=True)
bpy.ops.render.render(animation=True)
print("EXTENSION_RENDER_FINISHED",kind,flush=True)
