from pathlib import Path
import subprocess
import cv2,numpy as np
import imageio_ffmpeg
root=Path.home()/"Downloads"/"slingshot_quality_proof"
v5=root/"cinematic_20m_v4"/"final"/"01_EGG_20M_8SEC_V5.mp4"
v6=root/"cinematic_v6_egg"/"EGG_20M_8SEC_V6.mp4"
out=root/"cinematic_v6_egg"/"V5_VS_V6_LAST_2_5_SEC.mp4"
ff=imageio_ffmpeg.get_ffmpeg_exe()
c1=cv2.VideoCapture(str(v5));c2=cv2.VideoCapture(str(v6))
for c in (c1,c2):c.set(cv2.CAP_PROP_POS_FRAMES,132)
p=subprocess.Popen([ff,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s","728x680","-r","24","-i","pipe:0",
 "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p","-frames:v","60","-movflags","+faststart",str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 for i in range(60):
  a,x=c1.read();b,y=c2.read()
  if not (a and b):raise RuntimeError("FRAME_MISSING "+str(i))
  xx=cv2.resize(x,(360,640),interpolation=cv2.INTER_AREA)
  yy=cv2.resize(y,(360,640),interpolation=cv2.INTER_AREA)
  frame=np.full((680,728,3),(17,18,24),dtype=np.uint8)
  frame[40:680,0:360]=xx
  frame[40:680,368:728]=yy
  cv2.putText(frame,"V5 - BEFORE",(22,27),cv2.FONT_HERSHEY_SIMPLEX,.62,(245,245,245),1,cv2.LINE_AA)
  cv2.putText(frame,"V6 - AFTER",(389,27),cv2.FONT_HERSHEY_SIMPLEX,.62,(245,245,245),1,cv2.LINE_AA)
  p.stdin.write(frame.tobytes())
 p.stdin.close();err=p.stderr.read().decode(errors="replace");rc=p.wait()
 if rc:raise RuntimeError("ffmpeg "+err)
finally:
 c1.release();c2.release()
check=cv2.VideoCapture(str(out))
assert int(check.get(cv2.CAP_PROP_FRAME_COUNT))==60
check.release()
print("VERIFIED_SHORT_COMPARISON",out,out.stat().st_size)
