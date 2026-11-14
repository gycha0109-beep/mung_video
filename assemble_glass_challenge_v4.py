from pathlib import Path
import subprocess, json, wave, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v4"
RAW=OUT/"frames"
FRAMES=OUT/"frames_titled"
FRAMES.mkdir(exist_ok=True)
DATA=json.loads((OUT/"physics_results.json").read_text(encoding="utf8"))
assert DATA["total"]==20 and DATA["frames"]==192 and DATA["broken"]>0
FONT=Path("C:/Windows/Fonts/segoeuib.ttf")
if not FONT.exists():FONT=Path("C:/Windows/Fonts/arialbd.ttf")
font_large=ImageFont.truetype(str(FONT),58)
font_medium=ImageFont.truetype(str(FONT),35)
font_small=ImageFont.truetype(str(FONT),25)
broken=[e for e in DATA["break_events"] if e["broken"]]
stop=next(e for e in DATA["break_events"] if not e["broken"])
def draw_f(f):
    path=RAW/f"frame_{f:04d}.png"
    assert path.is_file() and path.stat().st_size>20000,("MISSING",path)
    bgr=cv2.imread(str(path))
    assert bgr is not None and bgr.shape[:2]==(1280,720),(path,bgr.shape if bgr is not None else None)
    image=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay=Image.new("RGBA",image.size,(0,0,0,0))
    d=ImageDraw.Draw(lay)
    current=sum(int(f>=e["frame"]) for e in broken)
    recent=any(abs(f-e["frame"])<=2 for e in broken)
    d.rounded_rectangle((38,45,682,160),radius=24,fill=(2,13,23,186),outline=(55,170,218,125),width=2)
    d.text((59,53),"GLASS RUN  /  20 PANELS",font=font_small,fill=(158,214,243,255))
    d.text((57,88),f"{current:02d}",font=font_large,fill=(255,195,96,255) if recent else (243,250,255,255))
    d.text((144,112),"/ 20 SHATTERED",font=font_medium,fill=(224,237,249,245))
    if f<48:
        d.rounded_rectangle((76,1100,644,1195),radius=18,fill=(4,19,31,168))
        d.text((96,1120),"DRAW / RELEASE / BREAK",font=font_medium,fill=(255,244,222,255))
    if f>=stop["frame"]:
        d.rounded_rectangle((62,1014,658,1196),radius=22,fill=(1,13,27,210),outline=(242,163,99,180),width=3)
        d.text((98,1030),"FINAL RESULT",font=font_small,fill=(142,210,246,255))
        d.text((98,1065),f"{DATA['broken']} / {DATA['total']}",font=font_large,fill=(255,200,98,255))
        d.text((99,1140),f"STOPPED AT GLASS #{stop['number']:02d}",font=font_small,fill=(245,245,245,255))
    image=Image.alpha_composite(image,lay).convert("RGB")
    return image

for f in range(1,193):
    output=FRAMES/f"frame_{f:04d}.png"
    valid=False
    if output.exists() and output.stat().st_size>20000:
        try:
            with Image.open(output) as check:
                check.load()
                valid=check.size==(720,1280)
        except (OSError,ValueError):
            valid=False
    if not valid:
        img=draw_f(f)
        temp=output.with_suffix(".partial.png")
        img.save(temp,optimize=False)
        temp.replace(output)
    if f%24==0:print("OVERLAY",f,"/192",flush=True)

# Recorded sound clips mixed locally from Mixkit (licensed source WAV kept offline).
wav=OUT/"GLASS_V4_RECORDED_SFX_MIX.wav"
assert wav.is_file() and wav.stat().st_size>100000
mp4=OUT/"GLASS_20_PANELS_8SEC_V4.mp4"
command=["ffmpeg","-hide_banner","-loglevel","error","-y","-framerate","24",
         "-i",str(FRAMES/"frame_%04d.png"),"-i",str(wav),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","160k","-t","8","-movflags","+faststart",str(mp4)]
subprocess.run(command,check=True)
p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,nb_frames,r_frame_rate","-show_entries","format=duration",
                 "-of","json",str(mp4)],capture_output=True,text=True,check=True)
info=json.loads(p.stdout)
streams=info["streams"]
vid=next(s for s in streams if s.get("codec_name")=="h264")
aud=next(s for s in streams if s.get("codec_name")=="aac")
assert (vid["width"],vid["height"],int(vid["nb_frames"]),vid["r_frame_rate"])==(720,1280,192,"24/1"),vid
assert abs(float(info["format"]["duration"])-8.0)<.05,info
subprocess.run(["ffmpeg","-v","error","-i",str(mp4),"-f","null","NUL"],check=True)
contact=OUT/"STORYBOARD.jpg"
shots=[1,40,49,57,72,95,120,146,154,171,184,192]
thumbs=[draw_f(f).resize((216,384)) for f in shots]
canvas=Image.new("RGB",(216*6,384*2),(12,18,25))
for i,im in enumerate(thumbs):
    canvas.paste(im,((i%6)*216,(i//6)*384))
canvas.save(contact,quality=86)
html="""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Glass Run | 쇠구슬 vs 유리판 20장</title><style>
:root{color-scheme:dark}body{margin:0;background:#0c111a;color:#eff6ff;font-family:system-ui,'Malgun Gothic',sans-serif;padding:20px}
main{margin:auto;max-width:980px}h1{font-size:1.65rem;margin:6px 0}p{color:#b7c8d9;line-height:1.6}
video{display:block;width:min(100%,460px);margin:22px auto;border-radius:12px;background:#000}
img{width:100%;border-radius:9px} .note{padding:13px;background:#162334;border-radius:9px}
a{color:#8ccfff}code{overflow-wrap:anywhere}
</style></head><body><main>
<h1>GLASS RUN V4 — 새총 발사와 유리판 20장</h1>
<p>8초 · 720×1280 · 24fps · 하나의 3D 장면. 고무줄을 당긴 뒤 쇠구슬이 감속하며 연속 관통하고, 최종 개수에서 멈추는 숏폼 시안입니다.</p>
<video controls playsinline preload="metadata" src="GLASS_20_PANELS_8SEC_V4.mp4"></video>
<p class="note">관통 모델 결과: <strong>17/20장</strong> · 18번째 판에서 정지. 관통력은 간략화된 에너지 계산이며, 조각 낙하는 Blender 강체 시뮬레이션입니다. 정밀한 충격·파괴 시뮬레이션으로 해석하지 마세요.</p>
<h2>장면 흐름 — 12개 확인 프레임</h2>
<img src="STORYBOARD.jpg" alt="발사, 다중 충돌, 정지의 흐름">
<p><a href="VIEW_GLASS_V3_VS_V4.html">V3 / V4 영상 비교</a> · <a href="../cinematic_50m_v11_extension/VIEW_ALL_50M_V11.html">기존 소재 영상</a></p>
</main></body></html>"""
(OUT/"VIEW_GLASS_CHALLENGE_V4.html").write_text(html,encoding="utf-8")
(ROOT/"OPEN_GLASS_CHALLENGE_V4.cmd").write_text('@echo off\r\nsetlocal\r\nstart "" "%~dp0glass_panel_challenge_v4\\VIEW_GLASS_CHALLENGE_V4.html"\r\n',encoding="ascii")
(OUT/"assembly_verification.json").write_text(json.dumps({"streams":streams,"duration":info["format"]["duration"],
     "file_bytes":mp4.stat().st_size,"shattered":DATA["broken"],"frames":192,"decoded_ok":True},indent=2),encoding="utf-8")
print("ASSEMBLY_DONE",mp4,"size",mp4.stat().st_size,flush=True)
