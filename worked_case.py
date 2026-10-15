"""FULL WORKED CASE - elective CS, previous 2 scars (real case, grounded in the 100-cases book).
Bedside: recovering mother + pigeon doctor; two sheets fill live - CHIEF COMPLAINT (gold) then
HOPI labour (pre-op -> intra-op -> post-op), each via headline Q -> answer types in. 480x270->4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24
INTRO=3.0; SD=4.5; OUTRO=4.5; NS=8; DUR=INTRO+NS*SD+OUTRO
TLX=uitext.TL()
GOLD=(230,186,96); GOLDB=(236,204,140); CYAN=(0,188,204); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM

CCF=[("COMPLAINT","Elective caesarean"),("INDICATION","Previous 2 scars")]
HOF=[("PRE-OP","IV line, catheter"),("INTRA-OP","General anaesth., ~1h"),
     ("COMPLICATIONS","None"),("POST-OP","Awake 30m, ate 6h, walked 2h"),
     ("BLEEDING","No heavy bleeding"),("BOWEL / GAS","Not passed yet")]

def tiny_heart(d,cx,cy,r,c):
    el(d,cx-r,cy-r,cx,cy+int(r*0.5),c); el(d,cx,cy-r,cx+r,cy+int(r*0.5),c)
    d.polygon([(cx-r,cy),(cx+r,cy),(cx,cy+r+1)],fill=c)
Q=[["What brought","you in today?"],["Why was it a","caesarean?"],["How were you","prepared for it?"],
   ["What happened","during the op?"],["Any problems","during it?"],["How has your","recovery been?"],
   ["Any heavy","bleeding after?"],["Passed motion","or gas yet?"]]
PATIENT=[["I had a planned","caesarean"],["I'd had two","before"],["A drip and","a catheter"],
   ["Asleep - about","an hour"],["No, it went","fine"],["Woke soon, ate,","then walked"],
   ["No, nothing","heavy"],["Not yet"]]
PHASE=["CHIEF COMPLAINT","CHIEF COMPLAINT","HOPI  -  PRE-OP","HOPI  -  INTRA-OP","HOPI  -  INTRA-OP",
       "HOPI  -  POST-OP","HOPI  -  POST-OP","HOPI  -  POST-OP"]

def seg(t):
    if t<INTRO: return -1,0.0,0.0
    st=t-INTRO
    if st>=NS*SD: return NS,1.0,SD
    gi=int(st//SD); local=st-gi*SD; return gi,smooth((local-1.9)/1.3),local

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),(16,20,30)); d=ImageDraw.Draw(im)
    warmth=0.82
    BR.background(d,t*0.3,warmth)
    BR.nightstand(d,30,196,flowers=1.0)
    BR.bed(d)
    br=1.4*(0.5+0.5*math.sin(2*math.pi*t/4.5))
    BR.mother(d,t,ctr=0.0,breath=br,eye=0.0,sweat=0.0,warmth=warmth,holdbaby=1.0)
    BR.iv_pole(d,250,t)
    gi,fill,local=seg(t)
    dfy=252
    if gi>=NS: dfy=252-int(5*abs(math.sin((t-(INTRO+NS*SD))*5.0)))   # happy hop at the end
    BR.student(d,278,dfy,t=t,writing=1.0)
    # phase banner
    if 0<=gi<NS:
        ph=PHASE[gi]; pa=smooth(local/0.3)*smooth((SD-local)/0.3) if local>0 else 1.0
        TLX.add(14,7,ph,lerp((16,20,30),(GOLDB if gi<2 else CYAN),1.0),'small')
    elif gi<0:
        TLX.add(14,7,"TAKING THE HISTORY",TEXT,'small'); TLX.add(14,21,"elective CS  -  previous 2 scars",TEXTDIM,'tiny')
    else:
        TLX.add(14,7,"LABOUR HISTORY  -  DONE",lerp((16,20,30),(120,220,160),1.0),'small')

    # ---- sheets ----
    if gi<0: cca,ccf,hoa,hof=-1,0.0,-1,0.0
    elif gi>=NS: cca,ccf,hoa,hof=2,1.0,6,1.0
    elif gi<2: cca,ccf,hoa,hof=gi,fill,-1,0.0
    else: cca,ccf,hoa,hof=2,1.0,gi-2,fill
    # chief complaint sheet (gold header tag)
    sx=294
    hud.history_sheet(d,TLX,sx,38,178,66,"CHIEF COMPLAINT",CCF,cca,ccf,t)
    rr(d,sx,35,sx+178,37,GOLD)
    # hopi labour sheet
    hud.history_sheet(d,TLX,sx,112,178,152,"HOPI  -  LABOUR",HOF,hoa,hof,t)
    rr(d,sx,109,sx+178,111,CYAN)

    # ---- doctor asks  ->  patient answers ----
    if 0<=gi<NS:
        if local<1.3:
            hud.speech_bubble(d,TLX,176,148,Q[gi],272,size='small')       # doctor asks
        else:
            hud.speech_bubble(d,TLX,116,92,PATIENT[gi],122,size='small')  # patient answers

    # ---- outro note ----
    if gi>=NS:
        tc=t-(INTRO+NS*SD); na=smooth(tc/0.5); hb=abs(math.sin(tc*5))
        # confetti over the scene (left of the sheets)
        rc=np.random.default_rng(3); xs=rc.uniform(12,286,46); spd=rc.uniform(22,46,46); ofs=rc.uniform(0,250,46)
        cols=[(236,196,110),(0,188,204),(236,120,150),(120,210,150)]
        for i in range(46):
            cy=int((tc*spd[i]+ofs[i])%252)+14; cx=int(xs[i]); s=1+(i%2)
            d.rectangle([cx,cy,cx+s,cy+s],fill=cols[i%4])
        # cute success emotes bobbing above mother & doctor
        tiny_heart(d,96,int(106-7*hb),5,(236,120,150))
        tiny_heart(d,278,int(196-7*hb),4,(236,196,110))
        for a in (0,120,240):
            ar=math.radians(a+tc*140)
            d.point((96+int(15*math.cos(ar)),int(106-7*hb)+int(14*math.sin(ar))),fill=(252,240,180))
            d.point((278+int(13*math.cos(ar)),int(196-7*hb)+int(12*math.sin(ar))),fill=(252,240,180))
        # success card ABOVE the characters
        cardc=lerp((16,20,30),(22,28,42),na)
        rr(d,10,34,292,114,cardc); d.rectangle([10,34,292,114],outline=lerp((16,20,30),(90,210,150),na))
        d.line([(24,58),(31,66)],fill=(90,210,150),width=2); d.line([(31,66),(46,46)],fill=(90,210,150),width=2)
        TLX.add(56,50,"LABOUR HISTORY COMPLETE!",lerp(cardc,(150,230,180),na),'small')
        TLX.add(24,74,"then the backbone continues:",lerp(cardc,TEXTDIM,na),'tiny')
        TLX.add(24,88,"ROS * current pregnancy * past obstetric",lerp(cardc,(190,196,210),na),'tiny')
        TLX.add(24,100,"past gynae * medical * family * drug * social",lerp(cardc,(190,196,210),na),'tiny')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/wc_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/worked_case_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
