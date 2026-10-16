"""WATERY DISCHARGE / ROM - characterise it (explain -> ask -> organise). Object-based montage:
a soaked liquor pad hero + per-item icon chip, the examinee ASKS, and a DISCHARGE Hx checklist
fills/ticks through the deck's watery-discharge row: gush/trickle, colour (clear/green-meconium/
blood-stained), odour, fever, contractions, bleeding, fetal movement. Red-flag panel = meconium
-> fetal distress, and fever+offensive -> chorioamnionitis. Items = deck Slide 05 ROM row.
480x270 -> 4K, 24fps, 14s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=14.0
TLX=uitext.TL()

WALL=(20,26,34); WALL2=(30,38,48); FLOOR=(26,32,40); FLOORH=(36,44,54)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(120,200,224)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
FLUID=(150,200,224); FLUID_D=(96,156,186); FLUID_H=(200,230,244)
MECON=(118,146,66); BLOOD=(176,34,48); AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146); SKIN=(242,201,170); GLASS=(150,160,178)
NITEMS=7
ITEMS=["GUSH or TRICKLE?","WHAT COLOUR?","ANY ODOUR?","ANY FEVER?","CONTRACTIONS?","ANY BLEEDING?","BABY MOVING?"]
STATUS=["AMOUNT","COLOUR","ODOUR","FEVER?","LABOUR?","BLEED?","FETAL"]
PEARL=["SUDDEN GUSH vs SLOW TRICKLE  -  HOW MUCH, WHEN",
       "CLEAR (normal)  *  GREEN/MECONIUM -> FETAL DISTRESS  *  BLOOD-STAINED",
       "OFFENSIVE SMELL -> INFECTION (CHORIOAMNIONITIS)",
       "FEVER + OFFENSIVE LIQUOR -> CHORIOAMNIONITIS",
       "CONTRACTIONS?  -  IS SHE IN LABOUR",
       "ANY BLEEDING MIXED WITH THE FLUID?",
       "REDUCED / ABSENT MOVEMENTS  =  FETAL ALARM"]

def pad(d,t):               # soaked liquor pad hero + drip
    x0,x1,yt,yb=46,96,100,150
    rr(d,x0,yt,x1,yb,(238,240,246)); el(d,x0-3,yt,x0+6,yb,(238,240,246)); el(d,x1-6,yt,x1+3,yb,(238,240,246))
    wl=yt+8+int(2*math.sin(2*math.pi*t/4.0))
    el(d,x0+3,wl,x1-3,yb-3,FLUID); el(d,x0+8,wl+3,x1-8,yb-7,FLUID_H)   # wet patch
    dyn=yb+6+int((t*22)%18)
    if dyn<yb+22: el(d,(x0+x1)//2-2,dyn,(x0+x1)//2+2,dyn+5,FLUID)       # drip
    TLX.add(x0+2,yt-11,"LIQUOR",(150,200,224),'tiny')

def icon(d,s,cx,cy):
    if s==0:        # gush vs trickle
        for yy in range(cy-10,cy+10,3): d.line([(cx-10,yy),(cx-6,yy+2)],fill=FLUID_H)   # gush stream
        el(d,cx-12,cy+8,cx-4,cy+13,FLUID)
        for i,yy in enumerate(range(cy-8,cy+10,8)): el(d,cx+9,yy,cx+12,yy+3,FLUID)      # trickle drops
    elif s==1:      # colour - clear / green(meconium) / blood
        for i,(c,lab) in enumerate([(FLUID_H,None),(MECON,None),(BLOOD,None)]):
            dx=cx-16+i*13
            d.polygon([(dx,cy+7),(dx-5,cy+1),(dx,cy-8),(dx+5,cy+1)],fill=c); el(d,dx-4,cy+1,dx+4,cy+7,c)
    elif s==2:      # odour - nose + smell waves
        d.polygon([(cx-2,cy-8),(cx-6,cy+4),(cx+2,cy+4)],fill=SKIN); el(d,cx-5,cy+2,cx-1,cy+6,SKIN); el(d,cx+1,cy+2,cx+5,cy+6,SKIN)
        for i,ox in enumerate((7,11,15)):
            for yy in (cy-6,cy-1,cy+4): d.arc([cx+ox,yy-3,cx+ox+6,yy+3],250,110,fill=lerp(WALL,MECON,0.8),width=1)
    elif s==3:      # thermometer (fever)
        rr(d,cx-2,cy-12,cx+2,cy+6,(238,240,246)); d.rectangle([cx-2,cy-12,cx+2,cy+6],outline=INKDIM)
        el(d,cx-4,cy+4,cx+4,cy+12,RED); rr(d,cx-1,cy-10,cx+1,cy+6,RED)
        for hy in range(cy-9,cy+4,3): d.line([(cx+3,hy),(cx+5,hy)],fill=(210,120,120))
    elif s==4:      # contractions - wave graph
        pts=[]
        for i in range(25):
            xx=cx-14+i; ph=(i/25)*2*math.pi*2; yy=cy+2-int(9*max(0,math.sin(ph)))
            pts.append((xx,yy))
        d.line(pts,fill=AMBER,width=2); d.line([(cx-14,cy+4),(cx+12,cy+4)],fill=(120,130,146))
    elif s==5:      # bleeding - red droplet
        d.polygon([(cx,cy+8),(cx-7,cy),(cx,cy-10),(cx+7,cy)],fill=BLOOD); el(d,cx-5,cy,cx+5,cy+7,BLOOD)
    else:           # baby moving - fetus + motion arcs
        el(d,cx-11,cy-4,cx+3,cy+10,(246,210,182)); el(d,cx-14,cy-10,cx-4,cy,(246,210,182))
        el(d,cx-12,cy-7,cx-9,cy-4,(80,60,50)); d.line([(cx+2,cy+2),(cx+8,cy-2)],fill=(246,210,182),width=2)
        for r in (14,18): d.arc([cx-r+2,cy-r,cx+r+2,cy+r],300,20,fill=GREEN,width=1)

def chip(d,s,t):
    cx,cy=158,114; pulse=0.5+0.5*math.sin(2*math.pi*t/3.0)
    x0,y0,x1,y1=cx-28,cy-24,cx+28,cy+24
    rr(d,x0,y0,x1,y1,(34,42,52)); rr(d,x0,y0,x1,y0+2,FLUID_H)
    d.rectangle([x0,y0,x1,y1],outline=lerp((70,100,120),ACCENT,pulse))
    icon(d,s,cx,cy)
    cw=TLX.w(STATUS[s],'small'); TLX.add(cx-cw/2,y1+3,STATUS[s],(150,200,224),'small')

def red_flags(d,x,y,w):
    rr(d,x,y,x+w,y+40,(30,38,46)); rr(d,x,y,x+w,y+2,(80,120,140))
    TLX.add(x+6,y+3,"RED FLAGS:",(150,200,224),'tiny')
    TLX.add(x+6,y+16,"green / meconium -> fetal distress",(190,206,214),'tiny')
    TLX.add(x+6,y+27,"fever + offensive -> chorioamnionitis",(190,206,214),'tiny')

def panel(d,x,y,w,cur):
    h=23+NITEMS*17+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"DISCHARGE Hx",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+13,(224,244,248))
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
    pad(d,t)
    chip(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,206,96,["TELL ME ABOUT","THE WATERS"],300)
    TLX.add(40,30,"CONFIRM LIQUOR - CHARACTERISE IT",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,20,136,s)
    TLX.add(388,11,"HISTORY",(150,150,162),'small')
    red_flags(d,36,196,172)
    TLX.add(214,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(214,254,PEARL[s],(196,210,220),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"WATERY DISCHARGE (ROM)",(10,14,24),'body'); TLX.add(16,5,"WATERY DISCHARGE (ROM)",TEXT,'body')
    TLX.add(16.4,21.3,"IS IT LIQUOR?  THEN CHARACTERISE",(10,14,24),'small'); TLX.add(16,21,"IS IT LIQUOR?  THEN CHARACTERISE",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/rom_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/rom_montage_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
