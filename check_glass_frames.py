from pathlib import Path
from PIL import Image
base=Path(r"C:\Users\hun\Documents\mung_video\glass_panel_challenge_v1\frames_titled")
bad=[]
for i in range(1,193):
    f=base/f"frame_{i:04d}.png"
    try:
        with Image.open(f) as im:
            im.load()
            if im.size!=(720,1280):bad.append((i,"WRONG_SIZE"))
    except Exception as exc:
        bad.append((i,str(exc)))
print("CHECKED",192,"BAD",bad,flush=True)
for i,e in bad:
    (base/f"frame_{i:04d}.png").unlink(missing_ok=True)
print("REMOVED_DAMAGED",len(bad),flush=True)
