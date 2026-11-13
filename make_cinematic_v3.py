from pathlib import Path
from functools import lru_cache
import subprocess,sys,wave,math
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageOps
import imageio_ffmpeg

ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
V2=ROOT/"cinematic_v2"
FF=imageio_ffmpeg.get_ffmpeg_exe()
TITLE={"egg":"01_EGG_CINEMATIC_V3","steel":"02_STEEL_CINEMATIC_V3","billiard":"03_BILLIARD_CINEMATIC_V3"}
FPS=24;SR=48000;W=720;H=1280;TOTAL=168
RNG=np.random.default_rng(20261111)
FLOW=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)
GRID_X,GRID_Y=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
flow_cache=None

def folder(kind,segment):
 if segment=="launch":return V2/kind/"launch_frames"
 if segment=="impact":
  return ROOT/"physics_proof_v1"/"frames" if kind=="steel" else ROOT/"three_shots"/kind/"impact"/"frames"
 return V2/kind/"replay_frames"

@lru_cache(maxsize=8)
def still(kind,seg,index):
 path=folder(kind,seg)/("frame_%04d.png"%index)
 frame=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if frame is None:raise FileNotFoundError(path)
 if frame.shape[:2]!=(H,W):frame=cv2.resize(frame,(W,H),interpolation=cv2.INTER_AREA)
 return frame

def blend_slow_frame(kind,pos,seg='replay'):
 global flow_cache
 fa=int(math.floor(pos));fb=min(58 if seg=='replay' else 48,fa+1)
 w=pos-fa
 aa=still(kind,seg,fa)
 if fb==fa or w<.015:return aa
 bb=still(kind,seg,fb)
 if w>.985:return bb
 key=(kind,seg,fa,fb)
 if flow_cache is None or flow_cache[0]!=key:
  a=cv2.cvtColor(cv2.resize(aa,(W//2,H//2)),cv2.COLOR_BGR2GRAY)
  b=cv2.cvtColor(cv2.resize(bb,(W//2,H//2)),cv2.COLOR_BGR2GRAY)
  fw=FLOW.calc(a,b,None)
  bw=FLOW.calc(b,a,None)
  fw=cv2.resize(fw,(W,H),interpolation=cv2.INTER_LINEAR)*2
  bw=cv2.resize(bw,(W,H),interpolation=cv2.INTER_LINEAR)*2
  flow_cache=(key,fw,bw)
 else:
  fw,bw=flow_cache[1],flow_cache[2]
 m1=cv2.remap(aa,GRID_X-w*fw[:,:,0],GRID_Y-w*fw[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
 m2=cv2.remap(bb,GRID_X-(1-w)*bw[:,:,0],GRID_Y-(1-w)*bw[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
 return cv2.addWeighted(m1,1-w,m2,w,0)

def get_frame(kind,i):
 if i<41:return still(kind,"launch",i+1)
 if i<=54:return still(kind,"impact",i-40)
 if i<=110:
  fraction=(i-54)/56
  return blend_slow_frame(kind,14+19*fraction,"impact")
 fraction=(i-110)/57
 return blend_slow_frame(kind,33+15*fraction,"impact")

def add_noise(audio,t,dur,amp,decay,lowpass=0):
 start=int(t*SR)
 n=int(dur*SR)
 noise=RNG.standard_normal(n)
 if lowpass:
  # One pole RC low-pass for the thump / rubber resonance.
  a=np.exp(-2*np.pi*lowpass/SR)
  noise=cv2.filter2D(noise.astype(np.float32).reshape(1,-1),-1,np.ones((1,35),np.float32)/35)[0].astype(float)
  noise*=1.2
 x=noise*np.exp(-decay*np.arange(n)/SR)*amp
 end=min(len(audio),start+n)
 if 0<=start<end:audio[start:end]+=x[:end-start]

def soundtrack(kind):
 audio=np.zeros(int(TOTAL*SR/FPS),np.float64)
 # Drawing tension builds, hold, then one sudden release.
 for t,vol in ((.20,.024),(.48,.029),(.79,.035),(1.0,.045)):
  add_noise(audio,t,.18,vol,20,lowpass=130)
 add_noise(audio,1.305,.23,.19,24)
 add_noise(audio,1.34,.13,.18,50)
 # Projectile flyby: the high frequency band goes up with proximity.
 b=int(1.36*SR);n=int(.84*SR)
 t=np.linspace(0,1,n,endpoint=False)
 w=RNG.standard_normal(n)
 wavelet=(w[1:]-w[:-1])
 fly=np.zeros(n)
 fly[:n-1]=wavelet*np.sin(np.pi*t[:n-1])**1.2 *(.14+.56*t[:n-1])*.13
 audio[b:b+n]+=fly
 hit=(41+12)/FPS
 if kind=="steel":
  add_noise(audio,hit,.95,.65,8,lowpass=270)
  add_noise(audio,hit+.03,.38,.32,25)
  for dt,vol in ((.12,.16),(.23,.11),(.39,.08),(.63,.05)):
   add_noise(audio,hit+dt,.24,vol,18)
 elif kind=="egg":
  add_noise(audio,hit,.45,.36,14,lowpass=370)
  add_noise(audio,hit+.05,.72,.18,6,lowpass=580)
  for dt,vol in ((.12,.07),(.35,.06),(.56,.04)):
   add_noise(audio,hit+dt,.28,vol,20)
 else:
  add_noise(audio,hit,.34,.36,30,lowpass=850)
  for dt,vol in ((.29,.17),(.55,.1),(.96,.045)):
   add_noise(audio,hit+dt,.25,vol,30,lowpass=700)
 # A damped, quieter replay makes the edit's alternate view apparent.
 replay=89/FPS+(16-12)/(35-12)*(50/FPS)
 add_noise(audio,replay,.6,.11,9,lowpass=245)
 audio=np.tanh(audio*1.3)*.8
 pcm=(audio*32767).astype("<i2")
 dest=V2/(kind+"_v3_sound.wav")
 with wave.open(str(dest),"wb") as wf:
  wf.setnchannels(2);wf.setsampwidth(2);wf.setframerate(SR)
  wf.writeframes(np.column_stack((pcm,pcm)).tobytes())
 return dest

def verify(file,n=TOTAL):
 cap=cv2.VideoCapture(str(file))
 count=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 rate=cap.get(cv2.CAP_PROP_FPS)
 dims=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 if (count,dims)!=(n,(W,H)) or abs(rate-FPS)>.1:
  raise RuntimeError("FRAME_QA_FAILED "+str((file,count,dims,rate)))
 frame_samples=[]
 preview=Image.new("RGB",(4*180,2*345),(15,15,20))
 d=ImageDraw.Draw(preview)
 for j,f in enumerate((1,16,32,38,58,85,118,160)):
  cap.set(cv2.CAP_PROP_POS_FRAMES,f)
  ok,fr=cap.read()
  if not ok or fr.mean()<4:raise RuntimeError("DECODE_MISSING "+str(f))
  frame_samples.append((f,float(fr.mean())))
  tile=Image.fromarray(cv2.cvtColor(cv2.resize(fr,(180,320)),cv2.COLOR_BGR2RGB))
  x=j%4*180;y=j//4*345
  preview.paste(tile,(x,y+25))
  d.text((x+8,y+6),f"{f/FPS:.2f}s",fill="#fff")
 cap.release()
 info=subprocess.run([FF,"-hide_banner","-i",str(file)],capture_output=True,text=True)
 if "Audio: aac" not in info.stderr:raise RuntimeError("AUDIO_MISSING")
 # Verify every encoded frame decodes without errors.
 out=subprocess.run([FF,"-v","error","-xerror","-i",str(file),"-f","null","NUL"],capture_output=True,text=True)
 if out.returncode:raise RuntimeError("DECODING_ERROR "+out.stderr)
 poster=V2/(file.stem+"_PROOF.jpg")
 preview.save(poster,quality=91)
 print("PASS",file.name,n,round(n/FPS,3),"sec AAC H264",file.stat().st_size,flush=True)

def encode(kind):
 global flow_cache
 flow_cache=None
 for seg,start,end in (("launch",1,41),("impact",1,48)):
  for fr in range(start,end+1):
   p=folder(kind,seg)/("frame_%04d.png"%fr)
   if not p.exists():raise FileNotFoundError(p)
 wav=soundtrack(kind)
 out=V2/(TITLE[kind]+".mp4")
 args=[FF,"-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
  "-i",str(wav),"-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-preset","fast","-crf","16","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-ar",str(SR),"-t",str(TOTAL/FPS),
  "-movflags","+faststart",str(out)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(TOTAL):
   fr=get_frame(kind,i)
   proc.stdin.write(fr.tobytes())
   if i%30==0:print("ENCODE",kind,i,"/",TOTAL,flush=True)
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  code=proc.wait()
  if code:raise RuntimeError("FFMPEG_EXIT "+str(code)+" "+err[-1400:])
 except BaseException:
  proc.kill();raise
 verify(out)
 return out

if __name__=="__main__":
 requested=sys.argv[1:] or ["egg","steel","billiard"]
 output=[encode(kind) for kind in requested]
 if len(requested)==3:
  manifest=V2/"concat_v3.txt"
  manifest.write_text("\n".join("file '"+f.as_posix().replace("'","")+"'" for f in output),encoding="utf-8")
  master=V2/"SLINGSHOT_THREE_MATERIALS_CINEMATIC_V3_MASTER.mp4"
  subprocess.run([FF,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(manifest),"-c","copy","-movflags","+faststart",str(master)],check=True)
  verify(master,TOTAL*3)
  print("MASTER_VERIFIED",master,flush=True)
