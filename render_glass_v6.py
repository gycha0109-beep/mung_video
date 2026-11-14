import bpy,time,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v6"
bpy.ops.wm.open_mainfile(filepath=str(O/"GLASS_V6_QUALITY_FINAL.blend"))
s=bpy.context.scene
mode=(sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview")
assert mode in ("preview","full")
s.render.resolution_percentage=65 if mode=="preview" else 100
s.cycles.samples=32 if mode=="preview" else 48
D=O/("preview_final" if mode=="preview" else "frames")
D.mkdir(exist_ok=True)
frames=([1,17,24,29,32,37,41,43,46,49,55,65,84] if mode=="preview" else list(range(1,85)))
try:
    addon=bpy.context.preferences.addons.get("cycles")
    if addon:
        pref=addon.preferences
        pref.compute_device_type="CUDA"
        pref.get_devices()
        if any(d.type=="CUDA" for d in pref.devices):
            for device in pref.devices:device.use=(device.type=="CUDA")
            s.cycles.device="GPU"
            print("RENDER_GPU_CUDA",flush=True)
except Exception as ex:
    print("RENDER_CPU_FALLBACK",ex,flush=True)
start=time.time()
for f in frames:
    s.frame_set(f)
    p=D/(f"V6_{f:03d}.png" if mode=="preview" else f"frame_{f:04d}.png")
    if p.exists() and p.stat().st_size>30000:
        with p.open("rb") as im:
            h=im.read(24)
        pct=s.render.resolution_percentage/100
        w,hgt=struct.unpack(">II",h[16:24])
        if h[:8]==b"\x89PNG\r\n\x1a\n" and (w,hgt)==(int(720*pct),int(1280*pct)):
            print("SKIP",f,flush=True)
            continue
    s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    print("V6_FRAME",mode,f,"of",len(frames),"elapsed",round(time.time()-start,1),flush=True)
print("V6_RENDER_DONE",mode,flush=True)
