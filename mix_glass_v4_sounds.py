from pathlib import Path
import json,wave,subprocess,math
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"glass_panel_challenge_v4"
SRC=OUT/"assets_local"
META=json.loads((ROOT/"glass_panel_challenge_v3"/"physics_results.json").read_text(encoding="utf8"))
SR=48000
DURATION=8
out=np.zeros((SR*DURATION,2),dtype=np.float32)
rng=np.random.default_rng(90411)

def load(name):
    p=SRC/name
    raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(p),"-vn","-ac","2","-ar",str(SR),"-f","f32le","pipe:1"],capture_output=True,check=True).stdout
    x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
    print("ASSET",name,round(len(x)/SR,2),"peak",round(float(np.max(np.abs(x))),3),flush=True)
    return x

breaks=load("glass_break_thud.wav")
metal=load("glass_metal_contact.wav")
debris=load("glass_debris_sweep.wav")
whoosh=load("projectile_arrow_whoosh.wav")
elastic=load("rubber_squeak.wav")

def add(t,src,vol=1,dur=None,start=0,speed=1,fade_in=.003,fade_out=.07,pan=0):
    ix=max(0,int(start*SR))
    n=int(dur*SR) if dur is not None else len(src)-ix
    clip=src[ix:max(ix,ix+n)]
    if len(clip)<4:return
    if speed!=1:
        n2=max(1,int(len(clip)/speed))
        indices=np.minimum((np.arange(n2)*speed).astype(int),len(clip)-1)
        clip=clip[indices]
    head=max(0,int(fade_in*SR))
    tail=max(0,int(fade_out*SR))
    env=np.ones(len(clip),dtype=np.float32)
    if head:env[:min(head,len(clip))]*=np.linspace(0,1,min(head,len(clip)),dtype=np.float32)
    if tail:env[-min(tail,len(clip)):]*=np.linspace(1,0,min(tail,len(clip)),dtype=np.float32)
    offset=int(t*SR)
    if offset<0:
        clip=clip[-offset:]
        env=env[-offset:]
        offset=0
    n=min(len(clip),len(out)-offset)
    if n<=0:return
    l=vol*math.sqrt((1-pan)*.5)
    r=vol*math.sqrt((1+pan)*.5)
    out[offset:offset+n,0]+=clip[:n,0]*env[:n]*l
    out[offset:offset+n,1]+=clip[:n,1]*env[:n]*r

# Audible tension during the entire slow pull, then the quiet pre-release hold.
add(.48,elastic,.13,dur=1.28,start=.16,speed=.83,fade_in=.20,fade_out=.20)
add(1.52,elastic,.060,dur=.22,start=2.0,speed=1.05,fade_out=.10)
# Real recorded whizz of a fast moving object.
add(1.98,whoosh,.58,dur=1.02,fade_in=.02,fade_out=.18)
add(2.00,elastic,.065,dur=.17,start=1.15,speed=1.45,fade_out=.11)
broken=[e for e in META["break_events"] if e["broken"]]
for i,e in enumerate(broken):
    t=e["frame"]/24
    # Different playback positions and speeds avoid 17 identical crash waveforms.
    speed=1+.065*(i%5-2)
    amp=.47*(.89**(i/4))
    add(t,breaks,amp,dur=.23+.04*(i%3),start=.0,speed=speed,fade_in=.003,fade_out=.15,pan=.22*(i%3-1))
    add(t+.016,metal,.28*(.91**(i/6)),dur=.21,start=.02*(i%4),speed=1+.11*(i%5-2),fade_in=.001,fade_out=.10,pan=-.19*(i%3-1))
    if i in (0,4,9,15):
        add(t+.09,debris,.18,dur=.64,start=.15*(i%3),speed=1.01,fade_in=.02,fade_out=.29,pan=.2*(i%2-.5))
# 18th pane catches the steel ball without breaking.
stop=next(e for e in META["break_events"] if not e["broken"])
t=stop["frame"]/24
add(t,metal,.61,dur=.36,start=0,fade_out=.15)
add(t+.14,debris,.23,dur=1.25,start=.0,fade_in=.05,fade_out=.34)
add(t+.32,metal,.12,dur=.21,start=.11,speed=.76,fade_out=.13)
# Limit harsh overlap with soft saturation, gentle loudness normalization.
out=np.tanh(out*1.18)
peak=float(np.max(np.abs(out)))
if peak>.91:out*=.91/peak
wfile=OUT/"GLASS_V4_RECORDED_SFX_MIX.wav"
with wave.open(str(wfile),"wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
rms=float(np.sqrt(np.mean(out*out)))
report={"duration":8,"sample_rate":SR,"source":"Mixkit free sound effects (original local files excluded from Git)","source_assets":5,"impact_count":len(broken),"first_impact_seconds":broken[0]["frame"]/24,"stopping_impact_seconds":t,"peak":peak,"rms":rms,"file":wfile.name}
(OUT/"audio_mix_verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("AUDIO_COMPLETE",wfile,"peak",round(peak,3),"RMS",round(rms,4),flush=True)
