"""Pixel-art hospital scene: reclined pregnant patient, breathing + blink,
IV drip, fetal monitor. 320x180 grid -> nearest-neighbor x12 -> 3840x2160.
--preview saves one 4K PNG; otherwise pipes frames to ffmpeg -> MP4."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw

FFMPEG = r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
GW, GH, SCALE = 320, 180, 12
FPS, DUR = 20, 5.0

# ---- palette (dark medical theme) ----
WALL   =(16,24,40);  WALL2=(20,30,48); FLOOR=(26,38,58); FLOORH=(34,48,70)
TRIM   =(30,44,66)
FRAME  =(96,108,130); FRAME_D=(70,80,100)
MAT    =(228,232,240); MAT_D=(200,206,220)
PILLOW =(206,222,236)
BLANK  =(36,150,172); BLANK_D=(26,120,142); BLANK_H=(72,186,204)
SKIN   =(240,198,166); SKIN_D=(214,168,138)
SCARF  =(206,116,132); SCARF_D=(170,86,104); SCARF_H=(226,150,164)
HAIRLINE=(60,40,46)
IVPOLE =(120,132,150); BAG=(196,232,210); BAGLIQ=(150,214,180); DRIP=(170,222,235)
MONF   =(44,54,74); MONS=(8,14,22); ECG=(78,230,150); CYAN=(0,200,214)
CROSSR =(226,74,74)
EYE=(40,30,40)

def rr(d,x0,y0,x1,y1,c): d.rectangle([x0,y0,x1,y1],fill=c)

# 3x5 pixel digits for the monitor
FONT={ '0':["111","101","101","101","111"],'1':["010","110","010","010","111"],
 '2':["111","001","111","100","111"],'3':["111","001","111","001","111"],
 '4':["101","101","111","001","001"],'5':["111","100","111","001","111"],
 '6':["111","100","111","101","111"],'7':["111","001","010","010","010"],
 '8':["111","101","111","101","111"],'9':["111","101","111","001","111"]}
def pixtext(d,s,x,y,c):
    for ch in s:
        g=FONT.get(ch);
        if g:
            for ry,row in enumerate(g):
                for rx,v in enumerate(row):
                    if v=='1': d.point((x+rx,y+ry),fill=c)
        x+=4

def dome(d,cx,baseY,topY,halfw,c,hi,sh):
    for y in range(topY,baseY+1):
        frac=(y-topY)/max(1,(baseY-topY))
        w=int(halfw*math.sin(frac*math.pi/2))
        if w<=0: continue
        rr(d,cx-w,y,cx+w,y,c)
        if y<topY+3: rr(d,cx-max(0,w-2),y,cx+max(0,w-2),y,hi)  # top highlight band
    # right-side shade
    for y in range(topY+2,baseY):
        frac=(y-topY)/max(1,(baseY-topY)); w=int(halfw*math.sin(frac*math.pi/2))
        if w>3: rr(d,cx+w-2,y,cx+w,y,sh)

def frame(t):
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    # wall gradient + vignette-ish bands
    rr(d,0,0,GW-1,54,WALL2)
    rr(d,0,96,GW-1,97,TRIM)          # wall trim
    rr(d,0,98,GW-1,129,WALL)
    # floor
    rr(d,0,130,GW-1,GH-1,FLOOR); rr(d,0,130,GW-1,131,FLOORH)
    # wall medical cross plaque (top area)
    cx0,cy0=150,20
    rr(d,cx0-1,cy0-1,cx0+13,cy0+13,(236,240,246))
    rr(d,cx0+4,cy0+1,cx0+8,cy0+11,CROSSR); rr(d,cx0+1,cy0+4,cx0+11,cy0+8,CROSSR)

    # ---- IV pole + bag + drip ----
    rr(d,50,40,51,158,IVPOLE); rr(d,44,158,58,159,IVPOLE)       # pole + base
    rr(d,42,40,60,54,BAG); rr(d,44,43,58,54,BAGLIQ)             # bag
    rr(d,49,56,53,66,(210,220,230))                            # drip chamber
    # drip drop animation
    dphase=(t%1.3)/1.3
    dy=56+int(dphase*9)
    if dphase<0.75: rr(d,51,dy,51,dy+1,DRIP)
    # tube down then to the hand
    rr(d,51,66,51,120,DRIP)
    for (xa,ya,xb,yb) in [(51,120,70,124),(70,124,120,126)]:
        steps=max(abs(xb-xa),abs(yb-ya))
        for i in range(steps+1):
            x=round(xa+(xb-xa)*i/steps); y=round(ya+(yb-ya)*i/steps); d.point((x,y),fill=DRIP)

    # ---- bed ----
    rr(d,92,150,96,168,FRAME_D); rr(d,236,150,240,168,FRAME_D)  # legs
    rr(d,86,138,246,152,FRAME)                                   # base
    rr(d,88,120,244,138,MAT); rr(d,88,136,244,138,MAT_D)         # mattress
    rr(d,82,100,90,152,FRAME)                                    # headboard (left)
    rr(d,242,112,250,152,FRAME)                                  # footboard
    rr(d,92,112,120,122,PILLOW)                                  # pillow

    # ---- breathing ----
    br=0.5+0.5*math.sin(2*math.pi*t/4.0); dyb=int(round(1.8*br))

    # ---- blanket + belly bump ----
    rr(d,118,118,240,132,BLANK); rr(d,118,130,240,132,BLANK_D)
    dome(d,176,120,100-dyb,30,BLANK,BLANK_H,BLANK_D)             # pregnant bump
    rr(d,118,118,240,119,BLANK_H)                                # blanket top hilite

    # ---- patient head + scarf ----
    hx,hy=104,101
    rr(d,hx,hy,hx+14,hy+15,SKIN)                                 # head/face base
    rr(d,hx,hy-2,hx+14,hy+2,SCARF); rr(d,hx-2,hy+2,hx+1,hy+16,SCARF)  # scarf top+left
    rr(d,hx+13,hy+2,hx+16,hy+18,SCARF); rr(d,hx+12,hy+14,hx+18,hy+24,SCARF)  # right drape
    rr(d,hx,hy-2,hx+14,hy-1,SCARF_H); rr(d,hx+13,hy+2,hx+14,hy+16,SCARF_D)
    # face opening: keep skin in front-lower
    rr(d,hx+2,hy+3,hx+12,hy+14,SKIN)
    # eyes / blink
    blink = (t%3.2) > 3.04
    if blink:
        rr(d,hx+4,hy+8,hx+6,hy+8,SKIN_D); rr(d,hx+8,hy+8,hx+10,hy+8,SKIN_D)
    else:
        rr(d,hx+4,hy+7,hx+5,hy+8,EYE); rr(d,hx+8,hy+7,hx+9,hy+8,EYE)
    rr(d,hx+6,hy+11,hx+8,hy+11,SCARF_D)                          # mouth

    # ---- fetal monitor on stand (right) ----
    rr(d,276,78,278,150,FRAME_D); rr(d,268,150,286,151,FRAME_D) # stand
    rr(d,256,40,300,74,MONF); rr(d,259,43,297,71,MONS)          # screen
    # ECG scroll
    base=62; prev=None
    beat=(t*1.25)%1.0
    for sx in range(260,297):
        ph=((sx-260)/37 + t*0.9)%1.0
        y=base
        if 0.45<ph<0.5: y=base-10
        elif 0.5<=ph<0.55: y=base+6
        elif 0.40<ph<0.45: y=base-2
        if prev is not None:
            y0,y1=sorted((prev,y)); rr(d,sx,y0,sx,y1,ECG)
        d.point((sx,y),fill=ECG); prev=y
    # heart + HR number
    hb=1.0 if beat<0.12 else 0.0
    hc=(240,90,110) if hb else (190,70,90)
    rr(d,262,45,264,47,hc); rr(d,265,45,267,47,hc); rr(d,263,47,266,49,hc); rr(d,264,49,265,50,hc)
    pixtext(d,"140",283,45,ECG)

    return np.array(im,dtype=np.uint8)

def upscale(a):
    return np.array(Image.fromarray(a).resize((GW*SCALE,GH*SCALE),Image.NEAREST))

if __name__=='__main__':
    if '--preview' in sys.argv:
        out=r'D:/Ue/UE_5.8/obgyn_explainer/preview.png'
        Image.fromarray(upscale(frame(1.0))).save(out); print("wrote",out)
    else:
        OUT=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith('--') else r'D:/Ue/UE_5.8/obgyn_explainer/pixel_patient_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{GW}x{GH}','-r',str(FPS),'-i','-',
             '-vf',f'scale={GW*SCALE}:{GH*SCALE}:flags=neighbor,format=yuv420p',
             '-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
