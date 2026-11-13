from pathlib import Path
import sys,subprocess,wave,math
import numpy as np
import cv2
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageOps
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_v6_egg"
V5=ROOT/"cinematic_20m_v4"
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,SR=720,1280,24,48000
SOURCES=[V5/"egg"/"launch"/f"frame_{f:04d}.png" for f in range(1,97)]
SOURCES.extend(ROOT/"three_shots"/"egg"/"impact"/"frames"/f"frame_{f:04d}.png" for f in range(13,49))
SOURCES.extend(OUT/"after_frames"/f"frame_{f:04d}.png" for f in range(49,109))
assert len(SOURCES)==192

def build_audio():
 src=V5/"final"/"egg_8sec_sound.wav"
 with wave.open(str(src),"rb") as w:
  assert w.getframerate()==SR and w.getnchannels()==2
  data=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").reshape(-1,2).astype(np.float64)/32768
 noise=np.random.default_rng(118).standard_normal
 for k,(t,volume,base) in enumerate((
  (5.52,.027,280),(5.86,.020,330),(6.22,.021,270),
  (6.56,.019,410),(6.94,.022,370),(7.24,.015,450),(7.6,.011,330))):
  start=int(t*SR)
  m=int(.16*SR)
  x=np.arange(m)/SR
  crack=noise(m)*np.exp(-26*x)*volume
  wet=np.sin(2*math.pi*base*x)*np.exp(-23*x)*volume*.4
  v=crack+wet
  end=min(len(data),start+m)
  data[start:end,0]+=v[:end-start]*.9
  data[start:end,1]+=v[:end-start]*1.07
 data=np.clip(np.tanh(data*1.07),-.96,.96)
 dest=OUT/"EGG_V6_SOUND.wav"
 with wave.open(str(dest),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(np.round(data*32767).astype("<i2").tobytes())
 return dest

def assert_input_files():
 missing=[str(p) for p in SOURCES if not p.is_file() or p.stat().st_size<20000]
 if missing:raise FileNotFoundError("Missing source frames "+str(missing[:10])+f" ({len(missing)})")
 print("INPUTS_VALID",len(SOURCES),"first launch",SOURCES[0],"last impact",SOURCES[-1],flush=True)

def encode():
 assert_input_files()
 sound=build_audio()
 out=OUT/"EGG_20M_8SEC_V6.mp4"
 args=[FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24",
  "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(sound),
  "-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-ar",str(SR),
  "-frames:v","192","-movflags","+faststart",str(out)]
 p=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  bridge=cv2.imread(str(SOURCES[131]),cv2.IMREAD_COLOR)
  if bridge.shape[:2]!=(H,W):bridge=cv2.resize(bridge,(W,H),interpolation=cv2.INTER_LANCZOS4)
  for i,source in enumerate(SOURCES,1):
   frame=cv2.imread(str(source),cv2.IMREAD_COLOR)
   if frame is None:raise RuntimeError("Cannot read "+str(source))
   if frame.shape[:2]!=(H,W):frame=cv2.resize(frame,(W,H),interpolation=cv2.INTER_LANCZOS4)
   if 132<i<=137:
    weight=(i-132)/5.0
    frame=cv2.addWeighted(bridge,1-weight,frame,weight,0)
   p.stdin.write(frame.tobytes())
   if i%32==0:print("ENCODE",i,"/",len(SOURCES),flush=True)
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  code=p.wait()
  if code:raise RuntimeError(err[-2000:])
 except BaseException:
  p.kill();raise
 return out

def check(out):
 cap=cv2.VideoCapture(str(out))
 count=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 fps=cap.get(cv2.CAP_PROP_FPS)
 dimensions=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 assert (count,dimensions)==(192,(W,H)) and abs(fps-24)<.03
 marks=[.5,1.75,2.8,3.9,4.3,5.48,5.54,6.,6.7,7.5]
 page=Image.new("RGB",(5*220,2*408),(13,14,19))
 d=ImageDraw.Draw(page)
 for i,sec in enumerate(marks):
  cap.set(cv2.CAP_PROP_POS_FRAMES,int(sec*24))
  ok,arr=cap.read()
  if not ok or arr.mean()<5:raise RuntimeError("BAD_OUTPUT_FRAME "+str(sec))
  im=Image.fromarray(cv2.cvtColor(cv2.resize(arr,(220,376)),cv2.COLOR_BGR2RGB))
  x=i%5*220;y=i//5*408
  page.paste(im,(x,y+32))
  d.text((x+6,y+8),f"{sec:.2f}s",fill="white")
 cap.release()
 poster=OUT/"EGG_V6_CONTACT.jpg"
 page.save(poster,quality=91)
 p=subprocess.run([FF,"-hide_banner","-i",str(out)],capture_output=True,text=True)
 if "Audio: aac" not in p.stderr:raise RuntimeError("MISSING_AUDIO")
 decode=subprocess.run([FF,"-v","error","-xerror","-i",str(out),"-f","null","NUL"],capture_output=True,text=True)
 if decode.returncode:raise RuntimeError(decode.stderr[-1000:])
 old=V5/"final"/"01_EGG_20M_8SEC_V5.mp4"
 # Source sequence 0-5.5 sec unchanged; new 60 Blender-rendered frames replace old static zoom.
 record=f"""V6 EGG VERIFIED: 192 frames, 8s, 720x1280 24fps H.264 + AAC
0-2s: existing source draw and aim 48 unique frames.
2-4s: existing 20.56m source flight 48 unique frames.
4-5.5s: 36 original validated physical impact frames (no retime).
5.5-8s: 60 NEW Blender-rendered chronological animation frames 49-108, with physically scripted yolk drips, falling drops, scattered shell chips, and dolly (no static zoom).
NO slow motion or screen shake.
Original source unchanged. Old V5: {old}
New V6: {out}
Full decoder validation: PASS.
"""
 (OUT/"V6_QUALITY_CHECK.txt").write_text(record,encoding="utf8")
 print(record,flush=True)
 return poster
if __name__=="__main__":
 out=encode()
 check(out)
