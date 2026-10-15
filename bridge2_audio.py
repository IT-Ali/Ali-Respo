"""Audio for bridge v2 (~3s): quiet pad + pen-scratch while noting, a tick ding when the
field is recorded, and a soft pop as the sheet advances to the next question."""
import numpy as np, sys, wave
SR=44100; DUR=6.0; N=int(DUR*SR)
rng=np.random.default_rng(83)
buf=np.zeros(N+SR,np.float32)
def place(sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=len(buf) or len(sig)==0: return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]*g
t=np.arange(N)/SR; pad=np.zeros(N)
for f in [131,196,262,330]: pad+=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)
buf[:N]+=(pad/4.5).astype(np.float32)*0.045
def scratch(dur=0.5):
    n=int(SR*dur); y=np.zeros(n); k=0
    while k<n:
        L=min(int(SR*0.02),n-k); y[k:k+L]+=rng.standard_normal(L)*np.hanning(L)*0.5; k+=int(SR*(0.03+0.02*rng.random()))
    return (np.diff(y,prepend=0)*0.5).astype(np.float32)
def ding(f=1046,dur=0.4,dec=10):
    n=int(SR*dur); tt=np.arange(n)/SR; e=np.exp(-tt*dec)
    return ((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*10))*e*0.5).astype(np.float32)
def pop(f=600):
    n=int(SR*0.055); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt*55)+0.4*rng.standard_normal(n)*np.exp(-tt*120)).astype(np.float32)
place(scratch(1.9),0.6,g=0.10)
place(ding(880,dur=0.5),3.45,g=0.10)
place(pop(620),3.6,g=0.11)
buf=np.tanh(buf*1.0)*0.85; buf=buf[:N]; st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'bridge2_ambient.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
