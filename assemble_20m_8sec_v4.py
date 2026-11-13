from pathlib import Path
import subprocess, wave, os, json
import cv2, numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg

ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"/"cinematic_20m_v4"
FINAL=ROOT/"final";FINAL.mkdir(parents=True,exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
FPS=24;W=720;H=1280;SR=48000
LAUNCH_N=96
IMPACT_START=13
IMPACT_END=108
TOTAL=192
TITLES={"egg":"01_EGG_20M_8SEC_V4","steel":"02_STEEL_20M_8SEC_V4","billiard":"03_BILLIARD_20M_8SEC_V4"}
rng=np.random.default_rng(20261111)

def make_audio(kind):
 n=SR*8
 x=np.zeros(n,dtype=np.float64)
 def add(t,signal):
  a=round(t*SR);b=min(n,a+len(signal))
  if b>a:x[a:b]+=signal[:b-a]
 def sound(t,dur,vol,decay,freq,style="noise"):
  m=int(SR*dur);q=np.arange(m)/SR
  noise=rng.standard_normal(m)
  if style=="metal":wave=(.40*noise+.64*np.sin(2*np.pi*(freq*q+65*q*q)))
  elif style=="resin":wave=(.28*noise+.68*np.sin(2*np.pi*(freq*q*np.exp(-1.3*q))))
  elif style=="wet":wave=(.50*noise+.48*np.sin(2*np.pi*(freq*q+39*q*q)))
  else:wave=noise
  add(t,vol*wave*np.exp(-decay*q))
 # Outdoor ambience, restrained and low-level.
 ambience=rng.standard_normal(n)
 ambience=np.convolve(ambience,np.ones(120)/120,mode='same')
 x+=.017*ambience
 # Tension and release at exactly 2s.
 for t,a in ((.40,.026),(.85,.036),(1.22,.047),(1.61,.055)):
  sound(t,.22,a,21,100)
 sound(1.99,.26,.26,28,300)
 sound(2.035,.13,.19,48,520)
 # 20m flight 2-4 seconds, whoosh with increasing mid-high frequency energy.
 t=np.arange(2*SR)/SR
 noise=rng.standard_normal(len(t))
 high=np.zeros_like(noise)
 high[1:]=noise[1:]-noise[:-1]
 envelope=np.sin(np.pi*t/2.)**.7
 fading=(.35+.25*(t/2))
 add(2.,(.16*noise+.12*high)*envelope*fading)
 # Impact starts at 4s; no slow motion, reactions decay naturally.
 if kind=="egg":
  sound(4.,.48,.48,13,170,"wet")
  sound(4.08,.90,.22,7,85,"wet")
  for dt,a in ((.15,.07),(.38,.06),(.70,.045),(1.13,.025),(1.85,.014)):
   sound(4.+dt,.25,a,18,95,"wet")
 elif kind=="steel":
  sound(4.,1.2,.67,8,112,"metal")
  sound(4.045,.48,.35,14,720)
  for dt,a in ((.12,.26),(.27,.20),(.46,.16),(.74,.12),(1.04,.09),(1.54,.06),(2.03,.035)):
   sound(4.+dt,.33,a,17,315)
 else:
  sound(4.,.45,.42,19,405,"resin")
  for dt,a in ((.24,.19),(.54,.125),(.91,.08),(1.36,.051),(2.02,.031)):
   sound(4.+dt,.28,a,24,390,"resin")
 x=np.tanh(x*1.35)*.78
 pcm=np.asarray(np.round(x*32767),dtype="<i2")
 wav=FINAL/(kind+"_8sec_sound.wav")
 with wave.open(str(wav),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(np.column_stack((pcm,pcm)).tobytes())
 return wav

def sources(kind):
 launch=ROOT/kind/"launch"
 impact=ROOT/kind/"impact"
 files=[launch/("frame_%04d.png"%f) for f in range(1,LAUNCH_N+1)]
 files.extend([impact/("frame_%04d.png"%f) for f in range(IMPACT_START,IMPACT_END+1)])
 missing=[str(p) for p in files if not p.exists()]
 if missing:raise RuntimeError("MISSING_IMAGES "+kind+" "+repr(missing[:6])+" and "+str(len(missing)))
 assert len(files)==TOTAL
 return files

def verify(path,expected):
 probe=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
 assert "Audio: aac" in probe.stderr,path
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
 shape=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 assert n==expected and abs(fps-FPS)<.1 and shape==(W,H),(n,fps,shape,expected)
 canvas=Image.new("RGB",(4*180,2*335),(10,13,17))
 draw=ImageDraw.Draw(canvas)
 moments=[.12,1.1,1.9,2.2,2.9,3.85,4.4,7.5] if expected==192 else [1,4,7,9,12,17,20,23]
 for i,t in enumerate(moments):
  cap.set(cv2.CAP_PROP_POS_FRAMES,min(n-1,round(t*FPS)))
  ok,arr=cap.read()
  if not ok or arr.mean()<5:raise RuntimeError("BAD_FRAME "+str((path,t)))
  pic=Image.fromarray(cv2.cvtColor(cv2.resize(arr,(180,305)),cv2.COLOR_BGR2RGB))
  X=i%4*180;Y=i//4*335
  canvas.paste(pic,(X,Y+30))
  draw.text((X+6,Y+7),str(round(t,2))+"s",fill="white")
 cap.release()
 if expected==TOTAL:
  canvas.save(FINAL/(path.stem+"_CONTACT.jpg"),quality=90)
 command=[FF,"-v","error","-xerror","-i",str(path),"-f","null","NUL"]
 test=subprocess.run(command,capture_output=True,text=True)
 if test.returncode:raise RuntimeError("DECODE_FAILURE "+test.stderr[-2000:])
 print("PASS",path.name,expected,"frames",round(expected/FPS,3),"seconds",shape,"AAC",path.stat().st_size,flush=True)

def encode(kind):
 fs=sources(kind)
 wav=make_audio(kind)
 out=FINAL/(TITLES[kind]+".mp4")
 cmd=[FF,"-y","-hide_banner","-loglevel","error",
 "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
 "-i",str(wav),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast",
 "-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
 "-ar","48000","-frames:v",str(TOTAL),"-movflags","+faststart",str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for idx,filename in enumerate(fs,1):
   arr=cv2.imread(str(filename),cv2.IMREAD_COLOR)
   if arr is None:raise RuntimeError("MISSING_PIXELS "+str(filename))
   if arr.shape[:2]!=(H,W):arr=cv2.resize(arr,(W,H),interpolation=cv2.INTER_LANCZOS4)
   p.stdin.write(arr.tobytes())
   if idx%48==0:print("STAGED",kind,idx,"/",TOTAL,flush=True)
  p.stdin.close();err=p.stderr.read().decode(errors="replace")
  code=p.wait()
  if code:raise RuntimeError("ENCODE_ERROR "+err[-1000:])
 except BaseException:
  p.kill();raise
 verify(out,TOTAL)
 return out

def master(files):
 concat=FINAL/"concat_20m_8sec.txt"
 concat.write_text("\n".join("file '"+f.as_posix().replace("'","")+"'" for f in files),encoding="utf-8")
 dest=FINAL/"SLINGSHOT_THREE_MATERIALS_20M_24SEC_MASTER_V4.mp4"
 subprocess.run([FF,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(dest)],check=True)
 verify(dest,TOTAL*3)
 return dest
if __name__=="__main__":
 import sys
 jobs=sys.argv[1:] or ["egg","steel","billiard"]
 videos=[encode(k) for k in jobs]
 if len(jobs)==3:master(videos)
