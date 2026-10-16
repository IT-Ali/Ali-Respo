"""ANTEPARTUM VAGINAL BLEEDING - characterise the bleed (explain -> ask -> organise).
Object-based montage (like beat11 PPH): a blood-loss measuring jug hero + per-item icon chip,
the examinee ASKS, and a BLEEDING Hx checklist fills/ticks through the deck's bleeding
characterisation items: onset/amount, colour, clots, pain (painless->praevia / painful->
abruption), dizziness, fever, fetal movement. Red-flag panel = the praevia vs abruption split.
Items are the deck's vaginal-bleeding row (Slide 05). 480x270 -> 4K, 24fps, 14s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=14.0
TLX=uitext.TL()

WALL=(28,22,34); WALL2=(38,28,42); FLOOR=(34,26,40); FLOORH=(46,34,50)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
BLOOD=(176,34,48); BLOOD_D=(120,20,32); BLOOD_H=(214,60,74); DARKB=(96,24,34)
AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146); GLASS=(150,160,178); SKIN=(242,201,170)
NITEMS=7
ITEMS=["ONSET / AMOUNT?","WHAT COLOUR?","ANY CLOTS?","PAINLESS or PAINFUL?","DIZZY / FAINT?","ANY FEVER?","BABY MOVING?"]
STATUS=["AMOUNT","COLOUR","CLOTS","PAIN?","FAINT?","FEVER?","FETAL"]
PEARL=["HOW IT STARTED, HOW MUCH  -  DROPS vs FLOODING",
       "FRESH RED (PRAEVIA)  vs  DARK (ABRUPTION)",
       "CLOTS / TISSUE  =  HEAVIER LOSS",
       "PAINLESS -> PRAEVIA   *   PAINFUL / RIGID -> ABRUPTION",
       "DIZZY / FAINT  =  SIGNS OF BLOOD LOSS",
       "FEVER -> THINK INFECTION (e.g. SEPTIC)",
       "REDUCED / ABSENT MOVEMENTS  =  FETAL ALARM"]

def jug(d,t):
    x0,x1,yt,yb=52,86,96,178
    rr(d,x0-2,yt,x0,yb+2,GLASS); rr(d,x1,yt,x1+2,yb+2,GLASS); rr(d,x0-2,yb,x1+2,yb+2,GLASS)
    rr(d,x0,yt,x1,yb,(24,20,30))
    lvl=yb-int((yb-yt)*0.62); wob=1.2*math.sin(2*math.pi*t/4.0)
    for xx in range(x0,x1):
        sy=lvl+int(wob*math.sin((xx-x0)*0.55)); rr(d,xx,sy,xx,yb,BLOOD)
    rr(d,x0,lvl,x1,lvl+1,BLOOD_H)
    for frac,lab in [(0.25,"250"),(0.5,"500"),(0.75,"750"),(1.0,"1000")]:
        ty=yb-int((yb-yt)*frac); d.line([(x1,ty),(x1+4,ty)],fill=GLASS); TLX.add(x1+6,ty-4,lab,(180,176,186),'tiny')
    TLX.add(x0-4,yt-11,"BLOOD LOSS",(236,150,160),'tiny')

def icon(d,s,cx,cy):
    if s==0:        # onset/amount - soaked pads
        for i in range(3):
            px=cx-16+i*11; rr(d,px,cy-8,px+8,cy+9,(238,240,246)); el(d,px+1,cy-3,px+7,cy+7,BLOOD)
    elif s==1:      # colour - fresh red vs dark droplet
        d.polygon([(cx-9,cy+8),(cx-15,cy+1),(cx-9,cy-9),(cx-3,cy+1)],fill=BLOOD_H); el(d,cx-12,cy+1,cx-6,cy+7,BLOOD_H)
        d.polygon([(cx+9,cy+8),(cx+3,cy+1),(cx+9,cy-9),(cx+15,cy+1)],fill=DARKB); el(d,cx+6,cy+1,cx+12,cy+7,DARKB)
    elif s==2:      # clots in a kidney dish
        el(d,cx-16,cy+1,cx+16,cy+12,(210,216,226)); el(d,cx-14,cy+2,cx+14,cy+9,(34,40,56))
        for bx,by,r in [(cx-6,cy+6,4),(cx+3,cy+6,3),(cx+9,cy+5,3)]: el(d,bx-r,by-r,bx+r,by+r,BLOOD_D)
        el(d,cx-2,cy-9,cx+1,cy-5,BLOOD)
    elif s==3:      # painless vs painful - two bellies
        el(d,cx-17,cy-7,cx-3,cy+9,SKIN); d.arc([cx-13,cy-1,cx-7,cy+5],20,160,fill=(120,80,60))  # soft belly + calm smile
        el(d,cx+3,cy-7,cx+17,cy+9,(240,180,150))                                                  # tense belly
        for a in range(0,360,45):                                                                 # pain starburst
            ar=math.radians(a); d.line([(cx+10,cy+1),(cx+10+int(9*math.cos(ar)),cy+1+int(9*math.sin(ar)))],fill=RED)
        el(d,cx-13,cy+4,cx-9,cy+8,GREEN)                                                           # calm = tick dot (painless)
    elif s==4:      # dizzy / faint head
        el(d,cx-8,cy-6,cx+8,cy+10,SKIN)
        d.line([(cx-5,cy),(cx-2,cy)],fill=(120,80,60)); d.line([(cx+2,cy),(cx+5,cy)],fill=(120,80,60))
        rr(d,cx-2,cy+4,cx+2,cy+6,(180,120,100))
        for sx,sy in [(cx-12,cy-8),(cx+11,cy-7),(cx+13,cy+3)]:
            d.line([(sx-2,sy),(sx+2,sy)],fill=AMBER); d.line([(sx,sy-2),(sx,sy+2)],fill=AMBER)
    elif s==5:      # thermometer (fever)
        rr(d,cx-2,cy-12,cx+2,cy+6,(238,240,246)); d.rectangle([cx-2,cy-12,cx+2,cy+6],outline=INKDIM)
        el(d,cx-4,cy+4,cx+4,cy+12,RED); rr(d,cx-1,cy-10,cx+1,cy+6,RED)
        for hy in range(cy-9,cy+4,3): d.line([(cx+3,hy),(cx+5,hy)],fill=(200,120,120))
    else:           # baby moving - curled fetus + motion arcs
        el(d,cx-11,cy-4,cx+3,cy+10,(246,210,182))        # body
        el(d,cx-14,cy-10,cx-4,cy,(246,210,182))          # head
        el(d,cx-12,cy-7,cx-9,cy-4,(80,60,50))            # eye
        d.line([(cx+2,cy+2),(cx+8,cy-2)],fill=(246,210,182),width=2)  # limb (kick)
        for r in (14,18): d.arc([cx-r+2,cy-r,cx+r+2,cy+r],300,20,fill=GREEN,width=1)

def chip(d,s,t):
    cx,cy=158,114; pulse=0.5+0.5*math.sin(2*math.pi*t/3.0)
    x0,y0,x1,y1=cx-28,cy-24,cx+28,cy+24
    rr(d,x0,y0,x1,y1,(44,34,40)); rr(d,x0,y0,x1,y0+2,BLOOD_H)
    d.rectangle([x0,y0,x1,y1],outline=lerp((120,70,80),AMBER,pulse))
    icon(d,s,cx,cy)
    cw=TLX.w(STATUS[s],'small'); TLX.add(cx-cw/2,y1+3,STATUS[s],(236,180,150),'small')

def red_flags(d,x,y,w):
    rr(d,x,y,x+w,y+40,(46,30,34)); rr(d,x,y,x+w,y+2,(140,60,66))
    TLX.add(x+6,y+3,"PRAEVIA  vs  ABRUPTION:",(236,150,160),'tiny')
    TLX.add(x+6,y+16,"painless + fresh red -> ? praevia",(214,180,186),'tiny')
    TLX.add(x+6,y+27,"painful + tender/rigid -> ? abruption",(214,180,186),'tiny')

def panel(d,x,y,w,cur):
    h=23+NITEMS*17+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"BLEEDING Hx",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+13,(252,240,176))
        rr(d,x+7,ry+1,x+14,ry+8,(250,250,250)); d.rectangle([x+7,ry+1,x+14,ry+8],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+4),(x+10,ry+7)],fill=TICK); d.line([(x+10,ry+7),(x+14,ry)],fill=TICK)
        TLX.add(x+18,ry,it, INK if (done or now) else INKDIM,'small')
        ry+=17

def render(t):
    TLX.cmds=[]
    s=int(t//2)%NITEMS
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    jug(d,t)
    chip(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,206,96,["TELL ME ABOUT","THE BLEEDING"],300)
    TLX.add(40,30,"ANTEPARTUM - CHARACTERISE IT",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,20,136,s)
    TLX.add(388,11,"HISTORY",(150,150,162),'small')
    red_flags(d,36,196,172)
    TLX.add(214,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(214,254,PEARL[s],(206,186,192),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"VAGINAL BLEEDING",(10,14,24),'body'); TLX.add(16,5,"VAGINAL BLEEDING",TEXT,'body')
    TLX.add(16.4,21.3,"CHARACTERISE THE BLEED",(10,14,24),'small'); TLX.add(16,21,"CHARACTERISE THE BLEED",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/apb_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/apb_bleeding_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
