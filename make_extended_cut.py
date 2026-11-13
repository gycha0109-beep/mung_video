from pathlib import Path
from functools import lru_cache
import subprocess, wave, json, math, sys
import numpy as np
import cv2
from PIL import Image,ImageDraw
import imageio_ffmpeg

ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"extended_v1"
OUT.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
FPS=24
W,H=720,1280
N=180
SR=48000
LABEL={"egg":"01_EGG_EXTENDED_V1","steel":"02_STEEL_EXTENDED_V1","billiard":"03_BILLIARD_EXTENDED_V1"}
RNG=np.random.default_rng(20261111)
# Source-time maps, deliberately matching source flight frame 82 with impact frame 1.
CUTS=[
 (0,39,"launch",1,48),
 (40,54,"launch",48,62),
 (55,70,"launch",62,82),
 (71,84,"impact",1,14),
 (85,116,"impact",14,24),
 (117,166,"impact",24,48),
 (167,179,"impact",48,48)
]
FLOW=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)
BASE_X,BASE_Y=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
flow_cache=None

def sound_mix(kind):
 audio=np.zeros(N*SR//FPS,dtype=np.float64)
 def insert(start,x,amp=1):
  p=max(0,int(start*SR))
  n=min(len(audio)-p,len(x))
  if n>0:audio[p:p+n]+=x[:n]*amp
 def burst(t,dur,amp,sharp=25,freq=100):
  n=int(SR*dur);tv=np.arange(n)/SR
  noise=RNG.standard_normal(n)
  carrier=np.sin(2*np.pi*(freq*tv+60*tv*tv))
  v=(.65*noise+.35*carrier)*np.exp(-sharp*tv)
  insert(t,v,amp)
 t=np.arange(len(audio))/SR
 audio[:]=.006*RNG.standard_normal(len(audio))
 # Rubber band rises to a dry high-tension snap.
 for start in (.48,.91,1.34):
  burst(start,.16,.026,18,94)
 burst(1.68,.23,.28,25,190)
 burst(1.75,.16,.18,35,475)
 # Flyby whoosh that accelerates towards the target.
 start=1.81;end=3.54
 n=int((end-start)*SR)
 tv=np.linspace(0,1,n,endpoint=False)
 noise=RNG.standard_normal(n)
 roll=np.convolve(noise,np.ones(75)/75,mode="same")
 whoosh=(.22*noise+2.5*roll)*np.sin(np.pi*tv)**.8*(.18+.45*tv)
 insert(start,whoosh,.15)
 hit=84/FPS
 if kind=="egg":
  burst(hit,.55,.46,13,165)
  burst(hit+.05,.65,.18,9,64)
  for dt in (.19,.32,.52,.8):burst(hit+dt,.19,.055,24,260)
 elif kind=="steel":
  burst(hit,.85,.48,9,101)
  burst(hit+.045,.22,.28,21,620)
  for dt,vol in ((.13,.19),(.26,.15),(.41,.11),(.66,.06),(1.04,.035)):
   burst(hit+dt,.34,vol,13,160)
 else:
  burst(hit,.38,.39,24,385)
  for dt,vol in ((.33,.18),(.55,.095),(.86,.055),(1.2,.025)):
   burst(hit+dt,.22,vol,26,440)
 audio=np.tanh(audio*1.5)*.8
 pcm=(audio*32767).astype("<i2")
 wav=OUT/(kind+"_sound.wav")
 with wave.open(str(wav),"wb") as a:
  a.setnchannels(2);a.setsampwidth(2);a.setframerate(SR)
  a.writeframes(np.column_stack((pcm,pcm)).tobytes())
 return wav

def image_folder(kind,section):
 if section=="launch":
  return ROOT/"frames_pouch_v3" if kind=="steel" else ROOT/"three_shots"/kind/"launch"
 return ROOT/"physics_proof_v1"/"frames" if kind=="steel" else ROOT/"three_shots"/kind/"impact"/"frames"

@lru_cache(maxsize=9)
def img(kind,section,f):
 path=image_folder(kind,section)/("frame_%04d.png"%f)
 a=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if a is None:raise FileNotFoundError(str(path))
 if a.shape[:2]!=(H,W):a=cv2.resize(a,(W,H),interpolation=cv2.INTER_AREA)
 return a

def interpolated(kind,section,f):
 global flow_cache
 a=int(math.floor(f+.00001))
 b=min(a+1,82 if section=="launch" else 48)
 u=max(0.0,min(1.0,f-a))
 a_img=img(kind,section,a)
 if b==a or u<.035:return a_img.copy()
 b_img=img(kind,section,b)
 if u>.965:return b_img.copy()
 # Do not morph the original physical scene's camera cut at impact frame 15.
 if section=="impact" and a==14:return a_img.copy() if u<.5 else b_img.copy()
 # Optical interpolation is reserved for slow-motion; not for ballistic launch frames.
 if section=="launch":
  return a_img.copy() if u<.5 else b_img.copy()
 key=(kind,section,a,b)
 if flow_cache is None or flow_cache[0]!=key:
  aa=cv2.resize(a_img,(W//2,H//2),interpolation=cv2.INTER_AREA)
  bb=cv2.resize(b_img,(W//2,H//2),interpolation=cv2.INTER_AREA)
  gg=cv2.cvtColor(aa,cv2.COLOR_BGR2GRAY)
  hh=cv2.cvtColor(bb,cv2.COLOR_BGR2GRAY)
  fa=FLOW.calc(gg,hh,None)
  fb=FLOW.calc(hh,gg,None)
  fa=cv2.resize(fa,(W,H),interpolation=cv2.INTER_LINEAR)*2
  fb=cv2.resize(fb,(W,H),interpolation=cv2.INTER_LINEAR)*2
  flow_cache=(key,fa,fb)
 else:
  fa,fb=flow_cache[1],flow_cache[2]
 wa=cv2.remap(a_img,BASE_X-u*fa[:,:,0],BASE_Y-u*fa[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
 wb=cv2.remap(b_img,BASE_X-(1-u)*fb[:,:,0],BASE_Y-(1-u)*fb[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
 return cv2.addWeighted(wa,1-u,wb,u,0)

def timeline(i):
 for first,last,section,src1,src2 in CUTS:
  if first<=i<=last:
   t=(i-first)/max(1,last-first)
   # Decelerate near the moment of maximum material deformation.
   if section=="impact" and first==85:t=t*t*(3-2*t)
   return section,src1+(src2-src1)*t
 raise RuntimeError(i)

def crop_and_shake(frame,i):
 # Small motivated punch-in; preserve original camera cuts and physical layers.
 if i<39:z=1.01+.027*i/39
 elif i<71:z=1.03+(i-39)*.0003
 elif i<85:z=1.038+(i-71)*.0012
 elif i<104:z=1.09+(i-85)*.002
 else:z=1.13-.08*min(1,(i-104)/75)
 z=max(1.0,z)
 sx=round(W/z);sy=round(H/z)
 cx=W//2;cy=H//2
 shake={84:(0,3),85:(-6,-4),86:(5,3),87:(-4,-2),88:(3,2),89:(-2,1)}.get(i,(0,0))
 cx+=shake[0];cy+=shake[1]
 x0=max(0,min(W-sx,cx-sx//2));y0=max(0,min(H-sy,cy-sy//2))
 cut=frame[y0:y0+sy,x0:x0+sx]
 return cv2.resize(cut,(W,H),interpolation=cv2.INTER_LINEAR)

def verify(path):
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 fps=cap.get(cv2.CAP_PROP_FPS)
 dims=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 pics=[]
 qa=[]
 for s in (.12,1.5,2.06,2.88,3.55,4.15,5.7,7.12):
  frame_id=min(n-1,round(s*FPS))
  cap.set(cv2.CAP_PROP_POS_FRAMES,frame_id)
  ok,frame=cap.read()
  if not ok:raise RuntimeError("DECODE_FAIL "+str((path,s)))
  qa.append((s,float(frame.mean()),float(frame.std())))
  thumbs=cv2.resize(frame,(180,320),interpolation=cv2.INTER_AREA)
  pics.append(cv2.cvtColor(thumbs,cv2.COLOR_BGR2RGB))
 cap.release()
 result=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
 if n!=N or abs(fps-FPS)>.05 or dims!=(W,H) or "Audio: aac" not in result.stderr or any(mean<5 for _,mean,_ in qa):
  raise RuntimeError("QA_FAIL "+repr((n,fps,dims,result.stderr[-600:],qa)))
 canvas=Image.new("RGB",(180*4,350*2),(16,17,18))
 d=ImageDraw.Draw(canvas)
 for k,arr in enumerate(pics):
  x=(k%4)*180;y=(k//4)*350
  canvas.paste(Image.fromarray(arr),(x,y+22))
  d.text((x+7,y+4),f"{qa[k][0]:.2f} sec",fill="white")
 poster=OUT/(path.stem+"_PROOF.jpg")
 canvas.save(poster,quality=88)
 print("PASS",path.name,n,"frames",fps,"fps",dims,"AAC",len(qa),"keyframes",flush=True)
 return poster

def make(kind):
 global flow_cache
 flow_cache=None
 for section,maxf in (("launch",82),("impact",48)):
  for f in range(1,maxf+1):
   p=image_folder(kind,section)/("frame_%04d.png"%f)
   if not p.is_file():raise FileNotFoundError(p)
 wav=sound_mix(kind)
 path=OUT/(LABEL[kind]+".mp4")
 cmd=[FF,"-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
  "-i",str(wav),"-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-ar",str(SR),"-t",str(N/FPS),
  "-movflags","+faststart",str(path)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(N):
   section,fr=timeline(i)
   frame=interpolated(kind,section,fr)
   frame=crop_and_shake(frame,i)
   if i in (40,41,42,55,56,57):
    frame=cv2.addWeighted(frame,.90,cv2.GaussianBlur(frame,(7,7),1.8),.10,0)
   proc.stdin.write(frame.tobytes())
   if i%30==0:print("FRAME_PROGRESS",kind,i,"/",N,flush=True)
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  code=proc.wait()
  if code!=0:raise RuntimeError("FFMPEG "+str(code)+" "+err[-1400:])
 except BaseException:
  proc.kill()
  raise
 verify(path)
 print("OUTPUT",kind,path,path.stat().st_size,flush=True)
 return path

def master(videos):
 path=OUT/"SLINGSHOT_THREE_MATERIALS_EXTENDED_V1_MASTER.mp4"
 conc=OUT/"concat_extended.txt"
 conc.write_text("\n".join("file '"+p.as_posix().replace("'","") +"'" for p in videos),encoding="utf8")
 subprocess.run([FF,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0",
                 "-i",str(conc),"-c","copy","-movflags","+faststart",str(path)],check=True)
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 cap.release()
 if n!=3*N:raise RuntimeError("MASTER_FRAME_COUNT_MISMATCH "+str(n))
 print("MASTER_PASS",path,n,"frames",n/FPS,"sec",path.stat().st_size,flush=True)
 return path

if __name__=="__main__":
 requested=sys.argv[1:] or ["egg","steel","billiard"]
 vids=[make(k) for k in requested]
 if len(requested)==3: master(vids)
