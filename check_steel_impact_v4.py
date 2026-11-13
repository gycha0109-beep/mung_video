from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
r=Path.home()/"Downloads"/"slingshot_quality_proof"
v=r/"cinematic_20m_v4"/"steel"/"impact"
old=r/"physics_proof_v1"/"frames"
frs=[13,17,24,40,48]
can=Image.new("RGB",(5*240,2*440),(10,10,15));d=ImageDraw.Draw(can)
for i,f in enumerate(frs):
 for row,(label,folder) in enumerate((("OLD",old),("V4",v))):
  p=folder/f"frame_{f:04d}.png"
  with Image.open(p) as img:im=ImageOps.fit(img.convert("RGB"),(240,410))
  x=i*240;y=row*440
  can.paste(im,(x,y+30))
  d.text((x+7,y+8),f"{label} frame {f}",fill="white")
out=r/"cinematic_20m_v4"/"STEEL_IMPACT_COMPARE.jpg"
can.save(out,quality=90);print(out)
