from pathlib import Path
import re,cv2
r=Path.home()/"Downloads"/"slingshot_quality_proof"
o=r/"cinematic_50m_v10_egg"
html=o/"VIEW_EGG_V9T_VS_V10.html"
video=o/"EGG_50M_8SEC_V10_UNCUT.mp4"
assert html.is_file() and video.is_file()
refs=re.findall(r'src="([^"]+)"',html.read_text(encoding="utf-8"))
assert len(refs)==2,refs
for item in refs:
 p=(html.parent/item).resolve()
 assert p.exists(),p
 print("HTML_VIDEO_LINK_OK",p.name,flush=True)
cap=cv2.VideoCapture(str(video))
count=round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps=cap.get(cv2.CAP_PROP_FPS)
size=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
cap.release()
assert count==192 and abs(fps-24)<.03 and size==(720,1280),(count,fps,size)
assert (r/"OPEN_V10_UNCUT.cmd").exists()
print("V10_FINAL_VERIFIED",count,fps,size,video.stat().st_size,flush=True)
