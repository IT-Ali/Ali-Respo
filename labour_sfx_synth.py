"""Chill SFX bed for labour_history_map, timed to the build. Slide-music lullaby bed +
soft music-box bells (pills), gentle sparkles (items), soft swooshes, warm resolve chord.
Writes labour_history_map.wav."""
import numpy as np, wave
SR=44100; DUR=14.0; N=int(SR*DUR)
buf=np.zeros(N,np.float32)

def idx(t): return int(t*SR)
def addw(t0,w,amp=1.0):
    i=idx(t0); j=min(N,i+len(w))
    if i<0: w=w[-i:]; i=0
    buf[i:j]+=amp*w[:j-i]

def bell(freq,dur=0.8,atk=0.012):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.42))*np.clip(tt/atk,0,1)
    s=np.sin(2*np.pi*freq*tt)+0.35*np.sin(2*np.pi*2*freq*tt)+0.12*np.sin(2*np.pi*3*freq*tt)
    return s*e

def chord(freqs,dur=1.8,atk=0.05):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.5))*np.clip(tt/atk,0,1)
    s=sum(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt) for f in freqs)/len(freqs)
    return s*e

def whoosh(dur=0.5):
    n=int(SR*dur); tt=np.arange(n)/SR
    no=np.random.default_rng(int(dur*1000)).normal(0,1,n)
    no=np.convolve(no,np.ones(220)/220,'same')              # soft lowpass
    return no*np.sin(np.pi*tt/dur)**2

# ---- events (all soft / consonant, C-major-ish to sit under the lullaby) ----
for t0,f in [(0.9,523.25),(1.4,659.25),(2.4,783.99)]: addw(t0,bell(f,0.9),0.30)   # pill bells C-E-G
for t0 in [4.0,5.6,7.2,8.8,10.4,12.0]: addw(t0,bell(880.0,0.35),0.06)            # reason cycles (soft)
addw(3.2,whoosh(0.4),0.14)                                                        # arrow
addw(3.6,whoosh(0.55),0.16)                                                       # HOPI swell
for p0,cnt in [(4.0,6),(5.3,8),(6.6,8)]:                                          # item sparkles (gentle run)
    for i in range(cnt): addw(p0+0.25+i*0.14, bell(784+i*70,0.3), 0.045)
addw(9.1,chord([261.63,329.63,392.0],2.2),0.20)                                   # warm resolve chord
addw(9.2,whoosh(0.6),0.10)                                                         # footer settle
addw(9.55,bell(659.25,0.6),0.15)                                                   # end cue: gentle
addw(9.95,bell(783.99,1.1),0.19)                                                   #   two-note rise E->G

# ---- slide music bed (lullaby, looped, downmixed) ----
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.2*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.5,0,1)    # fade in/out
buf+=0.34*mus

# ---- normalize ----
pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/labour_history_map.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote labour_history_map.wav", round(len(pcm)/SR,2), "s")
