from pathlib import Path
import numpy as np,wave
root=Path.home()/"Downloads"/"slingshot_quality_proof"
sr=48000;N=sr*8
rng=np.random.default_rng(2417)
sound=np.zeros((N,2),dtype=np.float64)
def add(sec,w,volume=1.,pan=0):
 start=round(sec*sr);cnt=min(len(w),N-start)
 if start<0 or cnt<=0:return
 sound[start:start+cnt,0]+=w[:cnt]*volume*(1-pan)
 sound[start:start+cnt,1]+=w[:cnt]*volume*(1+pan)
def noise(sec,duration,volume,attack=.02,decay=.6,pan=0,lp=12):
 count=int(duration*sr);t=np.arange(count)/sr
 white=rng.standard_normal(count)
 smoothed=np.convolve(white,np.ones(lp)/lp,mode="same")
 env=(1-np.exp(-t/max(.002,attack)))*np.exp(-t/max(.02,decay))
 add(sec,smoothed*env,volume,pan)
def tone(sec,freq,seconds,volume,decay=7,pan=0):
 t=np.arange(int(seconds*sr))/sr
 a=(np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*freq*2.03*t))*np.exp(-decay*t)
 add(sec,a,volume,pan)
# Leather band tension creaks, elastic snap and dense steel flight.
for sec,v in [(0.3,.022),(.95,.024),(1.63,.043)]:
 tone(sec,157,.19,v,12)
 noise(sec,.23,.019,attack=.014,decay=.12,lp=33)
tone(1.995,115,.52,.19,decay=12)
tone(2.005,292,.23,.085,decay=18)
noise(2.01,.32,.15,attack=.002,decay=.07,lp=12)
noise(2.13,1.95,.17,attack=.20,decay=2.7,lp=27)
tone(2.28,182,1.4,.014,decay=1.9)
# Strike at 4.0s: low thud, ceramic sharp crack, shower of grit, gravity tails.
tone(4.0,62,1.4,.38,decay=11)
tone(4.01,230,.65,.14,decay=20)
tone(4.012,780,.32,.125,decay=23)
tone(4.024,1640,.28,.084,decay=39)
noise(4.00,1.8,.39,attack=.001,decay=.23,lp=6)
for k in range(85):
 sec=4.04+rng.random()*2.2
 freq=370+rng.random()*1250
 volume=.018+rng.random()*.025
 tone(sec,freq,.21,volume,decay=32,pan=float(rng.uniform(-.70,.70)))
 noise(sec,.24,.014,attack=.001,decay=.055,pan=float(rng.uniform(-.6,.6)),lp=8)
for sec in (4.52,5.14,5.73,6.42):
 tone(sec,99,.34,.06,decay=14,pan=float(rng.uniform(-.5,.5)))
noise(4.17,3.3,.11,attack=.08,decay=1.1,lp=52)
# Soft impact residual, stereo normalization.
sound[:4000]*=np.linspace(0,1,4000)[:,None]
sound[-9000:]*=np.linspace(1,0,9000)[:,None]
maxa=max(1,np.max(np.abs(sound))/.89)
sound=sound/maxa
out=root/"quality_proof_sound.wav"
with wave.open(str(out),"wb") as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
 w.writeframes((sound*32767).astype("<i2").tobytes())
print("SOUND_OK",out,out.stat().st_size,flush=True)
