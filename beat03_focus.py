"""Beat 3 FOCUS - held clips: route of delivery (vaginal / assisted / caesarean)."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
import birth_recovery as BR
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(26,32,50)
SKIN=BR.SKIN; CROSSR=(214,70,80)
GREEN=(84,196,146); AMBER=(236,172,92); BLUE=(126,164,232)
COL=[GREEN,AMBER,BLUE]
TITLES=["VAGINAL BIRTH","ASSISTED DELIVERY","CAESAREAN"]
PEARL=["VAGINAL - SPONTANEOUS, NO INSTRUMENTS","ASSISTED - FORCEPS OR VACUUM USED","CAESAREAN - SURGICAL BIRTH"]
PLAB=[f"ROUTE {i+1} / 3" for i in range(3)]
SUF=["1_vaginal","2_assisted","3_caesarean"]
CUE=["NORMAL BIRTH OR","CAESAREAN?"]
K=2.6
def S(v): return int(round(v*K))

def hero(d,s,t):
    col=COL[s]; cx,cy=CX,CY
    if s==0:
        d.arc([cx-S(14),cy-S(16),cx+S(14),cy+S(12)],200,340,fill=col,width=3); d.arc([cx-S(14),cy-S(14),cx+S(14),cy+S(14)],200,340,fill=col,width=3)
        el(d,cx-S(6),cy-S(8),cx+S(6),cy+S(4),SKIN)
        bob=int(S(3)*(0.5+0.5*math.sin(2*math.pi*2*t/12)))
        d.line([(cx,cy+S(6)+bob),(cx,cy+S(18)+bob)],fill=col,width=3); d.line([(cx-S(5),cy+S(13)+bob),(cx,cy+S(18)+bob)],fill=col,width=3); d.line([(cx+S(5),cy+S(13)+bob),(cx,cy+S(18)+bob)],fill=col,width=3)
    elif s==1:
        STEEL=(206,214,228)
        lx=cx-S(22); rx=cx+S(22)
        # FORCEPS (left): baby head cradled by two curved blades + crossed handles
        el(d,lx-S(6),cy-S(3),lx+S(6),cy+S(9),SKIN)
        d.arc([lx-S(13),cy-S(7),lx-S(1),cy+S(11)],90,270,fill=STEEL,width=2)
        d.arc([lx+S(1),cy-S(7),lx+S(13),cy+S(11)],270,90,fill=STEEL,width=2)
        d.line([(lx-S(7),cy+S(9)),(lx+S(2),cy+S(20))],fill=STEEL,width=2)
        d.line([(lx+S(7),cy+S(9)),(lx-S(2),cy+S(20))],fill=STEEL,width=2)
        TL.add(lx-TL.w("FORCEPS",'small')/2,cy+S(24),"FORCEPS",col,'small')
        # VACUUM (right): baby head + suction cup + handle
        el(d,rx-S(6),cy,rx+S(6),cy+S(12),SKIN)
        d.polygon([(rx-S(8),cy),(rx+S(8),cy),(rx+S(5),cy-S(7)),(rx-S(5),cy-S(7))],fill=col)
        d.line([(rx,cy-S(7)),(rx,cy-S(18))],fill=col,width=3); el(d,rx-S(4),cy-S(22),rx+S(4),cy-S(16),col)
        TL.add(rx-TL.w("VACUUM",'small')/2,cy+S(24),"VACUUM",col,'small')
    else:
        el(d,cx-S(16),cy+S(2),cx+S(16),cy+S(18),(230,196,176))
        for dx in range(-11,12,5): rr(d,cx+S(dx),cy+S(7),cx+S(dx)+S(2),cy+S(9),CROSSR)
        el(d,cx-S(5),cy-S(14),cx+S(5),cy-S(4),SKIN); d.line([(cx,cy-S(4)),(cx,cy+S(2))],fill=col,width=2)
        d.line([(cx-S(10),cy-S(10)),(cx+S(10),cy-S(10))],fill=col,width=2)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],3,CUE,"ROUTE OF DELIVERY",f'D:/Ue/UE_5.8/obgyn_explainer/bf3_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat03_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"ROUTE OF DELIVERY")
