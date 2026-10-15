"""Audio for the walk-in intro: warm pad + footstep taps while he walks (0.6-4.8s) +
a soft arrival chime + a bubble pop when the speech bubble appears."""
import numpy as np, sys, wave
SR=44100; DUR=12.0; N=int(DUR*SR)
rng=np.random.default_rng(71)
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
def ding(f=1046,dur=0.45,dec=9):
    n=int(SR*dur); tt=np.arange(n)/SR; e=np.exp(-tt*dec)
    return ((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*10))*e*0.5).astype(np.float32)
def pop(f=560):
    n=int(SR*0.055); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt*55)+0.4*rng.standard_normal(n)*np.exp(-tt*120)).astype(np.float32)
tt=0.6
while tt<4.85:
    place(step(118+int(rng.integers(0,10))),tt,g=0.11); tt+=0.42
place(ding(900,dur=0.5),5.05,g=0.09)
place(pop(600),5.25,g=0.11)
buf=np.tanh(buf*1.0)*0.85; buf=buf[:N]; st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'intro_ambient.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
