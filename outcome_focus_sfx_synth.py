"""Chill bed for outcome_focus (11 concepts x 6s = 66s). Lullaby bed + soft bell as each
concept comes up, gentle resolve chord at the end. Writes outcome_focus.wav."""
import numpy as np, wave
SR=44100; NIT=11; SEG=6.0; DUR=NIT*SEG; N=int(SR*DUR); buf=np.zeros(N,np.float32)
def idx(t): return int(t*SR)
def addw(t0,w,amp=1.0):
    i=idx(t0); j=min(N,i+len(w))
    if i<0: w=w[-i:]; i=0
    buf[i:j]+=amp*w[:j-i]
def bell(freq,dur=0.9,atk=0.012):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.42))*np.clip(tt/atk,0,1)
    return (np.sin(2*np.pi*freq*tt)+0.35*np.sin(2*np.pi*2*freq*tt)+0.12*np.sin(2*np.pi*3*freq*tt))*e
def chord(freqs,dur=2.4,atk=0.05):
    n=int(SR*dur); tt=np.arange(n)/SR
    e=np.exp(-tt/(dur*0.5))*np.clip(tt/atk,0,1)
    return sum(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt) for f in freqs)/len(freqs)*e
NOTE=[523.25,587.33,659.25,698.46, 587.33,659.25,698.46,783.99, 523.25,587.33,659.25]
for s in range(NIT):
    addw(s*SEG+0.08, bell(NOTE[s],1.0), 0.20)
addw(DUR-2.4, chord([261.63,329.63,392.0],2.2), 0.16)
with wave.open('/home/user/Ali-Respo/music.wav') as m:
    raw=np.frombuffer(m.readframes(m.getnframes()),np.int16).astype(np.float32)/32768.0
    if m.getnchannels()==2: raw=raw.reshape(-1,2).mean(axis=1)
mus=np.tile(raw,int(np.ceil(N/len(raw))))[:N]
mus*=np.clip(np.arange(N)/(1.4*SR),0,1)*np.clip((DUR-np.arange(N)/SR)/1.4,0,1)
buf+=0.32*mus
pk=np.max(np.abs(buf)); buf=buf/pk*0.92 if pk>0 else buf
pcm=(buf*32767).astype(np.int16)
with wave.open('/home/user/Ali-Respo/outcome_focus.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote outcome_focus.wav", round(len(pcm)/SR,2),"s")
