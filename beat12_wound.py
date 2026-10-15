"""Beat 12 - WOUND INSPECTION (Part C). Modest close-up of the sutured C-section wound
(skin band + incision + staples) in a framed panel; each sign of trouble cycles as an
annotation on the wound - tenderness, redness/warmth, swelling, discharge/pus, gaping
(breakdown), bleeding. 480x270 -> 4K, 24fps, 12s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(22,28,42); WALL2=(30,38,56); FLOOR=(28,38,56); FLOORH=(40,52,72)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
SKIN=BR.SKIN; SKIN_H=(250,216,188); SKIN_D=BR.SKIN_D; INC=(150,66,66); STAPLE=(176,184,202)
RED=(214,60,70); REDSKIN=(220,118,114); AMBER=(236,172,92); PUS=(236,216,120); BLOOD=(176,34,48)
ITEMS=["PAIN / TENDER","REDNESS / WARMTH","SWELLING","DISCHARGE / PUS","GAPING (BREAKDOWN)","BLEEDING / OOZE"]
STATUS=["TENDER","RED / WARM","SWOLLEN","DISCHARGE","GAPING","BLEEDING"]
PEARL=["IS THE WOUND TENDER TO TOUCH?",
       "RED, WARM EDGES = INFLAMMATION",
       "SWELLING / FIRM LUMP (HAEMATOMA?)",
       "PUS OR DISCHARGE = WOUND INFECTION",
       "WOUND EDGES SEPARATING = BREAKDOWN",
       "FRESH BLEEDING OR OOZING FROM WOUND"]

def wound_panel(d,s,t):
    x0,y0,x1,y1=44,84,214,178
    rr(d,x0,y0,x1,y1,(38,44,62)); rr(d,x0,y0,x1,y0+2,(72,80,102)); d.rectangle([x0,y0,x1,y1],outline=(72,80,102))
    sx0,sx1,sy0,sy1=52,206,116,166
    rr(d,sx0,sy0,sx1,sy1,SKIN); rr(d,sx0,sy0,sx1,sy0+3,SKIN_H); rr(d,sx0,sy1-3,sx1,sy1,SKIN_D)
    iy=142; ix0,ix1=70,188; cxp=129
    if s==1:   # erythema band
        rr(d,sx0+4,iy-13,sx1-4,iy+13,REDSKIN); rr(d,sx0+4,iy-13,sx1-4,iy-10,(236,150,146))
    if s==2:   # swelling - raised puffy band + outward arrows
        for yy in range(iy-16,iy+17):
            w=int(66*math.cos((yy-iy)/17*math.pi/2))
            rr(d,cxp-w,yy,cxp+w,yy,lerp(SKIN,SKIN_H,0.5))
        for ax in (92,166):
            d.line([(ax,iy-18),(ax,iy-24)],fill=ACCENT,width=2); d.polygon([(ax,iy-26),(ax-3,iy-22),(ax+3,iy-22)],fill=ACCENT)
            d.line([(ax,iy+18),(ax,iy+24)],fill=ACCENT,width=2); d.polygon([(ax,iy+26),(ax-3,iy+22),(ax+3,iy+22)],fill=ACCENT)
    # incision + staples (gaping breaks the middle)
    if s==4:
        d.line([(ix0,iy),(116,iy)],fill=INC,width=2); d.line([(162,iy),(ix1,iy)],fill=INC,width=2)
        el(d,116,iy-6,162,iy+6,(120,50,54)); el(d,120,iy-4,158,iy+4,(150,64,66))   # open (modest)
        for sxp in list(range(ix0+6,112,12))+list(range(166,ix1,12)):
            d.line([(sxp,iy-5),(sxp,iy+5)],fill=STAPLE)
        d.line([(132,iy-10),(126,iy-14)],fill=AMBER); d.line([(146,iy-10),(152,iy-14)],fill=AMBER)   # edges parting
    else:
        d.line([(ix0,iy),(ix1,iy)],fill=INC,width=2)
        for sxp in range(ix0+6,ix1,12): d.line([(sxp,iy-5),(sxp,iy+5)],fill=STAPLE)
    if s==0:   # pain starburst
        for a in range(0,360,45):
            ar=math.radians(a); d.line([(cxp+int(7*math.cos(ar)),iy+int(7*math.sin(ar))),(cxp+int(15*math.cos(ar)),iy+int(15*math.sin(ar)))],fill=AMBER,width=2)
    elif s==3: # discharge / pus droplet at a staple
        el(d,148,iy-3,156,iy+3,PUS); el(d,150,iy+2,155,iy+9,PUS); el(d,151,iy+8,154,iy+13,PUS)
    elif s==5: # bleeding - stained gauze over part of wound
        rr(d,150,iy-11,188,iy+9,(238,240,246)); rr(d,150,iy-11,188,iy-9,(214,218,228))
        el(d,158,iy-3,176,iy+5,BLOOD); el(d,164,iy+2,172,iy+8,(150,24,38))
        el(d,110,iy-2,124,iy+4,BLOOD)   # ooze on open skin
    TLX.add(x0+4,y0-11,"CLOSE-UP",(150,160,180),'tiny')
    cw=TLX.w(STATUS[s],'small'); TLX.add((x0+x1)/2-cw/2,y1+4,STATUS[s],(236,200,150),'small')

def note(d,x,y,w):
    rr(d,x,y,x+w,y+40,(40,30,34)); rr(d,x,y,x+w,y+2,(130,70,74))
    TLX.add(x+6,y+3,"INFECTION:",(236,150,160),'tiny'); TLX.add(x+72,y+3,"red * warm * swollen * pus * fever",(214,180,186),'tiny')
    TLX.add(x+6,y+16,"BREAKDOWN:",(236,180,140),'tiny'); TLX.add(x+80,y+16,"edges gaping",(214,186,180),'tiny')
    TLX.add(x+6,y+28,"BLEEDING:",(236,150,160),'tiny'); TLX.add(x+72,y+28,"fresh ooze / haematoma",(214,180,186),'tiny')

def panel(d,x,y,w,cur):
    h=23+len(ITEMS)*19+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"WOUND CHECK",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
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
    wound_panel(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,96,["HOW IS THE","WOUND HEALING?"],300)
    TLX.add(40,30,"CHECKING THE C-SECTION SCAR",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,22,136,s)
    TLX.add(392,13,"INSPECT",(150,150,162),'small')
    note(d,36,196,230)
    TLX.add(286,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(286,254,PEARL[s],(206,186,192),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"C-SECTION WOUND",(10,14,24),'body'); TLX.add(16,5,"C-SECTION WOUND",TEXT,'body')
    TLX.add(16.4,21.3,"LOOK AT THE SCAR",(10,14,24),'small'); TLX.add(16,21,"LOOK AT THE SCAR",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b12_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat12_wound_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
