"""Section TITLE CARD (~3.5s) shown before the Pre-op section onward. Big section title +
part label + subtitle, on a soft glow. 480x270 -> 4K. Usage: title_card.py <code> [--still t]"""
import numpy as np, math, sys, subprocess, os
from PIL import Image, ImageDraw
import birth_recovery as BR, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=3.5
TLX=uitext.TL()
ACCENT=BR.ACCENT
WALL=(20,26,42)
CARDS={
 '07':("PART B  -  IF CAESAREAN","C-SECTION PRE-OP","BEFORE THE OPERATION"),
 '08':("PART B  -  IF CAESAREAN","C-SECTION INTRA-OP","DURING THE OPERATION"),
 '09':("PART B  -  IF CAESAREAN","WHY THE CAESAREAN","THE INDICATION"),
 '10':("PART C  -  THE RECOVERY","POST-OP RECOVERY","SYSTEMS COMING BACK"),
 '11':("PART C  -  THE RECOVERY","POST-PARTUM BLEEDING","BLEEDING AFTER DELIVERY"),
 '12':("PART C  -  THE RECOVERY","THE C-SECTION WOUND","CHECKING THE SCAR"),
 '13':("PART C  -  THE RECOVERY","CLOTS & MOVING (VTE)","CLOT RISK & MOBILISING"),
 'apb':("A PRESENTING COMPLAINT","VAGINAL BLEEDING","CHARACTERISE THE BLEED"),
 'rom':("A PRESENTING COMPLAINT","WATERY DISCHARGE (ROM)","CONFIRM & CHARACTERISE"),
 'outcome':("CLOSING THE DELIVERY STORY","OUTCOME OF DELIVERY","HOW THE BABY DID"),
}

def render(code,t):
    TLX.cmds=[]
    part,title,sub=CARDS[code]; cx,cy=240,124
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    gr=int(132+8*(0.5+0.5*math.sin(2*math.pi*t/3.5)))
    d.ellipse([cx-gr,cy-int(gr*0.72),cx+gr,cy+int(gr*0.74)],fill=lerp(WALL,(40,52,78),0.4))
    d.ellipse([cx-int(gr*0.62),cy-int(gr*0.46),cx+int(gr*0.62),cy+int(gr*0.5)],fill=lerp(WALL,(50,64,92),0.45))
    pa=smooth((t-0.15)/0.5); pl=part
    TLX.add(cx-TLX.w(pl,'small')/2, cy-50, pl, lerp(WALL,ACCENT,pa),'small')
    ta=smooth(t/0.7); oy=int(12*(1-ta)); tw=TLX.w(title,'title')
    TLX.add(cx-tw/2+0.5, cy-24+oy+0.5, title,(8,12,22),'title')
    TLX.add(cx-tw/2, cy-24+oy, title, lerp(WALL,(236,240,248),ta),'title')
    la=smooth((t-0.5)/0.6); lw=int(72*la); rr(d,cx-lw,cy+18,cx+lw,cy+19,ACCENT)
    sa=smooth((t-0.75)/0.5)
    TLX.add(cx-TLX.w(sub,'small')/2, cy+26, sub, lerp(WALL,(150,160,182),sa),'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    code=[a for a in sys.argv[1:] if a in CARDS][0]
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(code,tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/btitle_{code}.png'); print("ok",code)
    else:
        OUT=f'D:/Ue/UE_5.8/obgyn_explainer/title_{code}_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(code,i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
