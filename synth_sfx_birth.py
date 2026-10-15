"""Procedural SFX for birth_recovery, aligned to the animation timeline. Writes WAV."""
import numpy as np, sys, wave
SR=44100; DUR=12.0
rng=np.random.default_rng(11)
N=int(DUR*SR)+SR
buf=np.zeros(N,np.float32)
def place(sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=N or len(sig)==0: return
    j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]*g
def env(n,a,d):
    e=np.ones(n); at=int(a*SR); dt=int(d*SR)
    if at>0: e[:at]=np.linspace(0,1,at)
    if dt>0: e[-dt:]=np.linspace(1,0,dt)
    return e
def tone(f,dur,a=0.004,d=None):
    n=int(SR*dur); t=np.arange(n)/SR
    if d is None: d=dur*0.6
    return (np.sin(2*np.pi*f*t)*env(n,a,d)).astype(np.float32)
def bell(f,dur=0.6,decay=6.0):
    n=int(SR*dur); t=np.arange(n)/SR; e=np.exp(-t*decay)
    y=(np.sin(2*np.pi*f*t)*e+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*decay*1.7)
       +0.18*np.sin(2*np.pi*3*f*t)*np.exp(-t*decay*2.4))
    a=int(SR*0.004); y[:a]*=np.linspace(0,1,a); return (y*0.5).astype(np.float32)
def beep(f,dur=0.07):
    n=int(SR*dur); t=np.arange(n)/SR
    y=np.sin(2*np.pi*f*t)*env(n,0.003,0.05)
    return y.astype(np.float32)

# ---- monitor beep (rate shifts labour->recovery), through whole clip ----
t=0.0; prev=0.0
while t<DUR-0.1:
    rate=2.0 if t>5.0 else 2.6
    ph=(t*rate)%1.0
    if ph<prev:  # new beat
        f=950 if t<5.0 else 820
        place(beep(f),t,g=0.12 if t<5.0 else 0.10)
    prev=ph; t+=1/SR*96

# ---- contraction low swells (labour) ----
tt=0.0
while tt<4.6:
    ctr=max(0.0, np.sin(2*np.pi*(tt+0.5)/2.1))**3
    tt+=1/SR*256
# place swells at contraction peaks: peaks near where sin((t+0.5)/2.1*2pi)=1 -> (t+0.5)/2.1 = .25 + k -> t = 2.1*.25 -0.5 +2.1k = 0.025+2.1k
for k in range(3):
    pk=0.025+2.1*k
    if pk<4.4:
        dur=1.3; n=int(SR*dur); t=np.arange(n)/SR
        e=(np.sin(np.pi*t/dur))**2            # swell in/out
        low=(np.sin(2*np.pi*72*t)+0.6*np.sin(2*np.pi*110*t))*e
        nz=rng.standard_normal(n)*e*0.25
        place((low*0.5+nz).astype(np.float32), pk-0.5, g=0.16)

# ---- birth chime (~4.9): warm ascending bell arpeggio ----
for i,f in enumerate([523.25,659.25,783.99,1046.5]):
    place(bell(f,dur=1.4,decay=4.0), 4.8+i*0.12, g=0.42)
# soft shimmer up
place((np.sin(2*np.pi*np.cumsum(np.linspace(700,1600,int(SR*0.5)))/SR)*env(int(SR*0.5),0.01,0.4)).astype(np.float32),4.85,g=0.10)

# ---- recovery warm pad (fade in ~5.5 -> end) ----
ps=5.3; pn=int((DUR-ps)*SR); pt=np.arange(pn)/SR
pad=np.zeros(pn,np.float32)
for f in [196.0,261.63,329.63]:   # G3 C4 E4 warm triad
    pad+=np.sin(2*np.pi*f*pt)*(1+0.02*np.sin(2*np.pi*0.2*pt))
pad*= np.clip((pt/2.0),0,1)        # fade in over 2s
pad*= np.clip((DUR-ps-pt)/1.5,0,1) # gentle tail
place((pad/3).astype(np.float32), ps, g=0.09)

# ---- heart twinkles (recovery, ~6.0-11.5) ----
tw=6.0
while tw<11.4:
    f=rng.choice([1318.5,1567.98,2093.0,2637.0])
    place(bell(f,dur=0.5,decay=9.0), tw, g=0.12)
    tw+=0.55+rng.random()*0.5

# ---- soft resolve near the end ----
place(bell(523.25,dur=1.6,decay=3.0),10.8,g=0.3)
place(bell(783.99,dur=1.6,decay=3.0),10.95,g=0.26)

# ---- master limiter ----
peak=float(np.max(np.abs(buf))); print("pre-limit peak",round(peak,3))
buf=np.tanh(buf*1.05)*0.9
buf=buf[:int(DUR*SR)]
st=np.stack([buf,buf],axis=1)
out=sys.argv[1] if len(sys.argv)>1 else 'birth_sfx.wav'
pcm=(np.clip(st,-1,1)*32767).astype('<i2')
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
