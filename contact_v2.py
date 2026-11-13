from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_v2"
frames=(1,14,22,30,32,33,34,35,37,41)
canvas=Image.new("RGB",(220*5,420*2),(15,15,20))
d=ImageDraw.Draw(canvas)
for i,f in enumerate(frames):
 p=r/"steel"/("check_%03d.png"%f)
 img=Image.open(p).convert("RGB")
 tile=ImageOps.fit(img,(220,392))
 x=(i%5)*220;y=(i//5)*420
 canvas.paste(tile,(x,y+28))
 d.text((x+8,y+8),str(f),fill="#fff")
out=r/"STEEL_LAUNCH_V2_CONTACT.jpg"
canvas.save(out,quality=91)
print(out)
