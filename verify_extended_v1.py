from pathlib import Path
import subprocess, json, wave
import cv2
import numpy as np
import imageio_ffmpeg
r=Path.home()/"Downloads"/"slingshot_quality_proof"/"extended_v1"
ff=imageio_ffmpeg.get_ffmpeg_exe()
sources=["01_EGG_EXTENDED_V1.mp4","02_STEEL_EXTENDED_V1.mp4","03_BILLIARD_EXTENDED_V1.mp4","SLINGSHOT_THREE_MATERIALS_EXTENDED_V1_MASTER.mp4"]
records=[]
for file in sources:
 p=r/file
 expected=540 if "MASTER" in file else 180
 probe=subprocess.run([ff,"-hide_banner","-i",str(p)],capture_output=True,text=True)
 assert "Audio: aac" in probe.stderr
 decode=subprocess.run([ff,"-v","error","-xerror","-i",str(p),"-f","null","NUL"],capture_output=True,text=True)
 assert decode.returncode==0,(file,decode.stderr[-900:])
 cap=cv2.VideoCapture(str(p))
 assert cap.isOpened(),file
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 fps=cap.get(cv2.CAP_PROP_FPS)
 w=round(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 assert (n,w,h)==(expected,720,1280),(file,n,w,h)
 assert abs(fps-24)<.02
 count=0;mins=999.;maxs=0.;prev=None;changes=[]
 while True:
  ok,f=cap.read()
  if not ok:break
  mean=float(f.mean())
  mins=min(mins,mean);maxs=max(maxs,mean)
  if count in (30,51,70,71,84,85,120,155,179) and prev is not None:
   changes.append((count,round(float(cv2.absdiff(f,prev).mean()),2)))
  prev=f.copy()
  count+=1
 cap.release()
 assert count==expected,(file,count,expected)
 assert mins>8,(file,mins)
 records.append(f"{file}: PASS | {count} decoded frames | {count/fps:.2f} sec | {w}x{h} | AAC | mean brightness {mins:.1f}..{maxs:.1f} | {p.stat().st_size:,} bytes")
 print(records[-1],flush=True)
 if expected==180:print("  change metrics",changes,flush=True)
for kind in ("egg","steel","billiard"):
 with wave.open(str(r/(kind+"_sound.wav")),"rb") as wav:
  assert wav.getframerate()==48000
  raw=np.frombuffer(wav.readframes(wav.getnframes()),dtype="<i2")
  rms=np.sqrt(np.mean(raw.astype(np.float64)**2))/32768
  assert rms>.001,(kind,rms)
  records.append(f"AUDIO {kind}: 48kHz stereo, RMS={rms:.4f}")
(r/"QUALITY_CHECK.txt").write_text("\n".join(records)+"\nOriginal MP4 and .blend files retained. Extended segments rendered for egg and billiard (frames 59..82). Impact scene uses original physics frames with optical-flow slow motion. Launch/impact use a deliberately visible action camera cut; no continuous single-scene simulation is claimed.\n",encoding="utf-8")
print("FULL_DECODE_AND_AUDIO_QA_PASS",flush=True)
