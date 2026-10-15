"""Beat 13 FOCUS - held clips: DVT leg, PE chest, mobilising, clot-risk falls."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
import birth_recovery as BR
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT
WALL=(20,26,42)
SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; SCARF=BR.SCARF; GOWN=BR.GOWN; GOWN_H=BR.GOWN_H; GOWN_D=BR.GOWN_D
REDSKIN=(220,118,114); RED=(214,60,70); AMBER=(236,172,92); GREEN=(84,196,146); LUNG=(230,150,160); LUNG_D=(196,110,124)
TITLES=["LEG PAIN / SWELLING","BREATHLESS / CHEST PAIN","GET UP & WALK","CLOT RISK FALLS"]
PEARL=["ONE-SIDED LEG PAIN / SWELLING = DVT","BREATHLESS / CHEST PAIN = CLOT ON LUNG (PE)",
       "GET HER UP & WALKING EARLY","EARLY WALKING LOWERS THE CLOT RISK"]
PLAB=[f"POINT {i+1} / 4" for i in range(4)]
SUF=["1_dvt-leg","2_pe-chest","3_mobilise","4_clot-risk"]
CUE=["ANY LEG OR","CHEST SYMPTOMS?"]
K=1.9
def S(v): return int(round(v*K))

def walker(d,cx,fy,t):
    ph=4*math.pi*t/3.0; sw=int(S(6)*math.sin(ph)); asw=int(S(5)*math.sin(ph+math.pi)); hip=fy-S(32)
    d.line([(cx,hip),(cx-sw-S(2),fy)],fill=SKIN,width=3); d.line([(cx,hip),(cx+sw+S(2),fy)],fill=SKIN,width=3)
    rr(d,cx-sw-S(5),fy-S(2),cx-sw+S(2),fy+S(2),(60,66,86)); rr(d,cx+sw-S(2),fy-S(2),cx+sw+S(5),fy+S(2),(60,66,86))
    rr(d,cx-S(10),fy-S(58),cx+S(10),hip+S(4),GOWN); rr(d,cx-S(10),fy-S(58),cx+S(10),fy-S(55),GOWN_H)
    d.line([(cx-S(9),fy-S(54)),(cx-S(9)+asw,fy-S(34))],fill=SKIN,width=3); d.line([(cx+S(9),fy-S(54)),(cx+S(9)-asw,fy-S(34))],fill=SKIN,width=3)
    hy=fy-S(74)
    el(d,cx-S(9),hy-S(4),cx+S(9),hy+S(14),SCARF); el(d,cx-S(6),hy,cx+S(6),hy+S(13),SKIN); rr(d,cx-S(7),hy-S(2),cx+S(7),hy,SCARF)
    rr(d,cx-S(9),hy+S(6),cx-S(6),hy+S(16),SCARF); rr(d,cx+S(6),hy+S(6),cx+S(9),hy+S(16),SCARF); rr(d,cx-S(5),hy+S(13),cx+S(5),hy+S(18),SCARF)
    d.point((cx-S(3),hy+S(6)),fill=SKIN_D); d.point((cx+S(3),hy+S(6)),fill=SKIN_D)

def hero(d,s,t):
    if s==0:
        rr(d,CX-S(44),CY-S(26),CX+S(44),CY-S(12),GOWN); rr(d,CX-S(44),CY-S(26),CX+S(44),CY-S(23),GOWN_H)
        rr(d,CX-S(30),CY-S(12),CX-S(20),CY+S(26),SKIN); el(d,CX-S(34),CY+S(22),CX-S(16),CY+S(32),SKIN)
        TL.add(CX-S(40),CY+S(36),"NORMAL",(170,180,196),'small')
        rr(d,CX+S(6),CY-S(12),CX+S(18),CY+S(2),SKIN); el(d,CX,CY+S(0),CX+S(28),CY+S(30),REDSKIN); el(d,CX+S(2),CY+S(26),CX+S(20),CY+S(36),SKIN)
        d.line([(CX+S(34),CY+S(4)),(CX+S(42),CY+S(4))],fill=ACCENT); d.line([(CX+S(34),CY+S(28)),(CX+S(42),CY+S(28))],fill=ACCENT); d.line([(CX+S(42),CY+S(4)),(CX+S(42),CY+S(28))],fill=ACCENT)
        TL.add(CX+S(2),CY+S(40),"SWOLLEN / RED",RED,'small')
    elif s==1:
        el(d,CX-S(30),CY-S(24),CX-S(2),CY+S(24),LUNG); el(d,CX+S(2),CY-S(24),CX+S(30),CY+S(24),LUNG)
        el(d,CX-S(30),CY-S(24),CX-S(2),CY-S(12),LUNG_D); el(d,CX+S(2),CY-S(24),CX+S(30),CY-S(12),LUNG_D)
        rr(d,CX-S(2),CY-S(32),CX+S(2),CY-S(16),(196,110,124))
        el(d,CX+S(8),CY-S(6),CX+S(18),CY+S(4),(70,52,60)); el(d,CX+S(10),CY-S(4),CX+S(16),CY+S(2),(40,30,36))
        pz=0.5+0.5*math.sin(2*math.pi*4*t/12)
        for a in range(0,360,45):
            ar=math.radians(a); d.line([(CX+S(13)+int(S(6)*math.cos(ar)),CY-S(1)+int(S(6)*math.sin(ar))),(CX+S(13)+int((S(11)+pz*S(2))*math.cos(ar)),CY-S(1)+int((S(11)+pz*S(2))*math.sin(ar)))],fill=RED,width=2)
        for sx,sy in [(CX+S(34),CY-S(20)),(CX+S(42),CY-S(12)),(CX+S(36),CY-S(4))]: d.arc([sx,sy,sx+S(10),sy+S(6)],200,360,fill=(150,170,196),width=2)
        TL.add(CX+S(30),CY-S(32),"SOB",ACCENT,'small'); TL.add(CX-S(30),CY+S(30),"PLEURITIC PAIN",RED,'small')
    elif s==2:
        walker(d,CX,CY+S(38),t)
        for i in range(3): d.line([(CX-S(18)-i*S(5),CY+S(14)-i*S(6)),(CX-S(26)-i*S(5),CY+S(14)-i*S(6))],fill=(70,84,110),width=2)
    else:
        mx,yt,yb=CX-S(44),CY-S(34),CY+S(36); risk=0.22+0.05*math.sin(2*math.pi*2*t/12)
        rr(d,mx-S(3),yt-S(3),mx+S(15),yb+S(5),(34,40,58)); d.rectangle([mx-S(3),yt-S(3),mx+S(15),yb+S(5)],outline=(70,78,98))
        fillh=int((yb-yt)*risk); rr(d,mx,yb-fillh,mx+S(12),yb,GREEN)
        TL.add(mx-S(5),yt-S(12),"CLOT RISK",(206,180,186),'small')
        TL.add(mx+S(19),yt-S(2),"HIGH",(236,130,130),'small'); TL.add(mx+S(19),yb-S(8),"LOW",(120,210,160),'small')
        ax=mx+S(34); off=int((t/12*2%1)*S(20))
        for cy0 in (yt+S(4)+off-S(20),yt+S(4)+off):
            if yt<=cy0<=yb-S(6): d.line([(ax-S(5),cy0),(ax,cy0+S(6))],fill=ACCENT,width=2); d.line([(ax,cy0+S(6)),(ax+S(5),cy0)],fill=ACCENT,width=2)
        walker(d,CX+S(34),CY+S(38),t)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],4,CUE,"CLOTS & MOVING",f'D:/Ue/UE_5.8/obgyn_explainer/bf13_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat13_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"CLOTS & MOVING")
