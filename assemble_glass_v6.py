from pathlib import Path
import json,subprocess
import cv2
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v6"
RAW=O/"frames"
WAV=O/"V6_LOCAL_MIX.wav"
MP4=O/"V6_LAUNCH_GLASS_3P5S.mp4"
expected=[RAW/f"frame_{i:04d}.png" for i in range(1,85)]
assert WAV.exists() and WAV.stat().st_size>100000
for i,p in enumerate(expected,1):
    assert p.exists() and p.stat().st_size>40000,("missing",i)
    img=cv2.imread(str(p))
    assert img is not None and img.shape[:2]==(1280,720),(i,None if img is None else img.shape)
print("ALL_84_FRAMES_DECODED",flush=True)
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-framerate","24",
                "-i",str(RAW/"frame_%04d.png"),"-i",str(WAV),
                "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
                "-c:a","aac","-b:a","160k","-t","3.5",
                "-movflags","+faststart",str(MP4)],check=True)
result=subprocess.run(["ffprobe","-v","error","-show_entries",
    "stream=codec_name,nb_frames,width,height,r_frame_rate",
    "-show_entries","format=duration","-of","json",str(MP4)],
    capture_output=True,text=True,check=True)
info=json.loads(result.stdout)
v=next(x for x in info["streams"] if x.get("codec_name")=="h264")
a=next(x for x in info["streams"] if x.get("codec_name")=="aac")
assert (v["width"],v["height"],v["r_frame_rate"],int(v["nb_frames"]))==(720,1280,"24/1",84)
assert abs(float(info["format"]["duration"])-3.5)<.04
subprocess.run(["ffmpeg","-v","error","-i",str(MP4),"-f","null","NUL"],check=True)
shots=[1,24,29,32,37,41,43,46,49,55,65,84]
thumbs=[]
font_path=Path("C:/Windows/Fonts/segoeui.ttf")
font=ImageFont.truetype(str(font_path),22) if font_path.is_file() else None
for f in shots:
    img=Image.open(RAW/f"frame_{f:04d}.png").convert("RGB").resize((180,320))
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,90,32),fill=(9,15,20))
    d.text((8,5),f"Frame {f}",font=font,fill=(220,235,245))
    thumbs.append(img)
sheet=Image.new("RGB",(180*6,320*2),(12,18,24))
for i,x in enumerate(thumbs):sheet.paste(x,((i%6)*180,(i//6)*320))
sheet.save(O/"STORYBOARD_V6.jpg",quality=90)
cap=cv2.VideoCapture(str(MP4))
samples={}
for fr in [1,24,32,43,46,55,84]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,fr-1)
    good,frame=cap.read()
    assert good and frame.shape[:2]==(1280,720),fr
    samples[str(fr)]={"brightness":round(float(frame.mean()),2),
                      "contrast":round(float(frame.std()),2)}
cap.release()
doc={"status":"PASS","scope":"V6 slingshot-to-single-glass 3.5s quality demo",
     "frame_count":84,"fps":24,"size":[720,1280],
     "duration_seconds":float(info["format"]["duration"]),
     "codec_video":"h264","codec_audio":"aac","decoded_all":True,
     "audio":"Mixkit licensed stock effects mixed into the final video",
     "video":MP4.name,"video_bytes":MP4.stat().st_size,
     "sample_measurements":samples,
     "limitations":"Artist-animated glass shards, not a measured shatter solver; 1 pane, not 20."}
(O/"verification_v6.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf8")
print("V6_VIDEO_VERIFIED",MP4,MP4.stat().st_size,flush=True)
