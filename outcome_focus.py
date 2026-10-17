"""OUTCOME OF DELIVERY - FOCUS clips: each outcome item BIG & centred, with the examinee asking
+ a pearl. Items = the college history-sheet's 'Outcome of Delivery' box (number, live/dead, sex,
weight, cry&move, colour, fetal distress, blood exchange, NICU, feeding, APGAR). Plays all 11
concepts in sequence as one 1080p clip. Reuses the focus_kit scaffold."""
import math, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
import focus_kit as FK
import birth_recovery as BR
from birth_recovery import rr, el, lerp, GW, GH, SCALE
CX,CY=FK.CX,FK.CY; TL=FK.TLX; ACCENT=FK.ACCENT; FFMPEG=BR.FFMPEG; FPS=24
WALL=(22,26,36)
SKIN=(242,201,170); SKIN_D=(206,160,128); SWAD=(226,232,244); SWAD_D=(196,204,222); SWAD_H=(240,244,252)
PINK=(236,146,170); BLUE=(120,168,224); AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146)
CYANO=(96,152,214); JAUND=(230,198,86); PALE=(228,222,210); INKDIM=(150,150,162); TEXT=BR.TEXT

TITLES=["NUMBER OF BABIES","LIVE or DEAD","MALE or FEMALE","BIRTH WEIGHT","CRIED & MOVED","COLOUR",
        "FETAL DISTRESS","BLOOD EXCHANGE","NICU ADMISSION","FEEDING","APGAR SCORE"]
PEARL=["SINGLE or TWINS  -  RECORD HOW MANY",
       "ALIVE  or  STILLBIRTH",
       "BOY  or  GIRL",
       "LOW  *  AVERAGE  *  HIGH  (term / preterm)",
       "CRIED IMMEDIATELY & MOVED  =  GOOD START",
       "CYANOSIS (BLUE) * JAUNDICE (YELLOW) * ANAEMIA (PALE)",
       "ANY DISTRESS DURING LABOUR / AT BIRTH",
       "DID THE BABY NEED A BLOOD / EXCHANGE TRANSFUSION",
       "NICU ADMISSION  ->  ALWAYS ASK WHY & HOW LONG",
       "BREAST  *  BOTTLE  *  MIXED",
       "A-P-G-A-R  *  7-10 GOOD * 4-6 MODERATE * 0-3 LOW"]
PLAB=[f"ITEM {i+1} / 11" for i in range(11)]
CUE=["HOW WAS","THE BABY?"]
IDENT="OUTCOME OF DELIVERY"
NIT=11; SEG=6.0
K=2.0
def S(v): return int(round(v*K))

def bundle(d,cx,cy,sc,sk=SKIN):
    """a swaddled newborn bundle centred at cx,cy, size scale sc."""
    w=int(16*sc); h=int(22*sc)
    d.polygon([(cx-w,cy+h),(cx-int(w*0.75),cy-int(h*0.6)),(cx+int(w*0.75),cy-int(h*0.6)),(cx+w,cy+h)],fill=SWAD)
    d.polygon([(cx-w,cy+h),(cx-int(w*0.75),cy-int(h*0.6)),(cx-int(w*0.3),cy-int(h*0.55)),(cx-int(w*0.4),cy+h)],fill=SWAD_H)
    d.polygon([(cx+int(w*0.4),cy+h),(cx+int(w*0.45),cy-int(h*0.55)),(cx+int(w*0.75),cy-int(h*0.6)),(cx+w,cy+h)],fill=SWAD_D)
    el(d,cx-w,cy+int(h*0.3),cx+w,cy+h,SWAD)
    fw=int(11*sc)
    el(d,cx-fw,cy-int(h*0.9),cx+fw,cy-int(h*0.1),sk); el(d,cx-fw,cy-int(h*0.35),cx-int(fw*0.4),cy-int(h*0.1),SKIN_D)
    rr(d,cx-fw,cy-int(h*0.9),cx+fw,cy-int(h*0.72),SWAD); el(d,cx-fw-2,cy-h,cx+2,cy-int(h*0.7),SWAD_H)
    ey=cy-int(h*0.45); d.ellipse([cx-int(5*sc),ey-2,cx-int(5*sc)+3,ey+1],fill=(70,54,50)); d.ellipse([cx+int(5*sc)-3,ey-2,cx+int(5*sc),ey+1],fill=(70,54,50))
    d.line([(cx-3,cy-int(h*0.25)),(cx+3,cy-int(h*0.25))],fill=SKIN_D)
    el(d,cx-int(9*sc),ey+3,cx-int(6*sc),ey+6,lerp(SKIN,PINK,0.4)); el(d,cx+int(6*sc),ey+3,cx+int(9*sc),ey+6,lerp(SKIN,PINK,0.4))

def hero(d,s,t):
    if s==0:        # NUMBER - one solid bundle + a faded second (single or twins?)
        bundle(d,CX-S(14),CY+S(4),1.0)
        # faded ghost second bundle
        bundle(d,CX+S(22),CY+S(6),0.8,sk=lerp(SKIN,WALL,0.45))
        TL.add(CX-S(26),CY+S(34),"SINGLE?",(180,210,232),'small'); TL.add(CX+S(6),CY+S(34),"TWINS?",(120,140,170),'small')
    elif s==1:      # LIVE/DEAD - big ECG + heart
        base=CY+S(2)
        pts=[(CX-S(34),base),(CX-S(16),base),(CX-S(12),base-S(18)),(CX-S(6),base+S(18)),(CX-S(1),base-S(6)),(CX+S(4),base),(CX+S(34),base)]
        d.line(pts,fill=GREEN,width=4)
        hx,hy=CX+S(20),CY-S(18); el(d,hx-S(7),hy-S(5),hx-S(1),hy+S(3),RED); el(d,hx+S(1),hy-S(5),hx+S(7),hy+S(3),RED); d.polygon([(hx-S(8),hy+S(1)),(hx,hy+S(11)),(hx+S(8),hy+S(1))],fill=RED)
        TL.add(CX-S(18),CY+S(24),"ALIVE  or  STILLBIRTH",(170,220,180),'small')
    elif s==2:      # SEX - big venus + mars
        el(d,CX-S(26),CY-S(16),CX-S(8),CY+S(2),PINK); d.line([(CX-S(17),CY+S(2)),(CX-S(17),CY+S(20))],fill=PINK,width=4); d.line([(CX-S(24),CY+S(11)),(CX-S(10),CY+S(11))],fill=PINK,width=4)
        el(d,CX+S(6),CY-S(2),CX+S(24),CY+S(16),BLUE); d.line([(CX+S(20),CY-S(2)),(CX+S(30),CY-S(14))],fill=BLUE,width=4); d.line([(CX+S(23),CY-S(14)),(CX+S(30),CY-S(14))],fill=BLUE,width=4); d.line([(CX+S(30),CY-S(14)),(CX+S(30),CY-S(7))],fill=BLUE,width=4)
        TL.add(CX-S(26),CY+S(24),"GIRL",(236,160,184),'small'); TL.add(CX+S(8),CY+S(24),"BOY",(150,186,230),'small')
    elif s==3:      # WEIGHT - scale dial with LOW/AVG/HIGH zones
        R=S(22); el(d,CX-R,CY-R-S(4),CX+R,CY+R-S(4),(238,240,246)); d.ellipse([CX-R,CY-R-S(4),CX+R,CY+R-S(4),],outline=INKDIM,width=2)
        cyc=CY-S(4)
        for a,lab,col in [(-55,"LOW",RED),(0,"AVG",GREEN),(55,"HIGH",AMBER)]:
            rad=math.radians(a-90)
            d.line([(CX+int((R-S(3))*math.cos(rad)),cyc+int((R-S(3))*math.sin(rad))),(CX+int(R*math.cos(rad)),cyc+int(R*math.sin(rad)))],fill=col,width=2)
        na=math.radians(0-90); d.line([(CX,cyc),(CX+int((R-S(6))*math.cos(na)),cyc+int((R-S(6))*math.sin(na)))],fill=RED,width=3)
        el(d,CX-S(3),cyc-S(3),CX+S(3),cyc+S(3),(52,56,72))
        TL.add(CX-S(10),CY+S(22),"kg",(200,206,218),'small')
    elif s==4:      # CRY & MOVE - crying face + motion + notes
        el(d,CX-S(16),CY-S(16),CX+S(16),CY+S(16),SKIN)
        d.ellipse([CX-S(6),CY-S(8),CX-S(2),CY-S(4)],fill=(70,54,50)); d.ellipse([CX+S(2),CY-S(8),CX+S(6),CY-S(4)],fill=(70,54,50))
        el(d,CX-S(5),CY+S(2),CX+S(5),CY+S(10),(120,60,60))        # open mouth
        el(d,CX-S(11),CY-S(2),CX-S(8),CY+S(4),BLUE)               # tear
        for r in (S(22),S(28)): d.arc([CX-r,CY-r,CX+r,CY+r],300,20,fill=GREEN,width=2)
        TL.add(CX+S(14),CY-S(22),"~",(170,220,180),'title'); TL.add(CX-S(26),CY+S(26),"CRIED RIGHT AWAY?",(170,220,180),'small')
    elif s==5:      # COLOUR - 3 big swatches + labels
        labs=[("CYANOSIS",CYANO),("JAUNDICE",JAUND),("ANAEMIA",PALE)]
        for i,(lab,c) in enumerate(labs):
            dx=CX-S(30)+i*S(30); rr(d,dx-S(11),CY-S(16),dx+S(11),CY+S(8),c); d.rectangle([dx-S(11),CY-S(16),dx+S(11),CY+S(8)],outline=(90,96,110))
            TL.add(dx-TL.w(lab,'tiny')/2,CY+S(12),lab,lerp(c,(255,255,255),0.3) if c!=PALE else (190,196,206),'tiny')
        TL.add(CX-S(22),CY-S(30),"normal = pink",(200,160,176),'tiny')
    elif s==6:      # FETAL DISTRESS - big CTG with deceleration
        x0=CX-S(30); x1=CX+S(30); base=CY-S(2)
        d.line([(x0,base-S(16)),(x0,base+S(14))],fill=(120,130,146),width=2); d.line([(x0,base+S(14)),(x1,base+S(14))],fill=(120,130,146),width=2)
        pts=[]
        for i in range(S(60)):
            xx=x0+i; frac=i/S(60)
            yy=base + (S(16) if 0.4<=frac<=0.68 else 0) + int(S(2)*math.sin(i*0.5))
            pts.append((xx,yy))
        d.line(pts,fill=AMBER,width=3)
        el(d,CX+S(20),CY-S(24),CX+S(34),CY-S(10),RED); TL.add(CX+S(25),CY-S(23),"!",(255,240,240),'small')
        TL.add(CX-S(30),CY+S(20),"DECELERATION = DISTRESS",(236,170,120),'small')
    elif s==7:      # BLOOD EXCHANGE - big syringe + red + exchange arrows
        rr(d,CX-S(22),CY-S(7),CX+S(12),CY+S(7),(236,238,244)); d.rectangle([CX-S(22),CY-S(7),CX+S(12),CY+S(7)],outline=INKDIM,width=2)
        rr(d,CX-S(22),CY-S(6),CX-S(4),CY+S(6),RED)
        rr(d,CX+S(12),CY-S(4),CX+S(20),CY+S(4),(160,170,186)); d.line([(CX+S(20),CY),(CX+S(32),CY)],fill=(160,170,186),width=2)
        d.polygon([(CX+S(32),CY+S(6)),(CX+S(28),CY+S(13)),(CX+S(36),CY+S(13))],fill=RED)
        rr(d,CX-S(28),CY-S(4),CX-S(22),CY+S(4),(120,130,146))
        TL.add(CX-S(26),CY+S(22),"EXCHANGE / BLOOD TRANSFUSION?",(230,150,150),'small')
    elif s==8:      # NICU - big incubator + why?
        rr(d,CX-S(26),CY-S(14),CX+S(26),CY+S(14),(44,54,74)); d.rectangle([CX-S(26),CY-S(14),CX+S(26),CY+S(14)],outline=(120,180,210),width=2)
        rr(d,CX-S(26),CY-S(14),CX+S(26),CY-S(10),(120,180,210))
        bundle(d,CX,CY+S(2),0.6)
        d.line([(CX-S(26),CY+S(14)),(CX-S(30),CY+S(26))],fill=(80,90,110),width=2); d.line([(CX+S(26),CY+S(14)),(CX+S(30),CY+S(26))],fill=(80,90,110),width=2)
        TL.add(CX-S(26),CY+S(22),"WHY?  HOW LONG?",(150,200,224),'small')
    elif s==9:      # FEEDING - breast + bottle
        # breast (left): curved shape + nipple
        el(d,CX-S(32),CY-S(12),CX-S(8),CY+S(12),lerp(SKIN,(250,220,200),0.5)); el(d,CX-S(16),CY-S(2),CX-S(11),CY+S(3),SKIN_D)
        TL.add(CX-S(34),CY+S(16),"BREAST",(236,196,180),'small')
        # bottle (right)
        bx=CX+S(16)
        rr(d,bx-S(8),CY-S(8),bx+S(8),CY+S(16),(236,240,248)); d.rectangle([bx-S(8),CY-S(8),bx+S(8),CY+S(16)],outline=INKDIM,width=2)
        rr(d,bx-S(6),CY+S(4),bx+S(6),CY+S(16),lerp((236,240,248),(240,228,196),0.8))
        rr(d,bx-S(6),CY-S(13),bx+S(6),CY-S(8),(200,206,218)); d.polygon([(bx-S(3),CY-S(18)),(bx+S(3),CY-S(18)),(bx+S(2),CY-S(13)),(bx-S(2),CY-S(13))],fill=(220,224,232))
        TL.add(bx-S(10),CY+S(20),"BOTTLE",(200,206,218),'small')
    else:           # APGAR - big zoned bar + letters + words
        x0,x1=CX-S(34),CX+S(34); yb=CY+S(2); seg=(x1-x0)//10
        for i in range(10):
            c=RED if i<3 else (AMBER if i<6 else GREEN)
            rr(d,x0+i*seg+1,yb-S(5),x0+(i+1)*seg-1,yb+S(5),c)
        d.polygon([(x1,yb-S(12)),(x1-S(5),yb-S(6)),(x1+S(5),yb-S(6))],fill=TEXT)
        TL.add(x0,yb+S(9),"0",(200,206,218),'tiny'); TL.add(x1-S(2),yb+S(9),"10",(200,206,218),'tiny')
        TL.add(CX-S(34),CY-S(26),"A P G A R",(170,210,226),'title')
        TL.add(CX-S(40),CY+S(22),"Appearance Pulse Grimace Activity Respiration",(190,200,216),'tiny')

def render(gs,t):
    return FK.frame(WALL,hero,gs,t,TITLES[gs],PEARL[gs],PLAB[gs],NIT,CUE,IDENT)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        Image.fromarray(render(s,tv)).save(f'/home/user/Ali-Respo/outcf_{s}.png'); print("ok",s)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/outcome_focus_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for s in range(NIT):
            for i in range(int(SEG*FPS)): p.stdin.write(render(s,i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
