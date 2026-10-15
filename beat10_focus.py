"""Beat 10 FOCUS - held clips per post-op recovery system."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el, HEART
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(38,30,46)
GREEN=(84,196,146); AMBER=(236,172,92); URINE=(236,214,120); MILK=(236,240,246); TICK=(40,172,112); SKIN=(242,201,170)
TITLES=["CONSCIOUSNESS","NAUSEA / APPETITE","FLATUS / BOWELS","URINE / CATHETER","IV / PAIN RELIEF","MOBILISING","BREASTFEEDING","FEVER / TEMP"]
PEARL=["IS SHE FULLY AWAKE & ORIENTATED?","APPETITE BACK, NAUSEA / VOMITING SETTLING",
       "GUT WORKING - FLATUS FIRST, THEN BOWELS","URINE OUTPUT GOOD / CATHETER REMOVED",
       "PAIN RELIEF WORKING + IV FLUIDS RUNNING","EARLY MOBILISATION LOWERS CLOT RISK",
       "IS BREASTFEEDING ESTABLISHED?","FEVER MAY MEAN INFECTION - CHECK"]
PLAB=[f"SYSTEM {i+1} / 8" for i in range(8)]
SUF=["1_consciousness","2_appetite","3_bowels","4_urine","5_pain-relief","6_mobilising","7_breastfeeding","8_fever"]
CUE=["HOW IS HER","RECOVERY GOING?"]
K=2.4
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        el(d,CX-S(10),CY-S(5),CX+S(10),CY+S(5),(246,248,252)); el(d,CX-S(4),CY-S(4),CX+S(4),CY+S(4),(40,60,96)); el(d,CX-S(2),CY-S(2),CX+S(2),CY+S(2),(10,16,28))
        for a in (-60,-30,0,30,60):
            ar=math.radians(a-90); d.line([(CX+int(S(13)*math.cos(ar)),CY+int(S(13)*math.sin(ar))),(CX+int(S(18)*math.cos(ar)),CY+int(S(18)*math.sin(ar)))],fill=AMBER,width=2)
    elif s==1:
        el(d,CX-S(16),CY+S(2),CX+S(16),CY+S(9),(228,232,240)); el(d,CX-S(11),CY+S(2),CX+S(11),CY+S(7),(200,206,216))
        d.line([(CX-S(20),CY-S(6)),(CX-S(20),CY+S(6))],fill=(210,214,224),width=2); d.line([(CX+S(20),CY-S(6)),(CX+S(20),CY+S(6))],fill=(210,214,224),width=2)
        for dx in (-5,2):
            yo=int(S(2)*math.sin(2*math.pi*2*t/12+dx))
            d.line([(CX+S(dx),CY-S(10)+yo),(CX+S(dx)+S(3),CY-S(15)+yo)],fill=(180,190,206),width=2)
    elif s==2:
        el(d,CX-S(16),CY-S(14),CX+S(16),CY+S(16),SKIN)
        d.arc([CX-S(10),CY-S(8),CX+S(2),CY+S(4)],0,360,fill=(196,120,110),width=3); d.arc([CX-S(2),CY-S(2),CX+S(10),CY+S(10)],0,360,fill=(196,120,110),width=3)
    elif s==3:
        rr(d,CX-S(11),CY-S(14),CX+S(11),CY+S(16),(236,232,190)); rr(d,CX-S(9),CY+S(1),CX+S(9),CY+S(14),URINE); d.line([(CX,CY-S(20)),(CX,CY-S(14))],fill=URINE,width=2)
        rr(d,CX-S(5),CY-S(22),CX+S(5),CY-S(18),(210,200,120))
    elif s==4:
        rr(d,CX-S(16),CY-S(16),CX-S(2),CY+S(4),(150,214,180)); rr(d,CX-S(16),CY-S(16),CX-S(2),CY-S(12),(120,190,160)); d.line([(CX-S(9),CY+S(4)),(CX-S(9),CY+S(18))],fill=(180,226,238),width=2)
        el(d,CX+S(2),CY-S(2),CX+S(16),CY+S(12),(238,240,246)); d.line([(CX+S(9),CY),(CX+S(9),CY+S(10))],fill=(200,120,130),width=2); d.line([(CX+S(4),CY+S(5)),(CX+S(14),CY+S(5))],fill=(200,120,130),width=2)
    elif s==5:
        ph=4*math.pi*t/3.0; sw=int(S(5)*math.sin(ph)); hip=CY+S(2)
        el(d,CX-S(5),CY-S(20),CX+S(5),CY-S(10),SKIN); rr(d,CX-S(5),CY-S(21),CX+S(5),CY-S(17),(58,44,46))   # skin head + hair
        rr(d,CX-S(3),CY-S(10),CX+S(3),hip,(86,148,198))                                                     # gown body
        d.line([(CX,hip),(CX-sw-S(3),CY+S(18))],fill=SKIN,width=3); d.line([(CX,hip),(CX+sw+S(3),CY+S(18))],fill=SKIN,width=3)
        d.line([(CX-S(1),CY-S(7)),(CX-S(8),CY-S(1))],fill=SKIN,width=2); d.line([(CX+S(1),CY-S(7)),(CX+S(8),CY-S(11))],fill=SKIN,width=2)
    elif s==6:
        el(d,CX-S(12),CY-S(4),CX+S(4),CY+S(12),(244,214,204)); el(d,CX-S(8),CY-S(9),CX+S(2),CY+S(1),SKIN)
        el(d,CX+S(6),CY-S(3),CX+S(11),CY+S(3),MILK)
        r=S(5); hy=CY-S(10)
        el(d,CX+S(6),hy-r//2,CX+S(10),hy+r//3,HEART); el(d,CX+S(10),hy-r//2,CX+S(14),hy+r//3,HEART); d.polygon([(CX+S(6),hy),(CX+S(14),hy),(CX+S(10),hy+r)],fill=HEART)
    else:
        rr(d,CX-S(3),CY-S(16),CX+S(3),CY+S(8),(236,240,246)); el(d,CX-S(6),CY+S(5),CX+S(6),CY+S(17),GREEN); rr(d,CX-S(2),CY-S(8),CX+S(2),CY+S(11),GREEN)
        for yy in (-10,-5,0): d.line([(CX+S(5),CY+S(yy)),(CX+S(11),CY+S(yy))],fill=GREEN,width=2)
    # reassuring tick (bottom-right of icon)
    d.line([(CX+S(16),CY+S(20)),(CX+S(20),CY+S(25))],fill=TICK,width=3); d.line([(CX+S(20),CY+S(25)),(CX+S(28),CY+S(13))],fill=TICK,width=3)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],8,CUE,"POST-OP RECOVERY",f'D:/Ue/UE_5.8/obgyn_explainer/bf10_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat10_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"POST-OP RECOVERY")
