"""Beat 6 FOCUS - held clips: GENERAL (asleep + mask) vs SPINAL/EPIDURAL (awake, numb).
Carries the '! DON'T ASSUME GENERAL' reminder on both."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
import birth_recovery as BR
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(26,32,50)
MASKC=(150,205,215); TUBE=(120,135,150); NEEDLE=(210,218,230); NUMB=(120,170,235)
SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; SCARF=BR.SCARF; GOWN=BR.GOWN; DARK=BR.DARK
TITLES=["GENERAL ANAESTHETIC","SPINAL / EPIDURAL"]
PEARL=["ASLEEP VIA MASK / TUBE - FULLY UNCONSCIOUS","AWAKE, NUMB FROM THE WAIST DOWN"]
PLAB=["TYPE 1 / 2","TYPE 2 / 2"]
SUF=["1_general","2_spinal"]
CUE=["WHAT ANAESTHESIA","WAS USED?"]
K=1.9
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        rr(d,CX-S(44),CY+S(12),CX+S(44),CY+S(28),(206,222,236)); rr(d,CX-S(44),CY+S(25),CX+S(44),CY+S(28),(184,200,216))
        hx,hy=CX-S(14),CY-S(2)
        el(d,hx-S(12),hy-S(11),hx+S(12),hy+S(9),SCARF); el(d,hx-S(8),hy-S(7),hx+S(8),hy+S(7),SKIN); rr(d,hx-S(9),hy-S(9),hx+S(9),hy-S(6),SCARF)
        rr(d,hx-S(9),hy-S(3),hx-S(6),hy+S(8),SCARF); rr(d,hx+S(6),hy-S(3),hx+S(9),hy+S(8),SCARF)
        d.line([(hx-S(5),hy+S(1)),(hx-S(1),hy+S(1))],fill=SKIN_D,width=2); d.line([(hx+S(1),hy+S(1)),(hx+S(5),hy+S(1))],fill=SKIN_D,width=2)
        el(d,hx+S(2),hy+S(4),hx+S(16),hy+S(16),MASKC); el(d,hx+S(2),hy+S(4),hx+S(16),hy+S(7),(190,225,232))
        d.line([(hx+S(16),hy+S(12)),(hx+S(34),hy+S(26))],fill=TUBE,width=2)
        rr(d,hx+S(32),hy+S(24),hx+S(48),hy+S(40),(176,214,196)); rr(d,hx+S(32),hy+S(24),hx+S(48),hy+S(28),(150,200,170))
        for i in range(3):
            zt=(t*0.5+i*0.34)%1.0; TL.add(hx+S(6)+i*S(5),hy-S(12)-zt*S(24),"z",(200,214,235),'body' if i==0 else 'small')
    else:
        ox,oy=CX,CY+S(6)
        rr(d,CX-S(50),oy+S(8),CX+S(50),oy+S(16),(96,108,130)); rr(d,CX-S(50),oy+S(16),CX+S(50),oy+S(24),(70,80,100))
        rr(d,ox-S(18),oy+S(8),ox-S(8),oy+S(38),NUMB); rr(d,ox-S(20),oy+S(36),ox-S(4),oy+S(44),(90,120,60))
        d.polygon([(ox-S(16),oy+S(8)),(ox+S(12),oy+S(8)),(ox+S(6),oy-S(26)),(ox-S(8),oy-S(30)),(ox-S(20),oy-S(12))],fill=GOWN)
        rr(d,ox+S(4),oy-S(24),ox+S(12),oy+S(2),(70,78,134))
        rr(d,ox-S(26),oy-S(18),ox-S(12),oy-S(4),(206,222,236))
        d.line([(ox-S(8),oy-S(26)),(ox-S(20),oy-S(12))],fill=SKIN,width=3)
        hx,hy=ox-S(12),oy-S(38)
        el(d,hx-S(9),hy-S(2),hx+S(9),hy+S(14),SCARF); el(d,hx-S(6),hy+S(2),hx+S(6),hy+S(13),SKIN); rr(d,hx-S(7),hy,hx+S(7),hy+S(2),SCARF)
        rr(d,hx-S(4),hy+S(6),hx-S(3),hy+S(8),DARK); rr(d,hx+S(3),hy+S(6),hx+S(4),hy+S(8),DARK)
        nx,ny=ox+S(12),oy-S(10)
        d.line([(nx,ny),(nx+S(16),ny-S(2))],fill=NEEDLE,width=2); rr(d,nx+S(16),ny-S(5),nx+S(30),ny+S(2),(210,218,230)); rr(d,nx+S(28),ny-S(4),nx+S(34),ny,(150,160,180))
        for i in range(3):
            yy=oy+S(12)+i*S(10)+int(S(2)*math.sin(2*math.pi*2*t/12+i)); TL.add(ox-S(32),yy,"~",NUMB,'body')
    TL.add(CX-TL.w("! DON'T ASSUME GENERAL",'small')/2,232,"! DON'T ASSUME GENERAL",(236,120,142),'small')

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],2,CUE,"ANAESTHESIA",f'D:/Ue/UE_5.8/obgyn_explainer/bf6_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat06_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"ANAESTHESIA")
