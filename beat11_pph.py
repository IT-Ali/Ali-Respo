"""Beat 11 - POST-PARTUM HAEMORRHAGE (Part C). Modest, object-based: a blood-loss
measuring jug (with the 500 mL PPH line) as the hero, and the specific questions cycle
as icon chips - heavy bleeding, clots/flooding, primary vs secondary, faint/dizzy,
treatment given, previous PPH (recurrence). 480x270 -> 4K, 24fps, 12s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(28,22,34); WALL2=(38,28,42); FLOOR=(34,26,40); FLOORH=(46,34,50)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
BLOOD=(176,34,48); BLOOD_D=(140,24,38); BLOOD_H=(206,60,74)
AMBER=(236,172,92); RED=(214,60,70); GREEN=(84,196,146); STEEL=(206,214,228); GLASS=(150,160,178)
ITEMS=["HEAVY BLEEDING?","CLOTS / FLOODING?","PRIMARY vs SECONDARY","FELT FAINT / DIZZY?","TREATMENT GIVEN?","PREVIOUS PPH?"]
STATUS=["SOAKED PADS","CLOTS","WHEN?","FAINT?","TREATED?","BEFORE?"]
PEARL=["SOAKING PADS FAST OR FLOODING = RED FLAG",
       "BIG CLOTS / FLOODING MEAN HEAVY LOSS",
       "PRIMARY <24H  vs  SECONDARY (DAYS-6 WKS)",
       "DIZZY / FAINT = SIGNS OF BLOOD LOSS",
       "UTEROTONICS / TRANSFUSION / THEATRE?",
       "PPH BEFORE RAISES THE RISK NEXT TIME"]

def jug(d,t):
    x0,x1,yt,yb=52,86,96,178
    rr(d,x0-2,yt,x0,yb+2,GLASS); rr(d,x1,yt,x1+2,yb+2,GLASS); rr(d,x0-2,yb,x1+2,yb+2,GLASS)
    rr(d,x0,yt,x1,yb,(24,20,30))
    lvl=yb-int((yb-yt)*0.70); wob=1.2*math.sin(2*math.pi*t/4.0)
    for xx in range(x0,x1):
        sy=lvl+int(wob*math.sin((xx-x0)*0.55)); rr(d,xx,sy,xx,yb,BLOOD)
    rr(d,x0,lvl,x1,lvl+1,BLOOD_H)
    for frac,lab in [(0.25,"250"),(0.5,"500"),(0.75,"750"),(1.0,"1000")]:
        ty=yb-int((yb-yt)*frac); d.line([(x1,ty),(x1+4,ty)],fill=GLASS); TLX.add(x1+6,ty-4,lab,(180,176,186),'tiny')
    thr=yb-int((yb-yt)*0.5); d.line([(x0-5,thr),(x1,thr)],fill=(236,110,110))
    TLX.add(x0-26,thr-4,"PPH",(236,130,130),'tiny')
    TLX.add(x0-4,yt-11,"BLOOD LOSS",(236,150,160),'tiny')

def icon(d,s,cx,cy):
    if s==0:        # soaked pads
        for i in range(3):
            px=cx-16+i*11; rr(d,px,cy-8,px+8,cy+9,(238,240,246)); el(d,px+1,cy-3,px+7,cy+7,BLOOD)
    elif s==1:      # clots in a kidney dish
        el(d,cx-16,cy+1,cx+16,cy+12,(210,216,226)); el(d,cx-14,cy+2,cx+14,cy+9,(34,40,56))
        for bx,by,r in [(cx-6,cy+6,4),(cx+3,cy+6,3),(cx+9,cy+5,3)]: el(d,bx-r,by-r,bx+r,by+r,BLOOD_D)
        el(d,cx-2,cy-9,cx+1,cy-5,BLOOD)
    elif s==2:      # timeline: primary <24h vs secondary
        d.line([(cx-17,cy+2),(cx+17,cy+2)],fill=(180,190,206),width=2)
        d.line([(cx-3,cy-4),(cx-3,cy+8)],fill=RED,width=2)
        el(d,cx-17,cy-11,cx-8,cy-2,(222,226,234)); el(d,cx-16,cy-10,cx-9,cy-3,(30,40,60))
        d.line([(cx-12,cy-7),(cx-12,cy-9)],fill=(230,234,240)); d.line([(cx-12,cy-7),(cx-10,cy-7)],fill=ACCENT)
        rr(d,cx+7,cy-11,cx+18,cy-2,(236,240,246)); rr(d,cx+7,cy-11,cx+18,cy-9,RED)
        for gx in (cx+9,cx+12,cx+15):
            for gy in (cy-7,cy-5): d.point((gx,gy),fill=(180,160,160))
    elif s==3:      # faint / dizzy head
        el(d,cx-8,cy-6,cx+8,cy+10,(242,201,170))
        d.line([(cx-5,cy,),(cx-2,cy)],fill=(120,80,60)); d.line([(cx+2,cy),(cx+5,cy)],fill=(120,80,60))
        rr(d,cx-2,cy+4,cx+2,cy+6,(180,120,100))
        for sx,sy in [(cx-12,cy-8),(cx+11,cy-7),(cx+13,cy+3)]:
            d.line([(sx-2,sy),(sx+2,sy)],fill=AMBER); d.line([(sx,sy-2),(sx,sy+2)],fill=AMBER)
    elif s==4:      # blood bag + syringe
        rr(d,cx-15,cy-10,cx-5,cy+6,BLOOD); rr(d,cx-15,cy-10,cx-5,cy-7,BLOOD_D); d.line([(cx-10,cy+6),(cx-10,cy+12)],fill=(180,226,238))
        rr(d,cx+1,cy-2,cx+15,cy+2,(238,240,246)); rr(d,cx+1,cy-2,cx+8,cy+2,(200,214,230))
        d.line([(cx+15,cy),(cx+20,cy)],fill=GLASS); rr(d,cx-2,cy-1,cx+1,cy+1,GLASS)
    else:           # previous PPH -> recurrence risk
        rr(d,cx-12,cy-11,cx+4,cy+9,(238,240,246))
        for ly in range(cy-7,cy+7,4): d.line([(cx-9,ly),(cx+1,ly)],fill=(176,186,200))
        el(d,cx-6,cy-6,cx-2,cy-1,BLOOD)
        d.arc([cx+2,cy-7,cx+17,cy+8],20,320,fill=AMBER,width=2); d.polygon([(cx+15,cy-6),(cx+19,cy-8),(cx+17,cy-2)],fill=AMBER)

def chip(d,s,t):
    cx,cy=158,114; pulse=0.5+0.5*math.sin(2*math.pi*t/3.0)
    x0,y0,x1,y1=cx-26,cy-24,cx+26,cy+24
    rr(d,x0,y0,x1,y1,(44,34,40)); rr(d,x0,y0,x1,y0+2,BLOOD_H)
    d.rectangle([x0,y0,x1,y1],outline=lerp((120,70,80),AMBER,pulse))
    icon(d,s,cx,cy)
    cw=TLX.w(STATUS[s],'small'); TLX.add(cx-cw/2,y1+3,STATUS[s],(236,180,150),'small')

def red_flags(d,x,y,w):
    rr(d,x,y,x+w,y+40,(46,30,34)); rr(d,x,y,x+w,y+2,(140,60,66))
    TLX.add(x+6,y+3,"RED FLAGS:",(236,150,160),'tiny')
    TLX.add(x+6,y+16,"pad soaked <1h  *  flooding",(214,180,186),'tiny')
    TLX.add(x+6,y+27,"big clots  *  dizzy / faint",(214,180,186),'tiny')

def panel(d,x,y,w,cur):
    h=23+len(ITEMS)*19+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"BLEEDING Hx",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+15,(252,240,176))
        rr(d,x+7,ry+2,x+15,ry+10,(250,250,250)); d.rectangle([x+7,ry+2,x+15,ry+10],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+6),(x+10,ry+9)],fill=TICK); d.line([(x+10,ry+9),(x+15,ry+1)],fill=TICK)
        TLX.add(x+20,ry+1,it, INK if (done or now) else INKDIM,'small')
        ry+=19

def render(t):
    TLX.cmds=[]
    s=int(t//2)%6
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    jug(d,t)
    chip(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,96,["DID YOU BLEED","HEAVILY AFTER?"],300)
    TLX.add(40,30,"AFTER DELIVERY - THE BLEEDING",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,22,136,s)
    TLX.add(390,13,"HISTORY",(150,150,162),'small')
    red_flags(d,36,196,172)
    TLX.add(214,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(214,254,PEARL[s],(206,186,192),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"POST-PARTUM BLEEDING",(10,14,24),'body'); TLX.add(16,5,"POST-PARTUM BLEEDING",TEXT,'body')
    TLX.add(16.4,21.3,"ASK HOW MUCH, HOW FAST",(10,14,24),'small'); TLX.add(16,21,"ASK HOW MUCH, HOW FAST",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b11_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat11_pph_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
