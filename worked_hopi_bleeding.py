"""THE WRITTEN HISTORY - DEMOGRAPHIC -> CHIEF COMPLAINT (gold sections), then the
HISTORY OF PRESENT ILLNESS as ONE continuous paragraph that writes itself out, PAUSING at each
sub-phase boundary (presentation -> pre-op -> intra-op -> post-op) with each sub-phase's words in
a slightly different tint and the strip highlighting the current one. Antepartum vaginal bleeding (placenta praevia), 100-cases book p.108."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; CPS=30.0; MAINPAUSE=1.6; SUBPAUSE=1.7; HDR=0.45
TLX=uitext.TL()
WALL=(18,20,30)
GOLD=(230,186,96); GOLDB=(236,204,140); CYAN=(0,188,204); CYAN_D=(10,96,108)
CREAM=(241,239,228); CREAM_D=(208,204,188); INK=(40,44,58); INKDIM=(150,150,162)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM
def spark(d,x,y,s,c):
    d.line([(x-s,y),(x+s,y)],fill=c); d.line([(x,y-s),(x,y+s)],fill=c)
def canon_mini(d,x,y,t):
    """Our pigeon doctor, compact, writing - bottom-right corner."""
    PIG=(80,82,92); PIGD=(60,62,72); EYEO=(242,172,60); CERE=(238,240,246)
    NAVY=(32,54,110); COAT=(238,240,246); COATD=(206,210,222); CLAW=(46,48,56)
    LAN=(200,60,66); BEAK=(216,184,96); STETH=(70,74,88)
    b=int(math.sin(t*5))
    rr(d,x-10,y-20,x+10,y-2,COAT); d.rectangle([x-10,y-20,x+10,y-2],outline=COATD)   # coat
    d.line([(x-6,y-20),(x-4,y-11)],fill=STETH); d.line([(x+6,y-20),(x+4,y-11)],fill=STETH); el(d,x-6,y-12,x-3,y-9,STETH)  # stethoscope
    d.line([(x-4,y-20),(x-2,y-12)],fill=LAN); d.line([(x+4,y-20),(x+2,y-12)],fill=LAN); rr(d,x-3,y-13,x+3,y-9,LAN)         # lanyard+badge
    rr(d,x-2,y-20,x+2,y-13,NAVY)                                                     # tie
    el(d,x-9,y-34,x+6,y-20,PIG); el(d,x-9,y-25,x-3,y-20,PIGD)                        # head
    d.polygon([(x-9,y-28),(x-16,y-26),(x-9,y-24)],fill=BEAK)                         # beak (left)
    el(d,x-11,y-28,x-8,y-25,CERE)                                                    # cere
    el(d,x-5,y-31,x-1,y-27,EYEO); el(d,x-4,y-30,x-2,y-28,(38,28,14))                 # orange eye
    rr(d,x-8,y-6+b,x+2,y+6+b,(210,206,190)); rr(d,x-7,y-5+b,x+1,y+5+b,(250,250,248)) # small clipboard
    for ly in range(y-3+b,y+4+b,2): d.line([(x-6,ly),(x-1,ly)],fill=(176,184,200))   # lines
    d.line([(x+6,y-10),(x+2,y-2+b)],fill=COAT,width=2)                               # arm
    el(d,x+1,y-3+b,x+4,y+0+b,CLAW)                                                   # charcoal hand
    d.line([(x+2,y-1+b),(x-3,y+2+b)],fill=(70,70,82),width=2)                        # pen
    d.line([(x-3,y+2+b),(x-6,y+4+b)],fill=(236,196,110))                            # gold nib

DEMO="Fatima Ahmed, 25, housewife, blood group A+, from Baghdad. Husband Jamal, 25, free worker. Gravida 4, para 3, abortion 0 - now 32 weeks, with two previous caesarean sections."
COMPLAINT="Admitted with painless vaginal bleeding of a few hours' duration."
SUBS=[("ONSET & AMOUNT","At 32 weeks she presented with vaginal bleeding for a few hours; it began as a few drops and, an hour later, became a large amount of fresh red blood with clots."),
 ("CHARACTER","It was painless - she had no abdominal pain and no uterine contractions."),
 ("SEVERITY & FETUS","She felt light-headed but did not faint, and the baby has been moving well."),
 ("BACKGROUND","This was not her first episode - she had bled once before at nineteen weeks, when she was found to have a low-lying placenta. She is now under observation and awaiting a blood transfusion.")]
SUBTAGS=[s[0] for s in SUBS]
SUBINK=[(40,44,58),(26,54,80),(22,66,62),(58,46,72)]   # subtle per-sub-phase tints (dark, readable)
HOPI=' '.join(t for _,t in SUBS); NC=len(HOPI)
HCS=[]                                                  # char -> sub index
for k,(_,t) in enumerate(SUBS):
    HCS+=[k]*len(t)
    if k<len(SUBS)-1: HCS.append(k)
CHUNKS=[len(SUBS[0][1])]+[len(t)+1 for _,t in SUBS[1:]]  # chars written per sub (rest +1 for space)
def hopi_state(te):
    prev=0; n=len(CHUNKS)
    for ci in range(n):
        wt=CHUNKS[ci]/CPS
        if te<wt: return prev+int(te*CPS), ci
        te-=wt; prev+=CHUNKS[ci]
        if ci<n-1:
            if te<SUBPAUSE: return prev, ci+1      # paused -> next sub lights up
            te-=SUBPAUSE
    return NC, n-1
HOPI_WRITE=NC/CPS+(len(CHUNKS)-1)*SUBPAUSE

PX0,PX1,PY0,PY1=12,468,26,270
TX0,MAXW,PITCH=28,432,12
def wrap(txt,maxw):
    words=txt.split(); SP=TLX.w(' ','small'); lines=[]; cur=[]; curw=0.0
    for w in words:
        ww=TLX.w(w,'small')
        if not cur: cur=[w]; curw=ww
        elif curw+SP+ww>maxw: lines.append(cur); cur=[w]; curw=ww
        else: curw+=SP; cur.append(w); curw+=ww
    if cur: lines.append(cur)
    S=' '.join(words); wstart=[]; c=0
    for w in words: wstart.append(c); c+=len(w)+1
    meta=[]; wi=0
    for line in lines:
        start=wstart[wi]; end=wstart[wi+len(line)-1]+len(line[-1]); meta.append((start,end,S[start:end])); wi+=len(line)
    return S,meta

# sections: (label, color, text, hasSub)
SECTIONS=[("DEMOGRAPHIC",GOLD,DEMO,False),("CHIEF COMPLAINT",GOLD,COMPLAINT,False),("HISTORY OF PRESENT ILLNESS",CYAN,HOPI,True)]
LAY=[]; y=40; sched=[]; tc=0.6
for lbl,col,txt,hasSub in SECTIONS:
    S,meta=wrap(txt,MAXW); hy=y; y+=15
    suby=None
    if hasSub: suby=y; y+=13
    liney=[]
    for m in meta: liney.append(y); y+=PITCH
    y+=6
    th=tc; tb=th+HDR
    td=tb+(HOPI_WRITE if hasSub else len(S)/CPS)
    tc=td+MAINPAUSE
    LAY.append((lbl,col,S,meta,hy,suby,liney,hasSub)); sched.append((th,tb,td))
DUR=sched[-1][2]+4.2
HOPI_TB=sched[2][1]
PAPER_BOT=270            # full document

_rng=np.random.default_rng(9); PN=42
_PX=_rng.uniform(0,480,PN); _PY=_rng.uniform(30,270,PN); _PSP=_rng.uniform(3,9,PN)
_PPH=_rng.uniform(0,6.28,PN); _PSZ=_rng.integers(1,3,PN)
_PCOL=[GOLDB if _rng.random()<0.5 else (120,210,224) for _ in range(PN)]
def bg_fx(d,t):
    for bx,by,tint,amp,per in [(110,120,GOLD,42,9.0),(380,150,CYAN,48,11.0)]:
        ox=amp*math.sin(2*math.pi*t/per); oy=16*math.cos(2*math.pi*t/(per*1.3))
        for r,a in [(74,0.05),(46,0.07)]:
            cx=int(bx+ox); cy=int(by+oy); d.ellipse([cx-r,cy-int(r*0.7),cx+r,cy+int(r*0.7)],fill=lerp(WALL,tint,a))
    for i in range(PN):
        py=(_PY[i]-t*_PSP[i])%240+30; px=(_PX[i]+6*math.sin(t*0.6+_PPH[i]))%480
        tw=0.35+0.65*(0.5+0.5*math.sin(t*2.2+_PPH[i])); s=int(_PSZ[i])
        d.rectangle([int(px),int(py),int(px)+s,int(py)+s],fill=lerp(WALL,_PCOL[i],0.5*tw))

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    bg_fx(d,t)
    TLX.add(16,5,"THE WRITTEN HISTORY",(8,12,22),'small'); TLX.add(15.6,4.6,"THE WRITTEN HISTORY",TEXT,'small')
    TLX.add(300,6,"one continuous story",TEXTDIM,'tiny')
    pa=smooth(t/0.5)
    rr(d,PX0,PY0,PX1,PAPER_BOT,lerp(WALL,CREAM,pa)); d.rectangle([PX0,PY0,PX1,PAPER_BOT],outline=CREAM_D); rr(d,PX0,PY0,PX1,PY0+2,lerp(WALL,GOLD,pa))
    for si,(lbl,col,S,meta,hy,suby,liney,hasSub) in enumerate(LAY):
        th,tb,td=sched[si]
        if t<th: break
        ha=smooth((t-th)/0.3); active=(tb<=t<td); bandbot=liney[-1]+9
        rr(d,PX0+2,hy-3,PX1-2,bandbot,lerp(CREAM,col,(0.13 if active else 0.08)*ha))
        if si>0: rr(d,PX0+10,hy-6,PX1-10,hy-6,lerp(CREAM,CREAM_D,0.6*ha))
        barc=lerp(CREAM,col,ha)
        if active: pu=0.5+0.5*math.sin(2*math.pi*t/1.2); barc=lerp(barc,(255,255,255),0.3*pu)
        rr(d,PX0+4,hy-1,PX0+6,bandbot-2,barc)
        TLX.add(TX0,hy,lbl,lerp(CREAM,lerp(INK,col,0.4),ha),'small')
        if hasSub:
            reveal,cseg=hopi_state(t-tb); sdone=reveal>=NC
            sx=TX0
            for j,tg in enumerate(SUBTAGS):
                hot=(j==cseg and not sdone); dn=(j<cseg or sdone)
                c=CYAN if hot else (lerp(CREAM,CYAN_D,0.8) if dn else INKDIM)
                TLX.add(sx,suby,tg,c,'tiny'); w=TLX.w(tg,'tiny')
                if hot: rr(d,int(sx),suby+9,int(sx+w),suby+10,CYAN)
                sx+=w
                if j<len(SUBTAGS)-1: TLX.add(sx,suby,"  -  ",(140,140,154),'tiny'); sx+=TLX.w("  -  ",'tiny')
        else:
            reveal=int(min(len(S),max(0,(t-tb)*CPS)))
        # body (color runs per sub-phase for HOPI, single INK otherwise)
        caret=None
        for (ms,me,ls),yv in zip(meta,liney):
            if reveal<=ms: continue
            if not hasSub:
                sub2=ls if reveal>=me else ls[:reveal-ms]; TLX.add(TX0,yv,sub2,INK,'small')
                if reveal<me: caret=(TX0+TLX.w(sub2,'small'),yv)
            else:
                i=ms
                while i<me and i<reveal:
                    sg=HCS[min(i,NC-1)]; j=i
                    while j<me and j<reveal and HCS[min(j,NC-1)]==sg: j+=1
                    pref=S[ms:i]; TLX.add(TX0+TLX.w(pref,'small'),yv,S[i:j],SUBINK[sg],'small'); i=j
                if ms<reveal<me: caret=(TX0+TLX.w(S[ms:reveal],'small'),yv)
        if caret and int(t*2)%2==0:
            rr(d,int(caret[0])+1,caret[1]-1,int(caret[0])+2,caret[1]+8,INK)
    if pa>0.5: canon_mini(d,432,266,t)                           # our pigeon, writing (corner)
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'/home/user/Ali-Respo/whb_{tv}.png'); print("ok",tv,"dur",round(DUR,1))
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else '/home/user/Ali-Respo/worked_hopi_bleeding_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
