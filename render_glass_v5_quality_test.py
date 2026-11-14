import bpy, time, json
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v5"
bpy.ops.wm.open_mainfile(filepath=str(out/"GLASS_V5_ONE_PANE_QUALITY_TEST.blend"))
s=bpy.context.scene
s.render.resolution_percentage=70
s.cycles.samples=32
dst=out/"quality_proof"
dst.mkdir(exist_ok=True)
try:
    addon=bpy.context.preferences.addons.get("cycles")
    if addon:
        pref=addon.preferences
        pref.compute_device_type="CUDA"
        pref.get_devices()
        devices=[d for d in pref.devices if d.type=="CUDA"]
        if devices:
            for d in pref.devices:d.use=(d.type=="CUDA")
            s.cycles.device="GPU"
            print("CUDA_DEVICE",[(d.name,d.type) for d in devices],flush=True)
except Exception as ex:
    print("GPU_FALLBACK",str(ex),flush=True)
t0=time.time()
previous=0
for f in [1,11,12,15,20,28]:
    for j in range(previous+1,f+1):s.frame_set(j)
    previous=f
    p=dst/f"FRAME_{f:03d}.png"
    if p.exists() and p.stat().st_size>30000:
        print("EXISTS",p,flush=True)
        continue
    s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    print("PROOF_RENDERED",f,"ELAPSED",round(time.time()-t0,1),flush=True)
print("PROOF_DONE",flush=True)
