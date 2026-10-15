"""Beat 2 - SITE: where did she deliver? Same patient in a HOME bedroom vs a
HOSPITAL room, seamless cross-fade loop. Reuses the cast from birth_recovery.
480x270 x8 -> 4K, 24fps, 12s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, text, lerp, smooth, FONT, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()   # crisp 4K pixel-font text layer

# ---- home palette ----
HWALL=(58,44,54); HWALL2=(72,56,66); HFLOOR=(78,58,46); HFLOORH=(96,72,56)
WOOD=(146,100,66); WOOD_D=(112,76,50); WOOD_H=(174,124,86)
CURTAIN=(206,138,150); CURTAIN_D=(172,108,122); CURTAIN_H=(226,162,172)
DAYSKY=(150,202,230); DAYSKY2=(190,224,244); CLOUD=(236,244,250)
LAMP=(246,214,120); LAMPGLOW=(255,232,150); LAMPBASE=(120,96,80)
PLANT=(90,164,104); PLANT_D=(66,130,80); POT=(176,112,80); POT_D=(140,86,60)
PICF=(120,82,56); PICIMG=(130,196,210); SUN=(246,206,120)
HEARTC=(236,110,130); WHITE=BR.WHITE; MAT=BR.MAT; MAT_D=BR.MAT_D
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; DARK=BR.DARK

def tri(p): return p*2 if p<0.5 else 2-2*p

def home_bed(d):
    rr(d,66,210,72,230,WOOD_D); rr(d,250,210,256,230,WOOD_D)      # legs
    rr(d,60,196,262,212,WOOD); rr(d,60,196,262,198,WOOD_H)        # base
    rr(d,62,170,260,196,MAT); rr(d,62,193,260,196,MAT_D)          # mattress
    rr(d,52,146,64,212,WOOD); rr(d,52,146,64,149,WOOD_H)          # wooden headboard
    rr(d,52,146,64,148,WOOD_H); el(d,52,142,64,150,WOOD)          # rounded top

def home_bg(t):
    im=Image.new('RGB',(GW,GH),HWALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,HWALL2); rr(d,0,150,GW-1,151,(90,68,78))
    rr(d,0,181,GW-1,GH-1,HFLOOR); rr(d,0,181,GW-1,183,HFLOORH)
    # rug under bed
    el(d,120,214,300,236,(150,96,110)); el(d,140,218,280,232,(176,120,134))
    # window + daylight + curtains
    rr(d,30,26,110,92,WOOD_D); rr(d,33,29,107,89,DAYSKY); rr(d,33,29,107,54,DAYSKY2)
    el(d,48,44,70,56,CLOUD); el(d,80,60,98,70,CLOUD)
    rr(d,69,29,70,89,WOOD_D); rr(d,33,58,107,59,WOOD_D)
    rr(d,24,22,38,98,CURTAIN); rr(d,24,22,27,98,CURTAIN_H); rr(d,35,22,38,98,CURTAIN_D)
    rr(d,102,22,116,98,CURTAIN); rr(d,102,22,105,98,CURTAIN_H); rr(d,113,22,116,98,CURTAIN_D)
    # framed picture (sun over hills)
    rr(d,154,28,188,58,PICF); rr(d,157,31,185,55,PICIMG)
    el(d,176,36,184,44,SUN); rr(d,157,48,185,55,(110,170,120))
    # wall shelf w/ tiny books
    rr(d,210,40,248,43,WOOD_D)
    for i,c in enumerate([(200,90,90),(90,150,200),(120,190,120),(220,200,110)]):
        rr(d,212+i*8,30,218+i*8,40,c)
    # potted plant (left foreground)
    rr(d,28,196,46,214,POT); rr(d,28,196,46,199,(196,134,100)); rr(d,28,210,46,214,POT_D)
    for dx,dy in [(-6,-16),(0,-22),(6,-16),(-3,-20),(3,-20)]:
        el(d,37+dx-3,196+dy-3,37+dx+3,196+dy+3,PLANT)
    rr(d,36,180,38,196,PLANT_D)
    home_bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def hosp_bg(t):
    im=Image.new('RGB',(GW,GH),BR.WALL_C); d=ImageDraw.Draw(im)
    BR.background(d,t,0.0)
    BR.iv_pole(d,44,t); BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def icon_home(d,x,y,c):
    d.polygon([(x,y+6),(x+7,y),(x+14,y+6)],fill=c); rr(d,x+2,y+6,x+12,y+14,c); rr(d,x+5,y+9,x+9,y+14,DARK)
def icon_hosp(d,x,y,c):
    rr(d,x,y,x+14,y+14,c); rr(d,x+6,y+2,x+8,y+6,(230,80,90)); rr(d,x+4,y+3,x+10,y+5,(230,80,90))

def badge(d,txt,icon,cx,yb,on):
    if on<0.5: return
    w=len(txt)*4+26; x0=cx-w//2
    rr(d,x0,yb,x0+w,yb+20,(16,18,30)); rr(d,x0,yb,x0+w,yb+1,ACCENT)
    icon(d,x0+5,yb+3,TEXT); text(d,txt,x0+22,yb+7,TEXT)

def render(t):
    TLX.cmds=[]
    # loop blend: home[0-4] cross[4-6] hosp[6-10] cross[10-12]->home
    if t<4: b=0.0
    elif t<6: b=smooth((t-4)/2)
    elif t<10: b=1.0
    else: b=1-smooth((t-10)/2)
    H=home_bg(t); X=hosp_bg(t)
    frame=(H*(1-b)+X*b)
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,1.0,1.0)
    BR.student(d,300,232,t=t,writing=1.0)
    # ---- exchange: ASK -> ANSWER -> RECORD, per phase, loop-safe ----
    loc = "HOME" if b<0.5 else "HOSPITAL"; homep = b<0.5
    if homep: ask_on=0.3<=t<4.2; ans_on=1.9<=t<4.2; rf=smooth((t-2.4)/1.2)
    else:     ask_on=6.2<=t<10.2; ans_on=7.7<=t<10.2; rf=smooth((t-8.1)/1.2)
    if ask_on:
        TLX.add(236,74,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,228,84,["WHERE DID YOU","DELIVER?"],300)
    if ans_on:
        TLX.add(32,76,"ANSWER",(236,120,142),'small')
        hud.speech_bubble(d,TLX,28,86,(["AT HOME"] if homep else ["IN HOSPITAL"]),96)
    fields=[("SITE",loc),("ROUTE",""),("DIFFICULTY",""),("EPISIOTOMY",""),("ANAESTHESIA","")]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,0,max(0.0,min(1.0,rf)),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    if ask_on:
        TLX.add(140,245,"WHY IT MATTERS:",(0,180,196),'small')
        TLX.add(140,254,("HOME - LESS MONITORING" if homep else "HOSPITAL - IMMEDIATE SUPPORT"),(172,180,198),'small')
    # title (shadow + main for readability over the window)
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"SITE OF DELIVERY",(10,14,24),'body'); TLX.add(16,5,"SITE OF DELIVERY",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN RECORD",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN RECORD",TEXTDIM,'small')
    # ---- upscale to 4K, draw crisp text ----
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big)
    TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b2_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat02_site_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
