"""Beat 9 - WHY THE CAESAREAN (indications). Cycles the real indications, each as a
little diagram: previous scar, breech/transverse lie, placenta praevia, failure to
progress, fetal compromise. Persistent reminder that 'elective' alone and sterilisation
are NOT indications. 480x270 -> 4K, 24fps, 12s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(24,30,48); WALL2=(30,38,58); FLOOR=(28,38,56); FLOORH=(38,50,70)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
UTER=(206,142,152); UTER_D=(176,110,122); AMN=(228,198,208); OSC=(236,168,180)
BABY=(242,201,170); BABY_D=(206,160,128); PLAC=(150,52,66); CORD=(176,150,70)
RED=(214,60,70); AMBER=(236,172,92); GREEN=(84,196,146); ECG=(96,230,150); STEEL=(206,214,228)
ITEMS=["PREVIOUS C-SECTION SCAR","BREECH / TRANSVERSE LIE","PLACENTA PRAEVIA","FAILURE TO PROGRESS","FETAL COMPROMISE"]
PEARL=["PREVIOUS UTERINE SCAR -> REPEAT SECTION",
       "BABY NOT HEAD-DOWN (BREECH OR LYING ACROSS)",
       "PLACENTA COVERS THE CERVIX - BLOCKS EXIT",
       "LABOUR STALLED DESPITE GOOD CONTRACTIONS",
       "BABY IN DISTRESS - DELIVER NOW"]

def womb(d,cx,cy,glow):
    # uterine body (pear) + amniotic fluid
    el(d,cx-34,cy-38,cx+34,cy+34,UTER_D); el(d,cx-32,cy-36,cx+32,cy+32,UTER)
    el(d,cx-28,cy-32,cx+28,cy+26,AMN)
    # lower segment + cervix (os) at the bottom
    rr(d,cx-9,cy+28,cx+9,cy+46,UTER); rr(d,cx-5,cy+32,cx+5,cy+46,OSC)
    if glow>0.02:
        g=int(140*glow); d.ellipse([cx-36,cy-40,cx+36,cy+48],outline=(g+80,g+40,g+40))

def baby(d,hx,hy,bx,by,sk=BABY):
    el(d,bx-9,by-8,bx+9,by+10,sk)                    # trunk
    el(d,hx-7,hy-7,hx+7,hy+7,sk)                      # head
    mx,my=(hx+bx)//2,(hy+by)//2; el(d,mx-4,my-4,mx+4,my+4,sk)  # curl
    d.point((hx-2,hy-1),fill=BABY_D); d.point((hx+2,hy-1),fill=BABY_D)

def clock(d,cx,cy,R,t):
    el(d,cx-R-1,cy-R-1,cx+R+1,cy+R+1,(222,226,234)); el(d,cx-R,cy-R,cx+R,cy+R,(28,36,56))
    for k in range(12):
        a=math.radians(k*30); el(d,cx+int((R-2)*math.sin(a)),cy-int((R-2)*math.cos(a)),cx+int((R-2)*math.sin(a)),cy-int((R-2)*math.cos(a)),(150,160,180))
    ah=2*math.pi*(t/12.0); d.line([(cx,cy),(cx+int((R-6)*math.sin(ah)),cy-int((R-6)*math.cos(ah)))],fill=TEXT,width=2)
    asec=2*math.pi*t; d.line([(cx,cy),(cx+int((R-3)*math.sin(asec)),cy-int((R-3)*math.cos(asec)))],fill=ACCENT)
    el(d,cx-2,cy-2,cx+2,cy+2,(222,226,234))

def depict(d,s,t):
    cx,cy=118,118; glow=0.5+0.5*math.sin(2*math.pi*t/12.0)
    if s==0:        # previous c-section scar on a draped lower belly (modest)
        el(d,cx-44,cy-6,cx+44,cy+54,(234,206,186)); el(d,cx-44,cy-6,cx+44,cy+54,None)   # belly mound
        el(d,cx-44,cy-6,cx+44,cy+54,(234,206,186))
        rr(d,cx-46,cy+40,cx+46,cy+70,BR.GOWN)                                            # gown/drape below
        d.line([(cx-26,cy+24),(cx+26,cy+24)],fill=(170,96,96),width=2)                   # healed scar
        for sxx in range(cx-24,cx+25,7): d.line([(sxx,cy+20),(sxx,cy+28)],fill=(150,78,78))  # suture ticks
        TLX.add(cx-30,cy-30,"OLD SCAR",RED,'tiny')
    elif s==1:      # breech - baby bottom-down, head up
        womb(d,cx,cy,glow)
        baby(d,cx,cy-18,cx-1,cy+8)                         # head up, bottom toward cervix
        d.line([(cx+26,cy-20),(cx+14,cy-16)],fill=TEXT); d.polygon([(cx+14,cy-16),(cx+20,cy-20),(cx+20,cy-12)],fill=TEXT)
        TLX.add(cx+28,cy-24,"HEAD UP",AMBER,'tiny')
    elif s==2:      # placenta praevia - placenta over the os
        womb(d,cx,cy,glow)
        d.pieslice([cx-22,cy+8,cx+22,cy+40],20,160,fill=PLAC)   # placenta low, covering os
        baby(d,cx+1,cy-6,cx,cy+2)                                # baby above, blocked
        d.line([(cx+30,cy+30),(cx+12,cy+30)],fill=RED); d.polygon([(cx+12,cy+30),(cx+18,cy+26),(cx+18,cy+34)],fill=RED)
        TLX.add(cx+30,cy+26,"COVERS OS",RED,'tiny')
    elif s==3:      # failure to progress - clock + stalled dilation bar
        clock(d,cx-22,cy-6,20,t)
        # dilation progress bar (stuck low)
        bx,by,bw=cx-30,cy+36,86
        rr(d,bx,by,bx+bw,by+12,(40,50,72)); rr(d,bx,by,bx+int(bw*0.32),by+12,AMBER)
        d.line([(bx+int(bw*0.32),by-3),(bx+int(bw*0.32),by+15)],fill=RED,width=2)
        TLX.add(bx,by-14,"4 cm ... STUCK",AMBER,'tiny')
        TLX.add(cx+6,cy-16,"HOURS PASS",TEXTDIM,'tiny')
    else:           # fetal compromise - CTG with decelerations + warning
        bx,by,bw=cx-36,cy+4,96
        rr(d,bx,by-24,bx+bw,by+20,(18,24,40)); rr(d,bx,by-24,bx+bw,by-22,(40,52,74))
        prev=None
        for i in range(bw):
            ph=(i/bw + (t/12.0)*6.0)%1.0           # 6 scrolls in 12s -> seamless
            yy=by-2
            # two deep decelerations
            for c in (0.3,0.7):
                dd=abs(((ph-c+0.5)%1.0)-0.5)
                if dd<0.07: yy=by-2+int((0.07-dd)/0.07*16)
            yy+=int(1.2*math.sin(i*0.9))
            if prev is not None:
                a,b=sorted((prev,yy)); d.line([(bx+i,a),(bx+i,b)],fill=ECG)
            d.point((bx+i,yy),fill=ECG); prev=yy
        d.polygon([(cx-8,cy-40),(cx+8,cy-40),(cx,cy-54)],fill=AMBER); TLX.add(cx-2,cy-50,"!",(40,30,10),'tiny')
        TLX.add(cx-30,cy-38,"DECELERATIONS",RED,'tiny')

def panel(d,x,y,w,h,cur):
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"INDICATIONS",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+15,(252,240,176))
        rr(d,x+7,ry+2,x+15,ry+10,(250,250,250)); d.rectangle([x+7,ry+2,x+15,ry+10],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+6),(x+10,ry+9)],fill=TICK); d.line([(x+10,ry+9),(x+15,ry+1)],fill=TICK)
        TLX.add(x+20,ry+1,it, INK if (done or now) else INKDIM,'small')
        ry+=19

def not_a_reason(d,x,y,w):
    rr(d,x,y,x+w,y+40,(42,30,36)); rr(d,x,y,x+w,y+2,(120,60,72))
    TLX.add(x+6,y+3,"NOT AN INDICATION:",(236,150,160),'tiny')
    for i,s in enumerate(["x  'elective' on its own","x  sterilisation / tubal tie"]):
        yy=y+16+i*11; TLX.add(x+6,yy,s,(210,180,186),'tiny')
        d.line([(x+7,yy+4),(x+13,yy+4)],fill=RED,width=2)   # strike through the x marker row

def render(t):
    TLX.cmds=[]
    s=int(t//2.4)%5
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    depict(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,98,["WHY DID YOU NEED","A CAESAREAN?"],300)
    TLX.add(40,30,"THE REASON FOR THE OPERATION",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,340,26,134,118,s)
    TLX.add(392,17,"REASONS",(150,150,162),'small')
    not_a_reason(d,36,196,150)
    TLX.add(200,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(200,254,PEARL[s],(172,180,198),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"WHY THE CAESAREAN",(10,14,24),'body'); TLX.add(16,5,"WHY THE CAESAREAN",TEXT,'body')
    TLX.add(16.4,21.3,"THE INDICATION MATTERS",(10,14,24),'small'); TLX.add(16,21,"THE INDICATION MATTERS",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b9_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat09_indications_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
