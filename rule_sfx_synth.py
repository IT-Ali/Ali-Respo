"""Chill SFX bed for rule_headline_detail, timed to the 5-topic cycle. Slide-music lullaby
bed + soft music-box bell per headline, routing swooshes, gentle sparkles per chip, warm
resolve chord. Writes rule_headline_detail.wav."""
import numpy as np, wave
SR=44100; W=3.8; DUR=19.2; N=int(SR*DUR)
buf=np.zeros(N,np.float32)

def idx(t): return int(t*SR)
def addw(t0,w,amp=1.0):
    i=idx(t0); j=min(N,i+len(w))
    if i<0: w=w[-i:]; i=0
    buf[i:j]+=amp*w[:j-i]
def bell(freq,dur=0.8,atk=0.012):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.42))*np.clip(tt/atk,0,1)
    return (np.sin(2*np.pi*freq*tt)+0.35*np.sin(2*np.pi*2*freq*tt)+0.12*np.sin(2*np.pi*3*freq*tt))*e
def chord(freqs,dur=1.8,atk=0.05):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.5))*np.clip(tt/atk,0,1)
    return sum(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt) for f in freqs)/len(freqs)*e
def whoosh(dur=0.5):
    n=int(SR*dur); tt=np.arange(n)/SR
    no=np.random.default_rng(int(dur*1000)).normal(0,1,n)
    no=np.convolve(no,np.ones(220)/220,'same')
    return no*np.sin(np.pi*tt/dur)**2

HEADNOTE=[523.25,587.33,659.25,587.33,523.25]   # soft C-D-E-D-C across the 5 topics
ROWCNT=[6,5,1,4,5]                               # chips per topic (headline+extras, or details-only for route/CC)
for c in range(5):
    T0=c*W
    addw(T0+0.1, bell(HEADNOTE[c],0.95), 0.27)                 # headline bell
    addw(T0+0.6, whoosh(0.4), 0.12)                            # routing swoosh
    for i in range(ROWCNT[c]):
        addw(T0+1.1+i*0.3, bell(900+i*70,0.3), 0.05)           # chip sparkles
addw(18.1, chord([261.63,329.63,392.0],2.0), 0.18)            # warm resolve

# ---- slide music bed ----
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.2*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.5,0,1)
buf+=0.34*mus

pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/rule_headline_detail.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote rule_headline_detail.wav", round(len(pcm)/SR,2), "s")
