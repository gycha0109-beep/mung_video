from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import imageio_ffmpeg, cv2, subprocess, ast
root=Path.home()/"Downloads"/"slingshot_quality_proof"
work=root/"physics_proof_v1"
frames=work/"frames"
allframes=[frames/("frame_%04d.png"%i) for i in range(1,49)]
missing=[x.name for x in allframes if not x.exists()]
if missing:raise RuntimeError("MISSING_RENDER_FRAMES "+repr(missing))
rows=[ast.literal_eval(x) for x in (work/"physics_samples.txt").read_text(encoding="utf-8").splitlines()]
assert len(rows)==9 and any(x[0]==17 and x[2]>=20 for x in rows),rows
ff=imageio_ffmpeg.get_ffmpeg_exe()
sound=root/"quality_proof_sound.wav"
out=work/"PHYSICS_IMPACT_2SEC_CYCLES.mp4"
cmd=[ff,"-y","-hide_banner","-loglevel","error","-framerate","24","-start_number","1",
     "-i",str(frames/"frame_%04d.png"),
     "-ss","3.5","-t","2","-i",str(sound),
     "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","medium","-crf","16",
     "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-t","2","-movflags","+faststart",str(out)]
subprocess.run(cmd,check=True)
cap=cv2.VideoCapture(str(out))
n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps=float(cap.get(cv2.CAP_PROP_FPS))
dims=(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
checks=[]
for idx in (0,8,12,14,17,22,31,47):
    cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
    ret,frame=cap.read()
    if not ret:raise RuntimeError("VIDEO_READ_FAILED_"+str(idx))
    checks.append((idx,round(frame.mean(),1)))
cap.release()
pr=subprocess.run([ff,"-hide_banner","-i",str(out)],capture_output=True,text=True)
audio="Audio: aac" in pr.stderr
if n!=48 or abs(fps-24)>.05 or dims!=(720,1280) or not audio or min(x[1] for x in checks)<7:
    raise RuntimeError("QA_FAILED "+repr((n,fps,dims,audio,checks)))
print("VIDEO_QA_PASS",out,"BYTES",out.stat().st_size,"FRAMES",n,"FPS",fps,"SIZE",dims,"AUDIO",audio,flush=True)
labels=[("Before contact",8),("Contact",13),("Physics +4",17),
        ("Debris motion",22),("Rubble",32),("Settle",44)]
W,H=240,460
board=Image.new("RGB",(W*3,H*2),(24,26,30))
draw=ImageDraw.Draw(board)
for i,(label,number) in enumerate(labels):
    with Image.open(frames/("frame_%04d.png"%number)) as im:
        tile=ImageOps.fit(im.convert("RGB"),(W,H-34))
    x=i%3*W; y=i//3*H
    board.paste(tile,(x,y+34))
    draw.text((x+8,y+9),label,fill=(245,245,245))
poster=work/"PHYSICAL_SIMULATION_6_MOMENTS.jpg"
board.save(poster,quality=92)
print("PROOF_CONTACT",poster,flush=True)
