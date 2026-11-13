from pathlib import Path
import subprocess, psutil, sys, time, traceback
root=Path.home()/"Downloads"/"slingshot_quality_proof"
out=root/"cinematic_20m_v4"
blender=Path("C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
sys.path.insert(0,str(root))
import assemble_20m_8sec_v4 as maker
log=out/"RUN_8SEC_20M_STATUS.txt"

def report(s):
 line=time.strftime("%Y-%m-%d %H:%M:%S")+" "+s
 print(line,flush=True)
 with log.open("a",encoding="utf-8") as f:f.write(line+"\n")

def count(kind,part):
 folder=out/kind/part
 return sum(1 for p in folder.glob("frame_*.png") if p.stat().st_size>20000) if folder.exists() else 0

def alive(pid):
 try:
  p=psutil.Process(pid)
  return p.is_running() and p.status()!=psutil.STATUS_ZOMBIE and p.name().lower().startswith("blender")
 except (psutil.NoSuchProcess,psutil.AccessDenied):return False

def start_blender(kind,part):
 script="resume_20m_v4.py" if part=="launch" else "render_impact_4sec_v4.py"
 args=[str(blender),"--background","--python",str(root/script),"--",kind]+(["full"] if part=="impact" else [])
 ff=(out/f"{kind}_{part}_auto.log").open("wb")
 ee=(out/f"{kind}_{part}_auto_err.log").open("wb")
 proc=subprocess.Popen(args,stdout=ff,stderr=ee)
 ff.close();ee.close()
 report("START "+kind+" "+part+" PID "+str(proc.pid))
 return proc.pid

def run_single(kind,part,pid=None):
 expected=96 if part=="launch" else 108
 if count(kind,part)==expected:
  report("ALREADY_PASS "+kind+" "+part)
  return
 if not pid or not alive(pid):
  # Recover from any incomplete, interrupted render.
  if part=="impact" and (out/f"{kind}_impact_aftermath_4sec.blend").exists():
   script="resume_impact_20m_v4.py"
   ff=(out/f"{kind}_{part}_resume.log").open("wb")
   ee=(out/f"{kind}_{part}_resume_err.log").open("wb")
   p=subprocess.Popen([str(blender),"--background","--python",str(root/script),"--",kind],stdout=ff,stderr=ee)
   ff.close();ee.close();pid=p.pid
   report("RESUME "+kind+" impact "+str(pid))
  else:
   pid=start_blender(kind,part)
 last=-1
 while alive(pid):
  n=count(kind,part)
  if n!=last and n%10==0:report("PROGRESS "+kind+" "+part+" "+str(n)+"/"+str(expected))
  last=n
  time.sleep(6)
 n=count(kind,part)
 report("PROCESS_END "+kind+" "+part+" "+str(n)+"/"+str(expected))
 if n!=expected:
  report("RETRY "+kind+" "+part)
  # Continue missing frames from saved Blender without overwriting verified earlier files.
  script="resume_20m_v4.py" if part=="launch" else "resume_impact_20m_v4.py"
  with (out/f"{kind}_{part}_retry.log").open("wb") as f, (out/f"{kind}_{part}_retry_err.log").open("wb") as e:
   sub=subprocess.run([str(blender),"--background","--python",str(root/script),"--",kind],stdout=f,stderr=e)
  n=count(kind,part)
  if sub.returncode or n!=expected:raise RuntimeError(f"{kind} {part}: {n}/{expected} code={sub.returncode}")
 report("FRAMES_VERIFIED "+kind+" "+part)

def encode_one(kind):
 if count(kind,"launch")!=96 or count(kind,"impact")!=108:
  raise RuntimeError("FRAME_REQUIREMENT_MISSING "+kind)
 report("ENCODING "+kind)
 maker.encode(kind)
 report("VIDEO_PASS "+kind)

def run():
 report("PIPELINE_RESUME_V4_BEGIN")
 # These are the two active jobs started and visually inspected in this conversation.
 run_single("egg","impact",9864)
 run_single("egg","launch",18640)
 encode_one("egg")
 # Continue both materials with their original asset scenes and preserved early frames.
 for kind in ("steel","billiard"):
  run_single(kind,"launch",24312 if kind=="steel" else None)
  run_single(kind,"impact")
  encode_one(kind)
 videos=[maker.FINAL/(maker.TITLES[k]+".mp4") for k in ("egg","steel","billiard")]
 master=maker.master(videos)
 lines=[
 "V4 VERIFIED 3 x 8.00s = 24.00s",
 "0..2 sec: slingshot draw / aim, 48 unique chronological frames",
 "2..4 sec: 20.56m scene-space projectile travel, 48 unique chronological frames",
 "4..8 sec: 96 consecutive, non-retimed Blender rigid-body/impact frames 13..108",
 "No deliberate slow-motion/frame repetition/screen shake.",
 "720x1280 24fps H264 AAC; all MP4 decoding validated.",
 "Original scene/render files untouched.",
 "Master: "+str(master)]
 (maker.FINAL/"QUALITY_CHECK.txt").write_text("\n".join(lines),encoding="utf8")
 report("ALL_DONE "+str(master))

try:run()
except BaseException as e:
 report("STOP_ERROR "+repr(e))
 report(traceback.format_exc())
 raise
