"""Beat 11 FOCUS - held clips per PPH question. Object-based / modest."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT
WALL=(28,22,34)
BLOOD=(176,34,48); BLOOD_D=(140,24,38); BLOOD_H=(206,60,74); AMBER=(236,172,92); RED=(214,60,70); GLASS=(150,160,178); URINE=(236,214,120)
TITLES=["HEAVY BLEEDING","CLOTS / FLOODING","PRIMARY vs SECONDARY","FELT FAINT / DIZZY","TREATMENT GIVEN","PREVIOUS PPH"]
PEARL=["SOAKING PADS FAST OR FLOODING = RED FLAG","BIG CLOTS / FLOODING MEAN HEAVY LOSS",
       "PRIMARY <24H  vs  SECONDARY (DAYS-6 WKS)","DIZZY / FAINT = SIGNS OF BLOOD LOSS",
       "UTEROTONICS / TRANSFUSION / THEATRE?","PPH BEFORE RAISES THE RISK NEXT TIME"]
PLAB=[f"QUESTION {i+1} / 6" for i in range(6)]
SUF=["1_heavy-bleeding","2_clots","3_primary-secondary","4_faint","5_treatment","6_previous"]
CUE=["DID YOU BLEED","HEAVILY AFTER?"]
K=2.0
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        x0,x1,yt,yb=CX-S(22),CX+S(22),CY-S(26),CY+S(44)
        rr(d,x0-2,yt,x0,yb+2,GLASS); rr(d,x1,yt,x1+2,yb+2,GLASS); rr(d,x0-2,yb,x1+2,yb+2,GLASS)
        rr(d,x0,yt,x1,yb,(24,20,30)); lvl=yb-int((yb-yt)*0.70); wob=S(1.2)*math.sin(2*math.pi*t/4.0)
        for xx in range(x0,x1):
            sy=lvl+int(wob*math.sin((xx-x0)*0.3)); rr(d,xx,sy,xx,yb,BLOOD)
        rr(d,x0,lvl,x1,lvl+1,BLOOD_H)
        for frac,lab in [(0.25,"250"),(0.5,"500"),(0.75,"750"),(1.0,"1000")]:
            ty=yb-int((yb-yt)*frac); d.line([(x1,ty),(x1+S(4),ty)],fill=GLASS); TL.add(x1+S(6),ty-4,lab,(180,176,186),'small')
        thr=yb-int((yb-yt)*0.5); d.line([(x0-S(6),thr),(x1,thr)],fill=(236,110,110)); TL.add(x0-S(30),thr-4,"PPH",(236,130,130),'small')
    elif s==1:
        el(d,CX-S(22),CY+S(2),CX+S(22),CY+S(16),(210,216,226)); el(d,CX-S(19),CY+S(4),CX+S(19),CY+S(12),(34,40,56))
        for bx,by,r in [(CX-S(8),CY+S(8),S(5)),(CX+S(4),CY+S(9),S(4)),(CX+S(12),CY+S(7),S(4))]: el(d,bx-r,by-r,bx+r,by+r,BLOOD_D)
        for i in range(3): el(d,CX-S(6)+i*S(6),CY-S(10)-i,CX-S(3)+i*S(6),CY-S(5)-i,BLOOD)
    elif s==2:
        d.line([(CX-S(34),CY+S(4)),(CX+S(34),CY+S(4))],fill=(180,190,206),width=3)
        d.line([(CX-S(4),CY-S(8)),(CX-S(4),CY+S(16))],fill=RED,width=3)
        el(d,CX-S(34),CY-S(22),CX-S(16),CY-S(4),(222,226,234)); el(d,CX-S(32),CY-S(20),CX-S(18),CY-S(6),(30,40,60))
        d.line([(CX-S(25),CY-S(13)),(CX-S(25),CY-S(18))],fill=(230,234,240),width=2); d.line([(CX-S(25),CY-S(13)),(CX-S(20),CY-S(13))],fill=ACCENT,width=2)
        rr(d,CX+S(14),CY-S(22),CX+S(34),CY-S(4),(236,240,246)); rr(d,CX+S(14),CY-S(22),CX+S(34),CY-S(18),RED)
        TL.add(CX-S(34),CY+S(10),"PRIMARY <24h",(170,180,196),'small'); TL.add(CX+S(4),CY+S(10),"SECONDARY",(170,180,196),'small')
    elif s==3:
        el(d,CX-S(16),CY-S(14),CX+S(16),CY+S(16),(242,201,170))
        d.line([(CX-S(10),CY-S(2)),(CX-S(4),CY-S(2))],fill=(120,80,60),width=2); d.line([(CX+S(4),CY-S(2)),(CX+S(10),CY-S(2))],fill=(120,80,60),width=2)
        rr(d,CX-S(4),CY+S(6),CX+S(4),CY+S(10),(180,120,100))
        for sx,sy in [(CX-S(22),CY-S(18)),(CX+S(20),CY-S(16)),(CX+S(24),CY+S(4)),(CX-S(24),CY+S(6))]:
            d.line([(sx-S(3),sy),(sx+S(3),sy)],fill=AMBER,width=2); d.line([(sx,sy-S(3)),(sx,sy+S(3))],fill=AMBER,width=2)
    elif s==4:
        rr(d,CX-S(30),CY-S(20),CX-S(10),CY+S(12),BLOOD); rr(d,CX-S(30),CY-S(20),CX-S(10),CY-S(14),BLOOD_D); d.line([(CX-S(20),CY+S(12)),(CX-S(20),CY+S(24))],fill=(180,226,238),width=2)
        rr(d,CX+S(2),CY-S(4),CX+S(30),CY+S(4),(238,240,246)); rr(d,CX+S(2),CY-S(4),CX+S(16),CY+S(4),(200,214,230))
        d.line([(CX+S(30),CY),(CX+S(40),CY)],fill=GLASS,width=2); rr(d,CX-S(4),CY-S(2),CX+S(2),CY+S(2),GLASS)
        TL.add(CX-S(30),CY+S(18),"UTEROTONIC / BLOOD",(206,186,192),'small')
    else:
        rr(d,CX-S(22),CY-S(22),CX+S(8),CY+S(18),(238,240,246))
        for ly in range(-14,15,8): d.line([(CX-S(16),CY+S(ly)),(CX-S(2),CY+S(ly))],fill=(176,186,200),width=2)
        el(d,CX-S(12),CY-S(12),CX-S(4),CY-S(4),BLOOD)
        d.arc([CX+S(4),CY-S(14),CX+S(34),CY+S(16)],20,320,fill=AMBER,width=3); d.polygon([(CX+S(30),CY-S(12)),(CX+S(38),CY-S(16)),(CX+S(34),CY-S(4))],fill=AMBER)
        TL.add(CX+S(6),CY+S(20),"RISK AGAIN",AMBER,'small')

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],6,CUE,"POST-PARTUM BLEEDING",f'D:/Ue/UE_5.8/obgyn_explainer/bf11_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat11_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"POST-PARTUM BLEEDING")
