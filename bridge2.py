"""BRIDGE v2 - at the bedside: the patient's answer is written onto the HISTORY SHEET
(types in + tick), then the sheet advances to highlight the NEXT question. One-shot ~3s.
Args: cur_label cur_answer next_label suffix  [done_label:done_ans ...]"""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=6.0
TLX=uitext.TL()
WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74); ACCENT=BR.ACCENT

args=[a for a in sys.argv[1:] if not a.startswith('--') and '=' not in a]
CUR_L = args[0] if len(args)>0 else "SITE"
CUR_A = args[1] if len(args)>1 else "HOSPITAL"
NXT_L = args[2] if len(args)>2 else "ROUTE"
SUF   = args[3] if len(args)>3 else "site-to-route"
DONE  = [tuple(x.split(':')) for x in args[4:]] if len(args)>4 else []

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72)); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,(214,70,80)); rr(d,438,27,448,31,(214,70,80))
    BR.iv_pole(d,44,0.0); BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def render(t):
    TLX.cmds=[]
    im=Image.fromarray(np.clip(scene_bg(),0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,1.0,1.0)
    BR.student(d,300,232,t=t,writing=1.0)
    fields=DONE[-2:]+[(CUR_L,CUR_A),(NXT_L,"")]
    ic=len(fields)-2
    if t<3.5: active=ic; fill=smooth((t-0.6)/2.0)
    else: active=ic+1; fill=0.0
    hud.history_sheet(d,TLX,340,26,134,130,"HISTORY SHEET",fields,active,min(1.0,fill),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    # captions
    if t<3.5:
        TLX.add(214,92,"NOTING",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,100,["WRITING IT","ON THE SHEET"],300)
    else:
        TLX.add(214,92,"NEXT",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,100,["NOW ASK:",NXT_L],300)
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"HISTORY TAKING",(10,14,24),'body'); TLX.add(16,5,"HISTORY TAKING",BR.TEXT,'body')
    TLX.add(16.4,21.3,"NOTE, THEN NEXT",(10,14,24),'small'); TLX.add(16,21,"NOTE, THEN NEXT",BR.TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bbr2_{tv}.png'); print("ok",tv)
    else:
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/bridge_{SUF}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
