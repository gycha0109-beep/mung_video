import bpy
from pathlib import Path
R=Path.home()/"Downloads"/"slingshot_quality_proof"
lines=[]
for kind in ["egg","steel","billiard"]:
 bpy.ops.wm.open_mainfile(filepath=str(R/"cinematic_v2"/f"{kind}_launch_v2.blend"))
 lines.append("KIND "+kind)
 for o in bpy.data.objects:
  if o.type=="FONT":
   lines.append("TEXT "+o.name+" BODY "+repr(o.data.body)+" loc "+repr(list(o.location)))
  if any(t in o.name.lower() for t in ("letter","graphic","hud","label","logo")):lines.append("SIMILAR "+o.name+" "+o.type)
 ob=bpy.data.objects.get("POLISHED STEEL SHOT")
 lines.append("BALL "+str(ob.dimensions[:])+" mats "+repr([m.name for m in ob.data.materials]))
 for m in ob.data.materials:
  if m and m.use_nodes:
   bs=m.node_tree.nodes.get("Principled BSDF")
   if bs:
    lines.append("MAT "+m.name+" BASE "+repr(bs.inputs["Base Color"].default_value[:])+" metallic "+str(bs.inputs["Metallic"].default_value))
(R/"v8_labels_report.txt").write_text("\n".join(lines),encoding="utf8")
print("DONE "+str(R/"v8_labels_report.txt"),flush=True)
