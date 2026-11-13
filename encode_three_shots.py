from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import subprocess, imageio_ffmpeg, cv2, wave, random, math, os, shutil
ROOT=Path.home()/"Downloads"/"slingshot_quality_proof"
OUT=ROOT/"three_shots"
OUT.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
FPS=24
FRAMES_LAUNCH=58
FRAMES_IMPACT=48
TOTAL=FRAMES_LAUNCH+FRAMES_IMPACT
RATE=48000
SOUNDS={"egg":"wet_splat","steel":"heavy_impact","billiard":"hard_rebound"}
TITLE={"egg":"01_EGG_SLINGSHOT","steel":"02_STEEL_SLINGSHOT","billiard":"03_BILLIARD_8_SLINGSHOT"}
rng=np.random.default_rng(201126)

def sound(t0,length,intensity=.1,typ="noise"):
    n=max(1,int(RATE*length))
    t=np.arange(n)/RATE
    white=rng.standard_normal(n)
    # Source sound, physical surface noises are short broadband bursts, not repeated beeps.
    if typ=="wet":
        w=.8*np.sin(2*np.pi*(160*t+90*t*t))+.45*np.sin(2*np.pi*305*t)+.36*white
        env=np.exp(-t*24)
    elif typ=="metal":
        w=.5*np.sin(2*np.pi*125*t)+.27*np.sin(2*np.pi*425*t)+.36*white
        env=np.exp(-t*10)
    elif typ=="resin":
        w=.74*np.sin(2*np.pi*465*t*np.exp(-3*t))+.24*white
        env=np.exp(-t*48)
    else:
        w=white
        env=np.exp(-t*30)
    sig=intensity*w*env
    start=int(t0*RATE)
    end=min(len(audio),start+len(sig))
    if end>start: audio[start:end]+=sig[:end-start]

def make_sound(kind, dest):
    global audio
    length=TOTAL/FPS
    audio=np.zeros(int(RATE*length),dtype=np.float64)
    # Take original 8-sec sound design for pull-back and release when compatible.
    source=ROOT/"quality_proof_sound.wav"
    try:
        with wave.open(str(source),"rb") as w:
            chan=w.getnchannels(); rate=w.getframerate(); width=w.getsampwidth()
            payload=w.readframes(int((FRAMES_LAUNCH/FPS)*rate))
        if width==2:
            raw=np.frombuffer(payload,dtype="<i2").astype(np.float64).reshape(-1,chan).mean(axis=1)/32768
            if rate != RATE:
                from scipy.signal import resample_poly
                raw=resample_poly(raw,RATE,rate)
            k=min(len(raw),int(FRAMES_LAUNCH/FPS*RATE))
            audio[:k]+=.73*raw[:k]
    except Exception as err:print("SOURCE_AUDIO_UNAVAILABLE",str(err),flush=True)
    release=2.10
    hit=FRAMES_LAUNCH/FPS+13/FPS
    sound(release,.31,.11,"noise")
    if kind=="egg":
        sound(hit,.32,.36,"wet")
        sound(hit+.06,.45,.20,"wet")
        for delay,amp in ((.18,.045),(.38,.035),(.62,.018)):sound(hit+delay,.10,amp,"wet")
    elif kind=="steel":
        sound(hit,.75,.58,"metal")
        for delay,amp in ((.08,.13),(.16,.10),(.29,.07),(.43,.045),(.60,.035)):
            sound(hit+delay,.10,amp,"noise")
    else:
        sound(hit,.17,.27,"resin")
        for delay,amp in ((.27,.13),(.57,.08),(.84,.055)):
            sound(hit+delay,.11,amp,"resin")
    audio=np.tanh(audio*1.3)*.78
    pcm=(audio*32767).astype("<i2")
    # Duplicate to stereo.
    stereo=np.column_stack((pcm,pcm)).tobytes()
    with wave.open(str(dest),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(stereo)

def source_frames(kind):
    if kind=="steel":
        launch=ROOT/"frames_pouch_v3"
        impact=ROOT/"physics_proof_v1"/"frames"
    else:
        launch=OUT/kind/"launch"
        impact=OUT/kind/"impact"/"frames"
    return launch,impact

def encode(kind):
    base=OUT/kind
    base.mkdir(parents=True,exist_ok=True)
    staged=base/"assembled_frames"
    staged.mkdir(exist_ok=True)
    launch,impact=source_frames(kind)
    srcs=[launch/("frame_%04d.png"%i) for i in range(1,FRAMES_LAUNCH+1)]
    srcs += [impact/("frame_%04d.png"%i) for i in range(1,FRAMES_IMPACT+1)]
    missing=[str(p) for p in srcs if not p.exists()]
    if missing:raise RuntimeError("MISSING "+kind+" "+str(missing[:5]))
    for i,src in enumerate(srcs,1):
        dest=staged/("frame_%04d.png"%i)
        if dest.exists():dest.unlink()
        if kind=="steel" and i<=FRAMES_LAUNCH:
            with Image.open(src) as im:
                im.convert("RGB").resize((720,1280),Image.Resampling.LANCZOS).save(dest,compress_level=2)
        else:
            # Hard link maintains identical pixels and avoids wasteful copies.
            try:os.link(src,dest)
            except OSError:shutil.copy2(src,dest)
    audio=base/"material_soundtrack.wav"
    make_sound(kind,audio)
    dest=OUT/(TITLE[kind]+".mp4")
    cmd=[FF,"-y","-hide_banner","-loglevel","error",
         "-framerate","24","-start_number","1","-i",str(staged/"frame_%04d.png"),
         "-i",str(audio),
         "-map","0:v:0","-map","1:a:0",
         "-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-ar","48000",
         "-frames:v",str(TOTAL),"-movflags","+faststart",str(dest)]
    subprocess.run(cmd,check=True)
    verify(dest,TOTAL)
    print("VIDEO_READY",kind,str(dest),dest.stat().st_size,flush=True)
    return dest

def verify(path,n_expected):
    cap=cv2.VideoCapture(str(path))
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=cap.get(cv2.CAP_PROP_FPS)
    checks=[]
    for fr in (0,int(n*.20),int(n*.45),int(n*.70),max(0,n-2)):
        cap.set(cv2.CAP_PROP_POS_FRAMES,fr)
        ok,img=cap.read()
        checks.append(ok and img is not None and float(img.mean())>5)
    cap.release()
    probe=subprocess.run([FF,"-hide_banner","-i",str(path)],
                         text=True,capture_output=True)
    audio_ok="Audio: aac" in probe.stderr
    if n!=n_expected or (w,h)!=(720,1280) or abs(fps-FPS)>.02 or not all(checks) or not audio_ok:
        raise RuntimeError("VIDEO_QA_FAILED "+repr((path,n,fps,w,h,checks,audio_ok)))
    print("PASS",path.name,n,"frames",fps,"fps",str(w)+"x"+str(h),"AAC",audio_ok,flush=True)

if __name__=="__main__":
    import sys
    requested=sys.argv[1:] or ["egg","steel","billiard"]
    if "all" in requested:requested=["egg","steel","billiard"]
    videos=[]
    for kind in requested:
        videos.append(encode(kind))
    if len(requested)==3:
        concat=OUT/"concat.txt"
        concat.write_text("\n".join("file '%s'"%p.as_posix().replace("'","") for p in videos),encoding="utf-8")
        master=OUT/"SLINGSHOT_THREE_MATERIALS_MASTER.mp4"
        subprocess.run([FF,"-y","-hide_banner","-loglevel","error",
                        "-f","concat","-safe","0","-i",str(concat),
                        "-c","copy","-movflags","+faststart",str(master)],check=True)
        verify(master,TOTAL*3)
        print("MASTER_READY",master,master.stat().st_size,flush=True)
        tiles=[("EGG / launch",OUT/"egg"/"launch"/"frame_0001.png"),
               ("EGG / collision",OUT/"egg"/"impact"/"frames"/"frame_0017.png"),
               ("STEEL / launch",ROOT/"frames_pouch_v3"/"frame_0001.png"),
               ("STEEL / collision",ROOT/"physics_proof_v1"/"frames"/"frame_0020.png"),
               ("8-BALL / launch",OUT/"billiard"/"launch"/"frame_0001.png"),
               ("8-BALL / collision",OUT/"billiard"/"impact"/"frames"/"frame_0017.png")]
        canvas=Image.new("RGB",(3*258,2*468),(20,22,25))
        d=ImageDraw.Draw(canvas)
        for idx,(label,src) in enumerate(tiles):
            with Image.open(src) as im:
                tile=ImageOps.fit(im.convert("RGB"),(258,437))
            x=(idx%3)*258; y=(idx//3)*468
            canvas.paste(tile,(x,y+31))
            d.text((x+7,y+10),label,fill=(251,251,251))
        poster=OUT/"THREE_SHOTS_VISUAL_PROOF.jpg"
        canvas.save(poster,quality=90)
        print("POSTER_READY",poster,flush=True)
