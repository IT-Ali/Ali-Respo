"""CLOSER clip - continues the hero's RECOVERY scene (warm dawn room, mother cradling
baby, flowers, monitor): the midwife waves goodbye and walks out of the room, leaving the
mother & baby resting. Opens on the identical recovery scene so it cuts seamlessly after
birth_recovery. One-shot 12s, 4K, 24fps."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0

def midwife_walk(d,cx,fy,t,moving,wave):
    SCRUB=BR.SCRUB; SCRUB_D=BR.SCRUB_D; SCRUB_H=BR.SCRUB_H; SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; WHITE=BR.WHITE; DARK=BR.DARK; ACC=BR.ACCENT
    if moving: ph=2*math.pi*2.2*t; bob=int(2*abs(math.sin(ph))); sw=int(6*math.sin(ph))
    else: bob=0; sw=0
    sh=bob
    el(d,cx-14,fy,cx+14,fy+3,(10,16,28))
    if moving:
        d.line([(cx,fy-38),(cx-2-sw,fy-1)],fill=SCRUB_D,width=5); d.line([(cx,fy-38),(cx+2+sw,fy-1)],fill=SCRUB_D,width=5)
        rr(d,cx-5-sw,fy-3,cx+1-sw,fy,WHITE); rr(d,cx-1+sw,fy-3,cx+5+sw,fy,WHITE)
    else:
        rr(d,cx-10,fy-40,cx+10,fy-6,SCRUB_D); rr(d,cx-1,fy-40,cx+1,fy-6,DARK)
        rr(d,cx-9,fy-7,cx-2,fy,WHITE); rr(d,cx+2,fy-7,cx+9,fy,WHITE)
    rr(d,cx-12,fy-74-sh,cx+12,fy-38,SCRUB); rr(d,cx-12,fy-74-sh,cx+12,fy-70-sh,SCRUB_H); rr(d,cx+8,fy-70,cx+12,fy-40,SCRUB_D)
    if wave>0.5:
        wv=int(2*math.sin(t*8))
        rr(d,cx-15,fy-72,cx-12,fy-50,SCRUB); rr(d,cx-15,fy-50,cx-12,fy-46,SKIN)
        rr(d,cx+12,fy-78,cx+15,fy-62,SCRUB); rr(d,cx+13+wv,fy-86,cx+18+wv,fy-78,SCRUB); rr(d,cx+14+wv,fy-90,cx+19+wv,fy-86,SKIN)
    else:
        rr(d,cx-15,fy-72,cx-12,fy-48,SCRUB); rr(d,cx+12,fy-72,cx+15,fy-48,SCRUB)
        rr(d,cx-15,fy-50,cx-12,fy-46,SKIN); rr(d,cx+12,fy-50,cx+15,fy-46,SKIN)
    hy=fy-96-sh
    el(d,cx-8,hy,cx+8,hy+20,SKIN); el(d,cx-9,hy-4,cx+9,hy+10,SCRUB); el(d,cx-9,hy-4,cx+4,hy+4,SCRUB_H)
    rr(d,cx-4,hy+8,cx-3,hy+10,DARK); rr(d,cx+2,hy+8,cx+3,hy+10,DARK); d.line([(cx-2,hy+15),(cx+2,hy+15)],fill=SKIN_D)
    d.line([(cx-5,hy+18),(cx-6,fy-60),(cx-1,fy-54)],fill=(210,218,228)); d.line([(cx+5,hy+18),(cx+6,fy-60),(cx+1,fy-54)],fill=(210,218,228)); el(d,cx-2,fy-56,cx+1,fy-53,ACC)

def render(t):
    im=Image.new('RGB',(GW,GH),BR.WALL_C); d=ImageDraw.Draw(im)
    BR.background(d,t,1.0)                 # warm dawn recovery room
    BR.iv_pole(d,44,t); BR.bed(d); BR.nightstand(d,266,188,1.0); BR.monitor(d,352,90,t,True)
    breath=1.4*(0.5+0.5*math.sin(2*math.pi*t/4.0))
    BR.mother(d,t,0.0,breath,0.0,0.0,1.0,1.0)   # cradling baby, calm, awake
    # midwife: waves (0-2.0s), walks out right (2.0-6.6s), then gone
    wf=smooth(max(0.0,min(1.0,(t-2.0)/4.4))); mx=int(round(312+(524-312)*wf))
    moving=(2.0<t<6.7) and wf<1.0
    if mx<505:
        midwife_walk(d,mx,232,t,moving, wave=1.0 if t<2.0 else 0.0)
    BR.hearts(d,t,1.0)
    # title (matches the hero's recovery frame)
    BR.text(d,"LABOUR & DELIVERY",14,12,BR.TEXT)
    rr(d,14,22,150,22,BR.HEART)
    BR.phase_label(d,t,"RECOVERY",1.0)
    arr=np.array(im,np.uint8)
    return np.array(Image.fromarray(arr).resize((GW*SCALE,GH*SCALE),Image.NEAREST),np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bleave_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/midwife_leaves_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
