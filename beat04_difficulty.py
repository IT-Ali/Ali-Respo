"""Beat 4 - EASY vs DIFFICULT + DURATION. Effort gauge (easy<->difficult needle) +
a duration timer, cycling an easy/short case and a difficult/long case. ASK->RECORD
template. 480x270 -> 4K, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74)
PANEL=(40,48,70); PANEL_D=(24,30,46); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT
CROSSR=(214,70,80); GREEN=(84,196,146); AMBER=(236,172,92); RED=(230,96,96)
ANSWC=(236,120,142)

# scenarios: (effort 0..1, hours, label)
SCN=[(0.15,4,"EASY"),(0.88,14,"DIFFICULT")]
PEARL=["QUICK, UNCOMPLICATED LABOUR",
       "PROLONGED/DIFFICULT - FAILURE TO PROGRESS, MORE RISK"]

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72))
    rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    rr(d,430,22,444,36,(236,240,246)); rr(d,435,24,439,34,CROSSR); rr(d,432,27,442,31,CROSSR)
    BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def gauge(d,gx,gy,R,e):
    for s,end,col in [(180,240,GREEN),(240,300,AMBER),(300,360,RED)]:
        d.arc([gx-R,gy-R,gx+R,gy+R],s,end,fill=col,width=4)
    th=math.radians(180+e*180)
    ex,ey=gx+(R-3)*math.cos(th),gy+(R-3)*math.sin(th)
    zone = GREEN if e<0.4 else (AMBER if e<0.65 else RED)
    d.line([(gx,gy),(ex,ey)],fill=zone,width=3)
    el(d,gx-4,gy-4,gx+4,gy+4,(222,226,234)); el(d,gx-2,gy-2,gx+2,gy+2,zone)
    # tick dots
    for a in (180,270,360):
        tx,ty=gx+R*math.cos(math.radians(a)),gy+R*math.sin(math.radians(a))
        el(d,int(tx)-1,int(ty)-1,int(tx)+1,int(ty)+1,TEXTDIM)

def timer(d,x,y,w,h,hours):
    rr(d,x,y,x+w,y+h,PANEL); d.rectangle([x,y,x+w,y+h],outline=(70,84,120))
    # little clock icon
    cx,cy=x+13,y+h//2+2
    el(d,cx-7,cy-7,cx+7,cy+7,(222,226,234)); el(d,cx-5,cy-5,cx+5,cy+5,(30,40,60))
    d.line([(cx,cy),(cx+3,cy-3)],fill=ACCENT); d.line([(cx,cy),(cx,cy+4)],fill=TEXT)

def render(t):
    TLX.cmds=[]
    cur=int(t//6)%2; lt=t-(t//6)*6.0
    e0,h0,_=SCN[cur]; ep,_,_=SCN[1-cur]
    k=smooth(min(1.0,lt/0.9)); e=ep+(e0-ep)*k
    hours=int(round(h0*smooth(min(1.0,(lt-0.9)/1.0)))) if lt>0.9 else 0
    frame=scene_bg()
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,1.0,1.0)
    BR.student(d,300,232,t=t,writing=1.0)
    # effort gauge + duration timer (the diagram = the answer)
    gx,gy,R=104,96,40
    gauge(d,gx,gy,R,e)
    timer(d,150,58,84,46,hours)
    # ASK (student)
    ask_on=lt>0.1; ans_on=lt>0.9; rf=smooth((lt-1.4)/1.3)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,210,98,["EASY OR DIFFICULT?","AND HOW LONG?"],300)
    # gauge/timer text labels (4K)
    TLX.add(gx-R-2,gy+5,"EASY",GREEN,'tiny'); TLX.add(gx+R-TLX.w("HARD",'tiny'),gy+5,"HARD",RED,'tiny')
    TLX.add(150,46,"DURATION",TEXTDIM,'tiny')
    TLX.add(178,66,(f"{hours} HRS" if ans_on else "-- HRS"),TEXT,'body')
    if ans_on:
        TLX.add(gx-TLX.w("ANSWER",'tiny')/2, gy-R-16, "ANSWER", ANSWC,'tiny')
        dw=SCN[cur][2]; dc=GREEN if cur==0 else RED           # big difficulty word by the gauge
        TLX.add(gx-TLX.w(dw,'small')/2, gy+14, dw, dc,'small')
    # RECORD
    diffval = (f"EASY  {h0}H" if cur==0 else f"DIFFICULT  {h0}H")
    fields=[("SITE","HOSPITAL"),("ROUTE","CAESAREAN"),("DIFFICULTY",diffval),("EPISIOTOMY",""),("ANAESTHESIA","")]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,2,max(0.0,min(1.0,rf)),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[cur],(172,180,198),'small')
    # title
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"EFFORT & DURATION",(10,14,24),'body'); TLX.add(16,5,"EFFORT & DURATION",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN RECORD",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN RECORD",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b4_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat04_difficulty_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
