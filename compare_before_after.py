from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import cv2
root=Path.home()/"Downloads"/"slingshot_quality_proof"
old=root.parent/"slingshot_pov_56s"/"slingshot_pov_56s.mp4"
cap=cv2.VideoCapture(str(old))
imgs=[]
for t in (.5,5.20):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
 ok,im=cap.read()
 if not ok:raise RuntimeError("OLD_FRAME_MISSING "+str(t))
 img=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
 imgs.append(img)
cap.release()
imgs.extend([Image.open(root/"hero_001.png"),Image.open(root/"hero_125.png")])
w,h=360,640
sheet=Image.new("RGB",(w*4,h+47),(16,18,22))
draw=ImageDraw.Draw(sheet)
labels=["PREVIOUS / PREPARE","PREVIOUS / IMPACT","NEW / PREPARE","NEW / IMPACT"]
for idx,im in enumerate(imgs):
 img=ImageOps.fit(im.convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
 sheet.paste(img,(idx*w,47))
 draw.text((idx*w+12,16),labels[idx],fill=(244,246,246))
out=root/"before_after.jpg"
sheet.save(out,quality=90)
print("SAVED_COMPARISON",out)
