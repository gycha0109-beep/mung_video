from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v6_egg"
can=Image.new("RGB",(6*200,390),(10,11,15))
d=ImageDraw.Draw(can)
for i,f in enumerate([48,49,60,75,90,108]):
 p=r/f"EGG_V6_PREVIEW_{f:03d}.png"
 with Image.open(p) as img:tile=ImageOps.fit(img.convert("RGB"),(200,360))
 can.paste(tile,(i*200,30))
 d.text((i*200+5,7),f"frame {f}",fill="white")
out=r/"V6_EGG_POST_PREVIEW_CONTACT.jpg"
can.save(out,quality=90)
print(out)
