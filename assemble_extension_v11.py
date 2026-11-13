from pathlib import Path
import numpy as np,cv2,wave,subprocess,sys,re
import imageio_ffmpeg
from PIL import Image,ImageDraw
R=Path.home()/"Downloads"/"slingshot_quality_proof"
BASE=R/"cinematic_50m_v11_extension"
OLD=R/"cinematic_50m_v8"/"final"
FF=imageio_ffmpeg.get_ffmpeg_exe()
FPS,SR,W,H=24,48000,720,1280
NAMES={"steel":"01_STEEL_50M_V11.mp4","billiard":"02_8BALL_50M_V11.mp4",
       "watermelon":"03_WATERMELON_50M_V11.mp4","cannon":"04_CANNON_50M_V11.mp4"}
def audio(kind):
 src=OLD/f"{kind if kind in ('steel','billiard') else ('steel' if kind=='cannon' else 'egg')}_50m_sound.wav"
 with wave.open(str(src),'rb') as f:
  assert (f.getnchannels(),f.getframerate(),f.getsampwidth())==(2,SR,2)
  a=np.frombuffer(f.readframes(f.getnframes()),dtype="<i2").reshape(-1,2).astype(np.float64)/32768
 assert len(a)==8*SR,len(a)
 rng=np.random.default_rng(237+len(kind))
 def add(t,dur,amp,hz,decay,noise=.45):
  start=int(t*SR);n=int(dur*SR);dt=np.arange(n)/SR
  sig=amp*np.exp(-decay*dt)*((1-noise)*np.sin(2*np.pi*hz*dt)+noise*rng.standard_normal(n))
  finish=min(len(a),start+n)
  a[start:finish,0]+=sig[:finish-start]
  a[start:finish,1]+=sig[:finish-start]*.92
 if kind=="steel":
  add(4,.34,.68,110,13,.55)
  add(4.12,.52,.25,68,7,.56)
 elif kind=="billiard":
  add(4,.23,.34,310,29,.2)
  add(4.07,.18,.14,520,24,.16)
 elif kind=="watermelon":
  add(4,.45,.45,116,13,.48)
  add(4.10,.34,.26,80,12,.60)
 elif kind=="cannon":
  # Silence the slingshot rubber noise before the new cannon launch bass.
  a[int(1.93*SR):int(2.22*SR)]*=.12
  add(2,.85,.67,55,6,.56)
  add(2.06,.42,.30,104,7,.74)
  add(4,.49,.70,61,9,.60)
 a=np.clip(np.tanh(a*1.07),-.97,.97)
 dest=BASE/kind/"V11_SYNC_SOUND.wav"
 with wave.open(str(dest),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
  f.writeframes(np.round(a*32767).astype("<i2").tobytes())
 return dest
def blur_background(im,f,kind):
 if f<49 or f>91:return im
 yy,xx=np.ogrid[:H,:W]
 radius=.105 if kind in ("steel","billiard","cannon") else .15
 centre=((xx-W*.5)/(W*radius))**2+((yy-H*.5)/(H*radius*.80))**2
 keep=np.clip((1.15-centre)/.5,0,1)
 strength=np.clip((f-48.)/12,0,1)*np.clip((yy-H*.24)/(H*.57),0,1)*(1-keep)
 kernel=np.ones((25,1),np.float32)/25.
 streak=cv2.filter2D(im,-1,kernel,borderType=cv2.BORDER_REFLECT101)
 return np.clip(im.astype(np.float32)*(1-strength[:,:,None]*.67)+streak.astype(np.float32)*(strength[:,:,None]*.67),0,255).astype('uint8')
def render_video(kind):
 d=BASE/kind
 frames=[d/"frames"/f"frame_{f:04d}.png" for f in range(1,193)]
 missing=[str(f) for f in frames if not f.is_file() or f.stat().st_size<12000]
 if missing:raise RuntimeError(f"{kind}: MISSING {len(missing)} first:{missing[:4]}")
 audiofile=audio(kind)
 video=d/NAMES[kind]
 proc=subprocess.Popen([FF,"-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
  "-i",str(audiofile),"-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-crf","18","-preset","fast","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-frames:v","192","-movflags","+faststart",str(video)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i,f in enumerate(frames,1):
   img=cv2.imread(str(f),cv2.IMREAD_COLOR)
   if img is None:raise RuntimeError("BAD_FRAME "+str(f))
   if img.shape[:2]!=(H,W):img=cv2.resize(img,(W,H),interpolation=cv2.INTER_LANCZOS4)
   img=blur_background(img,i,kind)
   proc.stdin.write(img.tobytes())
   if i%48==0:print("ASSEMBLE",kind,i,"/192",flush=True)
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  if proc.wait():raise RuntimeError(err[-1200:])
 except Exception:
  proc.kill();raise
 verify(video)
 storyboard(video,kind)
 print("V11_VIDEO_DONE",kind,video,flush=True)
def verify(path):
 cap=cv2.VideoCapture(str(path))
 num=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 wh=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
 assert (num,wh)==(192,(W,H)) and abs(fps-24)<.03,(num,wh,fps,path)
 r=subprocess.run([FF,"-v","error","-xerror","-i",str(path),"-f","null","NUL"],capture_output=True,text=True)
 assert r.returncode==0,r.stderr[-800:]
 r=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
 assert "Audio: aac" in r.stderr
 print("VIDEO_PASS",path.name,flush=True)
def storyboard(path,kind):
 video=cv2.VideoCapture(str(path))
 stamps=(.30,1.80,2.05,2.50,3.10,3.70,3.92,4.02,4.22,4.70,6.5,7.6)
 sheet=Image.new("RGB",(6*180,2*350),(13,15,22))
 text=ImageDraw.Draw(sheet)
 for i,t in enumerate(stamps):
  video.set(cv2.CAP_PROP_POS_FRAMES,int(t*FPS))
  ok,frame=video.read()
  assert ok
  tile=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(180,320)),cv2.COLOR_BGR2RGB))
  x=i%6*180;y=i//6*350
  sheet.paste(tile,(x,y+25))
  text.text((x+7,y+5),f"{t:.2f}s",fill="white")
 video.release()
 sheet.save(BASE/kind/f"{kind.upper()}_STORYBOARD.jpg",quality=90)
def make_viewer():
 videos=[(kind,label,NAMES[kind]) for kind,label in
         [("steel","쇠구슬 · 관통"),("billiard","8번 당구공 · 반발"),
          ("watermelon","수박 · 파열"),("cannon","대포 · 포탄")]]
 items=[]
 for k,label,file in videos:
  exists=(BASE/k/file).is_file()
  src=f"{k}/{file}" if exists else ""
  items.append(f'<article><h2>{label}</h2>'+
               (f'<video controls playsinline preload="metadata" loop src="{src}"></video>' if exists
                else f'<div class="previewpair"><img src="{k}/PREVIEW_048.png" alt="발사 모습"><img src="{k}/PREVIEW_101.png" alt="충돌 모습"></div><p class="pending">3D 장면 완성 · 전체 영상 렌더링 중</p>')+'</article>')
 html='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>새총 50m V11 — 재질 및 대포 4종 검토</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{background:#0c121b;color:#f1f4fb;font-family:system-ui,"Malgun Gothic",sans-serif;margin:0;padding:22px}
main{max-width:1220px;margin:auto}h1{font-size:1.6rem}p{color:#b9c8d9;line-height:1.5}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
article{background:#192230;border-radius:12px;border:1px solid #354355;padding:14px}
h2{font-size:1rem;margin:0 0 10px}video{width:100%;height:auto;max-height:640px;object-fit:contain;background:black;border-radius:5px}
.pending{padding:12px;color:#ddd}.previewpair{display:flex;gap:6px}.previewpair img{width:calc(50% - 3px);max-height:430px;object-fit:contain}
@media(max-width:650px){body{padding:8px}.grid{gap:5px}article{padding:6px}h2{font-size:.85rem}}
</style></head><body><main>
<h1>새총 50m V11 — 쇠구슬·당구공·수박·대포</h1>
<p>계란 V10의 공통 문법: 발사 → 투사체 고정 추적 → 벽 5.5m 전 카메라 정지 → 같은 3D 장면에서 충돌. 초점은 물체별 재질과 충돌 차이입니다.</p>
<div class="grid">'''+"\n".join(items)+'''</div>
<p>별도 프로토타입입니다. 수박 파열과 벽돌 파손은 키프레임 연출이며, 정밀한 유체·강체 시뮬레이션으로 오인하지 마세요. 카메라 컷이나 벽 배경 교체 없이 제작했습니다.</p>
<p><a href="../cinematic_50m_v10_egg/EGG_50M_8SEC_V10_UNCUT.mp4">계란 V10 기준 영상</a></p></main></body></html>'''
 out=BASE/"VIEW_ALL_50M_V11.html"
 out.write_text(html,encoding="utf8")
 print("VIEWER",out,flush=True)
 return out
if __name__=="__main__":
 tasks=sys.argv[1:]
 if not tasks or tasks==["viewer"]:
  make_viewer()
 else:
  for k in tasks:
   assert k in NAMES,k
   render_video(k)
  make_viewer()
