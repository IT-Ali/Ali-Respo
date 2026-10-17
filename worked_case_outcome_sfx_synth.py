"""Chill SFX bed for worked_case_outcome. Lullaby bed + soft bell as the examinee asks each outcome
question, a warm note as the mother answers, light pen ticks while the row records, a confirm chime
per row, warm resolve at the end. Writes worked_case_outcome.wav."""
import numpy as np, wave
SR=44100; INTRO=3.0; SD=4.5; NS=8; DUR=44.5; N=int(SR*DUR)
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
def tick(freq=1150,dur=0.04):
    n=int(SR*dur); tt=np.arange(n)/SR
    return np.sin(2*np.pi*freq*tt)*np.exp(-tt/(dur*0.3))
def chord(freqs,dur=2.2,atk=0.05):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.5))*np.clip(tt/atk,0,1)
    return sum(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt) for f in freqs)/len(freqs)*e

ASK=[523.25,587.33,659.25,587.33,523.25,493.88,440.0,493.88]
for gi in range(NS):
    T0=INTRO+gi*SD
    addw(T0+0.1, bell(ASK[gi],0.95), 0.20)            # examinee asks
    addw(T0+1.3, bell(392.0,0.8), 0.14)               # mother answers (warm lower note)
    for k in range(8): addw(T0+1.95+k*0.16, tick(), 0.028)  # pen ticks while recording
    addw(T0+3.35, bell(784.0,0.5), 0.10)              # row confirm
addw(INTRO+NS*SD, chord([261.63,329.63,392.0],2.4), 0.18)   # outro resolve (warm, baby healthy)
addw(INTRO+NS*SD+0.4, bell(523.25,1.3), 0.12)

with wave.open('/home/user/Ali-Respo/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.4*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.6,0,1)
buf+=0.32*mus
pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('/home/user/Ali-Respo/worked_case_outcome.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote worked_case_outcome.wav", round(len(pcm)/SR,2),"s")
