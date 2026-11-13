from pathlib import Path
import subprocess,cv2,numpy as np,sys
import assemble_20m_8sec_v4 as base
R=Path.home()/"Downloads"/"slingshot_quality_proof"
V4=R/"cinematic_20m_v4"
FINAL=V4/"final"
FF=base.FF
RATE=base.FPS
N=192
TITLES={"egg":"01_EGG_20M_8SEC_V5","steel":"02_STEEL_20M_8SEC_V5","billiard":"03_BILLIARD_20M_8SEC_V5"}
def launch_frame(kind,n):
 return V4/kind/"launch"/f"frame_{n:04d}.png"
def physics_frame(kind,n):
 if kind=="steel":return R/"physics_proof_v1"/"frames"/f"frame_{n:04d}.png"
 return R/"three_shots"/kind/"impact"/"frames"/f"frame_{n:04d}.png"
def photo(path):
 a=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if a is None:raise FileNotFoundError(path)
 if a.shape[:2]!=(1280,720):a=cv2.resize(a,(720,1280),interpolation=cv2.INTER_LANCZOS4)
 return a
def linger(source,i):
 # Settled aftermath: continuous camera dolly only, no physical slow motion or repeated frames.
 t=i/60.
 smooth=t*t*(3-2*t)
 zoom=1.+.075*smooth
 xscale=round(720*zoom);yscale=round(1280*zoom)
 pic=cv2.resize(source,(xscale,yscale),interpolation=cv2.INTER_LINEAR)
 center_x=xscale//2+round(7*smooth)
 center_y=yscale//2+round(5*smooth)
 x0=max(0,min(xscale-720,center_x-360))
 y0=max(0,min(yscale-1280,center_y-640))
 return pic[y0:y0+1280,x0:x0+720].copy()
def verify_break(kind,frames):
 # The steel wall must show an obvious physical difference before and after collision.
 if kind!="steel":return
 old_before=photo(physics_frame(kind,13))
 old_after=photo(physics_frame(kind,24))
 change=np.mean(cv2.absdiff(old_before,old_after))
 if change<4:raise RuntimeError("PHYSICS_ORIGINAL_NOT_DISTINCT "+str(change))
 print("STEEL_PHYSICS_CONFIRMED_PIXEL_CHANGE",round(float(change),2),flush=True)
def encode(kind):
 frames=[launch_frame(kind,i) for i in range(1,97)]+[physics_frame(kind,i) for i in range(13,49)]
 assert len(frames)==132
 missing=[p for p in frames if not p.is_file()]
 if missing:raise FileNotFoundError(missing[:3])
 verify_break(kind,frames)
 last=photo(physics_frame(kind,48))
 audio=base.make_audio(kind)
 dest=FINAL/(TITLES[kind]+".mp4")
 cmd=[FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r","24","-i","pipe:0","-i",str(audio),
  "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","192k","-ar","48000","-frames:v",str(N),"-movflags","+faststart",str(dest)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i,src in enumerate(frames,1):
   p.stdin.write(photo(src).tobytes())
  for i in range(1,61):
   p.stdin.write(linger(last,i).tobytes())
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  returncode=p.wait()
  if returncode:raise RuntimeError("FFMPEG: "+err[-1200:])
 except BaseException:p.kill();raise
 base.verify(dest,N)
 print("V5_RESTORED",kind,dest,flush=True)
 return dest
def master(videos):
 concat=FINAL/"concat_20m_8sec_v5.txt"
 concat.write_text("\n".join("file '"+f.as_posix().replace("'","")+"'" for f in videos),encoding="utf8")
 out=FINAL/"SLINGSHOT_THREE_MATERIALS_20M_24SEC_MASTER_V5.mp4"
 subprocess.run([FF,"-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(out)],check=True)
 base.verify(out,3*N)
 (FINAL/"QUALITY_CHECK_V5.txt").write_text(
  "Three videos x 192 frames = 8s each, 24s master.\n"
  "0-2sec 48 original chronological 20m-setup launch frames.\n"
  "2-4sec 48 new chronological 20m flight frames (20.56m, Blender scene coordinates).\n"
  "4-5.5sec ORIGINAL verified high-fidelity physics frames 13-48, no retime.\n"
  "5.5-8sec camera push-in over physically settled aftermath; no slow motion, no frame holds/shake.\n"
  "The final 2.5sec camera movement is a 2D reframing of the last original physics image; no additional rigid-body movement is claimed.\n"
  "720x1280,24fps,H264/AAC; decoding verified. Original source assets preserved.\n"
  "Master: "+str(out)+"\n",encoding="utf8")
 print("V5_MASTER_COMPLETE",out,flush=True)
if __name__=="__main__":
 vids=[encode(k) for k in ("egg","steel","billiard")]
 master(vids)
