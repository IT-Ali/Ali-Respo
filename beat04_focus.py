"""Beat 4 FOCUS - held clips: easy/short vs difficult/long labour (gauge + duration)."""
import math, sys
import focus_kit as FK
from birth_recovery import rr, el
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT; TEXT=FK.TEXT; TEXTDIM=FK.TEXTDIM
WALL=(26,32,50)
GREEN=(84,196,146); AMBER=(236,172,92); RED=(230,96,96)
TITLES=["EASY & SHORT","DIFFICULT & LONG"]
PEARL=["QUICK, UNCOMPLICATED LABOUR","PROLONGED / DIFFICULT LABOUR - MORE RISK"]
PLAB=["CASE 1 / 2","CASE 2 / 2"]
SUF=["1_easy","2_difficult"]
CUE=["EASY OR DIFFICULT?","AND HOW LONG?"]
SCN=[(0.15,"4 HRS","EASY",GREEN),(0.88,"14 HRS","DIFFICULT",RED)]
K=1.9
def S(v): return int(round(v*K))

def hero(d,s,t):
    e0,dur,word,wc=SCN[s]; e=e0+0.04*math.sin(2*math.pi*4*t/12)
    gx,gy,R=CX,CY+S(8),S(36)
    for a0,a1,col in [(180,240,GREEN),(240,300,AMBER),(300,360,RED)]:
        d.arc([gx-R,gy-R,gx+R,gy+R],a0,a1,fill=col,width=S(5))
    th=math.radians(180+e*180); zone=GREEN if e<0.4 else (AMBER if e<0.65 else RED)
    d.line([(gx,gy),(gx+int((R-S(4))*math.cos(th)),gy+int((R-S(4))*math.sin(th)))],fill=zone,width=3)
    el(d,gx-S(4),gy-S(4),gx+S(4),gy+S(4),(222,226,234)); el(d,gx-S(2),gy-S(2),gx+S(2),gy+S(2),zone)
    TL.add(gx-R-S(2),gy+S(6),"EASY",GREEN,'small'); TL.add(gx+R-TL.w("HARD",'small'),gy+S(6),"HARD",RED,'small')
    TL.add(gx-TL.w(word,'body')/2,gy+S(16),word,wc,'body')
    # duration readout
    bx,by=gx-S(34),gy+S(34)
    cx2,cy2=bx+S(10),by+S(10); el(d,cx2-S(8),cy2-S(8),cx2+S(8),cy2+S(8),(222,226,234)); el(d,cx2-S(6),cy2-S(6),cx2+S(6),cy2+S(6),(30,40,60))
    d.line([(cx2,cy2),(cx2+S(4),cy2-S(4))],fill=ACCENT,width=2); d.line([(cx2,cy2),(cx2,cy2+S(5))],fill=TEXT,width=2)
    TL.add(cx2+S(14),cy2-S(8),"DURATION",TEXTDIM,'small'); TL.add(cx2+S(14),cy2+S(2),dur,TEXT,'body')

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        FK.still(WALL,hero,s,tv,TITLES[s],PEARL[s],PLAB[s],2,CUE,"EFFORT & DURATION",f'D:/Ue/UE_5.8/obgyn_explainer/bf4_{s}.png'); print("ok",s)
    else:
        FK.render_all("beat04_focus",WALL,hero,TITLES,PEARL,PLAB,SUF,CUE,"EFFORT & DURATION")
