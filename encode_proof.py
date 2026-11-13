from pathlib import Path
import subprocess, imageio_ffmpeg, cv2
from PIL import Image,ImageOps,ImageDraw
root=Path.home()/"Downloads"/"slingshot_quality_proof"
frames=root/"frames"
paths=[frames/("frame_%04d.png"%i) for i in range(1,193)]
missing=[p.name for p in paths if not p.exists()]
if missing:raise RuntimeError("MISSING_"+str(len(missing))+" "+str(missing[:8]))
for n in (1,45,94,97,125,192):
 with Image.open(paths[n-1]) as im:
  if im.size!=(756,1344):raise RuntimeError("BAD_DIM "+str(n)+" "+str(im.size))
audio=root/"quality_proof_sound.wav"
out=root/"SLINGSHOT_STEEL_8SEC_QUALITY_PROOF.mp4"
ff=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ff,"-y","-hide_banner","-loglevel","warning",
 "-framerate","24","-start_number","1","-i",str(frames/"frame_%04d.png"),
 "-i",str(audio),"-map","0:v","-map","1:a",
 "-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
 "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
 "-c:a","aac","-b:a","192k","-movflags","+faststart","-t","8",str(out)]
subprocess.run(cmd,check=True)
cap=cv2.VideoCapture(str(out))
n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
ok=True
for f in (5,54,96,121,179):
 cap.set(cv2.CAP_PROP_POS_FRAMES,f)
 valid,im=cap.read()
 ok=ok and valid and im.mean()>5
cap.release()
info=subprocess.run([ff,"-hide_banner","-i",str(out)],capture_output=True,text=True)
if not (ok and n==192 and abs(fps-24)<.1 and (width,height)==(1080,1920) and "Audio: aac" in info.stderr):
 raise RuntimeError("VIDEO_QA_FAIL "+str((ok,n,fps,width,height)))
print("MP4_VERIFIED",out,out.stat().st_size,n,fps,width,height,flush=True)
# Side-by-side visual evidence, 6 moments.
srcs=[("0s | POV",1),("2s | RELEASE",49),("3.8s | FOLLOW",92),("4s | COLLISION",99),("5.2s | DEBRIS",125),("7.5s | RESULT",181)]
panelw=300;panelh=560
canvas=Image.new("RGB",(panelw*3,panelh*2),(16,20,25))
d=ImageDraw.Draw(canvas)
for j,(label,frame) in enumerate(srcs):
 with Image.open(frames/("frame_%04d.png"%frame)) as im:
  tile=ImageOps.fit(im.convert("RGB"),(panelw,panelh-30))
 col=j%3;row=j//3;x=col*panelw;y=row*panelh
 canvas.paste(tile,(x,y+30))
 d.text((x+12,y+8),label,fill=(246,248,243))
panel=root/"proof_6frames_contact.jpg"
canvas.save(panel,quality=92)
print("PROOF_CONTACT",panel,flush=True)
