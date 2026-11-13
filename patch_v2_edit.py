from pathlib import Path
p=Path.home()/"Downloads"/"slingshot_quality_proof"/"make_cinematic_v2.py"
s=p.read_text(encoding="utf8")
pairs=[
 ("FPS=24;SR=48000;W=720;H=1280;TOTAL=180","FPS=24;SR=48000;W=720;H=1280;TOTAL=168"),
 ("def blend_slow_frame(kind,pos):","def blend_slow_frame(kind,pos,seg='replay'):"),
 ("fa=int(math.floor(pos));fb=min(58,fa+1)","fa=int(math.floor(pos));fb=min(58 if seg=='replay' else 48,fa+1)"),
 ("aa=still(kind,\"replay\",fa)","aa=still(kind,seg,fa)"),
 ("bb=still(kind,\"replay\",fb)","bb=still(kind,seg,fb)"),
 ("key=(kind,fa,fb)","key=(kind,seg,fa,fb)"),
 (''' t=(i-89)/90
 t=t**1.22
 return blend_slow_frame(kind,12+46*t)''',''' if i<139:
  t=(i-89)/49
  return blend_slow_frame(kind,12+23*(t**1.15),'replay')
 t=(i-139)/28
 return blend_slow_frame(kind,36+12*t,'impact')'''),
 ("replay=89/FPS+(16-12)/(58-12)*(91/FPS)","replay=89/FPS+(16-12)/(35-12)*(50/FPS)"),
 ("for j,f in enumerate((1,16,27,32,36,49,57,70,85,95,114,144,160,177)[:8]):","for j,f in enumerate((1,16,32,38,58,85,118,160):"),
 ('("replay",12,58)','("replay",12,35)')
]
for old,new in pairs:
 if old not in s:raise RuntimeError("MISSING PATCH "+old)
 s=s.replace(old,new,1)
p.write_text(s,encoding="utf8")
compile(s,str(p),"exec")
print("V2_EDITED_FINAL_TIMELINE_168_FRAMES")
