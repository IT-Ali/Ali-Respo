"""Per-topic beats in that topic's own environment, in a given MODE:
  ask  = the doctor asks the question (nothing recorded yet)
  next = the answer is recorded (ticked) and the next question is cued  (= answer + bridge)
Renders at 4K. Usage: nextq.py <code> [--mode ask|next] [--still t]"""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
import beat07_preop as b7, beat08_intraop as b8, beat09_indications as b9
import beat10_recovery as b10, beat11_pph as b11, beat12_wound as b12, beat13_vte as b13
from birth_recovery import rr, el, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=4.0
TLX=uitext.TL()
ACCENT=BR.ACCENT; TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112); GREEN=(84,196,146)
AF=[("SITE","HOSPITAL"),("ROUTE","CAESAREAN"),("DIFFICULTY","DIFFICULT"),("ANAESTHESIA","SPINAL"),("EPISIOTOMY","YES")]

CFG={
 '02':dict(kind='sheet',bg='hosp',title=("SITE OF DELIVERY","ASK, THEN RECORD"),active=1,nxt="ROUTE",hold=1.0,ask=["WHERE DID YOU","DELIVER?"]),
 '03':dict(kind='sheet',bg='ward',title=("ROUTE OF DELIVERY","ASK, THEN RECORD"),active=2,nxt="DIFFICULTY",hold=1.0,ask=["NORMAL BIRTH OR","CAESAREAN?"]),
 '04':dict(kind='sheet',bg='ward',title=("EFFORT & DURATION","ASK, THEN RECORD"),active=3,nxt="ANAESTHESIA",hold=1.0,ask=["EASY OR DIFFICULT?","AND HOW LONG?"]),
 '06':dict(kind='sheet',bg='ward',title=("ANAESTHESIA","ASK, THEN RECORD"),active=4,nxt="EPISIOTOMY",hold=1.0,ask=["WHAT ANAESTHESIA","WAS USED?"]),
 '05':dict(kind='sheet',bg='ward',title=("EPISIOTOMY","ASK, THEN RECORD"),active=5,nxt="PRE-OP",hold=1.0,ask=["WAS AN","EPISIOTOMY DONE?"]),
 '07':dict(kind='check',bg='ward',title=("C-SECTION PRE-OP","PREP, THEN CHECK"),items=b7.ITEMS,ptitle="PRE-OP CHECKLIST",nxt="INTRA-OP",hold=0.0,ask=["WHAT WAS DONE","BEFORE THEATRE?"]),
 '10':dict(kind='check',bg='recov',title=("POST-OP RECOVERY","SYSTEMS COMING BACK"),items=b10.ITEMS,ptitle="RECOVERY CHECK",nxt="PPH",hold=1.0,ask=["HOW IS HER","RECOVERY GOING?"]),
 '08':dict(kind='check',bg=(22,28,44),title=("C-SECTION INTRA-OP","WHAT HAPPENED IN THEATRE"),items=b8.ITEMS,ptitle="INTRA-OP NOTES",nxt="INDICATIONS",ask=["HOW DID THE","OPERATION GO?"]),
 '09':dict(kind='check',bg=(24,30,48),title=("WHY THE CAESAREAN","THE INDICATION MATTERS"),items=b9.ITEMS,ptitle="INDICATIONS",nxt="RECOVERY",ask=["WHY DID YOU NEED","A CAESAREAN?"]),
 '11':dict(kind='check',bg=(28,22,34),title=("POST-PARTUM BLEEDING","ASK HOW MUCH, HOW FAST"),items=b11.ITEMS,ptitle="BLEEDING Hx",nxt="WOUND",ask=["DID YOU BLEED","HEAVILY AFTER?"]),
 '12':dict(kind='check',bg=(22,28,42),title=("C-SECTION WOUND","LOOK AT THE SCAR"),items=b12.ITEMS,ptitle="WOUND CHECK",nxt="VTE",ask=["HOW IS THE","WOUND HEALING?"]),
 '13':dict(kind='check',bg=(20,26,42),title=("CLOTS & MOVING","ASK, THEN GET MOVING"),items=b13.ITEMS,ptitle="VTE: ASK + MOVE",nxt="COMPLETE",ask=["ANY LEG OR","CHEST SYMPTOMS?"]),
}

def ward_bg(d):
    rr(d,0,0,GW-1,72,(32,40,60)); rr(d,0,150,GW-1,151,(40,50,72)); rr(d,0,181,GW-1,GH-1,(30,40,60)); rr(d,0,181,GW-1,183,(40,52,74))
    rr(d,436,22,450,36,(236,240,246)); rr(d,441,24,445,34,(214,70,80)); rr(d,438,27,448,31,(214,70,80))
    ccx,ccy=250,46; el(d,ccx-12,ccy-12,ccx+12,ccy+12,(222,226,234)); el(d,ccx-10,ccy-10,ccx+10,ccy+10,(30,40,60))
    d.line([(ccx,ccy),(ccx-5,ccy-4)],fill=(236,240,246)); d.line([(ccx,ccy),(ccx+5,ccy-4)],fill=ACCENT); el(d,ccx-1,ccy-1,ccx+1,ccy+1,(236,240,246))

def dark_bg(d,wall):
    rr(d,0,0,GW-1,70,lerp(wall,(255,255,255),0.03)); rr(d,0,183,GW-1,GH-1,lerp(wall,(0,0,0),0.1))

def check_panel(d,tl,x,y,w,title,items,ndone):
    h=23+len(items)*19+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D); rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    tl.add(x+6,y+3,title,INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,it in enumerate(items):
        rr(d,x+7,ry+2,x+15,ry+10,(250,250,250)); d.rectangle([x+7,ry+2,x+15,ry+10],outline=INKDIM)
        if i<ndone:
            d.line([(x+8,ry+6),(x+10,ry+9)],fill=TICK); d.line([(x+10,ry+9),(x+15,ry+1)],fill=TICK)
        tl.add(x+20,ry+1,it,INK if i<ndone else INKDIM,'small'); ry+=19

def render(code,t,mode='next'):
    TLX.cmds=[]
    cfg=CFG[code]; wall=cfg['bg'] if isinstance(cfg['bg'],tuple) else BR.WALL_C
    im=Image.new('RGB',(GW,GH),wall); d=ImageDraw.Draw(im)
    breath=1.1*(0.5+0.5*math.sin(2*math.pi*t/4.2)); blink=1.0 if (t%3.6)>3.46 else 0.0
    bedside = cfg['bg'] in ('hosp','ward','recov')
    if cfg['bg']=='hosp': BR.background(d,t,0.0); BR.iv_pole(d,44,t); BR.bed(d)
    elif cfg['bg']=='ward': ward_bg(d); BR.iv_pole(d,44,t); BR.bed(d)
    elif cfg['bg']=='recov': b10.recovery_bg(d); BR.iv_pole(d,44,t); BR.bed(d); BR.nightstand(d,266,188,1.0)
    else: dark_bg(d,wall)
    if bedside: BR.mother(d,t,0.0,breath,blink,0.0,1.0,cfg['hold'])
    BR.student(d,300,232,t=t,writing=0.0)
    if cfg['kind']=='sheet':
        act = (cfg['active']-1) if mode=='ask' else cfg['active']
        hud.history_sheet(d,TLX,340,26,134,130,"LABOUR & DELIVERY",AF,act,0.0,t)
        TLX.add(392,17,"RECORD IT" if mode=='next' else "ASK IT",(150,150,162),'small')
    else:
        check_panel(d,TLX,340,24,136,cfg['ptitle'],cfg['items'],0 if mode=='ask' else len(cfg['items']))
        TLX.add(392,15,"ASK" if mode=='ask' else "NOTED",(150,150,162),'small')
        if mode=='next' and not bedside:
            tw=TLX.w("RECORDED",'title'); TLX.add(150-tw/2+0.5,118.5,"RECORDED",(8,12,22),'title'); TLX.add(150-tw/2,118,"RECORDED",TEXTDIM,'title')
            d.line([(150-tw/2-26,128),(150-tw/2-18,138)],fill=GREEN,width=4); d.line([(150-tw/2-18,138),(150-tw/2-2,112)],fill=GREEN,width=4)
    if mode=='ask':
        TLX.add(214,92,"ASK",(0,180,196),'small'); hud.speech_bubble(d,TLX,208,100,cfg['ask'],300)
    else:
        TLX.add(214,92,"NEXT",(0,180,196),'small')
        hud.speech_bubble(d,TLX,208,100,["NOW ASK:",cfg['nxt']] if cfg['nxt']!="COMPLETE" else ["HISTORY","COMPLETE"],300)
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,cfg['title'][0],(10,14,24),'body'); TLX.add(16,5,cfg['title'][0],TEXT,'body')
    TLX.add(16.4,21.3,cfg['title'][1],(10,14,24),'small'); TLX.add(16,21,cfg['title'][1],TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    code=[a for a in sys.argv[1:] if a in CFG][0]
    mode='ask' if ('--mode' in sys.argv and sys.argv[sys.argv.index('--mode')+1]=='ask') else 'next'
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(code,tv,mode)).save(f'D:/Ue/UE_5.8/obgyn_explainer/bnq_{code}_{mode}.png'); print("ok",code,mode)
    else:
        tag='ask' if mode=='ask' else 'nextq'
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/{tag}_{code}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(code,i/FPS,mode).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
