"""Chill SFX bed for rom_montage (14s, 7 items cycling every 2s). Lullaby bed + soft bell as
each characterisation item comes up + gentle tick as it records, warm resolve. Writes rom_montage.wav."""
import numpy as np, wave
SR=44100; DUR=14.0; NIT=7; STEP=2.0; N=int(SR*DUR); buf=np.zeros(N,np.float32)
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
NOTE=[523.25,587.33,659.25,587.33,523.25,493.88,440.0]
for s in range(NIT):
    T0=s*STEP
    addw(T0+0.05, bell(NOTE[s],0.9), 0.17)        # item comes up
    addw(T0+1.1, tick(), 0.05)                    # records (tick)
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.2*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.2,0,1)
buf+=0.32*mus
pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('D:/Ue/UE_5.8/obgyn_explainer/rom_montage.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote rom_montage.wav", round(len(pcm)/SR,2),"s")
