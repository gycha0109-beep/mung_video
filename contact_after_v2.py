from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
p=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v2"/"steel"
files=[p/f"aftermath_check_{f:03d}.png" for f in (49,65,82,98)]
canvas=Image.new("RGB",(4*220,420),(10,10,10))
draw=ImageDraw.Draw(canvas)
for i,pic in enumerate(files):
 if not pic.exists():continue
 with Image.open(pic) as im:canvas.paste(ImageOps.fit(im.convert("RGB"),(220,390)),(i*220,30))
 draw.text((i*220+8,7),pic.stem,fill="white")
dest=p.parent/"AFTERMATH_STEEL_CONTACT.jpg"
canvas.save(dest,quality=90)
print(dest)
