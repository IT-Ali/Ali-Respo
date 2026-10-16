"""WATERY DISCHARGE / ROM - FOCUS clips: each characterisation item BIG & centred, with the
examinee asking + a pearl. Items = the deck's watery-discharge row. Plays all 7 concepts in
sequence as one 1080p clip. Reuses the focus_kit scaffold."""
import math, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
import focus_kit as FK
import birth_recovery as BR
from birth_recovery import rr, el, GW, GH, SCALE
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT; FFMPEG=BR.FFMPEG; FPS=24
WALL=(20,26,34)
FLUID=(150,200,224); FLUID_D=(96,156,186); FLUID_H=(200,230,244)
MECON=(118,146,66); BLOOD=(176,34,48); AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146); SKIN=(242,201,170); INKDIM=(150,150,162)
TITLES=["GUSH or TRICKLE","WHAT COLOUR","ANY ODOUR?","ANY FEVER?","CONTRACTIONS?","ANY BLEEDING?","BABY MOVING?"]
PEARL=["SUDDEN GUSH vs SLOW TRICKLE  -  HOW MUCH, WHEN",
       "CLEAR (normal)  *  GREEN/MECONIUM -> FETAL DISTRESS  *  BLOOD-STAINED",
       "OFFENSIVE SMELL -> INFECTION (CHORIOAMNIONITIS)",
       "FEVER + OFFENSIVE LIQUOR -> CHORIOAMNIONITIS",
       "CONTRACTIONS?  -  IS SHE IN LABOUR",
       "ANY BLEEDING MIXED WITH THE FLUID?",
       "REDUCED / ABSENT MOVEMENTS  =  FETAL ALARM"]
PLAB=[f"QUESTION {i+1} / 7" for i in range(7)]
CUE=["TELL ME ABOUT","THE WATERS"]
IDENT="WATERY DISCHARGE (ROM)"
NIT=7; SEG=6.0
K=2.0
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:        # gush vs trickle
        for yy in range(CY-S(16),CY+S(14),S(3)): d.line([(CX-S(20),yy),(CX-S(12),yy+S(2))],fill=FLUID_H,width=2)
        el(d,CX-S(24),CY+S(12),CX-S(10),CY+S(20),FLUID)
        for yy in range(CY-S(12),CY+S(16),S(10)): el(d,CX+S(14),yy,CX+S(19),yy+S(5),FLUID)
        TL.add(CX-S(26),CY+S(24),"GUSH",(150,200,224),'small'); TL.add(CX+S(8),CY+S(24),"TRICKLE",(150,200,224),'small')
    elif s==1:      # colour - clear / green(meconium) / blood
        for i,(c,lab) in enumerate([(FLUID_H,"CLEAR"),(MECON,"MECONIUM"),(BLOOD,"BLOOD")]):
            dx=CX-S(26)+i*S(26)
            d.polygon([(dx,CY+S(10)),(dx-S(9),CY+S(1)),(dx,CY-S(14)),(dx+S(9),CY+S(1))],fill=c); el(d,dx-S(7),CY+S(1),dx+S(7),CY+S(9),c)
        TL.add(CX-S(30),CY+S(16),"CLEAR",(180,220,236),'small'); TL.add(CX-S(6),CY+S(16),"GREEN",(150,180,110),'small'); TL.add(CX+S(16),CY+S(16),"BLOOD",(230,150,150),'small')
    elif s==2:      # odour - nose + smell waves
        d.polygon([(CX-S(6),CY-S(14)),(CX-S(14),CY+S(8)),(CX+S(2),CY+S(8))],fill=SKIN); el(d,CX-S(12),CY+S(4),CX-S(4),CY+S(12),SKIN); el(d,CX,CY+S(4),CX+S(8),CY+S(12),SKIN)
        for ox in (S(10),S(18),S(26)):
            for yy in (CY-S(8),CY,CY+S(8)): d.arc([CX+ox,yy-S(5),CX+ox+S(10),yy+S(5)],250,110,fill=lerp_mec(t),width=2)
        TL.add(CX-S(14),CY+S(18),"OFFENSIVE?",(170,190,120),'small')
    elif s==3:      # thermometer (fever)
        rr(d,CX-S(4),CY-S(22),CX+S(4),CY+S(10),(238,240,246)); d.rectangle([CX-S(4),CY-S(22),CX+S(4),CY+S(10)],outline=INKDIM)
        el(d,CX-S(8),CY+S(6),CX+S(8),CY+S(22),RED); rr(d,CX-S(2),CY-S(18),CX+S(2),CY+S(10),RED)
        for hy in range(-16,8,4): d.line([(CX+S(6),CY+S(hy)),(CX+S(11),CY+S(hy))],fill=(210,120,120),width=2)
        TL.add(CX-S(14),CY+S(26),"TEMP UP?",(230,160,150),'small')
    elif s==4:      # contractions - wave graph
        pts=[]
        for i in range(S(28)):
            xx=CX-S(14)+i; ph=(i/S(28))*2*math.pi*2.5; yy=CY+S(4)-int(S(14)*max(0,math.sin(ph)))
            pts.append((xx,yy))
        d.line(pts,fill=AMBER,width=3); d.line([(CX-S(14),CY+S(6)),(CX+S(14),CY+S(6))],fill=(120,130,146),width=2)
        TL.add(CX-S(22),CY+S(16),"IN LABOUR?",(230,200,140),'small')
    elif s==5:      # bleeding - red droplet
        d.polygon([(CX,CY+S(14)),(CX-S(12),CY+S(1)),(CX,CY-S(18)),(CX+S(12),CY+S(1))],fill=BLOOD); el(d,CX-S(9),CY+S(1),CX+S(9),CY+S(11),BLOOD)
        TL.add(CX-S(24),CY+S(20),"MIXED WITH FLUID?",(230,150,150),'small')
    else:           # baby moving - fetus + motion arcs
        el(d,CX-S(16),CY-S(4),CX+S(6),CY+S(18),(246,210,182)); el(d,CX-S(22),CY-S(16),CX-S(6),CY,(246,210,182))
        el(d,CX-S(18),CY-S(11),CX-S(13),CY-S(6),(80,60,50)); d.line([(CX+S(4),CY+S(4)),(CX+S(14),CY-S(2))],fill=(246,210,182),width=3)
        for r in (22,28): d.arc([CX-r+S(4),CY-r,CX+r+S(4),CY+r],300,20,fill=GREEN,width=2)
        TL.add(CX-S(18),CY+S(24),"STILL KICKING?",(170,220,180),'small')

def lerp_mec(t):
    from birth_recovery import lerp
    return lerp(WALL,MECON,0.9)

def render(gs,t):
    return FK.frame(WALL,hero,gs,t,TITLES[gs],PEARL[gs],PLAB[gs],NIT,CUE,IDENT)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        Image.fromarray(render(s,tv)).save(f'/home/user/Ali-Respo/romf_{s}.png'); print("ok",s)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/rom_focus_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for s in range(NIT):
            for i in range(int(SEG*FPS)): p.stdin.write(render(s,i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
