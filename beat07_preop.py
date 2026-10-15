"""Beat 7 - CAESAREAN PRE-OP. Pregnant patient being prepped for theatre; each pre-op
step DEPICTED in turn (elective/emergency, fetal-heart CTG, investigations, crossmatch,
IV access, catheter) with a pre-op checklist ticking. 480x270 -> 4K, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; CROSSR=(214,70,80); ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
RED=(214,60,70); BLOODC=(190,40,52); ECG=(78,230,150); IVC=(120,132,150); BAG=(150,214,180); URINE=(236,214,120)
ITEMS=["ELECTIVE/EMERGENCY","FETAL HEART (CTG)","INVESTIGATIONS","BLOOD CROSSMATCH","IV ACCESS","CATHETER"]
PEARL=["ELECTIVE (PLANNED) vs EMERGENCY - AND WHY",
       "FETAL MOVEMENT & FETAL HEART CHECKED",
       "BLOODS / INVESTIGATIONS SENT",
       "BLOOD CROSSMATCHED FOR THE OPERATION",
       "IV FLUIDS / DRUGS RUNNING",
       "URINARY CATHETER INSERTED"]

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72))
    rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,CROSSR); rr(d,438,27,448,31,CROSSR)
    BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def checklist(d,x,y,w,h,cur,t):
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"PRE-OP CHECKLIST",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+15,(252,240,176))
        # checkbox
        rr(d,x+7,ry+2,x+15,ry+10,(250,250,250)); d.rectangle([x+7,ry+2,x+15,ry+10],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+6),(x+10,ry+9)],fill=TICK); d.line([(x+10,ry+9),(x+15,ry+1)],fill=TICK)
        TLX.add(x+20,ry+1,it, INK if (done or now) else INKDIM,'small')
        ry+=19

def depict(d,s,t):
    # on/around the pregnant patient (belly ~ (150,150), blanket y172, hand ~ (118,166))
    if s==0:      # elective vs emergency badges
        rr(d,120,96,150,116,(70,110,180)); TLX.add(124,99,"PLAN",(235,240,250),'tiny')  # calendar-ish
        rr(d,122,98,148,102,(110,150,210))
        d.polygon([(168,116),(184,116),(176,98)],fill=RED); TLX.add(174,108,"!",(255,255,255),'tiny')  # alarm
        TLX.add(154,118,"vs",TEXTDIM,'tiny')
    elif s==1:    # fetal heart CTG on belly + trace
        rr(d,146,140,162,152,(60,70,96)); d.line([(154,152),(150,168)],fill=IVC)   # probe + strap
        prev=None
        for sx in range(170,220):
            ph=((sx-170)/50+t*0.9)%1.0; yy=120
            if 0.45<ph<0.5: yy=112
            elif 0.5<=ph<0.55: yy=126
            if prev is not None: a,b=sorted((prev,yy)); rr(d,sx,a,sx,b,ECG)
            d.point((sx,yy),fill=ECG); prev=yy
        TLX.add(174,100,"140 bpm",ECG,'tiny')
    elif s==2:    # investigations - test tubes on a tray
        rr(d,250,196,296,204,(90,100,124))
        for i,c in enumerate([(200,80,90),(120,160,210),(220,200,110)]):
            rr(d,256+i*12,180,262+i*12,198,(220,228,236)); rr(d,256+i*12,190,262+i*12,198,c)
    elif s==3:    # blood crossmatch bag
        rr(d,40,92,54,116,BLOODC); rr(d,40,92,54,96,(150,30,42)); d.line([(47,116),(47,150)],fill=IVC)
        TLX.add(42,100,"O+",(255,235,235),'tiny')
    elif s==4:    # IV access
        BR.iv_pole(d,40,t)
        d.line([(40,118),(70,150),(116,164)],fill=BAG)   # line to hand
        el(d,112,162,122,170,(242,201,170)); rr(d,116,163,120,167,(150,170,185))  # cannula on hand
    else:         # catheter + urine bag
        d.line([(170,190),(230,198),(240,210)],fill=URINE)       # tube
        rr(d,236,208,252,228,(236,228,160)); rr(d,236,208,252,212,(210,200,120))  # urine bag

def render(t):
    TLX.cmds=[]
    s=int(t//2)%6
    frame=scene_bg()
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    breath=1.2*(0.5+0.5*math.sin(2*math.pi*t/3.6))
    BR.mother(d,t,0.0,breath,1.0 if (t%3.6)>3.46 else 0.0,0.0,1.0,0.0)   # pregnant (belly), pre-op
    depict(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    # ASK
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,98,["WHAT WAS DONE","BEFORE THE OPERATION?"],300)
    # header + current item label
    TLX.add(40,30,"CAESAREAN - PREPARING FOR THE OPERATION",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    # checklist panel (top-right)
    checklist(d,340,26,134,135,s,t)
    TLX.add(392,17,"CHECKLIST",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[s],(172,180,198),'small')
    # title
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"C-SECTION PRE-OP",(10,14,24),'body'); TLX.add(16,5,"C-SECTION PRE-OP",TEXT,'body')
    TLX.add(16.4,21.3,"PREP, THEN CHECK",(10,14,24),'small'); TLX.add(16,21,"PREP, THEN CHECK",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b7_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat07_preop_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
