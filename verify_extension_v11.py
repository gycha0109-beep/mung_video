from pathlib import Path
import re,cv2
R=Path.home()/"Downloads"/"slingshot_quality_proof"
D=R/"cinematic_50m_v11_extension"
page=D/"VIEW_ALL_50M_V11.html"
text=page.read_text(encoding="utf8")
assert (R/"OPEN_EXTENSION_V11.cmd").is_file()
linked=re.findall(r'(?:src|href)="([^"]+)"',text)
for name in linked:
 path=(D/name).resolve()
 assert path.is_file(),name
 print("LINK_OK",name)
for kind,file in (("steel","01_STEEL_50M_V11.mp4"),("billiard","02_8BALL_50M_V11.mp4")):
 path=D/kind/file
 cap=cv2.VideoCapture(str(path))
 n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));wh=(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
 fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
 assert (n,wh)==(192,(720,1280)) and abs(fps-24)<.03,(kind,n,wh,fps)
 print("VIDEO_VERIFIED",kind,n,wh,fps)
for kind in ("watermelon","cannon"):
 folder=D/kind
 assert (folder/f"{kind.upper()}_V11_50M_SINGLE_SCENE.blend").is_file()
 assert (folder/"PREVIEW_048.png").is_file() and (folder/"PREVIEW_101.png").is_file()
 print("PREVIEW_READY",kind)
print("V11_CURRENT_STATUS_VERIFIED")
