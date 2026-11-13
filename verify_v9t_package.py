from pathlib import Path
import re,cv2
r=Path.home()/"Downloads"/"slingshot_quality_proof"
o=r/"cinematic_50m_v9t_egg"
html=o/"VIEW_EGG_SHORTS_VS_TRACKLOCK.html"
v=o/"EGG_50M_8SEC_TRACKLOCK_V9T.mp4"
assert html.is_file() and v.is_file()
links=re.findall(r'src="([^"]+)"',html.read_text(encoding="utf-8"))
for link in links:
 p=(html.parent/link).resolve()
 assert p.is_file(),p
 print("LINK_OK",p.name)
cap=cv2.VideoCapture(str(v))
f=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps=cap.get(cv2.CAP_PROP_FPS)
dims=round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()
assert (f,dims)==(192,(720,1280)) and abs(fps-24)<.01
assert (r/"OPEN_TRACKLOCK_V9T.cmd").is_file()
print("V9T_PACKAGING_PASS",f,dims,fps,round(v.stat().st_size/1048576,1),"MiB")
