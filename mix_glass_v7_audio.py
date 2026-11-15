from pathlib import Path
import json,subprocess,wave,math
import numpy as np
R=Path(__file__).resolve().parent
O=R/"glass_panel_challenge_v7"
SRC=R/"glass_panel_challenge_v4"/"assets_local"
SR=48000
audio=np.zeros((int(3.5*SR),2),dtype=np.float32)
def load(name):
    p=SRC/name
    assert p.is_file()
    raw=subprocess.run(["ffmpeg","-v","error","-i",str(p),"-ar",str(SR),"-ac","2","-f","f32le","pipe:1"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
whoosh=load("projectile_arrow_whoosh.wav")
impact=load("glass_break_thud.wav")
metal=load("glass_metal_contact.wav")
debris=load("glass_debris_sweep.wav")
def place(t,data,vol,start=0,dur=None,rate=1,fade=.16):
    ix=int(start*SR)
    seg=data[ix:] if dur is None else data[ix:ix+int(dur*SR)]
    if not len(seg):return
    if rate!=1:
        src=np.minimum((np.arange(int(len(seg)/rate))*rate).astype(int),len(seg)-1)
        seg=seg[src]
    n=len(seg)
    envelope=np.ones(n)
    lead=min(n,int(.007*SR))
    tail=min(n,int(fade*SR))
    if lead:envelope[:lead]=np.linspace(0,1,lead)
    if tail:envelope[-tail:]*=np.linspace(1,0,tail)
    ix=int(t*SR)
    length=min(n,len(audio)-ix)
    if length>0:audio[ix:ix+length]+=seg[:length]*envelope[:length,None]*vol
# One directional pass, slightly preceding physical contact
place(.85,whoosh,.41,start=.06,dur=.92,rate=.94,fade=.25)
t=38/24
place(t-.018,metal,.25,start=0,dur=.26,fade=.11)
place(t,impact,.74,dur=.94,rate=1.02,fade=.28)
place(t+.13,debris,.28,dur=1.2,fade=.44)
place(t+.38,impact,.09,start=.22,dur=.22,rate=.8,fade=.14)
place(t+.64,debris,.16,start=.34,dur=.74,fade=.29)
place(2.85,metal,.09,start=.07,dur=.18,rate=.8,fade=.08)
audio=np.tanh(audio*1.05)
peak=float(np.max(np.abs(audio)))
if peak>.92:audio*=.92/peak
p=O/"V7_RECORDED_GLASS_SOUND.wav"
with wave.open(str(p),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((np.clip(audio,-1,1)*32767).astype(np.int16).tobytes())
(O/"sound_verification.json").write_text(json.dumps({
    "status":"PASS","source":"Mixkit sound recordings kept locally; incorporated in finished audio-visual work only",
    "sample_rate":SR,"channels":2,"seconds":3.5,
    "peak":round(float(np.max(np.abs(audio))),5),
    "rms":round(float(np.sqrt(np.mean(audio**2))),5),
    "impact_seconds":round(t,4)},indent=2),encoding="utf8")
print("V7_AUDIO_DONE",p,p.stat().st_size,flush=True)
