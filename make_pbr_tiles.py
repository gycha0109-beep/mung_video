from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,random
root=Path.home()/"Downloads"/"slingshot_quality_proof"/"physics_proof_v1"
inp=root/"brick_pbr_2k"
out=root/"wall_tiles"
out.mkdir(exist_ok=True)
paths={x:inp/("Bricks077_2K-JPG_"+name+".jpg") for x,name in {"color":"Color","rough":"Roughness","normal":"NormalGL"}.items()}
ims={k:Image.open(p).convert("RGB") for k,p in paths.items()}
arr=np.asarray(ims["color"])
H,W=arr.shape[:2]
rng=random.Random(110926)
w,h=92,42
choices=[]
for j in range(11000):
    x=rng.randrange(2,W-w-2);y=rng.randrange(2,H-h-2)
    patch=arr[y:y+h,x:x+w]
    rd=patch[:,:,0].astype("int16")-patch[:,:,1].astype("int16")
    brickmask=(rd>13) & (patch[:,:,0]>55)
    quality=float(brickmask.mean())
    if quality<.975:continue
    if np.std(patch[:,:,0])<5:continue
    if any(abs(x-x0)<w and abs(y-y0)<h for x0,y0 in choices):continue
    choices.append((x,y))
    if len(choices)>=20:break
if len(choices)<8:
    raise RuntimeError("NO_USABLE_BRICK_PATCHES_"+str(len(choices)))
canvas=Image.new("RGB",(5*256,4*144),(18,20,22))
for i,(x,y) in enumerate(choices):
    for m,im in ims.items():
        patch=im.crop((x,y,x+w,y+h))
        patch.save(out/("%02d_%s.png"%(i,m)))
    large=ims["color"].crop((x,y,x+w,y+h)).resize((252,120))
    X=i%5*256;Y=i//5*144
    canvas.paste(large,(X,Y+20))
    ImageDraw.Draw(canvas).text((X+7,Y+4),str(i),fill=(255,255,255))
canvas.save(out/"PBR_TILE_CONTACT.png")
print("CROPS_EXTRACTED",len(choices),choices,"SIZE",W,H,flush=True)
