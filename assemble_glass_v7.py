import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import cv2
ROOT=Path(__file__).resolve().parent
O=ROOT/"glass_panel_challenge_v7"
F=O/"frames"
WAV=O/"V7_RECORDED_GLASS_SOUND.wav"
MP4=O/"V7_GLASS_SHATTER_3P5SEC.mp4"
FRAMES=84
assert WAV.is_file() and WAV.stat().st_size>100000
for n in range(1,FRAMES+1):
    p=F/f"frame_{n:04d}.png"
    assert p.is_file() and p.stat().st_size>30000,("MISSING_FRAME",n)
    im=cv2.imread(str(p),cv2.IMREAD_COLOR)
    assert im is not None and im.shape[:2]==(1280,720),("BAD_FRAME",n)
print("PNG_84_VALIDATED",flush=True)
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
     "-framerate","24","-i",str(F/"frame_%04d.png"),"-i",str(WAV),
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
     "-c:a","aac","-b:a","160k","-t","3.5","-movflags","+faststart",str(MP4)]
subprocess.run(cmd,check=True)
subprocess.run(["ffmpeg","-v","error","-i",str(MP4),"-f","null","NUL"],check=True)
info=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries",
                                 "stream=codec_name,width,height,nb_frames,r_frame_rate",
                                 "-show_entries","format=duration","-of","json",str(MP4)],
                                 capture_output=True,text=True,check=True).stdout)
v=next(i for i in info["streams"] if i.get("codec_name")=="h264")
a=next(i for i in info["streams"] if i.get("codec_name")=="aac")
assert (v["width"],v["height"],v["r_frame_rate"],int(v["nb_frames"]))==(720,1280,"24/1",84)
assert abs(float(info["format"]["duration"])-3.5)<.04
cap=cv2.VideoCapture(str(MP4))
samples={}
for n in [1,28,36,38,40,43,48,54,66,84]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,n-1)
    okay,img=cap.read()
    assert okay and img is not None and img.shape[:2]==(1280,720),n
    samples[str(n)]={"brightness":round(float(img.mean()),2),"contrast":round(float(img.std()),2)}
cap.release()
refs=[1,28,36,38,40,43,48,54,66,84]
w,h=216,384
story=Image.new("RGB",(w*5,h*2),(18,24,29))
fontpath=Path("C:/Windows/Fonts/segoeui.ttf")
font=ImageFont.truetype(str(fontpath),20) if fontpath.is_file() else None
for ix,n in enumerate(refs):
    im=Image.open(F/f"frame_{n:04d}.png").convert("RGB").resize((w,h))
    canvas=ImageDraw.Draw(im)
    canvas.rectangle((0,0,120,29),fill=(10,18,25))
    canvas.text((9,3),f"Frame {n}",font=font,fill=(244,247,250))
    story.paste(im,((ix%5)*w,(ix//5)*h))
story.save(O/"V7_STORYBOARD.jpg",quality=90)
report={"status":"PASS","type":"single-pane advanced physics quality test",
        "video":MP4.name,"video_bytes":MP4.stat().st_size,
        "resolution":[720,1280],"fps":24,"duration_seconds":3.5,
        "frames":84,"codec_video":"h264","codec_audio":"aac",
        "all_png_decoded":True,"full_mp4_decode":True,"sample_frames":samples,
        "limitations":"Pre-designed crack shapes; Blender rigid-body gravity after release, not physically measured crack propagation; one pane only"}
(O/"verification_v7.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf8")
print("V7_VERIFIED",MP4,MP4.stat().st_size,flush=True)
