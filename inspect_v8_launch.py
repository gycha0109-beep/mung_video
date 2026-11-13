import bpy,sys
from pathlib import Path
b=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v2"/"egg_launch_v2.blend"
bpy.ops.wm.open_mainfile(filepath=str(b))
s=bpy.context.scene
out=[]
for ob in s.objects:
 if any(q in ob.name.lower() for q in ['floor','wall','shot','pouch','band','latex','oak','camera','egg','polished','light','slingshot']):
  out.append('%-44s loc=%s dim=%s scale=%s'%(ob.name,str(tuple(round(x,3) for x in ob.location)),str(tuple(round(x,3) for x in ob.dimensions)),str(tuple(round(x,3) for x in ob.scale))))
o=bpy.data.objects.get("POLISHED STEEL SHOT")
if o:
 out.append('BALL materials '+str([(x.name,x.diffuse_color[:],x.use_nodes) for x in o.data.materials]))
 out.append('BALL rot '+str(o.rotation_euler[:])+' modifiers '+str([m.name for m in o.modifiers]))
out.append('WORLD '+str(s.world))
out.append('camera '+s.camera.name)
path=Path.home()/"Downloads"/"slingshot_quality_proof"/"v8_scene_inspection.txt"
path.write_text('\n'.join(out),encoding='utf8')
print('INSPECT',path,flush=True)
