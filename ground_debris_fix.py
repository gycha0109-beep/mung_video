import bpy,random
from pathlib import Path
root=Path.home()/"Downloads"/"slingshot_quality_proof"
blend=root/"slingshot_quality_proof_v2.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend))
random.seed(1201)
count=0
S=bpy.context.scene
for ob in bpy.data.objects:
 if ob.name.startswith("FRACTURED BRICK SHARD"):
  for f in (169,170,180,192):
   S.frame_set(f)
   p=ob.location.copy()
   p.z=max(.07,random.uniform(.09,.14))
   # Deflate trajectory to an actual ground landing rather than 4s hovering.
   ob.location=p
   ob.keyframe_insert(data_path="location",frame=f)
  count+=1
S.frame_start=145
S.frame_end=192
S.render.filepath=str(root/"frames"/"frame_")
S.render.resolution_percentage=70
S.frame_set(145)
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print("GROUNDED_DEBRIS",count,"RENDER_RANGE",S.frame_start,S.frame_end,flush=True)
