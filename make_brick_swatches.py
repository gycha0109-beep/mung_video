from PIL import Image,ImageOps,ImageEnhance,ImageDraw
from pathlib import Path
import random
root=Path.home()/"Downloads"/"slingshot_quality_proof"
src=Image.open(root/"brick_diff.jpg").convert("RGB")
sw,sh=src.size
print("ORIGINAL_SIZE",src.size)
out=root/"brick_faces";out.mkdir(exist_ok=True)
# Source scan: individual faces of real red bricks, avoiding grey mortar.
centers=[(47,26),(195,29),(339,29),(466,30),
(125,98),(266,98),(405,97),(65,168),(220,168),(389,168),
(121,248),(285,248),(447,249),(61,324),(220,322),(379,323),
(125,405),(280,405),(439,407),(70,477),(230,476),(384,474)]
random.seed(60)
sheet=Image.new("RGB",(4*200,6*150),(25,25,25))
for i in range(24):
 cx,cy=centers[i%len(centers)]
 cx=int(cx*sw/512);cy=int(cy*sh/512)
 dx=int(43*sw/512);dy=int(12*sh/512)
 crop=src.crop((max(0,cx-dx),max(0,cy-dy),min(sw,cx+dx),min(sh,cy+dy)))
 crop=crop.resize((512,256),Image.Resampling.LANCZOS)
 crop=ImageEnhance.Contrast(crop).enhance(1.18)
 crop=ImageEnhance.Color(crop).enhance(.91+random.random()*.19)
 crop.save(out/("brick_%02d.jpg"%i),quality=94)
 miniature=crop.resize((192,124),Image.Resampling.LANCZOS)
 sheet.paste(miniature,((i%4)*200,(i//4)*150))
 ImageDraw.Draw(sheet).text((i%4*200+5,i//4*150+125),str(i),fill="white")
sheet.save(root/"brick_swatches_contact.jpg",quality=90)
print("SWATCHES",len(list(out.glob("*.jpg"))),flush=True)
