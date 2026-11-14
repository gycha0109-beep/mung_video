from pathlib import Path
import json, math, subprocess, wave
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v5"
raw=out/"frames"
source=root/"glass_panel_challenge_v4"/"assets_local"
fps=24; count=36; sr=48000
assert len(list(raw.glob("frame_*.png")))==count,"Render not finished"
for f in range(1,count+1):
    p=raw/f"frame_{f:04d}.png"
    im=cv2.imread(str(p))
    assert im is not None and im.shape[:2]==(896,504),f
print("VALID_FRAMES",count,flush=True)
def read_wav(filename):
    p=source/filename
    proc=subprocess.run(["ffmpeg","-v","error","-i",str(p),"-ac","2","-ar",str(sr),"-f","f32le","pipe:1"],capture_output=True,check=True)
    return np.frombuffer(proc.stdout,dtype=np.float32).reshape(-1,2).copy()
sound=np.zeros((int(1.5*sr),2),dtype=np.float32)
def add(at,data,gain,offset=0,length=None):
    a=int(max(0,offset)*sr)
    b=len(data) if length is None else min(len(data),a+int(length*sr))
    seg=data[a:b]
    if not len(seg):return
    start=int(at*sr)
    end=min(len(sound),start+len(seg))
    if end<=start:return
    seg=seg[:end-start]
    env=np.ones((len(seg),1),dtype=np.float32)
    fi=min(int(sr*.004),len(seg))
    fo=min(int(sr*.14),len(seg))
    if fi:env[:fi,0]=np.linspace(0,1,fi)
    if fo:env[-fo:,0]*=np.linspace(1,0,fo)
    sound[start:end]+=gain*seg*env
add(.10,read_wav("projectile_arrow_whoosh.wav"),.37,0,.50)
add(.48,read_wav("glass_metal_contact.wav"),.23,0,.38)
add(.50,read_wav("glass_break_thud.wav"),.62,0,.67)
add(.61,read_wav("glass_debris_sweep.wav"),.17,0,.72)
sound=np.tanh(sound*1.05)
maxamp=float(np.max(np.abs(sound)))
if maxamp>.94:sound*=.94/maxamp
wav=out/"V5_ONE_PANE_AUDIO_MIX.wav"
with wave.open(str(wav),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes((np.clip(sound,-1,1)*32767).astype(np.int16).tobytes())
mp4=out/"V5_ONE_PANE_QUALITY_PROOF.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-framerate","24","-i",str(raw/"frame_%04d.png"),"-i",str(wav),"-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","18","-c:a","aac","-b:a","160k","-t","1.5","-movflags","+faststart",str(mp4)],check=True)
subprocess.run(["ffmpeg","-v","error","-i",str(mp4),"-f","null","NUL"],check=True)
info=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,nb_frames,width,height,r_frame_rate","-show_entries","format=duration","-of","json",str(mp4)],check=True,capture_output=True,text=True).stdout)
video=next(s for s in info["streams"] if s["codec_name"]=="h264")
assert (int(video["nb_frames"]),video["width"],video["height"],video["r_frame_rate"])==(36,504,896,"24/1")
assert abs(float(info["format"]["duration"])-1.5)<.05
shots=[1,11,12,15,20,28]
thumbs=[Image.open(raw/f"frame_{f:04d}.png").convert("RGB").resize((252,448)) for f in shots]
sheet=Image.new("RGB",(252*6,448),(20,21,22))
for i,im in enumerate(thumbs):sheet.paste(im,(i*252,0))
sheet.save(out/"V5_QUALITY_STORYBOARD.jpg",quality=87)
report={"status":"PASS","scope":"single glass-pane quality proof only","fps":24,"duration":1.5,"frames":36,"resolution":"504x896 test render","video":"V5_ONE_PANE_QUALITY_PROOF.mp4","source_sounds":"Mixkit, sourced locally from V4 and not redistributed separately","note":"This is not V5 full twenty-pane video and does not yet meet confirmed photoreal standard"}
(out/"quality_test_verification.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print("V5_ONE_PANE_VIDEO_VERIFIED",mp4,mp4.stat().st_size,flush=True)
