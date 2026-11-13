import sys,cv2
from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
sys.path.insert(0,str(r))
from assemble_50m_v9t_egg import directional_background_blur
o=r/"cinematic_50m_v9t_egg"
for f in (55,74,82):
 source=o/"launch_frames"/f"frame_{f:04d}.png"
 if not source.is_file():continue
 frame=cv2.imread(str(source))
 output=directional_background_blur(frame,f)
 path=o/f"BLUR_QA_{f:03d}.jpg"
 cv2.imwrite(str(path),output,[cv2.IMWRITE_JPEG_QUALITY,94])
 print("BLUR_PREVIEW_READY",path)
