"""BRIDGE v3 - the 'next question' tail, in the SAME environment as the topic's montage
(no writing animation, no fade). The answer is already recorded (ticked) and the next
question is highlighted. Hard-cut onto the end of the montage. One-shot ~4s, 4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=4.0
TLX=uitext.TL()
ACCENT=BR.ACCENT; TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM

# Site -> Route defaults (hospital environment, post-natal patient)
CUR_L="SITE"; CUR_A="HOSPITAL"; NXT_L="ROUTE"; SUF="site-to-route"
TITLE1="SITE OF DELIVERY"; TITLE2="ASK, THEN RECORD"; HOLD=1.0

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),BR.WALL_C); d=ImageDraw.Draw(im)
    BR.background(d,t,0.0); BR.iv_pole(d,44,t); BR.bed(d)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,0.0,HOLD)
    BR.student(d,300,232,t=t,writing=0.0)
    fields=[("SITE","HOSPITAL"),("ROUTE",""),("DIFFICULTY",""),("ANAESTHESIA",""),("EPISIOTOMY","")]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,1,0.0,t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    TLX.add(214,92,"NEXT",(0,180,196),'small')
    hud.speech_bubble(d,TLX,208,100,["NOW ASK:",NXT_L],300)
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,TITLE1,(10,14,24),'body'); TLX.add(16,5,TITLE1,TEXT,'body')
    TLX.add(16.4,21.3,TITLE2,(10,14,24),'small'); TLX.add(16,21,TITLE2,TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bbr3_{tv}.png'); print("ok",tv)
    else:
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/bridge3_{SUF}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
