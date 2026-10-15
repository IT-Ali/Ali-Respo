"""WHERE EACH PART GOES - organising THIS slide's labour history (with VFX).
CHIEF COMPLAINT = the 3 always-stated essentials (caesarean + elective/emergency + reason);
everything else = the HOPI, as the 3 operation phases PRE-OP -> INTRA-OP -> POST-OP.
Outcome of delivery = next slide. Build (~9s) then hold. 480x270 -> 4K, 24fps."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=14.0
TLX=uitext.TL()

WALL=(18,20,30); WALL2=(26,30,44)
GOLD=(230,186,96); GOLDB=(236,204,140); CARDBG=(40,34,20); CARDED=(150,120,60); INK=(36,30,16)
CYAN=(0,188,204); CYAN_D=(10,96,108); HOPIBG=(16,32,36); COLBG=(24,44,48); COLED=(14,70,80)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; DOT=(120,200,210)

REASONS=["previous 2 scars","placenta previa","fetal distress","failure to progress","CPD","bad obstetric Hx"]
PREOP=["delivery site","blood crossmatched","IV line","urinary catheter","consent","fasting (NPO)"]
INTRAOP=["anaesthesia (GA/regional)","route / incision","operation time","easy / difficult",
         "episiotomy (if vaginal)","forceps / instruments","blood loss / transfusion","complications in op"]
POSTOP=["return of consciousness","nausea / vomiting","bowel & flatus","micturition",
        "post-partum bleeding","mobility / walking","breast-feeding","analgesia"]

# ---- VFX setup ----
_T=0.0
_rng=np.random.default_rng(7); PN=58
_PX=_rng.uniform(0,480,PN); _PY=_rng.uniform(30,270,PN)
_PSP=_rng.uniform(3,9,PN); _PPH=_rng.uniform(0,6.28,PN); _PSZ=_rng.integers(1,3,PN)
_PCOL=[GOLDB if _rng.random()<0.5 else (120,210,224) for _ in range(PN)]

def oshoot(p):
    p=min(1.0,max(0.0,p)); c=1.70158
    return 1+(c+1)*((p-1)**3)+c*((p-1)**2)

def spark(d,x,y,s,c):
    d.line([(x-s,y),(x+s,y)],fill=c); d.line([(x,y-s),(x,y+s)],fill=c)

def bg_fx(d,t):
    for bx,by,tint,amp,per in [(150,110,GOLD,42,9.0),(330,205,CYAN,48,11.0),(60,235,CYAN,30,7.0),(420,80,GOLD,30,13.0)]:
        ox=amp*math.sin(2*math.pi*t/per); oy=16*math.cos(2*math.pi*t/(per*1.3))
        for r,a in [(74,0.045),(46,0.065)]:
            cx=int(bx+ox); cy=int(by+oy); d.ellipse([cx-r,cy-int(r*0.7),cx+r,cy+int(r*0.7)],fill=lerp(WALL,tint,a))
    for i in range(PN):
        py=(_PY[i]-t*_PSP[i])%240+30; px=(_PX[i]+6*math.sin(t*0.6+_PPH[i]))%480
        tw=0.35+0.65*(0.5+0.5*math.sin(t*2.2+_PPH[i])); s=int(_PSZ[i])
        d.rectangle([int(px),int(py),int(px)+s,int(py)+s],fill=lerp(WALL,_PCOL[i],0.55*tw))

def glow_rect(d,x0,y0,x1,y1,col,ed,per=2.6):
    pu=0.5+0.5*math.sin(2*math.pi*_T/per)
    d.rectangle([x0-2,y0-2,x1+2,y1+2],outline=lerp(WALL,col,0.10+0.09*pu))
    d.rectangle([x0-1,y0-1,x1+1,y1+1],outline=lerp(WALL,col,0.16+0.13*pu))
    d.rectangle([x0,y0,x1,y1],outline=lerp(ed,col,0.35+0.4*pu))

def pill(d,x,y,w,h,txt,size,p,num=None):
    if p<=0: return
    ox=int(-6*(1-oshoot(p))); pc=min(1.0,p)
    base=lerp(CARDBG,GOLD,pc); rr(d,x+ox,y,x+w+ox,y+h,base); rr(d,x+ox,y,x+w+ox,y+2,lerp(CARDBG,GOLDB,pc))
    if pc>=1.0:                                               # shine sweep
        period=w+44; sh=(_T*72+x*2.1)%period-22
        for dy in range(h):
            sx=x+ox+int(sh)+int(dy*0.5)
            if 0<=sx-(x+ox)<w: d.line([(sx,y+dy),(sx,y+dy)],fill=lerp(base,(255,255,255),0.5))
            if 0<=sx+1-(x+ox)<w: d.line([(sx+1,y+dy),(sx+1,y+dy)],fill=lerp(base,(255,255,255),0.28))
    tw=TLX.w(txt,size); TLX.add(x+ox+(w-tw)/2,y+h/2-3.2,txt,lerp(CARDBG,INK,pc),size)
    if num is not None:
        el(d,x+ox-5,y+h/2-6,x+ox+7,y+h/2+6,lerp(CARDBG,GOLDB,pc)); d.ellipse([x+ox-5,y+h/2-6,x+ox+7,y+h/2+6],outline=lerp(CARDBG,INK,pc))
        TLX.add(x+ox-1.3,y+h/2-4,str(num),lerp(CARDBG,INK,pc),'tiny')

def col(d,x,w,title,items,p0,t):
    y0,y1=150,246; hp=smooth((t-p0)/0.4)
    rr(d,x,y0,x+w,y1,lerp(HOPIBG,COLBG,hp)); d.rectangle([x,y0,x+w,y1],outline=COLED)
    rr(d,x,y0,x+w,y0+12,lerp(HOPIBG,CYAN_D,hp))
    TLX.add(x+5,y0+2,title,lerp(HOPIBG,(224,244,246),hp),'tiny')
    if hp>0:                                                  # moving glint on header edge
        gx=x+4+int(((t-p0)*54)%(w-8)); d.line([(gx,y0+12),(gx+5,y0+12)],fill=lerp(HOPIBG,(200,245,255),hp))
    for i,it in enumerate(items):
        pi=smooth((t-(p0+0.25+i*0.14))/0.3)
        if pi<=0: continue
        iy=y0+17+i*10; ox=int(-5*(1-oshoot(pi)))
        el(d,x+6+ox,iy+2,x+9+ox,iy+5,lerp(HOPIBG,DOT,pi))
        if 0.1<pi<0.9:
            g=math.sin(pi*math.pi); spark(d,x+7+ox,iy+3,2+int(2*g),lerp(HOPIBG,(230,250,255),g))
        TLX.add(x+12+ox,iy,it,lerp(HOPIBG,(206,226,230),pi),'tiny')

def render(t):
    global _T; _T=t; TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    bg_fx(d,t)
    rr(d,0,0,GW-1,30,WALL2)
    TLX.add(16,4,"WHERE EACH PART GOES",(8,12,22),'body'); TLX.add(15.6,3.6,"WHERE EACH PART GOES",TEXT,'body')
    TLX.add(16,20,"the complaint says the big 3  -  the rest is HOPI detail",TEXTDIM,'small')

    # ---- CHIEF COMPLAINT card ----
    pc=smooth((t-0.3)/0.4); cx0,cy0,cx1,cy1=36,38,444,120
    rr(d,cx0,cy0,cx1,cy1,lerp(WALL,CARDBG,pc)); rr(d,cx0,cy0,cx1,cy0+3,lerp(WALL,GOLD,pc))
    if pc>=1.0: glow_rect(d,cx0,cy0,cx1,cy1,GOLD,CARDED)
    else: d.rectangle([cx0,cy0,cx1,cy1],outline=lerp(WALL,CARDED,pc))
    TLX.add(cx0+8,cy0+5,"CHIEF COMPLAINT",lerp(WALL,GOLDB,pc),'small')
    tagpu=0.6+0.4*(0.5+0.5*math.sin(2*math.pi*t/1.6))
    tag="ALWAYS STATED  -  THE BIG 3"; TLX.add(cx1-8-TLX.w(tag,'tiny'),cy0+6,tag,lerp(WALL,GOLD,pc*tagpu),'tiny')
    pill(d,66,cy0+22,150,18,"ELECTIVE / EMERGENCY",'small',smooth((t-0.9)/0.4),num=1)
    pill(d,236,cy0+22,172,18,"CAESAREAN SECTION",'small',smooth((t-1.4)/0.4),num=2)
    p3=smooth((t-2.0)/0.4)
    if p3>0: TLX.add(72,cy0+53,"due to",lerp(CARDBG,(214,206,186),p3),'small')
    ridx=int((t-2.4)/1.6)%len(REASONS) if t>2.4 else 0
    pill(d,150,cy0+48,196,18,REASONS[ridx],'small',smooth((t-2.4)/0.4),num=3)
    ps=smooth((t-2.8)/0.5)
    if ps>0:
        TLX.add(80,cy0+42,"how it was decided",lerp(CARDBG,(170,160,130),ps),'tiny')
        TLX.add(262,cy0+42,"the operation",lerp(CARDBG,(170,160,130),ps),'tiny')
        TLX.add(150,cy0+68,"the indication  (why)",lerp(CARDBG,(170,160,130),ps),'tiny')

    # ---- flowing arrow ----
    pa=smooth((t-3.2)/0.4)
    if pa>0:
        ac=lerp(WALL,CYAN,pa); d.line([(240,122),(240,138)],fill=ac,width=2); d.polygon([(234,136),(246,136),(240,144)],fill=ac)
        for k in range(3):
            fy=122+((_T*26+k*7)%20)
            if fy<137: d.line([(240,int(fy)),(240,int(fy)+3)],fill=lerp(CYAN,(220,250,255),0.7))
        TLX.add(250,130,"the rest",ac,'tiny')

    # ---- HOPI block ----
    ph=smooth((t-3.6)/0.4)
    if ph>0:
        rr(d,36,142,444,249,lerp(WALL,HOPIBG,ph))
        if ph>=1.0: glow_rect(d,36,142,444,249,CYAN,CYAN_D,per=3.0)
        else: d.rectangle([36,142,444,249],outline=lerp(WALL,CYAN_D,ph))
        TLX.add(42,143.5,"HISTORY OF PRESENT ILLNESS",lerp(WALL,(224,244,246),ph),'small')
        tg="the story of THIS delivery  -  pre-op -> intra-op -> post-op   (outcome = next slide)"
        TLX.add(444-8-TLX.w(tg,'tiny'),145,tg,lerp(WALL,CYAN,ph),'tiny')
        col(d,44,124,"PRE-OP  (before)",PREOP,4.0,t)
        col(d,176,124,"INTRA-OP  (during)",INTRAOP,5.3,t)
        col(d,308,124,"POST-OP  (after)",POSTOP,6.6,t)

    # ---- footer ----
    pf=smooth((t-9.2)/0.6)
    if pf>0:
        rr(d,8,252,472,269,lerp(WALL,(30,26,34),pf))
        r="Complaint = caesarean + elective/emergency + reason (always)   *   the details go in the HOPI"
        rw=TLX.w(r,'small'); TLX.add(240-rw/2,255,r,lerp(WALL,(210,200,180),pf),'small')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/lhm_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/labour_history_map_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
