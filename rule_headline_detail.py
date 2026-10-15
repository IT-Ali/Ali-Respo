"""THE RULE: one headline question (always ask) -> then WHERE it lands. Most headlines go to
the HOPI with their extras; ROUTE (the delivery mode) goes to the CHIEF COMPLAINT, only its
details to HOPI. Cycles through this slide's topics. With VFX. 480x270 -> 4K, 24fps."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; W=3.8; DUR=19.2
TLX=uitext.TL()

WALL=(18,20,30); WALL2=(26,30,44)
GOLD=(230,186,96); GOLDB=(236,204,140); CARDBG=(40,34,20); CARDED=(150,120,60); INK=(36,30,16)
CYAN=(0,188,204); CYAN_D=(10,96,108); HOPIBG=(16,32,36); COLBG=(24,44,48); COLED=(14,70,80)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; DOT=(120,200,210)

# (name, dest, headline, extras)   dest = where the HEADLINE lands
TOPICS=[
 ("PPH","HOPI","Did she bleed heavily?",["amount / pads","clots","timing (1ry / 2ry)","felt faint?","treatment given"]),
 ("EPISIOTOMY","HOPI","Any cut or stitches?",["bleeding at the site","perineal pain","dysuria","haematuria"]),
 ("ROUTE","CC","How did she deliver?",["forceps / vacuum (if assisted)"]),
 ("DIFFICULTY","HOPI","Easy or difficult labour?",["how long","obstructed / prolonged","what was done"]),
 ("RECOVERY","HOPI","How was recovery?",["bowel & flatus","bladder","mobility","feeding"]),
]
CC_ITEMS=["route of delivery","elective / emergency","indication (reason)"]

_T=0.0
_rng=np.random.default_rng(5); PN=50
_PX=_rng.uniform(0,480,PN); _PY=_rng.uniform(30,270,PN)
_PSP=_rng.uniform(3,9,PN); _PPH=_rng.uniform(0,6.28,PN); _PSZ=_rng.integers(1,3,PN)
_PCOL=[GOLDB if _rng.random()<0.5 else (120,210,224) for _ in range(PN)]

def oshoot(p):
    p=min(1.0,max(0.0,p)); c=1.70158; return 1+(c+1)*((p-1)**3)+c*((p-1)**2)
def spark(d,x,y,s,c):
    d.line([(x-s,y),(x+s,y)],fill=c); d.line([(x,y-s),(x,y+s)],fill=c)
def arrow(d,x0,y0,x1,y1,col):
    d.line([(x0,y0),(x1,y1)],fill=col,width=2); a=math.atan2(y1-y0,x1-x0)
    for aa in (a+2.6,a-2.6): d.line([(x1,y1),(x1-7*math.cos(aa),y1-7*math.sin(aa))],fill=col,width=2)
def bg_fx(d,t):
    for bx,by,tint,amp,per in [(130,120,GOLD,42,9.0),(370,150,CYAN,48,11.0),(60,235,CYAN,30,7.0)]:
        ox=amp*math.sin(2*math.pi*t/per); oy=16*math.cos(2*math.pi*t/(per*1.3))
        for r,a in [(74,0.05),(46,0.07)]:
            cx=int(bx+ox); cy=int(by+oy); d.ellipse([cx-r,cy-int(r*0.7),cx+r,cy+int(r*0.7)],fill=lerp(WALL,tint,a))
    for i in range(PN):
        py=(_PY[i]-t*_PSP[i])%240+30; px=(_PX[i]+6*math.sin(t*0.6+_PPH[i]))%480
        tw=0.35+0.65*(0.5+0.5*math.sin(t*2.2+_PPH[i])); s=int(_PSZ[i])
        d.rectangle([int(px),int(py),int(px)+s,int(py)+s],fill=lerp(WALL,_PCOL[i],0.55*tw))
def glow_rect(d,x0,y0,x1,y1,col,ed,k,per=2.6):
    pu=0.5+0.5*math.sin(2*math.pi*_T/per)
    d.rectangle([x0-2,y0-2,x1+2,y1+2],outline=lerp(WALL,col,(0.10+0.09*pu)*k))
    d.rectangle([x0,y0,x1,y1],outline=lerp(ed,col,(0.35+0.4*pu)*k) if k>0 else ed)

def render(t):
    global _T; _T=t; TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    bg_fx(d,t)
    rr(d,0,0,GW-1,30,WALL2)
    TLX.add(16,4,"ONE HEADLINE  ->  WHERE IT LANDS",(8,12,22),'body'); TLX.add(15.6,3.6,"ONE HEADLINE  ->  WHERE IT LANDS",TEXT,'body')
    TLX.add(16,20,"always ask the headline  -  most go to the HOPI; only the route (mode) notes to the complaint",TEXTDIM,'small')

    c=min(len(TOPICS)-1,int(t//W)); local=t-c*W
    vis=min(smooth(local/0.35),smooth((W-local)/0.35))
    name,dest,headline,details=TOPICS[c]; isCC=(dest=="CC")

    # topic name
    lead="ASKING ABOUT   "
    lw=TLX.w(lead,'small')+TLX.w(name,'body'); sx=168-lw/2
    TLX.add(sx,46,lead,lerp(WALL,TEXTDIM,vis),'small'); TLX.add(sx+TLX.w(lead,'small'),42,name,lerp(WALL,GOLDB,vis),'body')

    # ---- HEADLINE pill (always ask) ----
    pin=smooth(local/0.4); ox=int(-10*(1-oshoot(pin)))
    px0,py0,px1,py1=36,94,212,138
    TLX.add(px0+2,82,"ALWAYS ASK",lerp(WALL,GOLD,vis),'tiny')
    base=lerp(WALL,GOLD,vis)
    rr(d,px0+ox,py0,px1+ox,py1,base); rr(d,px0+ox,py0,px1+ox,py0+2,lerp(WALL,GOLDB,vis))
    if vis>0.9:
        period=(px1-px0)+44; sh=(_T*72)%period-22
        for dy in range(py1-py0):
            sx2=px0+ox+int(sh)+int(dy*0.5)
            if 0<=sx2-(px0+ox)<(px1-px0): d.line([(sx2,py0+dy),(sx2,py0+dy)],fill=lerp(base,(255,255,255),0.5))
    hw=TLX.w(headline,'small'); TLX.add((px0+px1)/2-hw/2+ox,py0+15,headline,lerp(WALL,INK,vis),'small')
    # destination badge
    g=smooth((local-0.55)/0.4)
    badge=("-> goes to the CHIEF COMPLAINT" if isCC else "-> goes to the HOPI")
    TLX.add(px0+2,py1+4,badge,lerp(WALL,(GOLDB if isCC else CYAN),vis*g),'tiny')

    # ---- CHIEF COMPLAINT bin (the big 3) ----
    bx0,by0,bx1,by1=300,52,462,104
    rr(d,bx0,by0,bx1,by1,lerp(WALL,CARDBG,vis)); glow_rect(d,bx0,by0,bx1,by1,GOLD,CARDED,vis if isCC else 0.0,2.4)
    rr(d,bx0,by0,bx1,by0+12,lerp(WALL,CARDED,vis*0.6))
    TLX.add(bx0+5,by0+2,"CHIEF COMPLAINT",lerp(WALL,GOLDB,vis),'tiny')
    for i,it in enumerate(CC_ITEMS):
        hot=(isCC and i==0)
        k=vis*(g if hot else 0.5)
        iy=by0+17+i*11
        lbl=it
        if hot: rr(d,bx0+3,iy-1,bx1-3,iy+9,lerp(CARDBG,(90,72,34),g*vis))
        el(d,bx0+8,iy+3,bx0+11,iy+6,lerp(CARDBG,GOLD,k))
        TLX.add(bx0+15,iy,lbl,lerp(CARDBG,(GOLDB if hot else (170,150,110)),k),'tiny')

    # ---- HOPI bin (extras; + headline if dest HOPI) ----
    hx0,hy0,hx1,hy1=300,110,462,240
    tk=smooth((local-0.8)/0.4)*vis
    rr(d,hx0,hy0,hx1,hy1,lerp(WALL,HOPIBG,tk)); glow_rect(d,hx0,hy0,hx1,hy1,CYAN,CYAN_D,tk if not isCC else vis*0.6,3.0)
    rr(d,hx0,hy0,hx1,hy0+13,lerp(WALL,CYAN_D,tk))
    TLX.add(hx0+5,hy0+2,("HOPI  -  THE EXTRAS" if isCC else "HOPI  -  HEADLINE + EXTRAS"),lerp(WALL,(224,244,246),tk),'tiny')
    rows=([] if isCC else [(headline,True)])+[(e,False) for e in details]
    for i,(it,main) in enumerate(rows):
        ci=smooth((local-(1.1+i*0.3))/0.35); kk=ci*vis
        if kk<=0: continue
        cy=hy0+19+i*18; cox=int(-14*(1-oshoot(ci)))
        fill=lerp(HOPIBG,(34,64,72) if main else COLBG,kk); barc=lerp(HOPIBG,(130,235,248) if main else CYAN,kk)
        rr(d,hx0+6+cox,cy,hx1-6+cox,cy+15,fill); rr(d,hx0+6+cox,cy,hx0+8+cox,cy+15,barc)
        el(d,hx0+12+cox,cy+6,hx0+15+cox,cy+9,lerp(HOPIBG,DOT,kk))
        if 0.1<ci<0.9:
            gg=math.sin(ci*math.pi); spark(d,hx0+13+cox,cy+8,2+int(2*gg),lerp(HOPIBG,(230,250,255),gg*vis))
        TLX.add(hx0+19+cox,cy+2,it+("   (the main Q)" if main else ""),lerp(HOPIBG,(224,244,248) if main else (206,226,230),kk),'tiny')

    # ---- routing arrow headline -> its home ----
    if g>0:
        ac=lerp(WALL,(GOLD if isCC else CYAN),vis*g)
        if isCC: arrow(d,214+ox,108,298,80,ac)
        else: arrow(d,214+ox,124,298,150,ac)

    # ---- progress dots ----
    for i in range(len(TOPICS)):
        dx=124-(len(TOPICS)*14)//2+i*14
        if i==c: el(d,dx-4,168,dx+4,176,GOLD)
        else: el(d,dx-2,170,dx+2,174,(70,76,92))

    # ---- footer rule ----
    pf=smooth((t-0.5)/0.6)
    rr(d,8,246,472,267,lerp(WALL,(28,24,34),pf))
    r="Always ask the headline  *  route (mode) -> complaint  *  everything else -> HOPI"
    rw=TLX.w(r,'small'); TLX.add(240-rw/2,250,r,lerp(WALL,(210,200,180),pf),'small')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/rhd_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/rule_headline_detail_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
