"""Beat 6 - ANAESTHESIA ("don't assume general"). Depicts the two scenarios:
GENERAL = patient reclined, asleep, gas mask + Zzz;  SPINAL/EPIDURAL = patient sitting
up, awake, needle in the lower back, legs numb. ASK->RECORD template. 12s loop, 4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; CROSSR=(214,70,80); ANSWC=(236,120,142)
MASKC=(150,205,215); MASKD=(110,170,185); TUBE=(120,135,150); NEEDLE=(210,218,230)
NUMB=(120,170,235); SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; SCARF=BR.SCARF; SCARF_D=BR.SCARF_D; GOWN=BR.GOWN; DARK=BR.DARK

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72))
    rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,CROSSR); rr(d,438,27,448,31,CROSSR)
    return np.array(im,np.uint8).astype(np.float32)

def ga_mask(d,mx,hy,t):
    # gas mask over nose/mouth of the reclined patient + tube + bag + Zzz
    el(d,mx-7,hy+8,mx+9,hy+20,MASKC); el(d,mx-7,hy+8,mx+9,hy+11,(190,225,232))
    d.line([(mx-7,hy+10),(mx-14,hy+8)],fill=MASKD)                 # strap
    d.line([(mx+8,hy+16),(mx+22,hy+30)],fill=TUBE,width=2)         # tube down-right
    rr(d,mx+20,hy+30,mx+34,hy+44,(176,214,196)); rr(d,mx+20,hy+30,mx+34,hy+33,(150,200,170))  # gas bag
    for i in range(3):                                            # Zzz rising
        zt=(t*0.5+i*0.33)%1.0
        TLX.add(mx+10+i*4, hy-6-zt*18, "z", (200,214,235),'small' if i==0 else 'tiny')

def spinal_patient(d,t):
    # side view: sitting on bed edge, hunched forward, needle in lower back, legs numb
    ox,oy=150,170
    # bed edge / couch
    rr(d,70,oy,250,oy+10,(96,108,130)); rr(d,70,oy+10,250,oy+24,(70,80,100))
    rr(d,74,oy+24,82,oy+44,(70,80,100)); rr(d,238,oy+24,246,oy+44,(70,80,100))
    # numb legs hanging (tinted)
    rr(d,ox-20,oy,ox-10,oy+34,NUMB); rr(d,ox-22,oy+32,ox-6,oy+40,(90,120,60))  # thigh/shin + shoe
    # hips + curved back (facing right) leaning forward-left
    d.polygon([(ox-18,oy),(ox+14,oy),(ox+8,oy-30),(ox-10,oy-34),(ox-22,oy-14)],fill=GOWN)  # torso/back
    rr(d,ox+6,oy-28,ox+14,oy-2,(70,78,134))                       # back (right side, where needle goes)
    # arms hugging a pillow in front
    rr(d,ox-26,oy-20,ox-14,oy-6,(206,222,236))                    # pillow
    d.line([(ox-10,oy-28),(ox-22,oy-14)],fill=SKIN,width=3)       # arm
    # head (hunched down), hijab, awake
    hx,hy=ox-14,oy-40
    el(d,hx-9,hy-2,hx+9,hy+14,SCARF); el(d,hx-6,hy+2,hx+6,hy+13,SKIN)
    rr(d,hx-7,hy,hx+7,hy+2,SCARF)
    rr(d,hx-4,hy+6,hx-3,hy+8,DARK); rr(d,hx+2,hy+6,hx+3,hy+8,DARK)   # open (awake) eyes
    # needle/syringe into lower back from the right
    nx,ny=ox+14,oy-14
    d.line([(nx,ny),(nx+16,ny-2)],fill=NEEDLE,width=1)
    rr(d,nx+16,ny-6,nx+30,ny+2,(210,218,230)); rr(d,nx+28,ny-4,nx+34,ny,(150,160,180))  # barrel+plunger
    # numbness sparkles on legs + arrow
    for i in range(3):
        yy=oy+6+i*10+int(2*math.sin(t*4+i))
        TLX.add(ox-30, yy, "~", NUMB,'tiny')

def render(t):
    TLX.cmds=[]
    ga = (int(t//6)%2==0)
    frame=scene_bg()
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    if ga:
        BR.bed(d)
        BR.mother(d,t,0.0,0.8*(0.5+0.5*math.sin(2*math.pi*t/5)),1.0,0.0,1.0,0.0)  # reclined, eyes shut
        ga_mask(d,96,124,t)
    else:
        spinal_patient(d,t)
    BR.student(d,300,232,t=t,writing=1.0)
    # ASK
    ask_on=True; lt=t-(t//6)*6.0; rf=smooth((lt-1.4)/1.3)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,98,["WHAT ANAESTHESIA","WAS USED?"],300)
    # big scenario label + "answer"
    lbl = "GENERAL - FULLY ASLEEP" if ga else "SPINAL / EPIDURAL - AWAKE, NUMB BELOW"
    lc = MASKC if ga else NUMB
    TLX.add(40,34,"ANSWER",ANSWC,'tiny')
    TLX.add(40,44,lbl,lc,'small')
    TLX.add(40,62,"! DON'T ASSUME GENERAL",(236,120,142),'small')
    # RECORD
    anv = "GENERAL" if ga else "SPINAL/EPIDURAL"
    fields=[("SITE","HOSPITAL"),("ROUTE","CAESAREAN"),("DIFFICULTY","DIFFICULT"),("EPISIOTOMY","YES"),("ANAESTHESIA",anv)]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,4,max(0.0,min(1.0,rf)),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,("GENERAL = ASLEEP VIA MASK/TUBE" if ga else "SPINAL = AWAKE, NUMB FROM WAIST DOWN"),(172,180,198),'small')
    # title
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"ANAESTHESIA",(10,14,24),'body'); TLX.add(16,5,"ANAESTHESIA",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN RECORD",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN RECORD",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b6_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat06_anaesthesia_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
