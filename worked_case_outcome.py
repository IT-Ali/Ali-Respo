"""WORKED CASE - the OUTCOME of delivery at the bedside. A recovered mother cradling her newborn +
pigeon examinee; the examinee asks the 'Outcome of Delivery' questions, she answers, and each records
to the OUTCOME sheet. Grounded in the 100-cases book's documented outcome facts (term, live female,
average birth weight, breastfeeding - elective-CS case p.87); the abnormal-screen items (colour,
special care) are the NORMAL answers for a healthy term baby, not invented pathology. APGAR is NOT
asked of the mother (it is a delivery-record item). 480x270 -> 4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24
INTRO=3.0; SD=4.5; OUTRO=5.5; NS=8; DUR=INTRO+NS*SD+OUTRO
TLX=uitext.TL()
GOLD=(230,186,96); GOLDB=(236,204,140); CYAN=(0,188,204); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM
GREENB=(120,220,160)

OUTF=[("NUMBER","One baby"),("SEX","A girl"),("LIVE / TERM","Live, at term"),
      ("BIRTH WEIGHT","Average"),("CRIED & MOVED","Yes, at once"),("COLOUR","Pink (normal)"),
      ("SPECIAL CARE","No - with mum"),("FEEDING","Breastfeeding")]

Q=[["How many","babies?"],["Boy or","girl?"],["Born alive","and at term?"],["How much","did she weigh?"],
   ["Did she cry","straight away?"],["What was","her colour?"],["Any special","care needed?"],
   ["How are you","feeding her?"]]
PATIENT=[["Just one"],["A girl"],["Yes - alive,","at term"],["Average","weight"],
   ["Yes, cried","at once"],["Pink,","normal"],["No, she's","here with me"],["Breast-","feeding"]]

def seg(t):
    if t<INTRO: return -1,0.0,0.0
    st=t-INTRO
    if st>=NS*SD: return NS,1.0,SD
    gi=int(st//SD); local=st-gi*SD; return gi,smooth((local-1.9)/1.3),local

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),(16,20,30)); d=ImageDraw.Draw(im)
    warmth=0.84
    BR.background(d,t*0.3,warmth)
    BR.nightstand(d,30,196,flowers=1.0)
    BR.bed(d)
    br=1.3*(0.5+0.5*math.sin(2*math.pi*t/4.5))
    BR.mother(d,t,ctr=0.0,breath=br,eye=0.0,sweat=0.0,warmth=warmth,holdbaby=1.0)   # recovered, cradling baby
    gi,fill,local=seg(t)
    dfy=252
    if gi>=NS: dfy=252-int(5*abs(math.sin((t-(INTRO+NS*SD))*5.0)))
    BR.student(d,278,dfy,t=t,writing=1.0)
    # phase banner
    if 0<=gi<NS:
        TLX.add(14,7,"OUTCOME OF DELIVERY",lerp((16,20,30),CYAN,1.0),'small')
        TLX.add(14,21,"the baby  -  record how it did",TEXTDIM,'tiny')
    elif gi<0:
        TLX.add(14,7,"CLOSING THE STORY",TEXT,'small'); TLX.add(14,21,"delivered  -  now the baby",TEXTDIM,'tiny')
    else:
        TLX.add(14,7,"OUTCOME  -  DONE",lerp((16,20,30),GREENB,1.0),'small')

    # ---- single OUTCOME sheet ----
    hoa = -1 if gi<0 else (NS if gi>=NS else gi)
    hof = 0.0 if gi<0 else (1.0 if gi>=NS else fill)
    sx=294
    hud.history_sheet(d,TLX,sx,40,178,194,"OUTCOME OF DELIVERY",OUTF,hoa,hof,t)
    rr(d,sx,37,sx+178,39,CYAN)

    # ---- examinee asks -> mother answers ----
    if 0<=gi<NS:
        if local<1.3:
            hud.speech_bubble(d,TLX,176,150,Q[gi],272,size='small')
        else:
            hud.speech_bubble(d,TLX,118,96,PATIENT[gi],124,size='small')

    # ---- outro: warm summary card ----
    if gi>=NS:
        tc=t-(INTRO+NS*SD); na=smooth(tc/0.5)
        cardc=lerp((16,20,30),(22,30,26),na)
        rr(d,10,36,286,118,cardc); d.rectangle([10,36,286,118],outline=lerp((16,20,30),GREENB,na))
        el(d,22,48,34,60,lerp(cardc,GREENB,na)); d.line([(25,54),(28,57)],fill=(16,20,30)); d.line([(28,57),(32,51)],fill=(16,20,30))
        TLX.add(42,49,"OUTCOME RECORDED",lerp(cardc,GREENB,na),'small')
        TLX.add(24,68,"one term, live girl  *  average weight  *  feeding well",lerp(cardc,(206,226,214),na),'tiny')
        TLX.add(24,82,"NICU? -> would ask why.   APGAR = from the birth record.",lerp(cardc,(236,210,150),na),'tiny')
        TLX.add(24,98,"delivery story closed  ->  next: current pregnancy * ROS * past obs ...",lerp(cardc,TEXTDIM,na),'tiny')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/wco_{tv}.png'); print("ok",tv,"dur",round(DUR,1))
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/worked_case_outcome_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
