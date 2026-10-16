"""ANTEPARTUM BLEEDING - FOCUS clips: each characterisation item shown BIG & centred (explain
in detail), with the examinee asking + a pearl. Items = the deck's vaginal-bleeding row. Plays
all 7 concepts in sequence as one 1080p clip. Reuses the focus_kit scaffold (FK.frame)."""
import math, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
import focus_kit as FK
import birth_recovery as BR
from birth_recovery import rr, el, GW, GH, SCALE
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT; FFMPEG=BR.FFMPEG; FPS=24
WALL=(28,22,34)
BLOOD=(176,34,48); BLOOD_D=(120,20,32); BLOOD_H=(214,60,74); DARKB=(96,24,34)
AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146); GLASS=(150,160,178); SKIN=(242,201,170); INKDIM=(150,150,162)
TITLES=["ONSET / AMOUNT","WHAT COLOUR","ANY CLOTS?","PAINLESS or PAINFUL","DIZZY / FAINT","ANY FEVER?","BABY MOVING?"]
PEARL=["HOW IT STARTED, HOW MUCH  -  DROPS vs FLOODING",
       "FRESH RED (PRAEVIA)  vs  DARK (ABRUPTION)",
       "CLOTS / TISSUE  =  HEAVIER LOSS",
       "PAINLESS -> PRAEVIA   *   PAINFUL / RIGID -> ABRUPTION",
       "DIZZY / FAINT  =  SIGNS OF BLOOD LOSS",
       "FEVER -> THINK INFECTION (e.g. SEPTIC)",
       "REDUCED / ABSENT MOVEMENTS  =  FETAL ALARM"]
PLAB=[f"QUESTION {i+1} / 7" for i in range(7)]
CUE=["TELL ME ABOUT","THE BLEEDING"]
IDENT="VAGINAL BLEEDING"
NIT=7; SEG=6.0
K=2.0
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:        # onset / amount - soaked pads
        for i in range(3):
            px=CX-S(30)+i*S(21); rr(d,px,CY-S(16),px+S(15),CY+S(18),(238,240,246))
            el(d,px+S(2),CY-S(6),px+S(13),CY+S(13),BLOOD)
        TL.add(CX-S(30),CY+S(22),"PADS SOAKED?",(206,186,192),'small')
    elif s==1:      # colour - fresh red vs dark droplet
        d.polygon([(CX-S(16),CY+S(14)),(CX-S(26),CY+S(2)),(CX-S(16),CY-S(16)),(CX-S(6),CY+S(2))],fill=BLOOD_H); el(d,CX-S(22),CY+S(2),CX-S(10),CY+S(12),BLOOD_H)
        d.polygon([(CX+S(16),CY+S(14)),(CX+S(6),CY+S(2)),(CX+S(16),CY-S(16)),(CX+S(26),CY+S(2))],fill=DARKB); el(d,CX+S(10),CY+S(2),CX+S(22),CY+S(12),DARKB)
        TL.add(CX-S(26),CY+S(20),"FRESH RED",(230,150,150),'small'); TL.add(CX+S(4),CY+S(20),"DARK / OLD",(150,120,130),'small')
    elif s==2:      # clots in a kidney dish
        el(d,CX-S(26),CY+S(2),CX+S(26),CY+S(18),(210,216,226)); el(d,CX-S(22),CY+S(4),CX+S(22),CY+S(14),(34,40,56))
        for bx,by,r in [(CX-S(10),CY+S(10),S(6)),(CX+S(4),CY+S(11),S(5)),(CX+S(14),CY+S(9),S(4))]: el(d,bx-r,by-r,bx+r,by+r,BLOOD_D)
        for i in range(3): el(d,CX-S(6)+i*S(7),CY-S(12)-i,CX-S(2)+i*S(7),CY-S(6)-i,BLOOD)
    elif s==3:      # painless vs painful bellies
        el(d,CX-S(30),CY-S(14),CX-S(4),CY+S(16),SKIN); d.arc([CX-S(24),CY-S(2),CX-S(10),CY+S(8)],20,160,fill=(120,80,60),width=2)
        el(d,CX+S(4),CY-S(14),CX+S(30),CY+S(16),(240,180,150))
        for a in range(0,360,40):
            ar=math.radians(a); d.line([(CX+S(17),CY+S(1)),(CX+S(17)+int(S(14)*math.cos(ar)),CY+S(1)+int(S(14)*math.sin(ar)))],fill=RED,width=2)
        TL.add(CX-S(28),CY+S(20),"PAINLESS",(150,210,170),'small'); TL.add(CX+S(6),CY+S(20),"PAINFUL",(236,150,150),'small')
    elif s==4:      # dizzy / faint head
        el(d,CX-S(16),CY-S(14),CX+S(16),CY+S(16),SKIN)
        d.line([(CX-S(10),CY-S(2)),(CX-S(4),CY-S(2))],fill=(120,80,60),width=2); d.line([(CX+S(4),CY-S(2)),(CX+S(10),CY-S(2))],fill=(120,80,60),width=2)
        rr(d,CX-S(4),CY+S(6),CX+S(4),CY+S(10),(180,120,100))
        for sx,sy in [(CX-S(22),CY-S(18)),(CX+S(20),CY-S(16)),(CX+S(24),CY+S(4)),(CX-S(24),CY+S(6))]:
            d.line([(sx-S(3),sy),(sx+S(3),sy)],fill=AMBER,width=2); d.line([(sx,sy-S(3)),(sx,sy+S(3))],fill=AMBER,width=2)
    elif s==5:      # thermometer (fever)
        rr(d,CX-S(4),CY-S(22),CX+S(4),CY+S(10),(238,240,246)); d.rectangle([CX-S(4),CY-S(22),CX+S(4),CY+S(10)],outline=INKDIM)
        el(d,CX-S(8),CY+S(6),CX+S(8),CY+S(22),RED); rr(d,CX-S(2),CY-S(18),CX+S(2),CY+S(10),RED)
        for hy in range(-16,8,4): d.line([(CX+S(6),CY+S(hy)),(CX+S(11),CY+S(hy))],fill=(210,120,120),width=2)
        TL.add(CX-S(14),CY+S(26),"TEMP UP?",(230,160,150),'small')
    else:           # baby moving - curled fetus + motion arcs
        el(d,CX-S(16),CY-S(4),CX+S(6),CY+S(18),(246,210,182))        # body
        el(d,CX-S(22),CY-S(16),CX-S(6),CY,(246,210,182))            # head
        el(d,CX-S(18),CY-S(11),CX-S(13),CY-S(6),(80,60,50))         # eye
        d.line([(CX+S(4),CY+S(4)),(CX+S(14),CY-S(2))],fill=(246,210,182),width=3)  # limb (kick)
        for r in (22,28): d.arc([CX-r+S(4),CY-r,CX+r+S(4),CY+r],300,20,fill=GREEN,width=2)
        TL.add(CX-S(18),CY+S(24),"STILL KICKING?",(170,220,180),'small')

def render(gs,t):
    return FK.frame(WALL,hero,gs,t,TITLES[gs],PEARL[gs],PLAB[gs],NIT,CUE,IDENT)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        Image.fromarray(render(s,tv)).save(f'/home/user/Ali-Respo/apbf_{s}.png'); print("ok",s)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/apb_bleeding_focus_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for s in range(NIT):
            for i in range(int(SEG*FPS)): p.stdin.write(render(s,i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
