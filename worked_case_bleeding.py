"""WORKED CASE - antepartum VAGINAL BLEEDING (? placenta praevia), grounded in the 100-cases book
(p.108: 25y, 2 prev CS, 32wk, painless bleeding, drops->large+clots, prior bleed at 19wk, low-lying).
Bedside: PREGNANT patient (still antepartum) + pigeon doctor; CHIEF COMPLAINT (gold) then HOPI - the
bleed characterised, each via headline Q -> patient answers -> it records. 480x270 -> 4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24
INTRO=3.0; SD=4.5; OUTRO=5.0; NS=8; DUR=INTRO+NS*SD+OUTRO
TLX=uitext.TL()
GOLD=(230,186,96); GOLDB=(236,204,140); CYAN=(0,188,204); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM
RED=(226,92,96); REDB=(242,150,150)

CCF=[("COMPLAINT","Vaginal bleeding"),("DURATION","A few hours")]
HOF=[("ONSET / AMOUNT","Drops -> large + clots"),("PAIN?","Painless  (praevia)"),
     ("CONTRACTIONS","None"),("DIZZY / FAINT?","Light-headed"),
     ("FETAL MOVEMENTS","Good"),("BEFORE / CAUSE","Bled 19wk; low-lying")]

Q=[["What brought","you in today?"],["How long has","it been going?"],["How much - and","any clots?"],
   ["Any pain with","the bleeding?"],["Any tightenings","or contractions?"],["Felt dizzy","or faint?"],
   ["Is the baby","still moving?"],["Happened before","- any trigger?"]]
PATIENT=[["I've been","bleeding"],["Just a few","hours"],["Drops, then a","lot - with clots"],
   ["No, no pain","at all"],["No tightenings"],["A little","light-headed"],
   ["Yes, moving","well"],["Once, at 19wk","- low-lying"]]
PHASE=["CHIEF COMPLAINT","CHIEF COMPLAINT","HOPI  -  THE BLEED","HOPI  -  THE BLEED","HOPI  -  THE BLEED",
       "HOPI  -  THE BLEED","HOPI  -  THE BLEED","HOPI  -  THE BLEED"]

def seg(t):
    if t<INTRO: return -1,0.0,0.0
    st=t-INTRO
    if st>=NS*SD: return NS,1.0,SD
    gi=int(st//SD); local=st-gi*SD; return gi,smooth((local-1.9)/1.3),local

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),(16,20,30)); d=ImageDraw.Draw(im)
    warmth=0.80
    BR.background(d,t*0.3,warmth)
    BR.nightstand(d,30,196,flowers=1.0)
    BR.bed(d)
    br=1.4*(0.5+0.5*math.sin(2*math.pi*t/4.5))
    BR.mother(d,t,ctr=0.0,breath=br,eye=0.0,sweat=0.0,warmth=warmth,holdbaby=0.0)   # PREGNANT (antepartum)
    BR.iv_pole(d,250,t)                                                              # transfusion line
    gi,fill,local=seg(t)
    BR.student(d,278,252,t=t,writing=1.0)
    # phase banner
    if 0<=gi<NS:
        ph=PHASE[gi]
        TLX.add(14,7,ph,lerp((16,20,30),(GOLDB if gi<2 else CYAN),1.0),'small')
    elif gi<0:
        TLX.add(14,7,"TAKING THE HISTORY",TEXT,'small'); TLX.add(14,21,"vaginal bleeding  -  ? placenta praevia",TEXTDIM,'tiny')
    else:
        TLX.add(14,7,"BLEEDING HISTORY  -  DONE",lerp((16,20,30),REDB,1.0),'small')

    # ---- sheets ----
    if gi<0: cca,ccf,hoa,hof=-1,0.0,-1,0.0
    elif gi>=NS: cca,ccf,hoa,hof=2,1.0,6,1.0
    elif gi<2: cca,ccf,hoa,hof=gi,fill,-1,0.0
    else: cca,ccf,hoa,hof=2,1.0,gi-2,fill
    sx=294
    hud.history_sheet(d,TLX,sx,38,178,66,"CHIEF COMPLAINT",CCF,cca,ccf,t)
    rr(d,sx,35,sx+178,37,GOLD)
    hud.history_sheet(d,TLX,sx,112,178,152,"HOPI  -  THE BLEED",HOF,hoa,hof,t)
    rr(d,sx,109,sx+178,111,CYAN)

    # ---- doctor asks  ->  patient answers ----
    if 0<=gi<NS:
        if local<1.3:
            hud.speech_bubble(d,TLX,176,148,Q[gi],272,size='small')
        else:
            hud.speech_bubble(d,TLX,116,92,PATIENT[gi],122,size='small')

    # ---- outro: sober red-flag card (no celebration - she's actively bleeding) ----
    if gi>=NS:
        tc=t-(INTRO+NS*SD); na=smooth(tc/0.5)
        cardc=lerp((16,20,30),(30,22,26),na)
        rr(d,10,34,292,120,cardc); d.rectangle([10,34,292,120],outline=lerp((16,20,30),RED,na))
        # red-flag mark
        el(d,22,46,34,58,lerp(cardc,RED,na)); TLX.add(26.5,47.5,"!",lerp(cardc,(255,240,240),na),'small')
        TLX.add(42,47,"BLEEDING HISTORY COMPLETE",lerp(cardc,REDB,na),'small')
        TLX.add(24,66,"painless + fresh red + low-lying  ->  ? placenta praevia",lerp(cardc,(226,206,210),na),'tiny')
        TLX.add(24,80,"next:  resuscitate  *  NO vaginal exam  *  assess fetus",lerp(cardc,(236,200,150),na),'tiny')
        TLX.add(24,96,"then the backbone continues:",lerp(cardc,TEXTDIM,na),'tiny')
        TLX.add(24,107,"ROS * current pregnancy * past obstetric * gynae ...",lerp(cardc,(190,196,210),na),'tiny')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/wcb_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/worked_case_bleeding_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
