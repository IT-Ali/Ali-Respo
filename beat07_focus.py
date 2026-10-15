"""Beat 7 FOCUS - held clips per C-section pre-op step."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(26,32,50)
RED=(214,60,70); BLOODC=(190,40,52); ECG=(78,230,150); IVC=(120,132,150); BAG=(150,214,180); URINE=(236,214,120); HEART=(236,96,120)
TITLES=["ELECTIVE vs EMERGENCY","FETAL HEART (CTG)","INVESTIGATIONS","BLOOD CROSSMATCH","IV ACCESS","URINARY CATHETER"]
PEARL=["ELECTIVE (PLANNED) vs EMERGENCY - AND WHY","FETAL MOVEMENT & FETAL HEART CHECKED",
       "BLOODS / INVESTIGATIONS SENT","BLOOD CROSSMATCHED FOR THE OPERATION",
       "IV FLUIDS / DRUGS RUNNING","URINARY CATHETER INSERTED"]
PLAB=[f"STEP {i+1} / 6" for i in range(6)]
SUF=["1_elective-emergency","2_fetal-heart","3_investigations","4_crossmatch","5_iv-access","6_catheter"]
CUE=["WHAT WAS DONE","BEFORE THE OPERATION?"]
K=1.8
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        # ELECTIVE (calendar, calm) vs EMERGENCY (alarm, red)
        lx=CX-S(34)
        rr(d,lx-S(22),CY-S(20),lx+S(22),CY+S(18),(70,110,180)); rr(d,lx-S(22),CY-S(20),lx+S(22),CY-S(13),(110,150,210))
        for gx in range(-14,15,8):
            for gy in range(-4,13,8): el(d,lx+S(gx)-2,CY+S(gy)-2,lx+S(gx)+2,CY+S(gy)+2,(235,240,250))
        TL.add(lx-TL.w("ELECTIVE",'small')/2,CY+S(24),"ELECTIVE",(150,180,230),'small')
        TL.add(CX-S(2),CY-S(4),"vs",(150,160,180),'small')
        rx=CX+S(34)
        d.polygon([(rx-S(22),CY+S(16)),(rx+S(22),CY+S(16)),(rx,CY-S(20))],fill=RED); TL.add(rx-3,CY-S(2),"!",(255,255,255),'title')
        TL.add(rx-TL.w("EMERGENCY",'small')/2,CY+S(24),"EMERGENCY",(236,140,150),'small')
    elif s==1:
        bx,by,bw=CX-S(52),CY+S(4),S(104); base=by+S(6)
        rr(d,bx,by-S(30),bx+bw,by+S(20),(16,22,36)); rr(d,bx,by-S(30),bx+bw,by-S(28),(40,52,74))
        prev=None; beats=6
        for i in range(bw):
            ph=((i/bw)*beats+(t/12.0)*beats)%1.0; yy=base
            if 0.46<ph<0.50: yy=base-S(16)        # R spike
            elif 0.50<=ph<0.54: yy=base+S(5)       # S dip
            elif 0.42<ph<0.46: yy=base-S(3)        # Q
            elif 0.58<ph<0.64: yy=base-S(4)        # T wave
            if prev is not None:
                a,b=sorted((prev,yy)); d.line([(bx+i,a),(bx+i,b)],fill=ECG)
            d.point((bx+i,yy),fill=ECG); prev=yy
        TL.add(CX-TL.w("140 bpm",'body')/2,by-S(28),"140 bpm",ECG,'body')
        bp=0.5+0.5*math.sin(2*math.pi*4*t/12); r=S(7)+int(S(2)*bp); hy=by+S(36)
        el(d,CX-r,hy-r//2,CX-1,hy+r//3,HEART); el(d,CX+1,hy-r//2,CX+r,hy+r//3,HEART)
        d.polygon([(CX-r,hy),(CX+r,hy),(CX,hy+r)],fill=HEART)
    elif s==2:
        rr(d,CX-S(30),CY+S(20),CX+S(30),CY+S(28),(90,100,124))
        for i,c in enumerate([(200,80,90),(120,160,210),(220,200,110)]):
            tx=CX-S(24)+i*S(24)
            rr(d,tx-S(5),CY-S(22),tx+S(5),CY+S(22),(220,228,236)); rr(d,tx-S(5),CY+S(6),tx+S(5),CY+S(22),c); rr(d,tx-S(6),CY-S(24),tx+S(6),CY-S(20),(240,244,250))
    elif s==3:
        rr(d,CX-S(16),CY-S(28),CX+S(16),CY+S(14),BLOODC); rr(d,CX-S(16),CY-S(28),CX+S(16),CY-S(22),(150,30,42))
        d.line([(CX,CY+S(14)),(CX,CY+S(38))],fill=IVC,width=2)
        TL.add(CX-TL.w("O+",'title')/2,CY-S(14),"O+",(255,235,235),'title')
    elif s==4:
        px=CX-S(30)
        rr(d,px-1,CY-S(34),px+1,CY+S(40),IVC); rr(d,px-S(10),CY-S(34),px+S(8),CY-S(14),BAG); rr(d,px-S(9),CY-S(20),px+S(7),CY-S(14),(120,190,160))
        dp=(t%1.4)/1.4; dy=CY-S(14)+int(dp*S(10))
        if dp<0.7: d.line([(px,dy),(px,dy+2)],fill=(180,226,238))
        d.line([(px,CY-S(14)),(CX+S(18),CY+S(10)),(CX+S(34),CY+S(16))],fill=BAG,width=2)
        el(d,CX+S(30),CY+S(12),CX+S(44),CY+S(22),(242,201,170)); rr(d,CX+S(36),CY+S(14),CX+S(40),CY+S(18),(150,170,185))
        TL.add(CX+S(8),CY+S(26),"CANNULA",(150,170,190),'small')
    else:
        d.line([(CX-S(30),CY-S(10)),(CX+S(10),CY+S(14)),(CX+S(24),CY+S(26))],fill=URINE,width=3)
        rr(d,CX+S(18),CY+S(24),CX+S(42),CY+S(52),(236,228,160)); rr(d,CX+S(18),CY+S(24),CX+S(42),CY+S(28),(210,200,120))
        rr(d,CX+S(22),CY+S(34),CX+S(38),CY+S(50),URINE)
        TL.add(CX-S(40),CY-S(22),"CATHETER",(190,200,214),'small')

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],6,CUE,"C-SECTION PRE-OP",f'D:/Ue/UE_5.8/obgyn_explainer/bf7_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat07_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"C-SECTION PRE-OP")
