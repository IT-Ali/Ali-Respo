"""HISTORY SKELETON BUILDER - teaches how to organise the obstetric history sheet.
The backbone headings build top-to-bottom (gold = CORE, always), the pigeon doctor asks
the question that writes each line, and when HISTORY OF PRESENT ILLNESS appears a cyan
branch of HOPI ADD-ONS (per case) opens off it. Build (~12s) then hold. 480x270 -> 4K."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=17.0
TLX=uitext.TL()

WALL=(18,22,32); WALL2=(26,32,46)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(44,48,62); INKDIM=(120,126,142)
GOLD=(230,186,96); GOLDB=(236,204,140); GOLD_HI=(250,240,200)
CYAN=(0,188,204); CYAN_D=(10,96,108); ADDBG=(20,40,46); CHIP=(28,54,60)
TICK=(40,172,112); TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM

SX0,SX1,SY,PITCH=148,356,58,18
ROWS=[("DEMOGRAPHIC","name - age - job - blood group",False),
      ("GRAVIDA / PARA / ABORTION","G _   P _   A _",False),
      ("LMP  >  EDD  >  GA","the dates + gestational age",True),
      ("CHIEF COMPLAINT","the complaint + its duration",False),
      ("HISTORY OF PRESENT ILLNESS","the presenting story",False),
      ("REVIEW OF SYSTEMS","CVS Resp GI GU MSK Neuro",False),
      ("CURRENT PREGNANCY","1st - 2nd - 3rd trimester",False),
      ("PAST OBSTETRIC Hx","each pregnancy + outcome",False),
      ("PAST GYNAECOLOGICAL","menarche - cycle - contraception",False),
      ("THE CLOSERS","medical-family-surgical-drug-social",False)]
ADDONS=["PAIN  >  SOCRATES","BLEEDING  >  amount & clots","PREVIOUS CS  >  scars & why",
        "POST-OP  >  recovery + outcome","POST-DATE  >  dates & movements"]
QS=[["WHO IS","SHE?"],["HOW MANY","PREGNANCIES?"],["WHEN WAS HER","LAST PERIOD?"],
    ["WHAT BROUGHT","HER IN?"],["TELL ME THE","STORY..."],["ANY OTHER","SYSTEMS?"],
    ["HOW WAS THIS","PREGNANCY?"],["HER PAST","PREGNANCIES?"],["PERIODS &","CONTRACEPTION?"],
    ["MEDICAL,","FAMILY, DRUGS?"]]

def ap(i,t): return smooth((t-(0.7+i*1.25))/0.35)      # row appear progress 0..1
def apc(j,t): return smooth((t-(6.0+j*0.7))/0.35)      # add-on chip progress

def render(t):
    TLX.cmds=[]
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,34,WALL2)
    TLX.add(16,5,"ORGANISING THE HISTORY",(10,14,24),'body'); TLX.add(15.6,4.6,"ORGANISING THE HISTORY",TEXT,'body')
    TLX.add(16,23,"the order that scores  -  gold backbone + HOPI add-ons",TEXTDIM,'small')
    # legend
    rr(d,316,6,326,14,GOLD); TLX.add(330,6,"CORE",GOLDB,'tiny')
    rr(d,316,18,326,26,CYAN); TLX.add(330,18,"ADD-ON",CYAN,'tiny')

    # ----- backbone sheet -----
    nrow=len(ROWS); h=SY-44+nrow*PITCH+6
    d.rectangle([SX0-6,44,SX1+6,44+h],fill=CREAM,outline=CREAM_D)
    rr(d,(SX0+SX1)//2-8,41,(SX0+SX1)//2+8,45,(150,160,172))
    TLX.add(SX0-2,47,"THE HISTORY SHEET",INK,'small')
    rr(d,SX0-2,56,SX1+2,56,GOLD)
    cur=-1
    for i,(lab,val,star) in enumerate(ROWS):
        p=ap(i,t)
        if p<=0: continue
        cur=i; ry=SY+i*PITCH; ox=int(-7*(1-p))
        rowc=lerp(CREAM,INK,p); valc=lerp(CREAM,INKDIM,p); barc=lerp(CREAM,GOLD,p)
        if star: rr(d,SX0-5,ry-2,SX1+5,ry+PITCH-3,lerp(CREAM,GOLD_HI,p))   # LMP row highlight
        rr(d,SX0-5,ry-2,SX0-3,ry+PITCH-3,barc)                            # gold core bar
        bx=SX0+2+ox
        rr(d,bx,ry,bx+7,ry+7,(252,252,250)); d.rectangle([bx,ry,bx+7,ry+7],outline=lerp(CREAM,INKDIM,p))
        if p>0.6:
            d.line([(bx+1,ry+4),(bx+3,ry+6)],fill=TICK); d.line([(bx+3,ry+6),(bx+8,ry-1)],fill=TICK)
        TLX.add(bx+12,ry-1,lab,rowc,'small')
        if star: TLX.add(bx+12+TLX.w(lab,'small')+3,ry-1,"*",lerp(CREAM,GOLD,p),'small')
        TLX.add(bx+12,ry+8,val,valc,'tiny')
        rr(d,SX0+2,ry+PITCH-4,SX1-2,ry+PITCH-4,lerp(CREAM,CREAM_D,p))

    # ----- HOPI add-on branch (opens off row 4) -----
    pb=ap(4,t)
    if pb>0.4:
        hy=SY+4*PITCH+3
        ax0,ay0,ax1,ay1=361,96,477,208
        # connector elbow HOPI -> panel
        d.line([(SX1+5,hy),(359,hy)],fill=CYAN); d.line([(359,hy),(359,ay0+6)],fill=CYAN)
        d.line([(359,ay0+6),(ax0,ay0+6)],fill=CYAN)
        d.rectangle([ax0,ay0,ax1,ay1],fill=ADDBG,outline=CYAN_D)
        rr(d,ax0,ay0,ax1,ay0+12,CYAN_D)
        TLX.add(ax0+4,ay0+2,"HOPI ADD-ONS",(224,244,246),'tiny')
        TLX.add(ax0+4,ay0+13,"pick per case",CYAN,'tiny')
        for j,chip in enumerate(ADDONS):
            pc=apc(j,t)
            if pc<=0: continue
            cy=ay0+26+j*19; ox=int(-6*(1-pc))
            rr(d,ax0+4,cy,ax1-4,cy+16,lerp(ADDBG,CHIP,pc))
            rr(d,ax0+4,cy,ax0+6,cy+16,lerp(ADDBG,CYAN,pc))
            TLX.add(ax0+10+ox,cy+4,chip,lerp(ADDBG,(214,236,238),pc),'tiny')

    # ----- pigeon doctor + question bubble (left column) -----
    BR.student(d,74,252,t=t,writing=1.0)
    if t<12.2:
        q=QS[max(0,cur)]
    else:
        q=["ORGANISED =","FEWER Qs"]
    hud.speech_bubble(d,TLX,12,150,q,70,size='small')

    # ----- footer rule -----
    pf=smooth((t-12.5)/0.6)
    if pf>0:
        rr(d,8,250,472,268,lerp(WALL,(28,24,34),pf))
        r="Organised headings = fewer questions   *   never skip LMP / EDD / GA"
        rw=TLX.w(r,'small'); TLX.add(240-rw/2,254,r,lerp(WALL,(210,200,180),pf),'small')

    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/hs_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/history_skeleton_1080p.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','scale=1920:1080:flags=bicubic,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','18','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
