import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path.home()/"Downloads"/"slingshot_quality_proof"
kind=sys.argv[sys.argv.index("--")+1]
mode=sys.argv[sys.argv.index("--")+2] if len(sys.argv)>sys.argv.index("--")+2 else "preview"
source=(root/"physics_proof_v1"/"PHYSICAL_IMPACT_DEMO.blend" if kind=="steel"
        else root/"three_shots"/kind/"impact"/"PHYSICAL_IMPACT_DEMO.blend")
out=root/"cinematic_v2"/kind/"aftermath_frames"
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720;s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="video" else 75
s.render.fps=24
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.image_settings.compression=18
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.3
s.frame_end=98
s.rigidbody_world.point_cache.frame_end=98
cam=s.camera
cam.animation_data_clear()
cam.data.animation_data_clear()
def pose(f,loc,target,lens):
 cam.location=loc
 cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
 cam.keyframe_insert("location",frame=f);cam.keyframe_insert("rotation_euler",frame=f)
 cam.data.lens=lens;cam.data.keyframe_insert("lens",frame=f)
pose(49,(1.30,3.55,1.85),(0,.36,1.12),28)
pose(68,(1.74,2.55,1.55),(0,.20,1.0),34)
pose(83,(2.08,2.37,1.48),(0,.14,.95),38)
pose(98,(2.50,2.64,1.50),(0,.06,.88),42)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/"cinematic_v2"/(kind+"_aftermath_v2.blend")))
print("PHYSICS_WARMUP",kind,flush=True)
for f in range(2,49):
 s.frame_set(f)
print("PHYSICS_WARMED",kind,flush=True)
if mode=="preview":
 for f in (49,65,82,98):
  for n in range(s.frame_current+1,f+1):s.frame_set(n)
  s.render.filepath=str(root/"cinematic_v2"/kind/("aftermath_check_%03d.png"%f))
  bpy.ops.render.render(write_still=True)
  print("AFTERMATH_PREVIEW",kind,f,flush=True)
else:
 s.frame_start=49
 s.render.filepath=str(out/"frame_")
 bpy.ops.render.render(animation=True)
 print("AFTERMATH_RENDERED",kind,flush=True)
