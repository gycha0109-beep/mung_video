import bpy,sys
from pathlib import Path
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v8"
kind=sys.argv[sys.argv.index("--")+1]
mode=sys.argv[sys.argv.index("--")+2] if len(sys.argv)>sys.argv.index("--")+2 else "full"
source=R/"physics_proof_v1"/"PHYSICAL_IMPACT_DEMO.blend" if kind=="steel" else R/"three_shots"/kind/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.render.engine="BLENDER_EEVEE"
s.render.resolution_x=720
s.render.resolution_y=1280
s.render.resolution_percentage=100 if mode=="full" else 66
s.render.fps=24
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
s.render.image_settings.compression=15
s.render.use_motion_blur=True
s.render.motion_blur_shutter=.30
s.frame_start=1
s.frame_end=108
if s.rigidbody_world:s.rigidbody_world.point_cache.frame_end=108
# Billiard source contains physical ball and number but they were hidden in the old render.
if kind=='billiard':
 for object_name in ('PHYSICS 8 BALL','8 numbered billiard'):
  o=bpy.data.objects[object_name]
  o.hide_render=False
  print('BILLIARD_VISIBLE',o.name,flush=True)
# One fixed wide camera for entire aftermath; NO zoom, dolly, crop or retiming.
cam=s.camera
cam.animation_data_clear()
cam.data.animation_data_clear()
s.frame_set(13)
cam_pos=cam.location.copy()
cam_rot=cam.rotation_euler.copy()
cam_lens=cam.data.lens
cam.location=cam_pos
cam.rotation_euler=cam_rot
cam.data.lens=cam_lens
print("STATIC_IMPACT_CAMERA",kind,list(cam_pos),cam_lens,flush=True)
s.frame_set(1)
sav=OUT/f"{kind}_V8_IMPACT_STATIC.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(sav))
folder=OUT/kind/"impact"
folder.mkdir(parents=True,exist_ok=True)
samples={13,24,38,48,49,60,84,108}
# Rigid bodies must be warmed sequentially from frame1.
for f in range(1,109):
 s.frame_set(f)
 if mode=="preview" and f not in samples:continue
 if mode=="full" and f<(13 if kind=="billiard" else 49):continue
 dest=folder/f"frame_{f:04d}.png"
 s.render.filepath=str(dest)
 bpy.ops.render.render(write_still=True)
 if f%12==0 or f==108:print("STATIC_IMPACT_RENDER",kind,f,flush=True)
print("STATIC_CAMERA_DONE",kind,flush=True)
