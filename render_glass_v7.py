import bpy,time,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v7"
bpy.ops.wm.open_mainfile(filepath=str(O/"V7_ONE_PANE_PHYSICS_MASTER.blend"))
S=bpy.context.scene
mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "preview"
assert mode in ("preview","full")
S.render.resolution_percentage=60 if mode=="preview" else 100
S.cycles.samples=32 if mode=="preview" else 48
frames=[1,28,36,38,40,43,48,54,66,84] if mode=="preview" else list(range(1,85))
dest=O/("preview" if mode=="preview" else "frames")
dest.mkdir(exist_ok=True)
try:
    addon=bpy.context.preferences.addons.get("cycles")
    if addon:
        prefs=addon.preferences
        prefs.compute_device_type="CUDA"
        prefs.get_devices()
        gpu=[d for d in prefs.devices if d.type=="CUDA"]
        if gpu:
            for d in prefs.devices:d.use=d.type=="CUDA"
            S.cycles.device="GPU"
            print("GPU_CUDA",[(d.name,d.type) for d in gpu],flush=True)
except Exception as exc:print("GPU_UNAVAILABLE",str(exc),flush=True)
start=time.time()
last=0
for frame in frames:
    # Rigid bodies must be evaluated at *every* preceding frame for repeatable physics.
    for fr in range(last+1,frame+1):
        S.frame_set(fr)
    last=frame
    file=dest/(f"V7_{frame:03d}.png" if mode=="preview" else f"frame_{frame:04d}.png")
    if file.exists() and file.stat().st_size>30000:
        with file.open("rb") as f:head=f.read(24)
        size=struct.unpack(">II",head[16:24]) if len(head)>=24 else None
        expected=(int(720*S.render.resolution_percentage/100),int(1280*S.render.resolution_percentage/100))
        if head.startswith(b"\x89PNG\r\n\x1a\n") and size==expected:
            print("SKIP_VALID",frame,flush=True)
            continue
    S.render.filepath=str(file)
    bpy.ops.render.render(write_still=True)
    print("FRAME_DONE",mode,frame,"/",len(frames),"elapsed",round(time.time()-start,1),flush=True)
print("V7_RENDER_DONE",mode,flush=True)
