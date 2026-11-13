from pathlib import Path
import subprocess,wave,math,sys
import numpy as np,cv2,imageio_ffmpeg
from PIL import Image,ImageDraw
R=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=R/"cinematic_50m_v8"
FINAL=OUT/"final";FINAL.mkdir(parents=True,exist_ok=True)
V5=R/"cinematic_20m_v4"
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,SR=720,1280,24,48000
N=192
NAME={"egg":"01_EGG_50M_8SEC_V8.mp4","steel":"02_STEEL_50M_8SEC_V8.mp4","billiard":"03_BILLIARD_50M_8SEC_V8.mp4"}
def sources(kind):
 fs=[OUT/kind/"launch"/f"frame_{i:04d}.png" for i in range(1,97)]
 early_impact=OUT if kind=='billiard' else V5
 fs += [early_impact/kind/"impact"/f"frame_{i:04d}.png" for i in range(13,49)]
 fs += [OUT/kind/"impact"/f"frame_{i:04d}.png" for i in range(49,109)]
 assert len(fs)==192
 miss=[p for p in fs if not p.is_file() or p.stat().st_size<14000]
 if miss:raise RuntimeError(f"{kind}: MISSING_RENDERED_FRAMES {len(miss)} first {miss[:5]}")
 return fs
def make_audio(kind):
 source=V5/"final"/f"{kind}_8sec_sound.wav"
 with wave.open(str(source),"rb") as w:
  assert w.getnchannels()==2 and w.getframerate()==SR
  arr=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").reshape(-1,2).astype(np.float64)/32768
 rng=np.random.default_rng(20268+len(kind))
 # Higher velocity is audible: wind pitch increases toward wall, with a pass-by near 3.6s.
 total=int(2*SR);tt=np.arange(total)/SR;absolute=tt+2
 white=rng.standard_normal(total)
 hp=white-np.convolve(white,np.ones(25)/25,mode="same")
 envelope=(.11+.19*(tt/2.)**1.2)*np.sin(np.pi*(tt+.04)/2.08)**.35
 envelope=np.clip(envelope,0,None)
 swoosh=(.10*white+.18*hp)*envelope
 # peak at camera pass, followed by rushing final approach.
 swoosh+=.095*hp*np.exp(-((absolute-3.59)/.13)**2)
 swoosh+=.06*hp*np.exp(-((absolute-3.9)/.09)**2)
 a=2*SR;b=4*SR
 arr[a:b,0]+=swoosh*.96
 arr[a:b,1]+=swoosh*1.04
 arr=np.tanh(arr*1.03)
 arr=np.clip(arr,-.96,.96)
 path=FINAL/f"{kind}_50m_sound.wav"
 with wave.open(str(path),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(np.round(arr*32767).astype("<i2").tobytes())
 return path
def encode(kind):
 fs=sources(kind)
 audio=make_audio(kind)
 out=FINAL/NAME[kind]
 cmd=[FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
      "-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","192k","-ar","48000","-frames:v",str(N),"-movflags","+faststart",str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i,f in enumerate(fs,1):
   im=cv2.imread(str(f),cv2.IMREAD_COLOR)
   if im is None:raise RuntimeError("READ_FAILED "+str(f))
   if im.shape[:2]!=(H,W):im=cv2.resize(im,(W,H),interpolation=cv2.INTER_LANCZOS4)
   p.stdin.write(im.tobytes())
   if i%48==0:print("ENCODE_PROGRESS",kind,i,flush=True)
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  if p.wait():raise RuntimeError(err[-1500:])
 except BaseException:
  p.kill();raise
 verify(out,192)
 poster(out,kind)
 print("DONE_VIDEO",kind,str(out),flush=True)
 return out
def verify(path,count):
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 wh=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
 assert (n,wh)==(count,(720,1280)) and abs(fps-24)<.02,(n,wh,fps,path)
 chk=subprocess.run([FF,"-v","error","-xerror","-i",str(path),"-f","null","NUL"],capture_output=True,text=True)
 assert chk.returncode==0,chk.stderr[-1000:]
 chk=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
 assert "Audio: aac" in chk.stderr,chk.stderr[-700:]
 print("VIDEO_VERIFIED",path.name,n,wh,fps,flush=True)
def poster(path,kind):
 cap=cv2.VideoCapture(str(path))
 marks=[0.5,1.75,2.10,2.45,2.85,3.1,3.5,3.7,3.9,4.05,5.3,7.4]
 img=Image.new("RGB",(6*204,2*390),(13,14,19))
 drawer=ImageDraw.Draw(img)
 for i,t in enumerate(marks):
  cap.set(cv2.CAP_PROP_POS_FRAMES,int(t*24))
  success,frame=cap.read()
  assert success
  tile=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(204,357)),cv2.COLOR_BGR2RGB))
  x=i%6*204;y=i//6*390
  img.paste(tile,(x,y+27))
  drawer.text((x+6,y+6),f"{t:.2f}s",fill="white")
 cap.release()
 img.save(FINAL/(kind+"_50M_V8_CONTACT.jpg"),quality=93)
def master(paths):
 files=FINAL/"concat_50m_v8.txt"
 files.write_text("\n".join("file '"+str(x).replace("\\","/")+"'" for x in paths),encoding="utf8")
 out=FINAL/"SLINGSHOT_50M_THREE_MATERIALS_24SEC_MASTER_V8.mp4"
 subprocess.run([FF,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(files),"-c","copy","-movflags","+faststart",str(out)],check=True)
 verify(out,576)
 print("MASTER_DONE",out,flush=True)
 return out
def html():
 dest=FINAL/"VIEW_50M_V8.html"
 content='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>새총 50m V8 | 속도감 비교</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{background:#0b1018;color:#eff3f7;margin:0;font-family:system-ui,"Malgun Gothic",sans-serif;padding:24px}
main{max-width:1280px;margin:auto}h1{font-size:1.8rem;margin-bottom:.3em}p{color:#b5c0d0;line-height:1.5;margin-top:0}
.toolbar{display:flex;flex-wrap:wrap;gap:9px;margin:14px 0}button{cursor:pointer;padding:11px 15px;border:1px solid #4d6687;background:#1c2f4b;color:#fff;border-radius:8px}
button.active{background:#396bb0}button:hover{background:#3a587d}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
article{background:#171e2a;padding:13px;border:1px solid #324158;border-radius:12px}h2{font-size:1.04rem;margin:0 0 8px}
video{background:#000;display:block;width:100%;max-height:660px;border-radius:7px;object-fit:contain}
aside{margin-top:20px;max-width:640px}aside video{max-height:unset}small{color:#bbc5d3}
@media(max-width:720px){body{padding:10px}.grid{gap:6px}article{padding:6px}h2{font-size:.88rem}button{flex:1 1 auto}}
</style></head><body><main>
<h1>새총 V8 — 50m 고속 비행</h1><p>실제 장면 거리 50.56m · 8초 · 24fps. 기존 20m와 속도감, 투사체 디자인, 충돌 후 구도 비교. <strong>클로즈업 없음.</strong></p>
<div class="toolbar"><button id="egg" class="active" onclick="choose('egg')">계란</button><button id="steel" onclick="choose('steel')">쇠구슬</button><button id="billiard" onclick="choose('billiard')">8번 당구공</button></div>
<div class="toolbar"><button onclick="both('play')">동시 재생</button><button onclick="both('pause')">일시정지</button><button onclick="seek(2)">발사부터 보기</button><button onclick="seek(0)">처음부터 보기</button></div>
<div class="grid">
<article><h2>이전 / 20m V5</h2><video id="a" controls playsinline loop preload="metadata" src="../../cinematic_20m_v4/final/01_EGG_20M_8SEC_V5.mp4"></video></article>
<article><h2>변경 / 50m V8</h2><video id="b" controls playsinline loop preload="metadata" src="01_EGG_50M_8SEC_V8.mp4"></video></article>
</div>
<aside><h2>50m 3종 합본 / 24초</h2><video controls playsinline preload="metadata" src="SLINGSHOT_50M_THREE_MATERIALS_24SEC_MASTER_V8.mp4"></video></aside>
<p><small>V8: 발사체 실루엣과 광택 조정, 콘크리트 거리 표식, 발사체보다 느린 전방 카메라, 벽 근처 고정 카메라의 빠른 회전, 충돌 후 고정 광각 카메라. 충돌 물리/재료는 기존 원본 자산 기반. 마지막 4초는 확대하지 않습니다.</small></p>
</main><script>
const names={egg:["01_EGG_20M_8SEC_V5.mp4","01_EGG_50M_8SEC_V8.mp4"],steel:["02_STEEL_20M_8SEC_V5.mp4","02_STEEL_50M_8SEC_V8.mp4"],billiard:["03_BILLIARD_20M_8SEC_V5.mp4","03_BILLIARD_50M_8SEC_V8.mp4"]};
const a=document.getElementById('a'),b=document.getElementById('b');
function choose(k){a.pause();b.pause();a.src='../../cinematic_20m_v4/final/'+names[k][0];b.src=names[k][1];Object.keys(names).forEach(v=>document.getElementById(v).classList.toggle('active',v===k));a.load();b.load();}
function both(v){if(v==='pause'){a.pause();b.pause();}else{b.currentTime=a.currentTime;a.play().catch(()=>{});b.play().catch(()=>{});}}
function seek(t){a.pause();b.pause();a.currentTime=t;b.currentTime=t;setTimeout(()=>{a.play().catch(()=>{});b.play().catch(()=>{});},140)}
</script></body></html>'''
 dest.write_text(content,encoding="utf8")
 return dest
if __name__=="__main__":
 jobs=sys.argv[1:] or ["egg","steel","billiard"]
 done=[encode(k) for k in jobs]
 if len(jobs)==3:
  master(done)
  path=html()
  (FINAL/"V8_QUALITY_CHECK.txt").write_text(
   "50.56m measured world coordinate path on source projectile (frame48 to96).\n"
   "ALL THREE: 8 sec / 192 frames / 720x1280 / 24fps / H.264 / AAC / decode PASS.\n"
   "MASTER: 24 sec / 576 frames / decode PASS.\n"
   "2-4 sec: 50m flight with two physically grounded camera shots.\n"
   "4-8 sec: source collision fixed camera. No zoom, no dolly, no temporal stretching.\n"
   "Master: "+str(FINAL/"SLINGSHOT_50M_THREE_MATERIALS_24SEC_MASTER_V8.mp4")+"\n"
   "Comparison: "+str(path)+"\n",encoding="utf8")
  print("V8_RELEASE_ALL_DONE",path,flush=True)
