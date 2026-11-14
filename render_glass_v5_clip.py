import bpy,sys,time,struct
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v5"
bpy.ops.wm.open_mainfile(filepath=str(out/"GLASS_V5_ONE_PANE_QUALITY_TEST.blend"))
s=bpy.context.scene
s.render.resolution_percentage=70
s.cycles.samples=32
dest=out/"frames"
dest.mkdir(exist_ok=True)
try:
    addon=bpy.context.preferences.addons.get("cycles")
    if addon:
        pref=addon.preferences
        pref.compute_device_type="CUDA"
        pref.get_devices()
        cuda=[d for d in pref.devices if d.type=="CUDA"]
        if cuda:
            for d in pref.devices:d.use=(d.type=="CUDA")
            s.cycles.device="GPU"
except Exception as ex:print("CUDA_UNAVAILABLE",ex,flush=True)
start=time.time()
for f in range(1,37):
    s.frame_set(f)
    p=dest/f"frame_{f:04d}.png"
    if p.exists() and p.stat().st_size>30000:
        with p.open("rb") as h:header=h.read(24)
        if header[:8]==b"\x89PNG\r\n\x1a\n" and struct.unpack(">II",header[16:24])==(504,896):
            print("SKIP_EXISTING",f,flush=True)
            continue
    s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    print("RENDERED",f,"/36",round(time.time()-start,1),flush=True)
print("ALL_36_FINISHED",flush=True)
