"""BRIDGE / transition between two history questions: the current question is ticked off
(the doctor notes the answer), an arrow drops, and the NEXT question slides in highlighted.
Short one-shot (~3s), 4K. Args: from_title from_answer to_title suffix."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import focus_kit as FK
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=3.0
TLX=FK.TLX; CX,CY=FK.CX,FK.CY; ACCENT=FK.ACCENT
WALL=(22,28,44); GREEN=(84,196,146)

FROM_T=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith('--') else "SITE OF DELIVERY"
FROM_A=sys.argv[2] if len(sys.argv)>2 and not sys.argv[2].startswith('--') else "HOSPITAL"
TO_T  =sys.argv[3] if len(sys.argv)>3 and not sys.argv[3].startswith('--') else "ROUTE OF DELIVERY"
SUF   =sys.argv[4] if len(sys.argv)>4 and not sys.argv[4].startswith('--') else "site-to-route"

def pigeon_bust(d,hx,hy,t):
    COAT=(226,230,236); LAN=(220,90,104); PIG=(80,82,92); PIG_D=(56,58,68); PIG_H=(108,110,122); BEAK=(94,90,84); CERE=(238,240,244); EYEO=(242,172,60)
    d.polygon([(hx-13,hy+26),(hx+13,hy+26),(hx+9,hy+11),(hx-9,hy+11)],fill=COAT)
    d.polygon([(hx-3,hy+11),(hx+3,hy+11),(hx+2,hy+24),(hx-2,hy+24)],fill=(32,54,110))
    d.line([(hx-4,hy+12),(hx-2,hy+24)],fill=LAN); d.line([(hx+4,hy+12),(hx+2,hy+24)],fill=LAN)
    el(d,hx-8,hy-8,hx+8,hy+10,PIG); el(d,hx-7,hy-8,hx+4,hy-2,PIG_H); el(d,hx-8,hy+4,hx+8,hy+10,PIG_D)
    d.polygon([(hx-7,hy),(hx-15,hy+2),(hx-7,hy+5)],fill=BEAK)
    el(d,hx-9,hy-2,hx-5,hy+1,CERE)
    el(d,hx-4,hy-3,hx+1,hy+2,EYEO); el(d,hx-3,hy-2,hx,hy+1,(30,24,18)); d.point((hx-2,hy-3),fill=(255,255,255))

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,70,lerp(WALL,(255,255,255),0.03)); rr(d,0,183,GW-1,GH-1,lerp(WALL,(0,0,0),0.1))
    FK.glow(d,t,WALL)
    # pigeon doctor bust (top-left) 'noting the answer'
    pigeon_bust(d,40,48,t)
    TLX.add(58,30,"NOTED",(0,180,196),'small')
    # FROM question (completed, ticked)
    fw=TLX.w(FROM_T,'title'); fx=CX-fw/2
    TLX.add(fx,CY-44,FROM_T,(150,160,182),'title')
    TLX.add(CX-TLX.w(FROM_A,'small')/2,CY-18,FROM_A,(132,142,164),'small')
    ts=smooth((t-0.3)/0.6)
    if ts>0.05:
        tx=fx+fw+16; ty=CY-30; s=int(12*ts)
        d.line([(tx,ty),(tx+s//2,ty+s//2)],fill=GREEN,width=3); d.line([(tx+s//2,ty+s//2),(tx+s,ty-s)],fill=GREEN,width=3)
    # arrow down
    aa=smooth((t-0.9)/0.5)
    if aa>0.05:
        ay0=CY+2; ay1=CY+2+int(20*aa); d.line([(CX,ay0),(CX,ay1)],fill=ACCENT,width=3)
        if aa>0.85: d.polygon([(CX,ay1+7),(CX-5,ay1),(CX+5,ay1)],fill=ACCENT)
    # TO question (next, highlighted, slides up)
    if t>1.35:
        app=smooth((t-1.35)/0.7); w=TLX.w(TO_T,'title'); oy=int(16*(1-app))
        rr(d,int(CX-w/2-10),CY+36+oy,int(CX+w/2+10),CY+66+oy,(40,52,76))
        TLX.add(CX-w/2,CY+40+oy,TO_T,ACCENT,'title')
        TLX.add(CX-TLX.w("NEXT QUESTION",'small')/2,CY+72+oy,"NEXT QUESTION",(150,160,182),'small')
    return np.array(Image.fromarray(np.array(im,np.uint8)).resize((GW*SCALE,GH*SCALE),Image.NEAREST),np.uint8)

def frames():
    for i in range(int(DUR*FPS)):
        a=render(i/FPS); bd=ImageDraw.Draw(Image.fromarray(a));
        yield a
# text must be flushed at 4K; do it inside render via TLX
def render4k(t):
    TLX.cmds=[]; a=render(t); big=Image.fromarray(a); bd=ImageDraw.Draw(big); TLX.flush(bd); return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render4k(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bbridge_{tv}.png'); print("ok",tv)
    else:
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/bridge_{SUF}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render4k(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
