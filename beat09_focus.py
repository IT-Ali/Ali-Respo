"""Beat 9 FOCUS/LOCKED variant - one HELD clip per indication (spotlight + tiny progress).
Each clip stays locked on a single concept (big centred visual, concept title, 'N / 6'
progress dots, one pearl) with gentle idle motion so it loops seamlessly - for talking
over as background B-roll. Renders all 6 clips in one run. 480x270 -> 4K, 24fps, 12s."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(22,27,42)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT
UTER=(206,142,152); UTER_D=(176,110,122); AMN=(228,198,208); OSC=(236,168,180)
BABY=(242,201,170); BABY_D=(206,160,128); PLAC=(150,52,66)
RED=(214,60,70); AMBER=(236,172,92); GREEN=(84,196,146); ECG=(96,230,150)
CX,CY,K=236,130,1.5
SHOW_CUE=False
NAMES=["PREVIOUS C-SECTION SCAR","BREECH / TRANSVERSE","PLACENTA PRAEVIA","FAILURE TO PROGRESS","FETAL COMPROMISE","NOT AN INDICATION"]
PEARL=["PREVIOUS UTERINE SCAR -> REPEAT SECTION",
       "BABY NOT HEAD-DOWN (BREECH OR LYING ACROSS)",
       "PLACENTA COVERS THE CERVIX - BLOCKS THE EXIT",
       "LABOUR STALLED DESPITE GOOD CONTRACTIONS",
       "BABY IN DISTRESS - DELIVER NOW",
       "'ELECTIVE' ALONE & STERILISATION ARE NOT REASONS"]
SUFFIX=["1_previous-scar","2_breech","3_praevia","4_failure-to-progress","5_fetal-compromise","6_not-an-indication"]

def S(v): return int(round(v*K))

def glow(d,t):
    p=0.5+0.5*math.sin(2*math.pi*t/3.0); gr=int(118+8*p)
    d.ellipse([CX-gr,CY-int(gr*0.82),CX+gr,CY+int(gr*0.86)],fill=lerp(WALL,(40,52,78),0.45))
    d.ellipse([CX-int(gr*0.66),CY-int(gr*0.56),CX+int(gr*0.66),CY+int(gr*0.6)],fill=lerp(WALL,(52,66,96),0.5))

def womb(d,glowr):
    el(d,CX-S(34),CY-S(38),CX+S(34),CY+S(34),UTER_D); el(d,CX-S(32),CY-S(36),CX+S(32),CY+S(32),UTER)
    el(d,CX-S(28),CY-S(32),CX+S(28),CY+S(26),AMN)
    rr(d,CX-S(9),CY+S(28),CX+S(9),CY+S(46),UTER); rr(d,CX-S(5),CY+S(32),CX+S(5),CY+S(46),OSC)
    g=int(120*glowr); d.ellipse([CX-S(37),CY-S(41),CX+S(37),CY+S(49)],outline=(g+80,g+40,g+40))

def baby(d,hx,hy,bx,by):
    el(d,bx-S(9),by-S(8),bx+S(9),by+S(10),BABY); el(d,hx-S(7),hy-S(7),hx+S(7),hy+S(7),BABY)
    mx,my=(hx+bx)//2,(hy+by)//2; el(d,mx-S(4),my-S(4),mx+S(4),my+S(4),BABY)
    d.point((hx-S(2),hy-S(1)),fill=BABY_D); d.point((hx+S(2),hy-S(1)),fill=BABY_D)

def clock(d,cx,cy,R,t):
    el(d,cx-R-1,cy-R-1,cx+R+1,cy+R+1,(222,226,234)); el(d,cx-R,cy-R,cx+R,cy+R,(28,36,56))
    ah=2*math.pi*(t/12.0); d.line([(cx,cy),(cx+int((R-S(6))*math.sin(ah)),cy-int((R-S(6))*math.cos(ah)))],fill=TEXT,width=2)
    asec=2*math.pi*t; d.line([(cx,cy),(cx+int((R-S(3))*math.sin(asec)),cy-int((R-S(3))*math.cos(asec)))],fill=ACCENT)
    el(d,cx-2,cy-2,cx+2,cy+2,(222,226,234))

def hero(d,s,t):
    glow(d,t); gp=0.4+0.6*(0.5+0.5*math.sin(2*math.pi*t/3.0))
    if s==0:
        el(d,CX-S(44),CY-S(6),CX+S(44),CY+S(54),(234,206,186))
        rr(d,CX-S(46),CY+S(40),CX+S(46),CY+S(70),BR.GOWN)
        d.line([(CX-S(26),CY+S(24)),(CX+S(26),CY+S(24))],fill=(170,96,96),width=3)
        for sxx in range(-24,25,7):
            x=CX+S(sxx); d.line([(x,CY+S(20)),(x,CY+S(28))],fill=(150,78,78))
    elif s==1:
        womb(d,gp); baby(d,CX,CY-S(18),CX-S(1),CY+S(8))
        d.line([(CX+S(26),CY-S(20)),(CX+S(14),CY-S(16))],fill=TEXT); d.polygon([(CX+S(14),CY-S(16)),(CX+S(20),CY-S(20)),(CX+S(20),CY-S(12))],fill=TEXT)
        lw=TLX.w("HEAD UP",'small'); TLX.add(CX+S(30),CY-S(24),"HEAD UP",AMBER,'small')
    elif s==2:
        womb(d,gp); d.pieslice([CX-S(22),CY+S(8),CX+S(22),CY+S(40)],20,160,fill=PLAC); baby(d,CX+S(1),CY-S(6),CX,CY+S(2))
        d.line([(CX+S(30),CY+S(30)),(CX+S(12),CY+S(30))],fill=RED); d.polygon([(CX+S(12),CY+S(30)),(CX+S(18),CY+S(26)),(CX+S(18),CY+S(34))],fill=RED)
        TLX.add(CX+S(32),CY+S(26),"COVERS OS",RED,'small')
    elif s==3:
        clock(d,CX-S(30),CY-S(8),S(26),t)
        bx,by,bw=CX-S(18),CY+S(40),S(112)
        rr(d,bx,by,bx+bw,by+S(13),(40,50,72)); rr(d,bx,by,bx+int(bw*0.32),by+S(13),AMBER)
        d.line([(bx+int(bw*0.32),by-S(3)),(bx+int(bw*0.32),by+S(16))],fill=RED,width=2)
        TLX.add(bx,by-S(16),"4 cm ... STUCK",AMBER,'small')
    elif s==4:
        bx,by,bw=CX-S(48),CY+S(6),S(128)
        rr(d,bx,by-S(26),bx+bw,by+S(22),(18,24,40)); rr(d,bx,by-S(26),bx+bw,by-S(24),(40,52,74))
        prev=None
        for i in range(bw):
            ph=(i/bw+(t/12.0)*6.0)%1.0; yy=by-S(2)
            for c in (0.3,0.7):
                dd=abs(((ph-c+0.5)%1.0)-0.5)
                if dd<0.07: yy=by-S(2)+int((0.07-dd)/0.07*S(18))
            yy+=int(S(1.2)*math.sin(i*0.9))
            if prev is not None:
                a,b=sorted((prev,yy)); d.line([(bx+i,a),(bx+i,b)],fill=ECG)
            d.point((bx+i,yy),fill=ECG); prev=yy
        dby=by+S(22)+8; lw=TLX.w("DECELERATIONS",'small'); tx=int(CX-lw/2-16)
        d.polygon([(tx,dby+10),(tx+14,dby+10),(tx+7,dby-2)],fill=AMBER); TLX.add(tx+5,dby+1,"!",(40,30,10),'small')
        TLX.add(CX-lw/2,dby,"DECELERATIONS",RED,'small')
    else:
        for i,txt in enumerate(["'ELECTIVE' ALONE","STERILISATION"]):
            yy=CY-S(20)+i*S(52)
            rr(d,CX-S(96),yy-S(15),CX+S(96),yy+S(15),(46,34,40))
            tw=TLX.w(txt,'body'); TLX.add(CX-tw/2,yy-S(10),txt,(214,180,186),'body')
            cc=lerp((120,50,58),RED,gp)
            d.line([(CX-S(96),yy-S(15)),(CX+S(96),yy+S(15))],fill=cc,width=3); d.line([(CX-S(96),yy+S(15)),(CX+S(96),yy-S(15))],fill=cc,width=3)

def ask_cue(d):
    # small top-left 'the examinee is asking' cue (keeps the history-taking identity)
    COAT=(226,230,236); LAN=(220,90,104); INKc=(52,56,72)
    PIG=(80,82,92); PIG_D=(56,58,68); PIG_H=(108,110,122); BEAK=(94,90,84); CERE=(238,240,244); EYEO=(242,172,60)
    hx,hy=34,46
    d.polygon([(hx-13,72),(hx+13,72),(hx+9,57),(hx-9,57)],fill=COAT)
    d.polygon([(hx-3,57),(hx+3,57),(hx+2,70),(hx-2,70)],fill=(32,54,110))
    d.line([(hx-4,58),(hx-2,70)],fill=LAN); d.line([(hx+4,58),(hx+2,70)],fill=LAN)
    el(d,hx-8,hy-8,hx+8,hy+10,PIG); el(d,hx-7,hy-8,hx+4,hy-2,PIG_H); el(d,hx-8,hy+4,hx+8,hy+10,PIG_D)
    d.polygon([(hx-7,hy),(hx-15,hy+2),(hx-7,hy+5)],fill=BEAK)
    el(d,hx-9,hy-2,hx-5,hy+1,CERE)
    el(d,hx-4,hy-3,hx+1,hy+2,EYEO); el(d,hx-3,hy-2,hx,hy+1,(30,24,18)); d.point((hx-2,hy-2),fill=(255,255,255))
    bx0,by0,bx1,by1=50,32,156,64
    rr(d,bx0,by0,bx1,by1,(238,240,246)); d.polygon([(bx0,hy-2),(bx0-7,hy+2),(bx0,hy+6)],fill=(238,240,246))
    TLX.add(bx0+5,by0+4,"WHY DID YOU NEED",INKc,'tiny'); TLX.add(bx0+5,by0+16,"A CAESAREAN?",INKc,'tiny')
    TLX.add(bx0+2,by0-11,"THE EXAMINEE ASKS",(0,180,196),'tiny')

def progress(d,cur):
    n=6; gap=16; x0=CX-(n-1)*gap//2; y=52
    for i in range(n):
        r=4 if i==cur else 2; col=ACCENT if i==cur else (84,94,116)
        el(d,x0+i*gap-r,y-r,x0+i*gap+r,y+r,col)
    lab=f"INDICATION {cur+1} / {n}" if cur<5 else "KEY EXCEPTION"
    TLX.add(CX-TLX.w(lab,'small')/2,y+7,lab,(150,160,182),'small')

def render(s,t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,70,(28,34,52)); rr(d,0,183,GW-1,GH-1,(26,32,48))
    hero(d,s,t)
    # concept title (centred, big) with shadow
    lab=NAMES[s]; lw=TLX.w(lab,'title'); lx=CX-lw/2
    TLX.add(lx+0.5,16.5,lab,(8,12,22),'title'); TLX.add(lx,16,lab,ACCENT,'title')
    progress(d,s)
    ask_cue(d)
    pw=TLX.w(PEARL[s],'small'); TLX.add(CX-pw/2,250,PEARL[s],(202,208,222),'small')
    # beat identity corner
    rr(d,16,250,120,251,ACCENT); TLX.add(16,238,"WHY THE CAESAREAN",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        s=int(sys.argv[sys.argv.index('--still')+1]); tv=float(sys.argv[sys.argv.index('--still')+2])
        if '--cue' in sys.argv: SHOW_CUE=True
        Image.fromarray(render(s,tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bf9_{s}_{tv}.png'); print("ok",s,tv)
    elif '--cue-demo' in sys.argv:
        for tag,cue in [("clean",False),("cue",True)]:
            SHOW_CUE=cue
            OUT=f'D:/Ue/UE_5.8/obgyn_explainer/beat09_focus_demo_praevia_{tag}_4K.mp4'
            cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
                 '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
            p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            for i in range(int(DUR*FPS)): p.stdin.write(render(2,i/FPS).tobytes())
            p.stdin.close(); err=p.stderr.read(); p.wait()
            if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
            print(OUT, os.path.getsize(OUT))
    else:
        for s in range(6):
            OUT=f'D:/Ue/UE_5.8/obgyn_explainer/beat09_focus_{SUFFIX[s]}_4K.mp4'
            cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
                 '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
            p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            for i in range(int(DUR*FPS)): p.stdin.write(render(s,i/FPS).tobytes())
            p.stdin.close(); err=p.stderr.read(); p.wait()
            if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
            print(OUT, os.path.getsize(OUT))
