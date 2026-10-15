"""INTRO / START clip - the pigeon-doctor student walks across the ward to the patient's
bedside, then settles in and offers to take a history. One-shot 12s, 4K, 24fps."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()
WALL=(22,28,44); WALL2=(30,38,56); FLOOR=(28,38,56); FLOORH=(40,52,72)
ACCENT=BR.ACCENT; TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ANSWC=(236,120,142)

def ward_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72)); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    ccx,ccy=250,46
    el(d,ccx-12,ccy-12,ccx+12,ccy+12,(222,226,234)); el(d,ccx-10,ccy-10,ccx+10,ccy+10,(30,40,60))
    d.line([(ccx,ccy),(ccx-5,ccy-4)],fill=(236,240,246)); d.line([(ccx,ccy),(ccx+5,ccy-4)],fill=ACCENT); el(d,ccx-1,ccy-1,ccx+1,ccy+1,(236,240,246))
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,(214,70,80)); rr(d,438,27,448,31,(214,70,80))
    BR.iv_pole(d,44,0.0); BR.bed(d)
    return im

def pigeon_walk(d,cx,fy,t,moving,writing):
    COAT=(226,230,236); COAT_D=(198,204,214); SHIRT=(86,148,198); SHIRT_D=(62,118,166)
    TROUS=(58,64,84); SHOE=(34,38,52); CLIP=(150,110,74); PAPER=(238,240,246); PEN=(40,44,60); LAN=(220,90,104); CLAW=(46,48,56)
    PIG=(80,82,92); PIG_D=(56,58,68); PIG_H=(108,110,122); BEAK=(94,90,84); BEAK_D=(66,62,58); CERE=(238,240,244); EYEO=(242,172,60)
    if moving: ph=2*math.pi*2.2*t; bob=int(2*abs(math.sin(ph))); sw=int(6*math.sin(ph))
    else: ph=0.0; bob=int(1*math.sin(2*math.pi*t/3.5)); sw=0
    el(d,cx-13,fy,cx+13,fy+3,(10,16,28))                               # shadow
    if moving:
        d.line([(cx,fy-36),(cx-2-sw,fy-1)],fill=TROUS,width=5); d.line([(cx,fy-36),(cx+2+sw,fy-1)],fill=TROUS,width=5)
        rr(d,cx-5-sw,fy-3,cx+1-sw,fy,SHOE); rr(d,cx-1+sw,fy-3,cx+5+sw,fy,SHOE)
    else:
        rr(d,cx-9,fy-38,cx+9,fy-6,TROUS); rr(d,cx-1,fy-38,cx+1,fy-6,(44,48,66))
        rr(d,cx-9,fy-7,cx-2,fy,SHOE); rr(d,cx+2,fy-7,cx+9,fy,SHOE)
    rr(d,cx-10,fy-72-bob,cx+10,fy-36,SHIRT); rr(d,cx+6,fy-70,cx+10,fy-38,SHIRT_D)
    d.polygon([(cx-2,fy-71-bob),(cx+2,fy-71-bob),(cx+3,fy-60),(cx,fy-55),(cx-3,fy-60)],fill=(32,54,110))
    rr(d,cx-13,fy-74-bob,cx-6,fy-34,COAT); rr(d,cx+6,fy-74-bob,cx+13,fy-34,COAT)
    rr(d,cx-13,fy-74-bob,cx-11,fy-34,COAT_D); rr(d,cx+11,fy-74-bob,cx+13,fy-34,COAT_D)
    rr(d,cx-13,fy-74-bob,cx+13,fy-72-bob,COAT)
    d.polygon([(cx-6,fy-72-bob),(cx-2,fy-72-bob),(cx-5,fy-58)],fill=COAT); d.polygon([(cx+6,fy-72-bob),(cx+2,fy-72-bob),(cx+5,fy-58)],fill=COAT)
    d.line([(cx-4,fy-71-bob),(cx-2,fy-56)],fill=LAN); d.line([(cx+4,fy-71-bob),(cx+2,fy-56)],fill=LAN)
    rr(d,cx-3,fy-56,cx+3,fy-48,PAPER); rr(d,cx-3,fy-56,cx+3,fy-54,ACCENT)
    rr(d,cx-14,fy-72-bob,cx-11,fy-52,COAT)
    clx,cly=cx-20,fy-56
    rr(d,clx-1,cly-1,clx+15,cly+17,CLIP); rr(d,clx+1,cly+1,clx+13,cly+15,PAPER); rr(d,clx+4,cly-3,clx+10,cly+1,(120,130,150))
    for ly in range(cly+4,cly+14,3): rr(d,clx+3,ly,clx+11,ly,(176,186,200))
    rr(d,clx-3,cly+10,clx+2,cly+16,CLAW)
    pw=int(2*math.sin(t*9)) if writing>0.5 else 0
    rr(d,cx+11,fy-72-bob,cx+14,fy-56,COAT); rr(d,cx+9,fy-58,cx+14,fy-52,CLAW)
    d.line([(cx+11,fy-54),(clx+9+pw,cly+8)],fill=PEN); el(d,clx+8+pw,cly+7,clx+10+pw,cly+9,ACCENT)
    hy=fy-94-bob
    d.line([(cx-5,fy-76-bob),(cx-8,fy-64),(cx-5,fy-57)],fill=(44,48,58),width=1); d.line([(cx+5,fy-76-bob),(cx+8,fy-62),(cx+5,fy-57)],fill=(44,48,58),width=1)
    el(d,cx-7,fy-58,cx-3,fy-54,(196,202,212))
    el(d,cx-8,hy-2,cx+8,hy+18,PIG); el(d,cx-7,hy-2,cx+5,hy+5,PIG_H); el(d,cx-8,hy+11,cx+8,hy+18,PIG_D)
    d.polygon([(cx-7,hy+7),(cx-16,hy+9),(cx-7,hy+12)],fill=BEAK); d.polygon([(cx-7,hy+10),(cx-14,hy+9),(cx-7,hy+12)],fill=BEAK_D)
    el(d,cx-10,hy+5,cx-6,hy+8,CERE)
    el(d,cx-4,hy+4,cx+1,hy+9,EYEO); el(d,cx-3,hy+5,cx,hy+8,(30,24,18)); d.point((cx-2,hy+5),fill=(255,255,255))

def render(t):
    TLX.cmds=[]
    # same warm dawn recovery room as the hero/closer (so the bookends match)
    im=Image.new('RGB',(GW,GH),BR.WALL_C); d=ImageDraw.Draw(im)
    BR.background(d,t,1.0)
    BR.iv_pole(d,44,t); BR.bed(d); BR.nightstand(d,266,188,1.0); BR.monitor(d,352,90,t,True)
    breath=1.4*(0.5+0.5*math.sin(2*math.pi*t/4.0)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,1.0,1.0)
    wf=smooth(max(0.0,min(1.0,(t-0.5)/4.2))); sx=int(round(500+(300-500)*wf))
    moving = (0.5<t<4.95) and wf<1.0
    pigeon_walk(d,sx,232,t,moving,writing=(1.0 if (not moving and t>5.4) else 0.0))
    BR.hearts(d,t,1.0)
    if t>5.2:
        TLX.add(214,88,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,96,["LET ME TAKE","YOUR HISTORY"],300)
    # title (matches hero/closer recovery frame)
    BR.text(d,"LABOUR & DELIVERY",14,12,BR.TEXT)
    rr(d,14,22,150,22,BR.HEART)
    BR.phase_label(d,t,"TAKING A HISTORY",1.0)
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bintro_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/intro_walkin_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
