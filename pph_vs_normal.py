"""PPH vs NORMAL bleeding - ONE idea: the AMOUNT. Two blood-loss measuring jugs side by
side. Left (normal lochia, teal) settles well under the line; right (PPH, red) pours past
the 500/1000 mL line and overflows. 480x270 -> supersampled, 1920x1080, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(16,19,27)
L_BG=(14,32,30); L_BG2=(20,46,42)
R_BG=(38,18,22); R_BG2=(54,22,26)
GREEN=(84,196,146); RED=(230,70,78)
BLOOD=(176,34,48); BLOOD_D=(128,18,32); BLOOD_H=(210,62,76)
GLASS=(150,160,178); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; CYAN=(0,188,204)

def jug(d,cx,frac,pph,t):
    x0,x1,yt,yb=cx-21,cx+21,72,172; H=yb-yt
    rr(d,x0-2,yt,x0,yb+2,GLASS); rr(d,x1,yt,x1+2,yb+2,GLASS); rr(d,x0-2,yb,x1+2,yb+2,GLASS)
    rr(d,x0,yt,x1,yb,(24,20,28))
    lvl=yb-int(H*min(frac,1.0)); wob=1.3*math.sin(2*math.pi*t/4.0)
    for xx in range(x0,x1):
        sy=lvl+int(wob*math.sin((xx-x0)*0.5)); rr(d,xx,sy,xx,yb,BLOOD)
    rr(d,x0,lvl,x1,lvl+1,BLOOD_H)
    for f,lab in [(0.25,"250"),(0.5,"500"),(0.75,"750"),(1.0,"1000")]:
        ty=yb-int(H*f); d.line([(x1,ty),(x1+4,ty)],fill=GLASS); TLX.add(x1+6,ty-4,lab,(178,174,186),'tiny')
    thr=yb-int(H*0.5)
    for xx in range(x0,x1,6): d.line([(xx,thr),(xx+3,thr)],fill=(236,110,110))
    TLX.add(x0-30,thr-4,"PPH",(236,120,120),'tiny')
    shim=int(1.5*math.sin(2*math.pi*t/0.5))
    if pph:                                                         # active gush + overflow
        rr(d,cx-3+shim,56,cx+3+shim,lvl,BLOOD_H)
        if frac>=1.0:
            for ex in (x0,x1-2): rr(d,ex-1,yt,ex+1,yb+2,BLOOD_D)
            rr(d,x0-1,yt-2,x1+1,yt+2,BLOOD)
            el(d,cx-34,yb+2,cx+34,yb+11,BLOOD_D); el(d,cx-24,yb+3,cx+24,yb+8,BLOOD)
    else:                                                           # last trickle, settling
        rr(d,cx-1+shim,56,cx+1+shim,66,lerp((24,20,28),BLOOD_H,0.7))

def side(d,cx,x0,x1,bg,bg2,accent,title,frac,pph,amount,cap,t):
    rr(d,x0,42,x1,208,bg); rr(d,x0,42,x1,58,bg2)
    tw=TLX.w(title,'small'); TLX.add(cx-tw/2,46,title,accent,'small')
    rr(d,cx-tw/2,61,cx+tw/2,62,lerp(bg,accent,0.5))
    jug(d,cx,frac,pph,t)
    aw=TLX.w(amount,'body'); TLX.add(cx-aw/2,178,amount,accent,'body')
    cw=TLX.w(cap,'small'); TLX.add(cx-cw/2,196,cap,lerp(bg,(236,236,240),0.9),'small')

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    segs=[("NORMAL",GREEN),("   vs   ",TEXTDIM),("PPH",RED)]
    tot=sum(TLX.w(a,'body') for a,_ in segs); sx=240-tot/2
    for a,c in segs:
        TLX.add(sx+0.4,6.3,a,(8,10,16),'body'); TLX.add(sx,6,a,c,'body'); sx+=TLX.w(a,'body')
    sub="IT  COMES  DOWN  TO  THE  AMOUNT"; fw=TLX.w(sub,'small'); TLX.add(240-fw/2,27,sub,CYAN,'small')
    side(d,120,8,232,L_BG,L_BG2,GREEN,"NORMAL  (LOCHIA)",0.30,False,"~ 300 mL","a small loss, settling",t)
    side(d,360,248,472,R_BG,R_BG2,RED,"PPH  (HAEMORRHAGE)",1.05,True,"1000+ mL","pours past the line",t)
    for yy in range(46,206,6): d.line([(240,yy),(240,yy+3)],fill=(70,76,92))
    el(d,231,118,249,136,(26,30,40)); d.ellipse([231,118,249,136],outline=(90,96,112))
    TLX.add(234.2,122,"vs",(200,206,220),'tiny')
    rr(d,8,214,472,240,(26,22,30)); rr(d,8,214,472,216,(120,60,70))
    TLX.add(16,219,"THE LINE",(236,150,160),'tiny')
    foot=">= 500 mL after vaginal birth    *    >= 1000 mL after caesarean    =    PPH"
    fw2=TLX.w(foot,'small'); TLX.add(240-fw2/2,219,foot,(214,196,200),'small')
    rr(d,8,246,472,268,(20,24,34))
    rule="Same blood - the difference is HOW MUCH, and whether it crosses the line"
    rw=TLX.w(rule,'small'); TLX.add(240-rw/2,251,rule,(160,168,186),'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/pvn_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/pph_vs_normal_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
