from pathlib import Path
import json,subprocess,re
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v4"
RAW=OUT/"frames"
MP4=OUT/"GLASS_20_PANELS_8SEC_V4.mp4"
META=json.loads((OUT/"physics_results.json").read_text(encoding="utf-8"))
expected={f"frame_{i:04d}.png" for i in range(1,193)}
actual={p.name for p in RAW.glob("frame_*.png")}
assert actual==expected,{"missing":sorted(expected-actual),"unexpected":sorted(actual-expected)}
for i in range(1,193):
    path=RAW/f"frame_{i:04d}.png"
    a=cv2.imread(str(path),cv2.IMREAD_COLOR)
    assert a is not None and a.shape[:2]==(1280,720),str(path)
print("ALL_192_PNG_DECODED",flush=True)
def proc(cmd):
    return subprocess.run(cmd,capture_output=True,text=True,check=True)
info=json.loads(proc(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,nb_frames,r_frame_rate","-show_entries","format=duration",
                      "-of","json",str(MP4)]).stdout)
v=next(s for s in info["streams"] if s.get("codec_name")=="h264")
aud=next(s for s in info["streams"] if s.get("codec_name")=="aac")
assert (v["width"],v["height"],int(v["nb_frames"]),v["r_frame_rate"])==(720,1280,192,"24/1")
assert abs(float(info["format"]["duration"])-8)<.05
proc(["ffmpeg","-v","error","-i",str(MP4),"-f","null","NUL"])
cap=cv2.VideoCapture(str(MP4))
assert cap.isOpened()
samples={}
for f in (1,32,42,57,72,146,154,192):
    cap.set(cv2.CAP_PROP_POS_FRAMES,f-1)
    ok,frame=cap.read()
    assert ok and frame is not None and frame.shape[:2]==(1280,720),f
    samples[str(f)]={"avg":round(float(frame.mean()),2),"contrast":round(float(frame.std()),2)}
cap.release()
# Both HTML videos are referenced by their correct relative file paths.
page=OUT/"VIEW_GLASS_V3_VS_V4.html"
html=page.read_text(encoding="utf-8")
sources=re.findall(r'<video\b[^>]*\bsrc="([^"]+)"',html)
assert len(sources)==2,sources
for src in sources:
    assert (OUT/src).resolve().is_file(),src
assert 'id="start"' in html and 'id="hit"' in html and 'id="pause"' in html
assert META["total"]==20 and META["broken"]==17 and META["stop_pane"]==18
report={
    "result":"PASS",
    "video":MP4.name,"duration_seconds":8,
    "fps":24,"frames":192,"resolution":"720x1280",
    "video_codec":"h264","audio_codec":"aac",
    "broken":17,"stopped_at":18,
    "source_png_decoded":192,"full_video_decoded":True,
    "sample_frames":samples,"comparison_html_sources":sources,
    "sound":"mixed from 5 recorded free-use stock clips; source WAV excluded from Git",
    "known_limitation":"stylized procedural animation; no claim of photorealism or physically exact breakage",
}
(OUT/"verification_v4.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("V4_VERIFIED",json.dumps({"result":"PASS","png":192,"duration":8,"samples":samples},ensure_ascii=False),flush=True)
