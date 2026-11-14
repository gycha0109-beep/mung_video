import bpy,sys,time
from pathlib import Path
import struct
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v4"
scene_path=out/"GLASS_20_PANEL_CHALLENGE_V4_FINAL.blend"
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
s=bpy.context.scene
mode=(sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview")
assert mode in ("preview","full")
frames=([1,32,57,72,146,154,192] if mode=="preview" else list(range(1,193)))
dst=out/("preview_final" if mode=="preview" else "frames")
dst.mkdir(exist_ok=True)
s.render.resolution_percentage=65 if mode=="preview" else 100
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
start=time.time()
prior=0
for f in frames:
    for j in range(prior+1,f+1):s.frame_set(j)
    prior=f
    p=dst/(f"V4F_{f:03d}.png" if mode=="preview" else f"frame_{f:04d}.png")
    if p.exists() and p.stat().st_size>20000:
        try:
            with p.open('rb') as im:
                h=im.read(24)
            assert h[:8]==b'\x89PNG\r\n\x1a\n' and h[12:16]==b'IHDR'
            width,height=struct.unpack('>II',h[16:24])
            percent=65 if mode=='preview' else 100
            assert width==int(720*percent/100) and height==int(1280*percent/100),(width,height)
            print("SKIP_VALID",f,flush=True)
            continue
        except Exception:
            pass
    s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    print("V4_RENDERED",mode,f,"/192",round(time.time()-start,1),flush=True)
print("V4_RENDER_COMPLETE",mode,flush=True)
