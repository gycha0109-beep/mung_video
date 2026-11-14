from pathlib import Path
import json,math,wave,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v6"
ASSETS=ROOT/"glass_panel_challenge_v4"/"assets_local"
SR=48000
T=3.5
audio=np.zeros((int(T*SR),2),dtype=np.float32)
def load(filename):
    p=ASSETS/filename
    assert p.is_file(),p
    raw=subprocess.run(["ffmpeg","-v","error","-i",str(p),"-ar",str(SR),"-ac","2",
                        "-f","f32le","pipe:1"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
squeak=load("rubber_squeak.wav")
whoosh=load("projectile_arrow_whoosh.wav")
hit=load("glass_break_thud.wav")
metal=load("glass_metal_contact.wav")
debris=load("glass_debris_sweep.wav")
def add(at,src,gain,start=.0,dur=None,pitch=1.0,attack=.005,release=.08,pan=0):
    a=int(start*SR)
    length=len(src)-a if dur is None else int(dur*SR)
    clip=src[a:a+length]
    if len(clip)==0:return
    if pitch!=1:
        newlen=max(1,int(len(clip)/pitch))
        indices=np.minimum((np.arange(newlen)*pitch).astype(int),len(clip)-1)
        clip=clip[indices]
    n=len(clip)
    env=np.ones(n,dtype=np.float32)
    inn=min(n,int(attack*SR))
    off=min(n,int(release*SR))
    if inn:env[:inn]=np.linspace(0,1,inn)
    if off:env[-off:]*=np.linspace(1,0,off)
    dest=int(at*SR)
    limit=min(n,len(audio)-dest)
    if limit<=0:return
    l=math.sqrt((1-pan)*.5);r=math.sqrt((1+pan)*.5)
    audio[dest:dest+limit,0]+=gain*l*clip[:limit,0]*env[:limit]
    audio[dest:dest+limit,1]+=gain*r*clip[:limit,1]*env[:limit]
# Rubber draw (0.45–1.15 s), tension holds, fast pouch snap at ~1.30 s.
add(.35,squeak,.18,start=.30,dur=.86,pitch=.92,attack=.13,release=.17)
add(1.12,squeak,.05,start=2.1,dur=.17,release=.10)
add(31/24,squeak,.18,start=1.3,dur=.15,pitch=1.35,release=.09)
# The launch is an actual flying object sound, not white noise.
add(31/24+.055,whoosh,.55,start=.06,dur=.57,pitch=1.06,release=.24)
# Glass impact at frame 43: crack + metal contact + cascading glass on concrete.
impact=43/24
add(impact,metal,.31,dur=.28,pan=-.14,release=.12)
add(impact+.006,hit,.79,dur=.78,pitch=.98,release=.31)
add(impact+.080,debris,.25,dur=1.25,attack=.08,release=.35,pan=.15)
add(impact+.36,hit,.19,dur=.19,pitch=1.15,release=.12)
add(impact+.61,debris,.16,start=.43,dur=.75,release=.33)
# Steel ball hits the floor, makes a smaller bounce, then settles.
add(64/24,metal,.16,start=.08,dur=.20,pitch=.85,release=.10)
add(73/24,metal,.075,start=.05,dur=.15,pitch=.93,release=.08)
# Simple headroom for many overlapping transients.
audio=np.tanh(audio*1.15)
peak=float(np.max(np.abs(audio)))
if peak>.91:audio*=.91/peak
wav=OUT/"V6_LOCAL_MIX.wav"
with wave.open(str(wav),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((audio*32767).astype(np.int16).tobytes())
info={"fps":24,"duration_seconds":3.5,"impact_frame":43,"source_sounds":5,
      "source":"Mixkit local licensed WAV files (not redistributed)","file":wav.name,
      "rms":float(np.sqrt(np.mean(audio**2))),"peak":float(np.max(np.abs(audio)))}
(OUT/"sound_info.json").write_text(json.dumps(info,indent=2),encoding="utf8")
print("SOUND_COMPLETE",wav,wav.stat().st_size,flush=True)
