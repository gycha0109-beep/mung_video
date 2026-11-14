import bpy,sys,time,json
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v3"
scene_path=out/"GLASS_20_PANEL_CHALLENGE_V3.blend"
assert scene_path.exists(),scene_path
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
s=bpy.context.scene
mode=(sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview")
assert mode in ("preview","full")
frames=[1,40,49,57,60,63,72,95,120,146,154,171,192] if mode=="preview" else list(range(1,193))
dst=out/("preview" if mode=="preview" else "frames")
dst.mkdir(exist_ok=True)
s.render.resolution_percentage=60 if mode=="preview" else 100
s.render.image_settings.file_format="PNG"
s.render.image_settings.color_mode="RGB"
if mode=="preview":
    try:s.render.engine="BLENDER_EEVEE"
    except Exception:pass
t0=time.time()
prev=0
for f in frames:
    for j in range(prev+1,f+1):
        s.frame_set(j)
    prev=f
    path=dst/(f"PREVIEW_{f:03d}.png" if mode=="preview" else f"frame_{f:04d}.png")
    if path.exists() and path.stat().st_size>40000:
        print("SKIP_FRAME",f,flush=True)
        continue
    s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    print("RENDERED",mode,f,"/",192,"elapsed",round(time.time()-t0,1),flush=True)
print("RENDER_DONE",mode,flush=True)
