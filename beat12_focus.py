"""Beat 12 FOCUS - held clips per wound sign. Modest: skin band + incision only."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
import birth_recovery as BR
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT
WALL=(22,28,42)
SKIN=BR.SKIN; SKIN_H=(250,216,188); SKIN_D=BR.SKIN_D; INC=(150,66,66); STAPLE=(176,184,202)
REDSKIN=(220,118,114); RED=(214,60,70); AMBER=(236,172,92); PUS=(236,216,120); BLOOD=(176,34,48)
TITLES=["PAIN / TENDER","REDNESS / WARMTH","SWELLING","DISCHARGE / PUS","GAPING (BREAKDOWN)","BLEEDING / OOZE"]
PEARL=["IS THE WOUND TENDER TO TOUCH?","RED, WARM EDGES = INFLAMMATION",
       "SWELLING / FIRM LUMP (HAEMATOMA?)","PUS OR DISCHARGE = WOUND INFECTION",
       "WOUND EDGES SEPARATING = BREAKDOWN","FRESH BLEEDING OR OOZING FROM WOUND"]
PLAB=[f"SIGN {i+1} / 6" for i in range(6)]
SUF=["1_tender","2_redness","3_swelling","4_discharge","5_gaping","6_bleeding"]
CUE=["HOW IS THE","WOUND HEALING?"]
K=2.0
def S(v): return int(round(v*K))

def hero(d,s,t):
    sx0,sx1,sy0,sy1=CX-S(58),CX+S(58),CY-S(22),CY+S(22); iy=CY; ix0,ix1=CX-S(50),CX+S(50)
    if s==1: pass
    rr(d,sx0,sy0,sx1,sy1,SKIN); rr(d,sx0,sy0,sx1,sy0+S(3),SKIN_H); rr(d,sx0,sy1-S(3),sx1,sy1,SKIN_D)
    if s==1:
        rr(d,sx0+S(4),iy-S(13),sx1-S(4),iy+S(13),REDSKIN); rr(d,sx0+S(4),iy-S(13),sx1-S(4),iy-S(10),(236,150,146))
    if s==2:
        for yy in range(iy-S(16),iy+S(17)):
            w=int(S(54)*math.cos((yy-iy)/S(17)*math.pi/2)); rr(d,CX-w,yy,CX+w,yy,(250,222,196))
        for ax in (CX-S(34),CX+S(34)):
            d.line([(ax,iy-S(18)),(ax,iy-S(26))],fill=ACCENT,width=2); d.polygon([(ax,iy-S(28)),(ax-S(4),iy-S(23)),(ax+S(4),iy-S(23))],fill=ACCENT)
            d.line([(ax,iy+S(18)),(ax,iy+S(26))],fill=ACCENT,width=2); d.polygon([(ax,iy+S(28)),(ax-S(4),iy+S(23)),(ax+S(4),iy+S(23))],fill=ACCENT)
    if s==4:
        d.line([(ix0,iy),(CX-S(16),iy)],fill=INC,width=3); d.line([(CX+S(16),iy),(ix1,iy)],fill=INC,width=3)
        el(d,CX-S(16),iy-S(7),CX+S(16),iy+S(7),(120,50,54)); el(d,CX-S(12),iy-S(5),CX+S(12),iy+S(5),(150,64,66))
        for sxp in list(range(ix0+S(6),CX-S(18),S(11)))+list(range(CX+S(18),ix1,S(11))): d.line([(sxp,iy-S(6)),(sxp,iy+S(6))],fill=STAPLE)
        d.line([(CX-S(6),iy-S(12)),(CX-S(12),iy-S(17))],fill=AMBER,width=2); d.line([(CX+S(6),iy-S(12)),(CX+S(12),iy-S(17))],fill=AMBER,width=2)
    else:
        d.line([(ix0,iy),(ix1,iy)],fill=INC,width=3)
        for sxp in range(ix0+S(6),ix1,S(11)): d.line([(sxp,iy-S(6)),(sxp,iy+S(6))],fill=STAPLE)
    if s==0:
        for a in range(0,360,45):
            ar=math.radians(a); d.line([(CX+int(S(8)*math.cos(ar)),iy+int(S(8)*math.sin(ar))),(CX+int(S(18)*math.cos(ar)),iy+int(S(18)*math.sin(ar)))],fill=AMBER,width=3)
    elif s==3:
        el(d,CX+S(16),iy-S(3),CX+S(24),iy+S(4),PUS); el(d,CX+S(18),iy+S(3),CX+S(23),iy+S(11),PUS); el(d,CX+S(19),iy+S(10),CX+S(22),iy+S(17),PUS)
    elif s==5:
        rr(d,CX+S(8),iy-S(13),CX+S(44),iy+S(11),(238,240,246)); rr(d,CX+S(8),iy-S(13),CX+S(44),iy-S(11),(214,218,228))
        el(d,CX+S(18),iy-S(3),CX+S(36),iy+S(6),BLOOD); el(d,CX+S(24),iy+S(2),CX+S(32),iy+S(9),(150,24,38))
        el(d,CX-S(40),iy-S(2),CX-S(26),iy+S(5),BLOOD)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],6,CUE,"C-SECTION WOUND",f'D:/Ue/UE_5.8/obgyn_explainer/bf12_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat12_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"C-SECTION WOUND")
