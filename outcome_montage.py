"""OUTCOME OF DELIVERY - the baby (explain -> ask -> organise). Object-based montage:
a swaddled newborn hero + per-item icon chip, the examinee ASKS, and an OUTCOME checklist
fills/ticks through the college history-sheet's 'Outcome of Delivery' box, organised into 3 groups:
THE BABY (number, live/dead, sex, weight) * AT BIRTH (cry&move, colour, distress, blood exchange)
* AFTER (NICU, feeding, APGAR). Items = the college sheet's outcome box ONLY. 480x270 -> 4K, 24fps."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=22.0
TLX=uitext.TL()

WALL=(22,26,36); WALL2=(32,38,50); FLOOR=(28,32,42); FLOORH=(38,44,56)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(120,200,224)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
SKIN=(242,201,170); SKIN_D=(206,160,128); SWAD=(226,232,244); SWAD_D=(196,204,222); SWAD_H=(240,244,252)
PINK=(236,146,170); BLUE=(120,168,224); AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146)
CYANO=(96,152,214); JAUND=(230,198,86); PALE=(228,222,210); GOLD=(230,186,96)

NITEMS=11
ITEMS=["NUMBER OF BABIES?","LIVE or DEAD?","MALE or FEMALE?","BIRTH WEIGHT?","CRIED & MOVED?",
       "COLOUR?","FETAL DISTRESS?","BLOOD EXCHANGE?","NICU - WHY & HOW LONG?","FEEDING?","APGAR SCORE?"]
STATUS=["NUMBER","LIVE?","SEX","WEIGHT","CRY/MOVE","COLOUR","DISTRESS","EXCHANGE","NICU","FEEDING","APGAR"]
PANEL=["Number","Live / dead","Male / female","Birth weight","Cried & moved","Colour",
       "Fetal distress","Blood exchange","NICU - why?","Feeding","APGAR score"]
PEARL=["SINGLE or TWINS  -  RECORD HOW MANY",
       "ALIVE or STILLBIRTH",
       "BOY or GIRL",
       "LOW  *  AVERAGE  *  HIGH BIRTH WEIGHT",
       "CRIED IMMEDIATELY & MOVED  =  GOOD START",
       "CYANOSIS (BLUE) * JAUNDICE (YELLOW) * ANAEMIA (PALE)",
       "ANY DISTRESS DURING LABOUR / AT BIRTH",
       "DID THE BABY NEED A BLOOD / EXCHANGE TRANSFUSION",
       "NICU ADMISSION  ->  ALWAYS ASK WHY & HOW LONG",
       "BREAST  *  BOTTLE  *  MIXED",
       "A-P-G-A-R:  7-10 GOOD * 4-6 MODERATE * 0-3 LOW"]
# groups: (label, [item indices])
GROUPS=[("THE BABY",[0,1,2,3]),("AT BIRTH",[4,5,6,7]),("AFTER",[8,9,10])]

def newborn(d,t):           # swaddled newborn in a little cot - hero
    cx=70; cy=124; sh=int(1.2*(0.5+0.5*math.sin(2*math.pi*t/4.0)))   # gentle breathing
    # cot / bassinet
    rr(d,cx-34,cy+18,cx+34,cy+40,(60,70,92)); rr(d,cx-34,cy+18,cx+34,cy+21,(78,90,116))
    d.line([(cx-34,cy+18),(cx-40,cy+48)],fill=(54,62,82),width=2); d.line([(cx+34,cy+18),(cx+40,cy+48)],fill=(54,62,82),width=2)
    # swaddle bundle
    d.polygon([(cx-20,cy+22-sh),(cx-15,cy-14-sh),(cx+15,cy-14-sh),(cx+20,cy+22-sh)],fill=SWAD)
    d.polygon([(cx-20,cy+22-sh),(cx-15,cy-14-sh),(cx-8,cy-13-sh),(cx-9,cy+22-sh)],fill=SWAD_H)   # light fold
    d.polygon([(cx+9,cy+22-sh),(cx+12,cy-13-sh),(cx+15,cy-14-sh),(cx+20,cy+22-sh)],fill=SWAD_D)  # shade fold
    el(d,cx-18,cy+6-sh,cx+18,cy+22-sh,SWAD)                         # rounded bottom of bundle
    # face peeking
    el(d,cx-11,cy-20-sh,cx+11,cy-2-sh,SKIN); el(d,cx-11,cy-8-sh,cx-5,cy-2-sh,SKIN_D)
    rr(d,cx-11,cy-20-sh,cx+11,cy-16-sh,SWAD); el(d,cx-13,cy-23-sh,cx+1,cy-15-sh,SWAD_H)  # cap edge
    d.point((cx-4,cy-11-sh),fill=(70,54,50)); d.point((cx+4,cy-11-sh),fill=(70,54,50))  # eyes
    d.line([(cx-2,cy-6-sh),(cx+2,cy-6-sh)],fill=SKIN_D)            # mouth
    el(d,cx-8,cy-9-sh,cx-6,cy-7-sh,lerp(SKIN,PINK,0.4)); el(d,cx+6,cy-9-sh,cx+8,cy-7-sh,lerp(SKIN,PINK,0.4))  # cheeks
    TLX.add(cx-20,cy-36,"THE NEWBORN",(150,200,224),'tiny')

def icon(d,s,cx,cy):
    if s==0:        # NUMBER - a small bundle
        d.polygon([(cx-7,cy+9),(cx-5,cy-6),(cx+5,cy-6),(cx+7,cy+9)],fill=SWAD)
        el(d,cx-5,cy-9,cx+5,cy-1,SKIN); rr(d,cx-5,cy-9,cx+5,cy-7,SWAD)
        d.point((cx-2,cy-5),fill=(70,54,50)); d.point((cx+2,cy-5),fill=(70,54,50))
    elif s==1:      # LIVE/DEAD - ECG heartbeat
        pts=[(cx-13,cy+2),(cx-6,cy+2),(cx-4,cy-8),(cx-1,cy+9),(cx+2,cy-3),(cx+5,cy+2),(cx+13,cy+2)]
        d.line(pts,fill=GREEN,width=2)
    elif s==2:      # SEX - female + male symbols
        el(d,cx-10,cy-8,cx-2,cy,PINK); d.line([(cx-6,cy),(cx-6,cy+8)],fill=PINK,width=2); d.line([(cx-9,cy+4),(cx-3,cy+4)],fill=PINK,width=2)   # venus
        el(d,cx+2,cy-2,cx+10,cy+6,BLUE); d.line([(cx+8,cy-2),(cx+13,cy-7)],fill=BLUE,width=2); d.line([(cx+10,cy-7),(cx+13,cy-7)],fill=BLUE,width=2); d.line([(cx+13,cy-7),(cx+13,cy-4)],fill=BLUE,width=2)  # mars
    elif s==3:      # WEIGHT - round scale dial
        el(d,cx-11,cy-11,cx+11,cy+11,(238,240,246)); d.ellipse([cx-11,cy-11,cx+11,cy+11],outline=INKDIM)
        for a in range(-60,61,30):
            rad=math.radians(a-90); d.line([(cx+int(8*math.cos(rad)),cy+int(8*math.sin(rad))),(cx+int(10*math.cos(rad)),cy+int(10*math.sin(rad)))],fill=INKDIM)
        na=math.radians(-20-90); d.line([(cx,cy),(cx+int(9*math.cos(na)),cy+int(9*math.sin(na)))],fill=RED,width=2)
        el(d,cx-2,cy-2,cx+2,cy+2,INK)
    elif s==4:      # CRY & MOVE - crying face + motion arcs
        el(d,cx-8,cy-8,cx+8,cy+8,SKIN); d.point((cx-3,cy-2),fill=(70,54,50)); d.point((cx+3,cy-2),fill=(70,54,50))
        el(d,cx-3,cy+2,cx+3,cy+6,(120,60,60))                        # open mouth (crying)
        el(d,cx-6,cy+1,cx-4,cy+5,BLUE)                               # tear
        for r in (12,16): d.arc([cx-r,cy-r,cx+r,cy+r],300,20,fill=GREEN,width=1)   # motion
    elif s==5:      # COLOUR - three swatches
        for i,c in enumerate([CYANO,JAUND,PALE]):
            dx=cx-12+i*9; rr(d,dx-3,cy-6,dx+3,cy+6,c); d.rectangle([dx-3,cy-6,dx+3,cy+6],outline=(90,96,110))
    elif s==6:      # FETAL DISTRESS - CTG with deceleration dip
        pts=[]
        for i in range(26):
            xx=cx-13+i; base=cy-4
            yy=base+ (int(9) if 10<=i<=17 else 0) + int(1.5*math.sin(i))   # dip = deceleration
            pts.append((xx,yy))
        d.line(pts,fill=AMBER,width=2); d.line([(cx-13,cy-10),(cx-13,cy+8)],fill=(120,130,146)); d.line([(cx-13,cy+8),(cx+13,cy+8)],fill=(120,130,146))
    elif s==7:      # BLOOD EXCHANGE - syringe with red + droplet
        rr(d,cx-10,cy-4,cx+6,cy+4,(236,238,244)); d.rectangle([cx-10,cy-4,cx+6,cy+4],outline=INKDIM)
        rr(d,cx-10,cy-3,cx-2,cy+3,RED)                              # red fluid
        rr(d,cx+6,cy-2,cx+10,cy+2,(160,170,186)); d.line([(cx+10,cy),(cx+15,cy)],fill=(160,170,186))  # needle
        d.polygon([(cx+15,cy+3),(cx+13,cy+7),(cx+17,cy+7)],fill=RED)  # drop
        rr(d,cx-13,cy-2,cx-10,cy+2,(120,130,146))                   # plunger
    elif s==8:      # NICU - incubator box with bundle inside
        rr(d,cx-13,cy-8,cx+13,cy+9,(44,54,74)); d.rectangle([cx-13,cy-8,cx+13,cy+9],outline=(120,180,210))
        rr(d,cx-13,cy-8,cx+13,cy-6,(120,180,210))
        d.polygon([(cx-4,cy+7),(cx-3,cy-2),(cx+3,cy-2),(cx+4,cy+7)],fill=SWAD); el(d,cx-3,cy-5,cx+3,cy+1,SKIN)  # baby inside
        d.line([(cx-13,cy+9),(cx-15,cy+15)],fill=(80,90,110)); d.line([(cx+13,cy+9),(cx+15,cy+15)],fill=(80,90,110))  # legs
    elif s==9:      # FEEDING - baby bottle
        rr(d,cx-5,cy-4,cx+5,cy+11,(236,240,248)); d.rectangle([cx-5,cy-4,cx+5,cy+11],outline=INKDIM)
        rr(d,cx-4,cy+3,cx+4,cy+11,lerp((236,240,248),(240,228,196),0.8))   # milk
        rr(d,cx-4,cy-7,cx+4,cy-4,(200,206,218)); d.polygon([(cx-2,cy-10),(cx+2,cy-10),(cx+1,cy-7),(cx-1,cy-7)],fill=(220,224,232))  # teat
        for my in range(cy-2,cy+2,2): d.line([(cx+2,my),(cx+4,my)],fill=INKDIM)   # measure lines
    else:           # APGAR - 0..10 zoned bar + marker
        x0,x1=cx-14,cx+14; yb=cy+2
        rr(d,x0,yb-3,x0+8,yb+3,RED); rr(d,x0+8,yb-3,x0+16,yb+3,AMBER); rr(d,x0+16,yb-3,x1,yb+3,GREEN)
        d.polygon([(x1-3,yb-8),(x1-7,yb-4),(x1+1,yb-4)],fill=TEXT)   # marker at good end
        TLX.add(cx-16,cy-13,"A P G A R",(170,210,226),'tiny')

def chip(d,s,t):
    cx,cy=160,112; pulse=0.5+0.5*math.sin(2*math.pi*t/3.0)
    x0,y0,x1,y1=cx-28,cy-24,cx+28,cy+24
    rr(d,x0,y0,x1,y1,(36,44,58)); rr(d,x0,y0,x1,y0+2,(150,200,224))
    d.rectangle([x0,y0,x1,y1],outline=lerp((70,100,120),ACCENT,pulse))
    icon(d,s,cx,cy)
    cw=TLX.w(STATUS[s],'small'); TLX.add(cx-cw/2,y1+3,STATUS[s],(150,200,224),'small')

def key_signs(d,x,y,w):
    rr(d,x,y,x+w,y+40,(32,40,50)); rr(d,x,y,x+w,y+2,(80,120,140))
    TLX.add(x+6,y+3,"ALWAYS NAIL:",(150,200,224),'tiny')
    TLX.add(x+6,y+16,"term/preterm * live/dead * sex * weight",(190,206,214),'tiny')
    TLX.add(x+6,y+27,"NICU -> why?   *   APGAR if told",(190,206,214),'tiny')

def panel(d,x,y,w,cur):
    # grouped checklist
    rows=sum(len(g[1]) for g in GROUPS); h=22+len(GROUPS)*11+rows*12+6
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"OUTCOME of DELIVERY",INK,'small'); rr(d,x+6,y+17,x+w-6,y+17,ACCENT)
    ry=y+22
    for glbl,idxs in GROUPS:
        TLX.add(x+6,ry,glbl,lerp(INK,ACCENT,0.5),'tiny'); ry+=11
        for i in idxs:
            done=i<cur; now=i==cur
            if now: rr(d,x+3,ry-1,x+w-3,ry+11,(224,244,248))
            rr(d,x+9,ry+1,x+15,ry+7,(250,250,250)); d.rectangle([x+9,ry+1,x+15,ry+7],outline=INKDIM)
            if done or now:
                d.line([(x+10,ry+4),(x+12,ry+6)],fill=TICK); d.line([(x+12,ry+6),(x+15,ry+1)],fill=TICK)
            TLX.add(x+20,ry,PANEL[i], INK if (done or now) else INKDIM,'small')
            ry+=12

def render(t):
    TLX.cmds=[]
    s=int(t//2)%NITEMS
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    newborn(d,t)
    chip(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,86,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,206,94,["HOW WAS","THE BABY?"],300)
    TLX.add(40,30,"CLOSE THE STORY - THE BABY",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,332,18,142,s)
    TLX.add(384,9,"HISTORY",(150,150,162),'small')
    key_signs(d,36,196,172)
    TLX.add(214,244,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(214,252,PEARL[s],(196,210,220),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"OUTCOME OF DELIVERY",(10,14,24),'body'); TLX.add(16,5,"OUTCOME OF DELIVERY",TEXT,'body')
    TLX.add(16.4,21.3,"THE BABY  -  RECORD HOW IT DID",(10,14,24),'small'); TLX.add(16,21,"THE BABY  -  RECORD HOW IT DID",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/outc_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/outcome_montage_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
