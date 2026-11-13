import bpy
from pathlib import Path
src=Path.home()/"Downloads"/"slingshot_quality_proof"/"three_shots"/"egg"/"impact"/"PHYSICAL_IMPACT_DEMO.blend"
bpy.ops.wm.open_mainfile(filepath=str(src))
s=bpy.context.scene
print("CAM",s.camera.name,s.camera.location[:],s.camera.data.lens)
print("COUNTS",len(bpy.data.objects))
for ob in bpy.data.objects:
 n=ob.name.lower()
 if any(v in n for v in ("egg","yolk","album","splatter","splash","fluid","drop","shell","wall","liquid","stain","puddle","ground","floor")):
  if ob.type not in ("MESH","CURVE","EMPTY"):continue
  print("OB",ob.name,"LOC",tuple(round(x,3) for x in ob.location),"DIM",tuple(round(x,3) for x in ob.dimensions),"mat",','.join(x.name if x else "NONE" for x in ob.data.materials) if getattr(ob.data,"materials",None) else "-",flush=True)
print("MARKERS",[(m.frame,m.name) for m in s.timeline_markers])
