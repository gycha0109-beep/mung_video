from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
a=(13,18,33,48,64,88,108)
c=Image.new("RGB",(7*165,320),(15,15,15));d=ImageDraw.Draw(c)
for i,f in enumerate(a):
 p=r/("egg_impact_preview_%03d.png"%f)
 with Image.open(p) as im:tile=ImageOps.fit(im.convert("RGB"),(165,295))
 c.paste(tile,(i*165,25));d.text((i*165+6,5),f"{f} ({(f-13)/24:.2f}s)",fill="white")
o=r/"EGG_IMPACT_4SEC_PROOF.jpg";c.save(o,quality=90);print(o)
