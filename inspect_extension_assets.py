import bpy
from pathlib import Path
R=Path.home()/"Downloads"/"slingshot_quality_proof"
out=[]
for kind in ("steel","billiard","egg"):
 p=R/"cinematic_50m_v8"/f"{kind}_50M_V8_LAUNCH.blend"
 bpy.ops.wm.open_mainfile(filepath=str(p))
 a=bpy.data.objects.get("POLISHED STEEL SHOT")
 out.append(f"KIND={kind} BLEND={p.exists()} BALL={a.name if a else '-'}")
 if a:
  out.append("DIMS "+str(tuple(round(x,3) for x in a.dimensions))+" SCALE "+str(tuple(round(x,3) for x in a.scale)))
  out.append("PARENTS "+str([(x.name,x.parent.name if x.parent else "",x.type) for x in bpy.data.objects if x.parent==a][:15]))
  out.append("MATERIALS "+str([(m.name,m.diffuse_color[:]) for m in a.data.materials]))
 out.append("Named 8 "+str([(x.name,x.type) for x in bpy.data.objects if "8" in x.name.lower() and ("billiard" in x.name.lower() or "number" in x.name.lower())][:20]))
o=R/"extension_asset_report.txt";o.write_text("\n".join(out),encoding="utf8")
print("REPORT",o,flush=True)
