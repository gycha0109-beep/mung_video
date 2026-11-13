from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path.home()/"Downloads"/"slingshot_quality_proof"
out=root/"extended_v1"
out.mkdir(exist_ok=True)
sets=[
("STEEL LAUNCH",root/"frames_pouch_v3",[1,30,48,52,58,67,73,82,88,94]),
("STEEL IMPACT",root/"physics_proof_v1"/"frames",[1,8,13,17,24,32,40,48]),
("EGG LAUNCH",root/"three_shots"/"egg"/"launch",[1,30,48,52,58]),
("EGG IMPACT",root/"three_shots"/"egg"/"impact"/"frames",[1,8,13,17,24,32,40,48]),
("BILLIARD LAUNCH",root/"three_shots"/"billiard"/"launch",[1,30,48,52,58]),
("BILLIARD IMPACT",root/"three_shots"/"billiard"/"impact"/"frames",[1,8,13,17,24,32,40,48])
]
w,h=180,320
sheet=Image.new("RGB",(w*10,(h+30)*len(sets)),(20,20,20))
draw=ImageDraw.Draw(sheet)
for row,(label,folder,frames) in enumerate(sets):
 for col,f in enumerate(frames):
  src=folder/f"frame_{f:04d}.png"
  if not src.exists():
   print("MISSING",src,flush=True);continue
  with Image.open(src) as im:
   tile=ImageOps.fit(im.convert("RGB"),(w,h))
   sheet.paste(tile,(col*w,row*(h+30)+30))
  draw.text((col*w+6,row*(h+30)+5),f"{label} {f:03d}",fill="white")
 print(label,"exists",len(list(folder.glob("frame_*.png"))),flush=True)
sheet.save(out/"INSPECTION_CONTACT.jpg",quality=79)
print("SHEET",out/"INSPECTION_CONTACT.jpg",flush=True)
