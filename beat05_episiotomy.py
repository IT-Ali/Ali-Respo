"""Beat 5 - EPISIOTOMY (rich/depictive). Episiotomy done -> cycles the follow-up
symptoms, DEPICTING each on/around the patient: bleeding at the site, a pain starburst
(patient winces), a toilet + pain bolt (dysuria), a specimen cup of bloody urine
(haematuria). ASK->RECORD template. 480x270 -> 4K, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; CROSSR=(214,70,80); ANSWC=(236,120,142)
RED=(214,60,70); RED_D=(170,36,48); BLOOD=(190,40,52); URINE=(240,214,120); PAIN=(236,120,120)
PANEL=(40,48,70)
NAMES=["BLEEDING","SITE PAIN","DYSURIA","HAEMATURIA"]
NCOL=[RED,PAIN,(126,164,232),RED]
PEARL=["BLEEDING - WATCH FOR EXCESS AT THE SITE",
       "PAIN - PERINEAL / EPISIOTOMY SITE",
       "DYSURIA - PAIN ON PASSING URINE",
       "HAEMATURIA - BLOOD IN THE URINE"]

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72))
    rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,CROSSR); rr(d,438,27,448,31,CROSSR)
    BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def starburst(d,cx,cy,r,col):
    for a in range(0,360,30):
        rr2=r if (a//30)%2==0 else int(r*0.5)
        ex,ey=cx+rr2*math.cos(math.radians(a)),cy+rr2*math.sin(math.radians(a))
        d.line([(cx,cy),(ex,ey)],fill=col,width=2)
    el(d,cx-3,cy-3,cx+3,cy+3,(255,255,255))

def toilet(d,x,y):
    rr(d,x+4,y,x+16,y+10,(214,222,230)); rr(d,x+6,y+2,x+14,y+6,(120,135,150))   # tank
    el(d,x,y+10,x+20,y+22,(224,230,238)); el(d,x+3,y+12,x+17,y+19,(150,170,195)) # bowl
    rr(d,x+4,y+22,x+16,y+26,(200,208,218))

def cup(d,x,y,fillc):
    d.polygon([(x,y),(x+16,y),(x+13,y+20),(x+3,y+20)],fill=(224,230,238))
    d.polygon([(x+2,y+8),(x+14,y+8),(x+12,y+19),(x+4,y+19)],fill=fillc)
    rr(d,x+2,y+8,x+14,y+9,(250,250,252))

def render(t):
    TLX.cmds=[]
    s=int(t//3)%4
    painful = s in (1,2)
    frame=scene_bg()
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    # patient reclined (winces for painful symptoms)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2))
    eye = 1.0 if (painful and (t*3)%1<0.8) else (1.0 if (t%3.6)>3.46 else 0.0)
    BR.mother(d,t,0.0,breath,eye,1.0 if painful else 0.0,1.0,1.0)
    BR.student(d,300,232,t=t,writing=1.0)
    # ---- depict the current symptom on/around the patient ----
    if s==0:      # BLEEDING at the site
        el(d,150,180,192,194,BLOOD); el(d,156,182,182,191,RED)
        for i in range(3):
            dy=198+int((t*22+i*7)%22)
            el(d,160+i*9,dy,164+i*9,dy+5,RED); d.polygon([(160+i*9,dy),(164+i*9,dy),(162+i*9,dy-4)],fill=RED)
        rr(d,270,198,290,214,(236,240,246)); el(d,274,202,286,210,RED)      # pad
    elif s==1:    # SITE PAIN
        starburst(d,172,180,12+int(2*math.sin(t*6)),RED)
        TLX.add(188,162,"OUCH!",PAIN,'small')
    elif s==2:    # DYSURIA
        toilet(d,168,112)
        for i in range(2):
            yy=132+int((t*30+i*6)%10); d.line([(178,yy),(178,yy+4)],fill=URINE,width=2)  # stream
        d.line([(190,116),(186,124),(192,124),(188,132)],fill=RED,width=2)  # pain bolt
    else:         # HAEMATURIA
        cup(d,170,112,RED)
        for i in range(2):
            dy=136+int((t*22+i*8)%14); el(d,176+i*6,dy,179+i*6,dy+4,RED)
    # ASK
    rf=smooth((t-1.2)/1.1)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,98,["WAS AN","EPISIOTOMY DONE?"],300)
    # header + progress pips + current symptom label
    TLX.add(40,30,"EPISIOTOMY DONE -> ASK ABOUT:",ANSWC,'tiny')
    for i in range(4):
        px=40+i*10; col=NCOL[i] if i==s else (70,80,105)
        el(d,px,44,px+5,49,col)
    TLX.add(40,54,NAMES[s],NCOL[s],'small')
    # RECORD
    fields=[("SITE","HOSPITAL"),("ROUTE","CAESAREAN"),("DIFFICULTY","DIFFICULT"),("EPISIOTOMY","YES - CHECK SITE"),("ANAESTHESIA","")]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,3,max(0.0,min(1.0,rf)),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[s],(172,180,198),'small')
    # title
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"EPISIOTOMY",(10,14,24),'body'); TLX.add(16,5,"EPISIOTOMY",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN RECORD",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN RECORD",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b5_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat05_episiotomy_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
