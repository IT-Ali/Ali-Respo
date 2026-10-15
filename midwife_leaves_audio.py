"""Audio for the closer: warm pad + a soft goodbye twinkle, footsteps as the midwife
walks out (2.2-6.4s), then a gentle settle. Calm, speak-over-able."""
import numpy as np, sys, wave
SR=44100; DUR=12.0; N=int(DUR*SR)
rng=np.random.default_rng(73)
buf=np.zeros(N+SR,np.float32)
def place(sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=len(buf) or len(sig)==0: return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]*g
t=np.arange(N)/SR; pad=np.zeros(N)
for f in [131,196,262,330]: pad+=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)
pad*=(1+0.06*np.sin(2*np.pi*0.25*t))
buf[:N]+=(pad/4.5).astype(np.float32)*0.055
def step(f=120):
    n=int(SR*0.1); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt*42)+0.3*rng.standard_normal(n)*np.exp(-tt*80)).astype(np.float32)
def ding(f=1046,dur=0.5,dec=8):
    n=int(SR*dur); tt=np.arange(n)/SR; e=np.exp(-tt*dec)
    return ((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*10))*e*0.5).astype(np.float32)
place(ding(1046,dur=0.6),0.3,g=0.07)          # goodbye twinkle
tt=2.25
while tt<6.45:
    place(step(118+int(rng.integers(0,10))),tt,g=0.10); tt+=0.42
place(ding(784,dur=0.7,dec=6),7.0,g=0.06)     # gentle settle
buf=np.tanh(buf*1.0)*0.85; buf=buf[:N]; st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'midwife_leaves_ambient.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
