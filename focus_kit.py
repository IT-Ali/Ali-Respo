"""Shared scaffold for the FOCUS/LOCKED clips (spotlight + tiny progress + student cue).
Each beat supplies a hero(d,s,t) that draws the active concept centred around (CX,CY),
plus titles / pearls / progress labels / suffixes / a constant ask-cue. render_all()
emits one held 12s seamless clip per concept. 480x270 -> 4K, 24fps."""
import numpy as np, math, subprocess, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()
ACCENT=BR.ACCENT; TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM
CX,CY=236,132
INK=(52,56,72)

def glow(d,t,wall):
    p=0.5+0.5*math.sin(2*math.pi*t/3.0); gr=int(118+8*p)
    d.ellipse([CX-gr,CY-int(gr*0.82),CX+gr,CY+int(gr*0.86)],fill=lerp(wall,(40,52,78),0.45))
    d.ellipse([CX-int(gr*0.66),CY-int(gr*0.56),CX+int(gr*0.66),CY+int(gr*0.6)],fill=lerp(wall,(52,66,96),0.5))

def progress(d,cur,n,label):
    gap=16; x0=CX-(n-1)*gap//2; y=52
    for i in range(n):
        r=4 if i==cur else 2; col=ACCENT if i==cur else (84,94,116)
        el(d,x0+i*gap-r,y-r,x0+i*gap+r,y+r,col)
    TLX.add(CX-TLX.w(label,'small')/2,y+7,label,(150,160,182),'small')

def ask_cue(d,lines):
    COAT=(226,230,236); LAN=(220,90,104)
    PIG=(80,82,92); PIG_D=(56,58,68); PIG_H=(108,110,122); BEAK=(94,90,84); CERE=(238,240,244); EYEO=(242,172,60)
    hx,hy=34,46
    d.polygon([(hx-13,72),(hx+13,72),(hx+9,57),(hx-9,57)],fill=COAT)
    d.polygon([(hx-3,57),(hx+3,57),(hx+2,70),(hx-2,70)],fill=(32,54,110))   # navy tie
    d.line([(hx-4,58),(hx-2,70)],fill=LAN); d.line([(hx+4,58),(hx+2,70)],fill=LAN)
    el(d,hx-8,hy-8,hx+8,hy+10,PIG); el(d,hx-7,hy-8,hx+4,hy-2,PIG_H); el(d,hx-8,hy+4,hx+8,hy+10,PIG_D)
    d.polygon([(hx-7,hy),(hx-15,hy+2),(hx-7,hy+5)],fill=BEAK)
    el(d,hx-9,hy-2,hx-5,hy+1,CERE)
    el(d,hx-4,hy-3,hx+1,hy+2,EYEO); el(d,hx-3,hy-2,hx,hy+1,(30,24,18)); d.point((hx-2,hy-2),fill=(255,255,255))
    w=max(TLX.w(l,'tiny') for l in lines); bx0,by0=50,32; bx1=int(bx0+10+w); by1=by0+16+11*(len(lines)-1)+10
    rr(d,bx0,by0,bx1,by1,(238,240,246)); d.polygon([(bx0,hy-2),(bx0-7,hy+2),(bx0,hy+6)],fill=(238,240,246))
    for i,l in enumerate(lines): TLX.add(bx0+5,by0+4+i*12,l,INK,'tiny')
    TLX.add(bx0+2,by0-11,"THE EXAMINEE ASKS",(0,180,196),'tiny')

def frame(wall,hero,s,t,title,pearl,plabel,pcount,cue_lines,identity):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),wall); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,70,lerp(wall,(255,255,255),0.03)); rr(d,0,183,GW-1,GH-1,lerp(wall,(0,0,0),0.1))
    glow(d,t,wall)
    hero(d,s,t)
    lw=TLX.w(title,'title'); lx=CX-lw/2
    TLX.add(lx+0.5,16.5,title,(8,12,22),'title'); TLX.add(lx,16,title,ACCENT,'title')
    progress(d,s,pcount,plabel)
    ask_cue(d,cue_lines)
    pw=TLX.w(pearl,'small'); TLX.add(CX-pw/2,250,pearl,(202,208,222),'small')
    rr(d,16,250,120,251,ACCENT); TLX.add(16,238,identity,TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

def still(wall,hero,s,t,title,pearl,plabel,pcount,cue_lines,identity,path):
    Image.fromarray(frame(wall,hero,s,t,title,pearl,plabel,pcount,cue_lines,identity)).save(path)

def render_all(prefix,wall,hero,titles,pearls,plabels,suffixes,cue_lines,identity):
    n=len(titles)
    for s in range(n):
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/{prefix}_{suffixes[s]}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)):
            p.stdin.write(frame(wall,hero,s,i/FPS,titles[s],pearls[s],plabels[s],n,cue_lines,identity).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
