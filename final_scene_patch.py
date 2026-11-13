import bpy,sys
from pathlib import Path
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
blend=ROOT/"slingshot_quality_proof_v2.blend"
bpy.ops.wm.open_mainfile(filepath=str(blend))
S=bpy.context.scene
for mat in bpy.data.materials:
 if mat.name.startswith("Photographed kiln-fired brick"):
  nodes=mat.node_tree.nodes
  links=mat.node_tree.links
  b=nodes.get("Principled BSDF")
  img=next((n for n in nodes if n.bl_idname=="ShaderNodeTexImage"),None)
  cr=next((n for n in nodes if n.bl_idname=="ShaderNodeValToRGB"),None)
  if img and cr and b:
   mix=nodes.new("ShaderNodeMixRGB")
   mix.blend_type="MIX"
   mix.inputs[0].default_value=.41
   links.new(cr.outputs["Color"],mix.inputs[1])
   links.new(img.outputs["Color"],mix.inputs[2])
   links.new(mix.outputs["Color"],b.inputs["Base Color"])
for obj in bpy.data.objects:
 if obj.name.startswith("Right hand with leather glove") or obj.name.startswith("Protective glove fingers") or obj.name.startswith("Wrist of shooter"):
  obj.hide_render=True
  obj.hide_viewport=True
for obj in bpy.data.objects:
 if obj.name=="Small lens legend":
  obj.data.body="10M   /   PULL   /   RELEASE"
S.render.resolution_percentage=70
S.render.filepath=str(ROOT/"frames"/"frame_")
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
print("FINAL_SCENE_PATCHED",blend,"materials",sum(1 for m in bpy.data.materials if m.name.startswith("Photographed kiln-fired brick")),flush=True)
