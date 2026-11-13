import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_20m_v4"
kind=sys.argv[sys.argv.index("--")+1]
mode=sys.argv[sys.argv.index("--")+2] if len(sys.argv)>sys.argv.index("--")+2 else "preview"
source=ROOT/"physics_proof_v1"/"PHYSICAL_IMPACT_DEMO.blend" if kind=="steel" else ROOT/"three_shots"/kind/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.open_mainfile(filepath=str(source))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=720
sc.render.resolution_y=1280
sc.render.resolution_percentage=100 if mode=="full" else 58
sc.render.fps=24
sc.render.image_settings.file_format="PNG"
sc.render.image_settings.color_mode="RGB"
sc.render.image_settings.compression=17
sc.render.use_motion_blur=True
sc.render.motion_blur_shutter=.3
sc.frame_start=1
sc.frame_end=108
sc.rigidbody_world.point_cache.frame_end=108
cam=sc.camera
# Maintain original physical camera and cut, with gentle settling camera move post-impact only.
def put_camera(fr,pos,target,lens):
 cam.location=pos
 cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat("-Z","Y").to_euler()
 cam.keyframe_insert("location",frame=fr)
 cam.keyframe_insert("rotation_euler",frame=fr)
 cam.data.lens=lens
 cam.data.keyframe_insert(data_path="lens",frame=fr)
# At f48, the projectile and fragment positions follow the preserved rigid-body simulation.
sc.frame_set(48)
start_pos=cam.location.copy()
start_aim=cam.rotation_euler.copy()
start_lens=cam.data.lens
for frame in (48,49):
 cam.location=start_pos
 cam.rotation_euler=start_aim
 cam.keyframe_insert("location",frame=frame)
 cam.keyframe_insert("rotation_euler",frame=frame)
 cam.data.lens=start_lens
 cam.data.keyframe_insert("lens",frame=frame)
# Restrained dolly, no jitter and no slowed physics.
p=start_pos
if kind=="steel":
 put_camera(76,(p.x+.12,p.y-.30,p.z+.04),(0,.2,1.3),start_lens+1.6)
 put_camera(108,(p.x+.2,p.y-.45,p.z+.09),(0,.15,1.26),start_lens+2.2)
else:
 put_camera(76,(p.x+.10,p.y-.26,p.z+.04),(0,0,1.3),start_lens+1)
 put_camera(108,(p.x+.18,p.y-.45,p.z+.08),(0,0,1.25),start_lens+2)
sc.frame_set(1)
save=OUT/f"{kind}_impact_aftermath_4sec.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(save))
print("IMPACT_4SEC_SETUP",kind,save,flush=True)
if mode=="preview":
 for frame in (13,18,33,48,64,88,108):
  for f in range(sc.frame_current+1,frame+1):sc.frame_set(f)
  sc.render.filepath=str(OUT/f"{kind}_impact_preview_{frame:03d}.png")
  bpy.ops.render.render(write_still=True)
  print("PREVIEW_IMPACT",kind,frame,flush=True)
elif mode=="full":
 directory=OUT/kind/"impact"
 directory.mkdir(parents=True,exist_ok=True)
 sc.render.filepath=str(directory/"frame_")
 bpy.ops.render.render(animation=True)
 print("COMPLETE_IMPACT_4SEC",kind,flush=True)
