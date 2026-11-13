import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path.home()/"Downloads"/"slingshot_quality_proof"
kind=sys.argv[sys.argv.index("--")+1]
mode=sys.argv[sys.argv.index("--")+2] if len(sys.argv)>sys.argv.index("--")+2 else "preview"
source=(root/"physics_proof_v1"/"PHYSICAL_IMPACT_DEMO.blend" if kind=="steel" else root/"three_shots"/kind/"impact"/"PHYSICAL_IMPACT_DEMO.blend")
out=root/"cinematic_v2"/kind/"replay_frames"
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720;s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="video" else 72
s.render.fps=24
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.image_settings.compression=20
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.28
s.frame_end=58
s.rigidbody_world.point_cache.frame_end=65
cam=s.camera
cam.animation_data_clear()
cam.data.animation_data_clear()
def pose(f,loc,target,lens):
 cam.location=loc
 cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
 cam.keyframe_insert("location",frame=f);cam.keyframe_insert("rotation_euler",frame=f)
 cam.data.lens=lens;cam.data.keyframe_insert("lens",frame=f)
pose(12,(-1.8,-3.65,1.82),(0,0,1.34),40)
pose(22,(-1.5,-3.25,1.56),(0,.02,1.3),43)
pose(36,(-1.2,-2.83,1.38),(0,.08,1.19),47)
pose(48,(-1.12,-2.66,1.30),(0,.12,1.08),50)
pose(58,(-1.12,-2.66,1.30),(0,.12,1.08),50)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/"cinematic_v2"/(kind+"_replay_v2.blend")))
for f in range(2,12):s.frame_set(f)
print("REPLAY_SCENE_READY",kind,flush=True)
if mode=="preview":
 for fr in (12,17,23,34,48,58):
  for j in range(s.frame_current+1,fr+1):s.frame_set(j)
  s.render.filepath=str(root/"cinematic_v2"/kind/("replay_check_%03d.png"%fr))
  bpy.ops.render.render(write_still=True)
  print("REPLAY_PREVIEW",kind,fr,flush=True)
else:
 s.frame_start=12
 s.render.filepath=str(out/"frame_")
 bpy.ops.render.render(animation=True)
 print("REPLAY_FRAMES_DONE",kind,flush=True)
