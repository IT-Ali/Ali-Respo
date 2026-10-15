"""Beat 10 - POST-OP RECOVERY CHECK (Part C). Reuses our recovery-bed scene (mother
cradling baby). Eight recovery systems light up in turn - consciousness, nausea/appetite,
flatus/bowels, urine/catheter, IV/pain relief, mobilising, breastfeeding, fever - each as
a little icon card, with the recovery checklist ticking. 480x270 -> 4K, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
GREEN=(84,196,146); AMBER=(236,172,92); RED=(214,60,70); URINE=(236,214,120); MILK=(236,240,246)
WARM_WALL=(40,30,46); WARM_WALL2=(54,40,58); WARM_FLOOR=(46,38,56); DAWN=(240,180,120)
ITEMS=["CONSCIOUSNESS","NAUSEA / APPETITE","FLATUS / BOWELS","URINE / CATHETER","IV / PAIN RELIEF","MOBILISING","BREASTFEEDING","FEVER / TEMP"]
STATUS=["AWAKE","EATING","FLATUS OK","URINE OK","PAIN OK","WALKING","FEEDING","NO FEVER"]
PEARL=["IS SHE FULLY AWAKE & ORIENTATED?",
       "APPETITE BACK, NAUSEA/VOMITING SETTLING",
       "GUT WORKING - FLATUS FIRST, THEN BOWELS",
       "URINE OUTPUT GOOD / CATHETER REMOVED",
       "PAIN RELIEF WORKING + IV FLUIDS RUNNING",
       "EARLY MOBILISATION LOWERS CLOT RISK",
       "IS BREASTFEEDING ESTABLISHED?",
       "FEVER MAY MEAN INFECTION - CHECK"]

def recovery_bg(d):
    rr(d,0,0,GW-1,GH-1,WARM_WALL); rr(d,0,0,GW-1,70,WARM_WALL2)
    rr(d,0,150,GW-1,151,(50,42,58)); rr(d,0,181,GW-1,GH-1,WARM_FLOOR); rr(d,0,181,GW-1,183,(64,52,66))
    # window with soft dawn sky
    rr(d,28,26,112,92,(72,60,78)); rr(d,31,29,109,89,(90,70,80)); el(d,84,56,106,78,DAWN)
    rr(d,69,29,70,89,(72,60,78)); rr(d,31,58,109,59,(72,60,78))
    # wall clock (static, loop-safe) at ~10:10
    ccx,ccy=250,46
    el(d,ccx-12,ccy-12,ccx+12,ccy+12,(222,226,234)); el(d,ccx-10,ccy-10,ccx+10,ccy+10,(30,40,60))
    d.line([(ccx,ccy),(ccx-5,ccy-4)],fill=(236,240,246)); d.line([(ccx,ccy),(ccx+5,ccy-4)],fill=ACCENT)
    el(d,ccx-1,ccy-1,ccx+1,ccy+1,(236,240,246))
    rr(d,150,30,164,44,(236,240,246)); rr(d,155,32,159,42,(214,70,80)); rr(d,152,35,162,39,(214,70,80))

def catheter_bag(d,glow):
    # urine bag hung off the bed rail (lower right of bed)
    rr(d,238,200,252,222,(236,232,190)); rr(d,239,208,251,221,URINE); rr(d,238,200,252,203,(210,202,140))
    d.line([(214,192),(230,198),(240,200)],fill=URINE)     # catheter tube to bag
    if glow>0.3: d.rectangle([236,198,254,224],outline=AMBER)

def icon(d,s,cx,cy):
    if s==0:      # consciousness - open eye + alert sparks
        el(d,cx-10,cy-5,cx+10,cy+5,(246,248,252)); el(d,cx-4,cy-4,cx+4,cy+4,(40,60,96)); el(d,cx-2,cy-2,cx+2,cy+2,(10,16,28))
        for a in (-45,0,45):
            ar=math.radians(a-90); d.line([(cx+int(13*math.cos(ar)),cy+int(13*math.sin(ar))),(cx+int(17*math.cos(ar)),cy+int(17*math.sin(ar)))],fill=AMBER)
    elif s==1:    # appetite - plate + cutlery + steam
        el(d,cx-11,cy+2,cx+11,cy+8,(228,232,240)); el(d,cx-7,cy+2,cx+7,cy+6,(200,206,216))
        d.line([(cx-14,cy-4),(cx-14,cy+4)],fill=(210,214,224)); d.line([(cx+14,cy-4),(cx+14,cy+4)],fill=(210,214,224))
        for dx in (-3,2): d.line([(cx+dx,cy-8),(cx+dx+2,cy-11)],fill=(170,180,196))   # steam
    elif s==2:    # gut working - belly with intestine loop
        el(d,cx-11,cy-9,cx+11,cy+11,(242,201,170))
        d.arc([cx-7,cy-5,cx+1,cy+3],0,360,fill=(196,120,110),width=2); d.arc([cx-1,cy-1,cx+7,cy+7],0,360,fill=(196,120,110),width=2)
    elif s==3:    # urine / catheter - bag with fluid
        rr(d,cx-7,cy-9,cx+7,cy+11,(236,232,190)); rr(d,cx-6,cy+1,cx+6,cy+10,URINE); d.line([(cx,cy-13),(cx,cy-9)],fill=URINE)
    elif s==4:    # IV / pain relief - drip bag + pill
        rr(d,cx-9,cy-10,cx-1,cy+4,(150,214,180)); d.line([(cx-5,cy+4),(cx-5,cy+12)],fill=(180,226,238))
        el(d,cx+2,cy+1,cx+12,cy+9,(238,240,246)); d.line([(cx+7,cy+2),(cx+7,cy+8)],fill=(200,120,130)); d.line([(cx+3,cy+5),(cx+11,cy+5)],fill=(200,120,130))
    elif s==5:    # mobilising - walking figure
        el(d,cx-2,cy-12,cx+3,cy-7,(60,66,86)); rr(d,cx-1,cy-7,cx+2,cy+2,(86,148,198))
        d.line([(cx,cy+2),(cx-5,cy+11)],fill=(60,66,86),width=2); d.line([(cx+1,cy+2),(cx+7,cy+10)],fill=(60,66,86),width=2)
        d.line([(cx,cy-4),(cx-6,cy-1)],fill=(86,148,198),width=2); d.line([(cx+1,cy-4),(cx+7,cy-6)],fill=(86,148,198),width=2)
    elif s==6:    # breastfeeding - baby + milk drop + heart
        el(d,cx-9,cy-3,cx+3,cy+9,(244,214,204)); el(d,cx-6,cy-7,cx+2,cy+1,(242,201,170))
        el(d,cx+5,cy-2,cx+8,cy+2,MILK)
        d.polygon([(cx+9,cy-8),(cx+13,cy-8),(cx+11,cy-4)],fill=BR.HEART); el(d,cx+8,cy-9,cx+11,cy-6,BR.HEART); el(d,cx+11,cy-9,cx+14,cy-6,BR.HEART)
    else:         # fever - thermometer (normal, green)
        rr(d,cx-2,cy-12,cx+2,cy+6,(236,240,246)); el(d,cx-4,cy+4,cx+4,cy+12,GREEN); rr(d,cx-1,cy-6,cx+1,cy+8,GREEN)
        d.line([(cx+4,cy-8),(cx+8,cy-8)],fill=GREEN); d.line([(cx+4,cy-3),(cx+7,cy-3)],fill=GREEN)

def spotlight(d,s,t):
    # compact icon badge floating above the patient + short caption + arrow to her
    cx,cy=150,86; pulse=0.5+0.5*math.sin(2*math.pi*t/3.0)
    x0,y0,x1,y1=cx-22,cy-22,cx+22,cy+22
    rr(d,x0,y0,x1,y1,(252,246,224)); rr(d,x0,y0,x1,y0+2,AMBER)
    d.rectangle([x0,y0,x1,y1],outline=lerp(CREAM_D,AMBER,pulse))
    icon(d,s,cx,cy)
    # green check (corner)
    d.line([(x1-11,cy+8),(x1-8,cy+12)],fill=TICK,width=2); d.line([(x1-8,cy+12),(x1-2,cy+3)],fill=TICK,width=2)
    # caption centred under the badge
    cw=TLX.w(STATUS[s],'small'); TLX.add(cx-cw/2,y1+3,STATUS[s],(236,200,120),'small')
    # arrow down-left toward patient
    d.line([(x0+4,y1),(x0-12,y1+16)],fill=AMBER,width=2); d.polygon([(x0-12,y1+16),(x0-6,y1+13),(x0-8,y1+20)],fill=AMBER)

def panel(d,x,y,w,cur):
    h=23+len(ITEMS)*18+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"RECOVERY CHECK",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+14,(252,240,176))
        rr(d,x+7,ry+1,x+15,ry+9,(250,250,250)); d.rectangle([x+7,ry+1,x+15,ry+9],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+5),(x+10,ry+8)],fill=TICK); d.line([(x+10,ry+8),(x+15,ry)],fill=TICK)
        TLX.add(x+20,ry,it, INK if (done or now) else INKDIM,'small')
        ry+=18

def render(t):
    TLX.cmds=[]
    s=int(t//1.5)%8
    im=Image.new('RGB',(GW,GH),WARM_WALL); d=ImageDraw.Draw(im)
    recovery_bg(d)
    BR.iv_pole(d,44,t)
    if s==4: d.rectangle([37,98,52,118],outline=AMBER)        # highlight IV
    BR.bed(d)
    BR.nightstand(d,266,188,1.0)
    catheter_bag(d,1.0 if s==3 else 0.0)
    breath=1.2*(0.5+0.5*math.sin(2*math.pi*t/4.0))
    BR.mother(d,t,0.0,breath,0.0,0.0,1.0,1.0)                  # recovery: cradling baby, awake, calm
    if s==6: d.ellipse([100,150,116,166],outline=BR.HEART)   # highlight baby/feeding
    spotlight(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,96,["HOW IS HER","RECOVERY GOING?"],300)
    TLX.add(40,30,"AFTER THEATRE - CHECKING RECOVERY",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,20,138,s)
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[s],(200,188,196),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"POST-OP RECOVERY",(10,14,24),'body'); TLX.add(16,5,"POST-OP RECOVERY",TEXT,'body')
    TLX.add(16.4,21.3,"SYSTEMS COMING BACK",(10,14,24),'small'); TLX.add(16,21,"SYSTEMS COMING BACK",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b10_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat10_recovery_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
