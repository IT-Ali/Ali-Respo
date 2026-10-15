"""Beat 8 - CAESAREAN INTRA-OP. Modest theatre scene (draped patient, surgical lights,
surgeon's hands) + cycles the intra-op points: time/duration, smooth vs difficult, and
complications to ask about (excessive bleeding, transfusion, organ injury). 4K, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(22,28,44); WALL2=(28,36,54); FLOOR=(28,38,56); FLOORH=(38,50,70)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; CROSSR=(214,70,80); ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
DRAPE=(46,150,120); DRAPE_D=(32,120,96); SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; SCARF=BR.SCARF
GLOVE=(96,170,200); STEEL=(200,210,224); RED=(214,60,70); BLOODC=(190,40,52); AMBER=(236,172,92); GREEN=(84,196,146)
LIGHT=(250,246,214)
ITEMS=["TIME & DURATION","SMOOTH vs DIFFICULT","EXCESSIVE BLEEDING?","TRANSFUSION?","ORGAN INJURY?"]
PEARL=["DATE / TIME & HOW LONG THE OP TOOK",
       "WAS THE OPERATION SMOOTH OR DIFFICULT",
       "ASK ABOUT EXCESSIVE BLOOD LOSS",
       "DID SHE NEED A BLOOD TRANSFUSION",
       "BLADDER / BOWEL / ORGAN INJURY"]

def surg_light(d,x,y):
    el(d,x-16,y-8,x+16,y+8,(70,84,110)); el(d,x-13,y-6,x+13,y+6,LIGHT); el(d,x-8,y-3,x+8,y+3,(255,255,240))
    d.line([(x,y+8),(x,y-20)],fill=(80,92,116))
    for dx in (-10,0,10):
        d.line([(x+dx,y+7),(x+dx//2,y+40)],fill=(255,250,220,))

def or_scene(d,t):
    # table
    rr(d,66,210,72,230,(70,80,100)); rr(d,250,210,256,230,(70,80,100))
    rr(d,60,196,262,212,(96,108,130)); rr(d,62,186,260,196,(214,220,230))
    # pillow + asleep head (left)
    rr(d,66,172,104,188,(206,222,236))
    hx,hy=86,170
    el(d,hx-10,hy-2,hx+10,hy+15,SCARF); el(d,hx-6,hy+2,hx+6,hy+13,SKIN); rr(d,hx-7,hy,hx+7,hy+2,SCARF)
    d.line([(hx-4,hy+7),(hx-1,hy+7)],fill=SKIN_D); d.line([(hx+1,hy+7),(hx+4,hy+7)],fill=SKIN_D)   # asleep
    # green surgical drape over the body + fold lines
    rr(d,108,176,258,196,DRAPE); rr(d,108,176,258,178,(70,185,150)); rr(d,108,193,258,196,DRAPE_D)
    for fx in range(126,254,22): rr(d,fx,180,fx,192,DRAPE_D)
    # drape screen (separates head from field)
    rr(d,112,150,118,180,DRAPE); rr(d,110,150,120,153,(70,185,150))
    # surgeon gloved hands + instrument over the field (modest)
    el(d,168,168,182,180,GLOVE); el(d,186,170,200,182,GLOVE)
    d.line([(190,172),(206,160)],fill=STEEL,width=2); el(d,204,157,210,163,STEEL)   # instrument

def small_gauge(d,gx,gy,R,e):
    for s,end,col in [(180,240,GREEN),(240,300,AMBER),(300,360,RED)]:
        d.arc([gx-R,gy-R,gx+R,gy+R],s,end,fill=col,width=3)
    th=math.radians(180+e*180); ex,ey=gx+(R-2)*math.cos(th),gy+(R-2)*math.sin(th)
    d.line([(gx,gy),(ex,ey)],fill=(222,226,234),width=2); el(d,gx-3,gy-3,gx+3,gy+3,(222,226,234))

def depict(d,s,t):
    if s==0:      # clock + duration
        cx,cy=70,108; el(d,cx-14,cy-14,cx+14,cy+14,(222,226,234)); el(d,cx-11,cy-11,cx+11,cy+11,(30,40,60))
        a=t*1.2; d.line([(cx,cy),(cx+6*math.sin(a),cy-6*math.cos(a))],fill=TEXT); d.line([(cx,cy),(cx+9*math.sin(a*8),cy-9*math.cos(a*8))],fill=ACCENT)
        TLX.add(96,100,"45 MIN",TEXT,'small')
    elif s==1:    # smooth/difficult gauge
        small_gauge(d,90,116,24,0.75)
        TLX.add(70,124,"DIFFICULT",RED,'tiny')
    elif s==2:    # excessive bleeding - jug filling + pool
        rr(d,54,96,78,126,(50,60,86)); rr(d,56,106,76,124,BLOODC)      # jug w/ blood
        for i in range(3):
            yy=190+int((t*22+i*7)%16); el(d,150+i*14,yy,156+i*14,yy+5,BLOODC)  # drips at field
        TLX.add(86,104,"! BLOOD LOSS",RED,'tiny')
    elif s==3:    # transfusion bag -> arm
        rr(d,50,92,66,116,BLOODC); rr(d,50,92,66,96,(150,30,42)); d.line([(58,116),(80,150),(110,176)],fill=BLOODC)
        TLX.add(70,100,"O+",(255,235,235),'tiny')
    else:         # organ injury warning
        d.polygon([(70,96),(92,96),(81,78)],fill=AMBER); TLX.add(79,86,"!",(40,30,10),'tiny')
        TLX.add(98,96,"BLADDER / BOWEL?",AMBER,'tiny')

def checklist(d,x,y,w,h,cur):
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"INTRA-OP NOTES",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(ITEMS):
        done=i<cur; now=i==cur
        if now: rr(d,x+3,ry-2,x+w-3,ry+15,(252,240,176))
        rr(d,x+7,ry+2,x+15,ry+10,(250,250,250)); d.rectangle([x+7,ry+2,x+15,ry+10],outline=INKDIM)
        if done or now:
            d.line([(x+8,ry+6),(x+10,ry+9)],fill=TICK); d.line([(x+10,ry+9),(x+15,ry+1)],fill=TICK)
        TLX.add(x+20,ry+1,it, INK if (done or now) else INKDIM,'small')
        ry+=19

def render(t):
    TLX.cmds=[]
    s=int(t//2.4)%5
    frame=np.array(Image.new('RGB',(GW,GH),WALL),np.uint8).astype(np.float32)
    im=Image.fromarray(frame.astype(np.uint8)); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    surg_light(d,150,30); surg_light(d,210,30)
    or_scene(d,t)
    depict(d,s,t)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,98,["HOW DID THE","OPERATION GO?"],300)
    TLX.add(40,30,"DURING THE OPERATION",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    checklist(d,340,26,134,118,s)
    TLX.add(392,17,"NOTES",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[s],(172,180,198),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"C-SECTION INTRA-OP",(10,14,24),'body'); TLX.add(16,5,"C-SECTION INTRA-OP",TEXT,'body')
    TLX.add(16.4,21.3,"WHAT HAPPENED IN THE OPERATION",(10,14,24),'small'); TLX.add(16,21,"WHAT HAPPENED IN THE OPERATION",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b8_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat08_intraop_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
