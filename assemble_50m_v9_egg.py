from pathlib import Path
import subprocess,wave,math
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw
R=Path.home()/"Downloads"/"slingshot_quality_proof"
O=R/"cinematic_50m_v9_egg"
OLD=R/"cinematic_50m_v8"/"final"
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,SR=720,1280,24,48000
SOURCE=[O/"launch_frames"/f"frame_{n:04d}.png" for n in range(1,97)]
SOURCE += [O/"impact_frames"/f"frame_{n:04d}.png" for n in range(13,109)]
assert len(SOURCE)==192
def sound():
 src=OLD/"egg_50m_sound.wav"
 with wave.open(str(src),"rb") as f:
  assert f.getnchannels()==2 and f.getframerate()==SR
  a=np.frombuffer(f.readframes(f.getnframes()),dtype="<i2").astype(np.float64).reshape(-1,2)/32768.
 assert len(a)>=SR*8
 rng=np.random.default_rng(931)
 def add(t,dur,amp,hz,decay,noise=.48):
  ix=int(t*SR);n=int(dur*SR);tt=np.arange(n)/SR
  v=amp*np.exp(-tt*decay)*(np.sin(2*np.pi*hz*tt)*(.8-noise)+noise*rng.standard_normal(n))
  end=min(len(a),ix+n)
  a[ix:end,0]+=v[:end-ix]*.89
  a[ix:end,1]+=v[:end-ix]*1.08
 # Rubber recoil has its own distinct high-tension twang, not added debris.
 add(1.988,.15,.33,245,32,.40)
 add(2.023,.21,.25,126,20,.36)
 # Audible high-velocity passage while camera and ground run past each other.
 for t,volume in [(2.55,.055),(2.85,.080),(3.18,.105),(3.53,.110),(3.81,.075)]:
  add(t,.16,volume,540,16,.82)
 # Egg first-contact sound: sharp brittle crack and heavy wet body, timed at t=4.
 add(4.001,.19,.60,310,38,.79)
 add(4.025,.47,.37,106,14,.58)
 add(4.09,.58,.20,84,11,.66)
 a=np.clip(np.tanh(a*1.12),-.96,.96)
 dest=O/"EGG_V9_RELAUNCH_SOUND.wav"
 with wave.open(str(dest),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
  f.writeframes(np.round(a*32767).astype("<i2").tobytes())
 return dest
def encode():
 absent=[str(p) for p in SOURCE if not p.is_file() or p.stat().st_size<14000]
 if absent:raise FileNotFoundError("MISSING "+str(len(absent))+" "+repr(absent[:5]))
 a=sound()
 out=O/"EGG_50M_8SEC_V9_PREVIEW.mp4"
 args=[FF,"-y","-hide_banner","-loglevel","error",
 "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
 "-i",str(a),"-map","0:v:0","-map","1:a:0",
 "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
 "-c:a","aac","-b:a","192k","-ar",str(SR),"-frames:v","192",
 "-movflags","+faststart",str(out)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i,f in enumerate(SOURCE,1):
   im=cv2.imread(str(f),cv2.IMREAD_COLOR)
   if im is None:raise RuntimeError("UNREADABLE "+str(f))
   if im.shape[:2]!=(H,W):im=cv2.resize(im,(W,H),interpolation=cv2.INTER_LANCZOS4)
   proc.stdin.write(im.tobytes())
   if i%48==0:print("ENCODE",i,"of 192",flush=True)
  proc.stdin.close()
  errors=proc.stderr.read().decode(errors="replace")
  if proc.wait()!=0:raise RuntimeError(errors[-2000:])
 except BaseException:
  proc.kill();raise
 return out
def check(path):
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 fps=cap.get(cv2.CAP_PROP_FPS)
 dims=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 if (n,dims)!=(192,(W,H)) or abs(fps-24)>.05:raise RuntimeError("BAD_FRAMES_FPS "+str((n,dims,fps)))
 marks=[.25,1.1,1.9,2.02,2.2,2.55,2.85,3.2,3.55,3.9,4.05,4.2,5.1,7.4]
 page=Image.new("RGB",(7*185,2*355),(15,17,23))
 d=ImageDraw.Draw(page)
 for i,t in enumerate(marks):
  cap.set(cv2.CAP_PROP_POS_FRAMES,int(t*FPS))
  ok,frame=cap.read()
  if not ok or np.mean(frame)<8:raise RuntimeError("FRAME_INVALID "+str(t))
  tile=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(185,330)),cv2.COLOR_BGR2RGB))
  x=(i%7)*185;y=(i//7)*355
  page.paste(tile,(x,y+25))
  d.text((x+6,y+4),f"{t:.2f}s",fill="white")
 cap.release()
 page.save(O/"V9_EGG_QUALITY_CONTACT.jpg",quality=93)
 p=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
 assert "Audio: aac" in p.stderr
 d=subprocess.run([FF,"-v","error","-xerror","-i",str(path),"-f","null","NUL"],capture_output=True,text=True)
 if d.returncode:raise RuntimeError("DECODE_FAIL "+d.stderr[-1200:])
 print("V9_VIDEO_PASS",n,dims,fps,flush=True)
def html():
 code="""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>50m 계란 비행 V8 / V9 비교</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{background:#0d1119;color:#f0f3fa;font-family:system-ui,"Malgun Gothic",sans-serif;padding:22px;margin:0}
main{max-width:1300px;margin:auto}h1{font-size:1.55rem;margin-bottom:8px}p{color:#b8c2d3}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
article{background:#19212e;border:1px solid #394557;border-radius:12px;padding:14px}
video{width:100%;height:auto;max-height:700px;background:#000;border-radius:7px;display:block;object-fit:contain}
button{cursor:pointer;background:#263b57;border:1px solid #526b8b;color:white;padding:10px 13px;border-radius:6px;margin:4px}
@media(max-width:700px){.grid{gap:6px}article{padding:6px}body{padding:9px}h2{font-size:.85rem}}
</style></head><body><main>
<h1>새총 50m 계란 — V8 / V9 시안 비교</h1>
<p>관찰 기준: ① 발사 장력과 폭발감 ② 투사체가 떠 있는 느낌 감소 ③ 벽 충돌의 힘 ④ 바닥·벽돌·투사체 질감. <strong>충돌 후 확대는 없습니다.</strong></p>
<div><button onclick="sync('play')">동시 재생</button><button onclick="sync('pause')">일시정지</button><button onclick="seek(2)">2초부터 비교</button><button onclick="seek(4)">4초 충돌부터</button><button onclick="seek(0)">처음부터</button></div>
<div class="grid">
<article><h2>V8 — 변경 전</h2><video id="a" controls playsinline loop preload="metadata" src="../cinematic_50m_v8/final/01_EGG_50M_8SEC_V8.mp4"></video></article>
<article><h2>V9 — 개선 시안</h2><video id="b" controls playsinline loop preload="metadata" src="EGG_50M_8SEC_V9_PREVIEW.mp4"></video></article>
</div>
<p>V9는 현재 <strong>계란 1종 검증 시안</strong>입니다. 50.56m 거리 유지, 빠른 밴드 복원, 개선된 비행 카메라 및 재질, 넓은 충돌 구도를 비교하세요. 실제 유체 시뮬레이션은 아직 적용되지 않았습니다.</p>
</main><script>
const a=document.getElementById('a'),b=document.getElementById('b');
function sync(mode){if(mode==='pause'){a.pause();b.pause()}else{b.currentTime=a.currentTime;a.play().catch(()=>{});b.play().catch(()=>{})}}
function seek(t){a.pause();b.pause();a.currentTime=t;b.currentTime=t;setTimeout(()=>{a.play().catch(()=>{});b.play().catch(()=>{})},140)}
</script></body></html>"""
 path=O/"VIEW_EGG_V8_VS_V9.html"
 path.write_text(code,encoding="utf-8")
 return path
if __name__=="__main__":
 path=encode();check(path);page=html()
 (O/"V9_EGG_CHECK.txt").write_text(
 "Actual 50.56m launch path; revised elastic release and dynamic tracking.\n"
 "8.00s, 192 frames, 720x1280, 24fps H264 AAC verified.\n"
 "First 96 launch frames and 96 physical impact frames newly rendered.\n"
 "Static post-impact camera, no zoom.\n"
 "Status: REVIEW PREVIEW, visual approval not yet established; original V8 preserved.\n"
 "Compare: "+str(page)+"\n",encoding="utf8")
 print("V9_EGG_REVIEW_READY",path,page,flush=True)
