"""Soft lullaby bed (pad chords + music-box melody) for birth_recovery. Writes WAV."""
import numpy as np, sys, wave
SR=44100; DUR=12.0; N=int(DUR*SR)
buf=np.zeros(N+SR,np.float32)
def place(sig,t,g=1.0):
    i=int(t*SR)
    if i<0: sig=sig[-i:]; i=0
    if i>=len(buf) or len(sig)==0: return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]*g

NOTE=dict(C3=130.81,E3=164.81,F3=174.61,G3=196.0,A3=220.0,B3=246.94,
 C4=261.63,D4=293.66,E4=329.63,F4=349.23,G4=392.0,A4=440.0,B4=493.88,
 C5=523.25,D5=587.33,E5=659.25,F5=698.46,G5=783.99,A5=880.0,C6=1046.5)

def pad(freqs,dur,fade=0.35):
    n=int(SR*dur); t=np.arange(n)/SR
    y=np.zeros(n)
    for f in freqs:
        y+=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)
    y*= (1+0.05*np.sin(2*np.pi*0.25*t))          # slow tremolo
    e=np.ones(n); a=int(fade*SR)
    e[:a]=np.linspace(0,1,a); e[-a:]=np.linspace(1,0,a)
    return (y/len(freqs)/1.3*e).astype(np.float32)

def box(f,dur=0.9,decay=3.6):
    n=int(SR*dur); t=np.arange(n)/SR; e=np.exp(-t*decay)
    y=(np.sin(2*np.pi*f*t)*e + 0.4*np.sin(2*np.pi*2*f*t)*np.exp(-t*decay*1.6)
       +0.15*np.sin(2*np.pi*3*f*t)*np.exp(-t*decay*2.2))
    a=int(SR*0.005); y[:a]*=np.linspace(0,1,a)
    return (y*0.5).astype(np.float32)

# ---- chord pad progression (2s each, warm & hopeful) ----
def ch(*names): return [NOTE[n] for n in names]
prog=[(0.0,ch('C3','C4','E4','G4')),
      (2.0,ch('G3','B3','D4','G4')),
      (4.0,ch('F3','A3','C4','F4')),
      (6.0,ch('C4','E4','G4','C3')),
      (8.0,ch('A3','C4','E4','A4')),
      (10.0,ch('F3','A3','C4','F4')),
      (10.9,ch('C3','C4','E4','G4'))]
for i,(t0,fr) in enumerate(prog):
    dur = (prog[i+1][0]-t0 if i+1<len(prog) else DUR-t0)+0.4
    # labour quieter, recovery fuller
    g=0.12 if t0<4.0 else (0.16 if t0<6.0 else 0.18)
    place(pad(fr,dur),t0,g=g)

# ---- music-box melody ----
mel=[(0.3,'E5',.8),(1.1,'D5',.8),
     (2.3,'G5',.6),(3.1,'D5',.9),
     (4.3,'C5',.7),(5.1,'A4',1.0),      # around the birth — tender
     (6.3,'E5',.7),(7.1,'G5',1.0),
     (8.3,'A4',.7),(9.1,'C5',1.0),
     (10.3,'G5',.6),(11.0,'C5',1.4)]    # resolve, held
for t0,nm,du in mel:
    g=0.14 if t0<4.0 else 0.18
    place(box(NOTE[nm],dur=du),t0,g=g)
# a little sparkle at the birth lift
for i,nm in enumerate(['C5','E5','G5','C6']):
    place(box(NOTE[nm],dur=1.0,decay=4.5),4.8+i*0.1,g=0.10)

peak=float(np.max(np.abs(buf))); print("pre peak",round(peak,3))
buf=np.tanh(buf*1.0)*0.85
buf=buf[:N]
st=np.stack([buf,buf],1)
out=sys.argv[1] if len(sys.argv)>1 else 'music.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print("wrote",out,"peak",round(float(np.max(np.abs(buf))),3))
