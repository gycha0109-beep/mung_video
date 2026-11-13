from pathlib import Path
import subprocess, imageio_ffmpeg, cv2
from PIL import Image, ImageDraw, ImageOps
root = Path.home() / "Downloads" / "slingshot_quality_proof"
frames = root / "frames_pouch_v3"
paths = [frames/("frame_%04d.png"%i) for i in range(1,193)]
missing = [p.name for p in paths if not p.exists()]
if missing:
    raise RuntimeError("MISSING_FRAMES "+str(len(missing))+" "+str(missing[:8]))
sound = root/"quality_proof_sound.wav"
out = root/"SLINGSHOT_STEEL_8SEC_POUCH_V3.mp4"
ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ff,"-y","-hide_banner","-loglevel","warning",
    "-framerate","24","-start_number","1","-i",str(frames/"frame_%04d.png"),
    "-i",str(sound),"-map","0:v","-map","1:a",
    "-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
    "-c:v","libx264","-preset","fast","-crf","17",
    "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
    "-movflags","+faststart","-t","8",str(out)]
subprocess.run(cmd,check=True)
cap = cv2.VideoCapture(str(out))
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = float(cap.get(cv2.CAP_PROP_FPS))
shape = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
frames_ok = True
for frame in (0,30,48,51,67,96,125,179):
    cap.set(cv2.CAP_PROP_POS_FRAMES,frame)
    okay,img = cap.read()
    frames_ok = frames_ok and okay and img is not None and img.mean()>6
cap.release()
info = subprocess.run([ff,"-hide_banner","-i",str(out)],capture_output=True,text=True)
audio_ok = "Audio: aac" in info.stderr
if n != 192 or abs(fps-24)>.1 or shape!=(1080,1920) or not frames_ok or not audio_ok:
    raise RuntimeError("QA_FAILED "+repr((n,fps,shape,frames_ok,audio_ok)))
print("MP4_VERIFIED",out,out.stat().st_size,n,fps,shape,"AUDIO_OK",flush=True)
samples=[("1 | cradle",1),("30 | drawing",30),("48 | full pull",48),("51 | release",51),
         ("67 | flight",67),("96 | collision",96)]
w,h=270,505
canvas=Image.new("RGB",(3*w,2*h),(20,23,28))
draw=ImageDraw.Draw(canvas)
for idx,(label,fr) in enumerate(samples):
    with Image.open(paths[fr-1]) as src:
        tile=ImageOps.fit(src.convert("RGB"),(w,h-27))
    x=(idx%3)*w;y=(idx//3)*h
    canvas.paste(tile,(x,y+27))
    draw.text((x+10,y+7),label,fill=(255,255,255))
proof=root/"POUCH_V3_RELEASE_PROOF.jpg"
canvas.save(proof,quality=88)
print("PROOF_VERIFIED",proof,flush=True)
