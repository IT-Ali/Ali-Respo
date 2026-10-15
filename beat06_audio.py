"""Ambient + UI SFX for Beat 4 (Effort & Duration). Warm pad + per-phase ask/answer/
record SFX + a gauge-swing swoosh. Seamless 12s loop, quiet for talk-over."""
import numpy as np, sys, wave
SR=44100; DUR=12.0; N=int(DUR*SR)
rng=np.random.default_rng(14)
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

def pop(f=560):
    n=int(SR*0.055); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt*55)+0.4*rng.standard_normal(n)*np.exp(-tt*120)).astype(np.float32)
def scratch(dur=1.0):
    n=int(SR*dur); y=np.zeros(n); k=0
    while k<n:
        L=min(int(SR*0.02),n-k); y[k:k+L]+=rng.standard_normal(L)*np.hanning(L)*0.5
        k+=int(SR*(0.03+0.02*rng.random()))
    return (np.diff(y,prepend=0)*0.5).astype(np.float32)
def ding(f=1046,dur=0.6,dec=7):
    n=int(SR*dur); tt=np.arange(n)/SR; e=np.exp(-tt*dec)
    return ((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*10))*e*0.5).astype(np.float32)
def swoosh(dur=0.55):
    n=int(SR*dur); sweep=np.linspace(300,1300,n); ph=2*np.pi*np.cumsum(sweep)/SR
    return ((0.5*np.sin(ph)+0.5*rng.standard_normal(n))*np.hanning(n)*0.3).astype(np.float32)

# 2 phases at 0 and 6: ask, gauge swing, answer settle, record scratch, confirm
DINGF=[880,660]
for p in range(2):
    t0=p*6.0
    place(pop(600),t0+0.12,g=0.12)
    place(swoosh(0.55),t0+0.9,g=0.55)
    place(pop(470),t0+1.0,g=0.10); place(ding(DINGF[p]),t0+1.0,g=0.11)
    place(scratch(1.0),t0+1.6,g=0.14)
    place(ding(1046),t0+2.9,g=0.10)

buf=np.tanh(buf*1.0)*0.85; buf=buf[:N]; st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'beat04_ambient.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
