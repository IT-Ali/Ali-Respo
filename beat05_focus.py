"""Beat 5 FOCUS - held clips per episiotomy follow-up symptom (bleeding, perineal pain,
dysuria, haematuria). Object-based / modest."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(26,32,50)
RED=(214,60,70); BLOOD=(190,40,52); URINE=(240,214,120); PAIN=(236,120,120)
TITLES=["BLEEDING","PERINEAL PAIN","DYSURIA","HAEMATURIA"]
PEARL=["WATCH FOR EXCESS BLEEDING AT THE SITE","PAIN AT THE PERINEAL / EPISIOTOMY SITE",
       "DYSURIA - PAIN ON PASSING URINE","HAEMATURIA - BLOOD IN THE URINE"]
PLAB=[f"SYMPTOM {i+1} / 4" for i in range(4)]
SUF=["1_bleeding","2_perineal-pain","3_dysuria","4_haematuria"]
CUE=["ANY PROBLEMS SINCE","THE STITCHES?"]
K=1.8
def S(v): return int(round(v*K))

def starburst(d,cx,cy,r,col):
    for a in range(0,360,30):
        r2=r if (a//30)%2==0 else int(r*0.5)
        d.line([(cx,cy),(cx+int(r2*math.cos(math.radians(a))),cy+int(r2*math.sin(math.radians(a))))],fill=col,width=3)
    el(d,cx-3,cy-3,cx+3,cy+3,(255,255,255))

def hero(d,s,t):
    if s==0:
        rr(d,CX-S(26),CY-S(34),CX+S(26),CY+S(34),(238,240,246)); el(d,CX-S(23),CY-S(31),CX+S(23),CY+S(31),(248,250,252))
        el(d,CX-S(14),CY-S(8),CX+S(14),CY+S(18),BLOOD); el(d,CX-S(9),CY-S(4),CX+S(9),CY+S(12),RED)
        for i in range(3):
            dy=CY+S(36)+int((t*24+i*9)%S(34)); el(d,CX-S(10)+i*S(9),dy,CX-S(6)+i*S(9),dy+S(6),RED)
    elif s==1:
        starburst(d,CX,CY,S(30)+int(S(3)*math.sin(2*math.pi*4*t/12)),RED)
        tw=TL.w("OUCH!",'title'); TL.add(CX-tw/2,CY+S(36),"OUCH!",PAIN,'title')
    elif s==2:
        tx,ty=CX,CY-S(4)
        el(d,tx-S(16),ty+S(2),tx+S(16),ty+S(22),(224,230,238)); el(d,tx-S(12),ty+S(5),tx+S(12),ty+S(17),(150,170,195))
        rr(d,tx-S(12),ty-S(16),tx+S(12),ty+S(2),(214,222,230)); rr(d,tx-S(9),ty-S(13),tx+S(9),ty-S(6),(120,135,150))
        rr(d,tx-S(10),ty+S(22),tx+S(10),ty+S(28),(200,208,218))
        for i in range(2):
            yy=ty+S(3)+int((t*30+i*6)%S(11)); d.line([(tx,yy),(tx,yy+S(5))],fill=URINE,width=2)
        d.line([(tx+S(22),ty-S(8)),(tx+S(16),ty),(tx+S(24),ty),(tx+S(18),ty+S(10))],fill=RED,width=3)
    else:
        cx2,cy2=CX,CY-S(4)
        d.polygon([(cx2-S(16),cy2-S(12)),(cx2+S(16),cy2-S(12)),(cx2+S(12),cy2+S(22)),(cx2-S(12),cy2+S(22))],fill=(224,230,238))
        d.polygon([(cx2-S(12),cy2-S(2)),(cx2+S(12),cy2-S(2)),(cx2+S(9),cy2+S(20)),(cx2-S(9),cy2+S(20))],fill=RED)
        rr(d,cx2-S(16),cy2-S(12),cx2+S(16),cy2-S(10),(250,250,252))
        for i in range(2):
            dy=cy2+S(26)+int((t*22+i*8)%S(16)); el(d,cx2-S(5)+i*S(10),dy,cx2-S(2)+i*S(10),dy+S(5),RED)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],4,CUE,"EPISIOTOMY",f'D:/Ue/UE_5.8/obgyn_explainer/bf5_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat05_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"EPISIOTOMY")
