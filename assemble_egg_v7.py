from pathlib import Path
import subprocess,math,wave,sys,json
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"cinematic_v7_egg"
V5=ROOT/"cinematic_20m_v4"
V6=ROOT/"cinematic_v6_egg"
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,SR=720,1280,24,48000
SRC=[V5/"egg"/"launch"/f"frame_{n:04d}.png" for n in range(1,97)]
SRC += [ROOT/"three_shots"/"egg"/"impact"/"frames"/f"frame_{n:04d}.png" for n in range(13,49)]
SRC += [OUT/"after_frames"/f"frame_{n:04d}.png" for n in range(49,109)]
assert len(SRC)==192
def audio():
 source=V5/"final"/"egg_8sec_sound.wav"
 with wave.open(str(source),"rb") as w:
  assert (w.getnchannels(),w.getframerate())==(2,SR)
  raw=w.readframes(w.getnframes())
 a=np.frombuffer(raw,dtype="<i2").astype(np.float64).reshape(-1,2)/32768
 rng=np.random.default_rng(7722)
 # Glassy shell impact and two descending viscous liquid contacts.
 for sec,amplitude,freq,duration in [
  (6.330,.049,187,.22),(6.543,.060,127,.24),
  (6.920,.021,181,.17),(7.039,.035,143,.20)]:
  at=int(sec*SR); n=int(duration*SR); xx=np.arange(n)/SR
  body=np.sin(2*math.pi*freq*xx)*np.exp(-21*xx)*amplitude
  body+=rng.normal(0,1,n)*np.exp(-39*xx)*amplitude*.30
  right=min(len(a),at+n)
  if right>at:
   a[at:right,0]+=body[:right-at]*.93
   a[at:right,1]+=body[:right-at]*1.05
 a=np.clip(np.tanh(a),-.965,.965)
 sound=OUT/"EGG_V7_CHAIN_SYNC.wav"
 with wave.open(str(sound),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((a*32767).astype("<i2").tobytes())
 return sound
def decoded_frame(path):
 frame=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if frame is None:raise RuntimeError("UNREADABLE "+str(path))
 if frame.shape[:2]!=(H,W):
  frame=cv2.resize(frame,(W,H),interpolation=cv2.INTER_LANCZOS4)
 return frame
def movie():
 missing=[str(p) for p in SRC if not p.is_file() or p.stat().st_size<13000]
 if missing:raise FileNotFoundError(f"Missing {len(missing)} inputs first: {missing[:4]}")
 out=OUT/"EGG_20M_8SEC_V7.mp4"
 aud=audio()
 p=subprocess.Popen([FF,"-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
  "-i",str(aud),"-map","0:v:0","-map","1:a:0",
  "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-ar",str(SR),
  "-frames:v","192","-movflags","+faststart",str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  previous=decoded_frame(SRC[131])
  for i,f in enumerate(SRC,1):
   frame=decoded_frame(f)
   if 133<=i<=137:
    alpha=(i-132)/5
    frame=cv2.addWeighted(previous,1-alpha,frame,alpha,0)
   p.stdin.write(frame.tobytes())
   if i%32==0:print("ENCODE",i,flush=True)
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  if p.wait()!=0:raise RuntimeError(err[-2500:])
 except BaseException:
  p.kill();raise
 return out
def split_tail():
 old=V6/"EGG_20M_8SEC_V6.mp4"
 new=OUT/"EGG_20M_8SEC_V7.mp4"
 path=OUT/"V6_V7_AFTERMATH_SPLIT.mp4"
 a=cv2.VideoCapture(str(old));b=cv2.VideoCapture(str(new))
 for c in [a,b]:c.set(cv2.CAP_PROP_POS_FRAMES,132)
 p=subprocess.Popen([FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s","728x680","-r","24","-i","pipe:0",
  "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p","-frames:v","60","-movflags","+faststart",str(path)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(60):
   ok1,left=a.read();ok2,right=b.read()
   if not(ok1 and ok2):raise RuntimeError("MISSING_COMPARE_FRAME "+str(i))
   frame=np.full((680,728,3),(17,18,24),dtype=np.uint8)
   frame[40:,0:360]=cv2.resize(left,(360,640),interpolation=cv2.INTER_AREA)
   frame[40:,368:]=cv2.resize(right,(360,640),interpolation=cv2.INTER_AREA)
   cv2.putText(frame,"V6 / BEFORE",(22,27),cv2.FONT_HERSHEY_SIMPLEX,.60,(245,245,245),1,cv2.LINE_AA)
   cv2.putText(frame,"V7 / AFTER",(385,27),cv2.FONT_HERSHEY_SIMPLEX,.60,(245,245,245),1,cv2.LINE_AA)
   p.stdin.write(frame.tobytes())
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  if p.wait()!=0:raise RuntimeError(err[-2000:])
 finally:
  a.release();b.release()
 return path
def poster(out):
 cap=cv2.VideoCapture(str(out))
 marks=[.5,1.75,2.8,3.9,4.3,5.5,5.9,6.33,6.54,6.92,7.12,7.65]
 page=Image.new("RGB",(6*200,2*395),(13,14,19))
 d=ImageDraw.Draw(page)
 for i,t in enumerate(marks):
  cap.set(cv2.CAP_PROP_POS_FRAMES,int(t*24))
  ok,img=cap.read()
  if not ok:raise RuntimeError("CANNOT_GET_POSTER_FRAME")
  img=cv2.cvtColor(cv2.resize(img,(200,355)),cv2.COLOR_BGR2RGB)
  x=i%6*200;y=i//6*395
  page.paste(Image.fromarray(img),(x,y+32))
  d.text((x+7,y+8),f"{t:.2f}s",fill="white")
 cap.release()
 output=OUT/"EGG_V7_CONTACT.jpg"
 page.save(output,quality=92)
 return output
def make_html():
 html=r"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>계란 V7 — 연쇄 반응 비교</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{background:#0c0e13;color:#f0f2f4;font-family:system-ui,"Malgun Gothic",sans-serif;margin:0;padding:24px}
main{max-width:1320px;margin:auto}h1{font-size:1.55rem;margin:0 0 8px}p{color:#b8bec9;line-height:1.55}.tag{font-size:12px;color:#a0a9bb;border:1px solid #424654;border-radius:6px;padding:5px 8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{padding:14px;background:#171c26;border:1px solid #30394a;border-radius:12px}
.panel h2{font-size:1rem;margin:0 0 10px}video{width:100%;max-height:650px;background:#000;object-fit:contain;border-radius:7px}
.toolbar{display:flex;flex-wrap:wrap;gap:9px;margin:15px 0}
button{background:#28384e;border:1px solid #4e6786;border-radius:8px;color:white;padding:10px 15px;cursor:pointer}button:hover{background:#395773}
footer{margin-top:24px}.split{max-width:960px;margin:auto}.split video{max-height:unset}
small{color:#c6cfdd}.accent{color:#c4ddff}
@media(max-width:700px){body{padding:10px}.grid{gap:7px}.panel{padding:6px}.panel h2{font-size:.85rem}video{max-height:540px}.toolbar button{flex:1 1 35%}}
</style></head>
<body><main>
<h1>계란 충돌 영상 — V6 / V7 비교</h1>
<p>두 버전 모두 8초·24fps·720×1280. <span class="accent">0~5.5초는 동일한 원본</span>이며, 달라지는 구간은 5.5~8초입니다. 정지 화면이 아닌 <strong>실제 움직임</strong>을 비교해 주세요.</p>
<div class="toolbar">
<button onclick="both('play')">두 영상 동시에 재생</button>
<button onclick="both('pause')">일시정지</button>
<button onclick="seek(5.5)">5.5초부터 비교</button>
<button onclick="seek(0)">처음부터 보기</button>
</div>
<div class="grid">
<div class="panel"><h2>V6 — 벽면 흐름 / 확대 중심</h2>
<video id="before" controls playsinline preload="metadata" loop src="../cinematic_v6_egg/EGG_20M_8SEC_V6.mp4"></video></div>
<div class="panel"><h2>V7 — 껍질 낙하 → 바닥 충돌 → 액체 재낙하</h2>
<video id="after" controls playsinline preload="metadata" loop src="EGG_20M_8SEC_V7.mp4"></video></div>
</div>
<footer><h2>후반 2.5초만 한 화면에서 보기</h2>
<div class="split"><video controls playsinline loop preload="metadata" src="V6_V7_AFTERMATH_SPLIT.mp4"></video></div>
<p><small>영상 개선 범위: 충돌 후 떨어지는 껍질, 두 차례의 액체 낙하와 바닥 흔적, 물체를 따라가는 카메라, 충돌과 맞춘 소리. 액체는 실제 유체 시뮬레이션이 아니라 중력 운동을 적용한 키프레임 연출입니다. 원본 계란 자국의 형태와 벽돌 표면은 아직 개선 대상입니다.</small></p>
</footer></main>
<script>
const v=[document.getElementById('before'),document.getElementById('after')];
function both(action){if(action==='pause'){v.forEach(x=>x.pause())}else{v[1].currentTime=v[0].currentTime;v.forEach(x=>x.play().catch(()=>{}));}}
function seek(t){v.forEach(x=>{x.pause();x.currentTime=t;});setTimeout(()=>v.forEach(x=>x.play().catch(()=>{})),140);}
</script></body></html>"""
 path=OUT/"VIEW_EGG_V6_VS_V7.html"
 path.write_text(html,encoding="utf-8")
 return path
def verify(out,split):
 cap=cv2.VideoCapture(str(out))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 fps=cap.get(cv2.CAP_PROP_FPS)
 w=round(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 cap.release()
 assert (n,w,h)==(192,720,1280) and abs(fps-24)<.03,(n,w,h,fps)
 d=subprocess.run([FF,"-v","error","-xerror","-i",str(out),"-f","null","NUL"],capture_output=True,text=True)
 assert d.returncode==0,d.stderr[-800:]
 p=subprocess.run([FF,"-hide_banner","-i",str(out)],capture_output=True,text=True)
 assert "Audio: aac" in p.stderr,p.stderr[-1000:]
 cp=cv2.VideoCapture(str(split))
 assert round(cp.get(cv2.CAP_PROP_FRAME_COUNT))==60
 cp.release()
 (OUT/"V7_QUALITY_CHECK.txt").write_text(
  "8 sec 192 frames 720x1280 24fps H.264+AAC: PASS\n"
  "Decoder and audio: PASS\n"
  "V6 vs V7 60-frame side-by-side tail: PASS\n"
  "0-5.5s from unchanged original launch and physical impact\n"
  "5.5-8s 60 new renders: chained shell fall, secondary contact, liquid gravity + timed puddle expansion.\n"
  "No slow motion. No simulated fluid solver claim; liquid is procedural keyframe animation.\n",encoding="utf-8")
if __name__=="__main__":
 out=movie()
 split=split_tail()
 p=poster(out)
 html=make_html()
 verify(out,split)
 print("V7_RELEASE_VERIFIED",out,split,p,html,flush=True)
