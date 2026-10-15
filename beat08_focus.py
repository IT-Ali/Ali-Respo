"""Beat 8 FOCUS - held clips per intra-op note."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
from PIL import ImageDraw
CX,CY=FK.CX,FK.CY; TL=FK.TLX
WALL=(22,28,44)
RED=(214,60,70); BLOODC=(190,40,52); AMBER=(236,172,92); GREEN=(84,196,146); TEXTC=(214,224,238); ACCENT=FK.ACCENT
TITLES=["TIME & DURATION","SMOOTH vs DIFFICULT","EXCESSIVE BLEEDING","TRANSFUSION","ORGAN INJURY"]
PEARL=["DATE / TIME & HOW LONG THE OP TOOK","WAS THE OPERATION SMOOTH OR DIFFICULT",
       "ASK ABOUT EXCESSIVE BLOOD LOSS","DID SHE NEED A BLOOD TRANSFUSION","BLADDER / BOWEL / ORGAN INJURY"]
PLAB=[f"NOTE {i+1} / 5" for i in range(5)]
SUF=["1_time-duration","2_smooth-difficult","3_excessive-bleeding","4_transfusion","5_organ-injury"]
CUE=["HOW DID THE","OPERATION GO?"]
K=1.9
def S(v): return int(round(v*K))

def hero(d,s,t):
    if s==0:
        R=S(30); el(d,CX-R-1,CY-R-1,CX+R+1,CY+R+1,(222,226,234)); el(d,CX-R,CY-R,CX+R,CY+R,(28,36,56))
        for k in range(12):
            a=math.radians(k*30); el(d,CX+int((R-S(3))*math.sin(a))-1,CY-int((R-S(3))*math.cos(a))-1,CX+int((R-S(3))*math.sin(a))+1,CY-int((R-S(3))*math.cos(a))+1,(150,160,180))
        ah=2*math.pi*(t/12.0); d.line([(CX,CY),(CX+int((R-S(12))*math.sin(ah)),CY-int((R-S(12))*math.cos(ah)))],fill=TEXTC,width=3)
        asec=2*math.pi*t; d.line([(CX,CY),(CX+int((R-S(5))*math.sin(asec)),CY-int((R-S(5))*math.cos(asec)))],fill=ACCENT,width=2)
        el(d,CX-3,CY-3,CX+3,CY+3,(222,226,234))
        TL.add(CX-TL.w("45 MIN",'title')/2,CY+S(38),"45 MIN",TEXTC,'title')
    elif s==1:
        gx,gy,R=CX,CY+S(6),S(40)
        for a0,a1,col in [(180,240,GREEN),(240,300,AMBER),(300,360,RED)]:
            d.arc([gx-R,gy-R,gx+R,gy+R],a0,a1,fill=col,width=S(5))
        e=0.78+0.06*math.sin(2*math.pi*4*t/12); th=math.radians(180+e*180)
        d.line([(gx,gy),(gx+int((R-S(3))*math.cos(th)),gy+int((R-S(3))*math.sin(th)))],fill=(230,234,240),width=3)
        el(d,gx-4,gy-4,gx+4,gy+4,(230,234,240))
        TL.add(CX-TL.w("DIFFICULT",'body')/2,gy+S(8),"DIFFICULT",RED,'body')
    elif s==2:
        jx0,jx1,jt,jb=CX-S(20),CX+S(20),CY-S(26),CY+S(24)
        rr(d,jx0-2,jt,jx0,jb+2,(150,160,178)); rr(d,jx1,jt,jx1+2,jb+2,(150,160,178)); rr(d,jx0-2,jb,jx1+2,jb+2,(150,160,178))
        rr(d,jx0,jt,jx1,jb,(24,20,30)); lvl=jb-int((jb-jt)*0.6)
        rr(d,jx0,lvl,jx1,jb,BLOODC); rr(d,jx0,lvl,jx1,lvl+1,(206,60,74))
        for i in range(3):
            dy=jb+S(10)+int((((t/12*6)+i*0.3)%1.0)*S(28)); el(d,CX-S(10)+i*S(10),dy,CX-S(6)+i*S(10),dy+S(6),BLOODC)
        TL.add(CX-TL.w("! BLOOD LOSS",'body')/2,jt-S(14),"! BLOOD LOSS",RED,'body')
    elif s==3:
        rr(d,CX-S(40),CY-S(26),CX-S(20),CY+S(10),BLOODC); rr(d,CX-S(40),CY-S(26),CX-S(20),CY-S(20),(150,30,42))
        TL.add(CX-S(38),CY-S(14),"O+",(255,235,235),'small')
        d.line([(CX-S(30),CY+S(10)),(CX-S(4),CY+S(26)),(CX+S(24),CY+S(30))],fill=BLOODC,width=3)
        for i in range(2):
            fp=((t/12*8)+i*0.5)%1.0; px=int(CX-S(30)+fp*S(54)); py=int(CY+S(10)+fp*S(20))
            el(d,px-1,py-1,px+1,py+1,(230,70,84))
        el(d,CX+S(20),CY+S(24),CX+S(40),CY+S(38),(242,201,170))
        TL.add(CX+S(10),CY+S(40),"INTO ARM",(236,180,170),'small')
    else:
        d.polygon([(CX-S(34),CY+S(26)),(CX+S(34),CY+S(26)),(CX,CY-S(34))],fill=AMBER)
        TL.add(CX-3,CY-S(6),"!",(40,30,10),'title')
        TL.add(CX-TL.w("BLADDER / BOWEL?",'body')/2,CY+S(32),"BLADDER / BOWEL?",AMBER,'body')

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],5,CUE,"C-SECTION INTRA-OP",f'D:/Ue/UE_5.8/obgyn_explainer/bf8_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat08_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"C-SECTION INTRA-OP")
