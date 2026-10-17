"""Chill SFX bed for worked_hopi (continuous HOPI with sub-phase pauses). Lullaby bed + soft
bell at each section header, pen ticks while writing, a soft chime at each HOPI sub-phase
boundary, warm resolve at the end. Writes worked_hopi_outcome.wav."""
import numpy as np, wave
import worked_hopi_outcome as WH
SR=44100; DUR=WH.DUR; SCHED=WH.sched; CPS=WH.CPS; HOPI_TB=WH.HOPI_TB; CHUNKS=WH.CHUNKS; SUBPAUSE=WH.SUBPAUSE
N=int(SR*DUR); buf=np.zeros(N,np.float32)

def idx(t): return int(t*SR)
def addw(t0,w,amp=1.0):
    i=idx(t0); j=min(N,i+len(w))
    if i<0: w=w[-i:]; i=0
    buf[i:j]+=amp*w[:j-i]
def bell(freq,dur=0.8,atk=0.012):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.42))*np.clip(tt/atk,0,1)
    return (np.sin(2*np.pi*freq*tt)+0.35*np.sin(2*np.pi*2*freq*tt)+0.12*np.sin(2*np.pi*3*freq*tt))*e
def tick(freq=1150,dur=0.04):
    n=int(SR*dur); tt=np.arange(n)/SR; return np.sin(2*np.pi*freq*tt)*np.exp(-tt/(dur*0.3))
def chord(freqs,dur=2.6,atk=0.05):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.5))*np.clip(tt/atk,0,1)
    return sum(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt) for f in freqs)/len(freqs)*e

ASK=[523.25,587.33,659.25]
# section header bells + body ticks (demographic, complaint linear)
for i,(th,tb,td) in enumerate(SCHED):
    addw(th, bell(ASK[i%len(ASK)],0.9), 0.17)
    if i<2:
        tt=tb+0.2
        while tt<td: addw(tt, tick(), 0.022); tt+=0.18
# HOPI: ticks per chunk (respect pauses) + soft chime at each sub boundary
t=HOPI_TB
for ci,chunk in enumerate(CHUNKS):
    wt=chunk/CPS; tt=t+0.1
    while tt<t+wt: addw(tt, tick(), 0.022); tt+=0.18
    t+=wt
    if ci<len(CHUNKS)-1:
        addw(t, bell(784.0,0.35), 0.08); addw(t+0.17, bell(987.77,0.45), 0.07)  # section-change cue (rising)
        t+=SUBPAUSE
addw(max(0,DUR-3.8), chord([261.63,329.63,392.0]), 0.17)   # warm resolve

with wave.open('/home/user/Ali-Respo/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.4*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.6,0,1)
buf+=0.32*mus

pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('/home/user/Ali-Respo/worked_hopi_outcome.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote worked_hopi_outcome.wav", round(len(pcm)/SR,2), "s")
