from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
frames=(1,24,40,48,50,53,62,74,86,95)
canvas=Image.new("RGB",(190*5,342*2),(12,13,17))
d=ImageDraw.Draw(canvas)
for i,f in enumerate(frames):
 p=r/("egg_preview_%03d.png"%f)
 if not p.exists():continue
 with Image.open(p) as im:
  img=ImageOps.fit(im.convert("RGB"),(190,312))
 x=i%5*190;y=i//5*342
 canvas.paste(img,(x,y+30))
 d.text((x+7,y+7),str(f)+"/96  "+str(round((f-1)/24,2))+"s",fill="white")
out=r/"EGG_20M_PREVIEW_CONTACT.jpg"
canvas.save(out,quality=89)
print(out)
