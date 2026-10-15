"""Beat 3 - ROUTE of delivery: vaginal -> assisted (forceps/vacuum) -> caesarean.
Diagram register: 3 route cards, cycles through each (teaches all 3), with the
ASK -> ANSWER -> RECORD template + clinical pearl. 480x270 -> 4K, 24fps, 12s loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(26,32,50); WALL2=(32,40,60); FLOOR=(30,40,60); FLOORH=(40,52,74)
PANEL=(40,48,70); PANEL_D=(28,34,52); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT
CROSSR=(214,70,80); SKIN=BR.SKIN; DARK=BR.DARK

ROUTES=["VAGINAL","ASSISTED","CAESAREAN"]
RCOL=[(84,196,146),(236,172,92),(126,164,232)]          # green / amber / blue
ANSW=[["NORMAL BIRTH"],["ASSISTED -","FORCEPS/VACUUM"],["CAESAREAN"]]
PEARL=["VAGINAL - SPONTANEOUS, NO INSTRUMENTS",
       "ASSISTED - FORCEPS OR VACUUM USED",
       "CAESAREAN - SURGICAL BIRTH"]
CARDX=[122,196,270]; CW=64; CTOP=30; CH=58

def scene_bg():
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,150,GW-1,151,(40,50,72))
    rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    # wall clock + medical cross (context, kept clear of the cards)
    ccx,ccy=44,40
    el(d,ccx-11,ccy-11,ccx+11,ccy+11,(222,226,234)); el(d,ccx-9,ccy-9,ccx+9,ccy+9,(30,40,60))
    d.line([(ccx,ccy),(ccx+5,ccy-5)],fill=TEXT); d.line([(ccx,ccy),(ccx+7,ccy+2)],fill=ACCENT)
    rr(d,420,24,434,38,(236,240,246)); rr(d,425,26,429,36,CROSSR); rr(d,422,29,432,33,CROSSR)
    BR.bed(d)
    return np.array(im,np.uint8).astype(np.float32)

def icon(d,i,cx,cy,col):
    if i==0:   # vaginal: baby head descending through the canal + down arrow
        d.arc([cx-9,cy-10,cx+9,cy+8],200,340,fill=col); d.arc([cx-9,cy-9,cx+9,cy+9],200,340,fill=col)
        el(d,cx-4,cy-5,cx+4,cy+3,SKIN)                       # baby head
        d.line([(cx,cy+4),(cx,cy+11)],fill=col); d.line([(cx-3,cy+8),(cx,cy+11)],fill=col); d.line([(cx+3,cy+8),(cx,cy+11)],fill=col)
    elif i==1: # assisted: baby head + vacuum cup + handle
        el(d,cx-4,cy-2,cx+4,cy+6,SKIN)                       # head
        d.polygon([(cx-5,cy-2),(cx+5,cy-2),(cx+3,cy-6),(cx-3,cy-6)],fill=col)  # cup
        d.line([(cx,cy-6),(cx,cy-11)],fill=col); el(d,cx-2,cy-13,cx+2,cy-10,col)  # handle+knob
    else:      # caesarean: belly + horizontal incision + baby lifted above
        el(d,cx-9,cy+1,cx+9,cy+12,(230,196,176))             # belly
        for dx in range(-7,8,3): rr(d,cx+dx,cy+4,cx+dx+1,cy+5,CROSSR)  # dashed incision
        el(d,cx-3,cy-9,cx+3,cy-3,SKIN); d.line([(cx,cy-3),(cx,cy+1)],fill=col)  # baby lifted
        d.line([(cx-6,cy-6),(cx+6,cy-6)],fill=col)           # hands/lift bar

def route_cards(d,cur,glow):
    for i,cx0 in enumerate(CARDX):
        act = (i==cur)
        col=RCOL[i]
        fill = PANEL if not act else tuple(min(255,int(c*0.22+PANEL[j]*0.8)) for j,c in enumerate(col))
        rr(d,cx0,CTOP,cx0+CW,CTOP+CH,fill)
        bc = col if act else tuple(int(c*0.5) for c in col)
        d.rectangle([cx0,CTOP,cx0+CW,CTOP+CH],outline=bc)
        if act:   # glow border
            d.rectangle([cx0-1,CTOP-1,cx0+CW+1,CTOP+CH+1],outline=col)
            d.rectangle([cx0-2,CTOP-2,cx0+CW+2,CTOP+CH+2],outline=tuple(int(c*0.4+PANEL[j]*0.6) for j,c in enumerate(col)))
        icon(d,i,cx0+CW//2,CTOP+22,col if act else tuple(int(c*0.55) for c in col))
        if i<2:   # arrow to next
            ax=cx0+CW+1; ay=CTOP+CH//2
            d.line([(ax,ay),(ax+5,ay)],fill=TEXTDIM); d.line([(ax+3,ay-2),(ax+5,ay)],fill=TEXTDIM); d.line([(ax+3,ay+2),(ax+5,ay)],fill=TEXTDIM)

def render(t):
    TLX.cmds=[]
    cur=int(t//4)%3
    lt=t-(t//4)*4.0
    glow=0.5+0.5*math.sin(2*math.pi*t*0.8)
    frame=scene_bg()
    im=Image.fromarray(np.clip(frame,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    BR.mother(d,t,0.0,breath,blink,0.0,1.0,1.0)
    BR.student(d,300,232,t=t,writing=1.0)
    route_cards(d,cur,glow)
    # card labels (4K text, centered)
    for i,cx0 in enumerate(CARDX):
        lab=ROUTES[i]; col = RCOL[i] if i==cur else TEXTDIM
        TLX.add(cx0+(CW-TLX.w(lab,'tiny'))/2, CTOP+CH-12, lab, col, 'tiny')
    # ASK (student) / ANSWER marked on the chosen card / RECORD on sheet
    ask_on = lt>0.1; ans_on = lt>0.9; rf=smooth((lt-1.3)/1.3)
    if t>=2.5:
        TLX.add(214,90,"ASK",(0,180,196),'small')
        hud.speech_bubble(d,TLX,210,98,["NORMAL BIRTH OR","CAESAREAN?"],300)
    if ans_on:
        # "ANSWER" tag + check badge on the chosen route card
        cx0=CARDX[cur]
        TLX.add(cx0+(CW-TLX.w("ANSWER",'tiny'))/2, CTOP-13, "ANSWER", (236,120,142),'tiny')
        bx,by=cx0+CW-5,CTOP-5
        el(d,bx-5,by-5,bx+5,by+5,(40,172,112))
        d.line([(bx-3,by),(bx-1,by+2)],fill=(240,245,248)); d.line([(bx-1,by+2),(bx+3,by-3)],fill=(240,245,248))
    fields=[("SITE","HOSPITAL"),("ROUTE",ROUTES[cur]),("DIFFICULTY",""),("EPISIOTOMY",""),("ANAESTHESIA","")]
    hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",fields,1,max(0.0,min(1.0,rf)),t)
    TLX.add(392,17,"RECORD IT",(150,150,162),'small')
    TLX.add(140,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(140,254,PEARL[cur],(172,180,198),'small')
    # title
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"ROUTE OF DELIVERY",(10,14,24),'body'); TLX.add(16,5,"ROUTE OF DELIVERY",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN RECORD",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN RECORD",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b3_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat03_route_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
