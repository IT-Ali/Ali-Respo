"""Beat 2 FOCUS - held clips: HOME vs HOSPITAL delivery."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el, HEART
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(30,28,44)
TITLES=["HOME DELIVERY","HOSPITAL DELIVERY"]
PEARL=["HOME - LESS MONITORING / SUPPORT ON HAND","HOSPITAL - IMMEDIATE SUPPORT & MONITORING"]
PLAB=["SITE 1 / 2","SITE 2 / 2"]
SUF=["1_home","2_hospital"]
CUE=["WHERE DID YOU","DELIVER?"]
K=2.0
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        rr(d,CX-S(28),CY-S(4),CX+S(28),CY+S(34),(196,150,120)); rr(d,CX-S(28),CY-S(4),CX+S(28),CY+S(0),(214,170,138))
        d.polygon([(CX-S(36),CY-S(2)),(CX+S(36),CY-S(2)),(CX,CY-S(36))],fill=(150,90,80))
        rr(d,CX-S(7),CY+S(14),CX+S(7),CY+S(34),(110,76,60)); el(d,CX+S(4),CY+S(24),CX+S(6),CY+S(26),(230,210,120))
        rr(d,CX-S(22),CY+S(2),CX-S(9),CY+S(14),(246,214,120)); rr(d,CX+S(9),CY+S(2),CX+S(22),CY+S(14),(246,214,120))
        d.line([(CX-S(15),CY+S(2)),(CX-S(15),CY+S(14))],fill=(176,120,70)); d.line([(CX+S(16),CY+S(2)),(CX+S(16),CY+S(14))],fill=(176,120,70))
        r=S(5)+int(S(1)*math.sin(2*math.pi*2*t/12)); hy=CY-S(16)
        el(d,CX-r,hy-r//2,CX-1,hy+r//3,HEART); el(d,CX+1,hy-r//2,CX+r,hy+r//3,HEART); d.polygon([(CX-r,hy),(CX+r,hy),(CX,hy+r)],fill=HEART)
    else:
        rr(d,CX-S(32),CY-S(28),CX+S(32),CY+S(34),(150,160,180)); rr(d,CX-S(32),CY-S(28),CX+S(32),CY-S(24),(176,186,206))
        for rx in range(-24,25,16):
            for ry in range(-18,30,14): rr(d,CX+S(rx),CY+S(ry),CX+S(rx)+S(8),CY+S(ry)+S(8),(96,150,196))
        rr(d,CX-S(8),CY+S(22),CX+S(8),CY+S(34),(120,86,70))
        rr(d,CX-S(10),CY-S(24),CX+S(10),CY-S(8),(236,240,246)); rr(d,CX-S(3),CY-S(22),CX+S(3),CY-S(10),(214,70,80)); rr(d,CX-S(7),CY-S(18),CX+S(7),CY-S(14),(214,70,80))
        px=CX-S(44); rr(d,px-1,CY-S(16),px+1,CY+S(30),(120,132,150)); rr(d,px-S(8),CY-S(16),px+S(6),CY-S(2),(150,214,180))

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],2,CUE,"SITE OF DELIVERY",f'D:/Ue/UE_5.8/obgyn_explainer/bf2_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat02_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"SITE OF DELIVERY")
