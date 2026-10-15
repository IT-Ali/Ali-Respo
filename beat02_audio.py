"""Gentle, seamless-looping ambient bed for Beat 2 (Site). Quiet (talk-over).
Warm pad throughout; home birds during the home half, soft monitor beep during hospital."""
import numpy as np, sys, wave
SR=44100; DUR=12.0; N=int(DUR*SR)
rng=np.random.default_rng(5)
buf=np.zeros(N+SR,np.float32)
def place(sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=len(buf) or len(sig)==0: return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]*g

# warm pad — integer freqs => phase aligns at 12s => seamless loop
t=np.arange(N)/SR
pad=np.zeros(N)
for f in [131,196,262,330]:
    pad+=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)
pad*=(1+0.06*np.sin(2*np.pi*0.25*t))   # 3 cycles over 12s -> seamless
buf[:N]+=(pad/len(pad)*0 + pad/4.5).astype(np.float32)*0.055

def bird():
    n=int(SR*0.14); tt=np.arange(n)/SR
    sweep=np.concatenate([np.linspace(2600,3300,n//2),np.linspace(3300,2400,n-n//2)])
    ph=2*np.pi*np.cumsum(sweep)/SR
    e=np.exp(-((tt-0.07)/0.05)**2)
    return (np.sin(ph)*e).astype(np.float32)
def beep(f=820):
    n=int(SR*0.07); tt=np.arange(n)/SR
    e=np.ones(n); a=int(0.003*SR); e[:a]=np.linspace(0,1,a); e[-int(0.05*SR):]=np.linspace(1,0,int(0.05*SR))
    return (np.sin(2*np.pi*f*tt)*e).astype(np.float32)

# home birds (home-dominant times, away from loop seam)
# (bird + hospital monitor beep both removed per request — just the warm pad bed)

# ---- UI SFX for the ask -> answer -> record exchange ----
def pop(f=560):
    n=int(SR*0.055); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt*55)+0.4*rng.standard_normal(n)*np.exp(-tt*120)).astype(np.float32)
def scratch(dur=1.1):
    n=int(SR*dur); y=np.zeros(n); k=0
    while k<n:
        g=int(SR*0.02); L=min(g,n-k)
        y[k:k+L]+=rng.standard_normal(L)*np.hanning(L)*0.5
        k+=int(SR*(0.03+0.02*rng.random()))
    return (np.diff(y,prepend=0)*0.5).astype(np.float32)
def ding(f=1046):
    n=int(SR*0.6); tt=np.arange(n)/SR; e=np.exp(-tt*7)
    return ((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*10))*e*0.5).astype(np.float32)
place(pop(600),0.3,g=0.13); place(pop(600),6.2,g=0.13)          # ask pops
place(pop(450),1.9,g=0.12); place(pop(450),7.7,g=0.12)          # answer pops
place(scratch(1.1),2.5,g=0.15); place(scratch(1.1),8.2,g=0.15)  # pen scratch while recording
place(ding(1046),3.7,g=0.11); place(ding(1046),9.4,g=0.11)      # confirm ding

buf=np.tanh(buf*1.0)*0.85
buf=buf[:N]; st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'beat02_ambient.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
