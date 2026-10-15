"""Beat 13 - VTE WARNING + MOBILISATION (FINAL beat). First the clot warning signs to
ASK about - one-sided leg pain/swelling (DVT) and breathless/chest pain (PE) - then the
payoff: the patient gets up and walks while the CLOT-RISK meter drops into the green.
480x270 -> 4K, 24fps, 12s seamless loop."""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
import birth_recovery as BR
import hud, uitext
from birth_recovery import rr, el, smooth, lerp, GW, GH, SCALE
FFMPEG=BR.FFMPEG; FPS=24; DUR=12.0
TLX=uitext.TL()

WALL=(20,26,42); WALL2=(28,36,54); FLOOR=(26,36,54); FLOORH=(38,50,70)
TEXT=BR.TEXT; TEXTDIM=BR.TEXTDIM; ACCENT=BR.ACCENT; ANSWC=(236,120,142)
CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162); TICK=(40,172,112)
SKIN=BR.SKIN; SKIN_D=BR.SKIN_D; SCARF=BR.SCARF; GOWN=BR.GOWN; GOWN_H=BR.GOWN_H; GOWN_D=BR.GOWN_D
REDSKIN=(220,118,114); RED=(214,60,70); AMBER=(236,172,92); GREEN=(84,196,146); LUNG=(230,150,160); LUNG_D=(196,110,124)
ITEMS=["LEG PAIN / SWELLING","BREATHLESS / CHEST PAIN","GET UP & WALK EARLY","CLOT RISK FALLS"]
PEARL=["ONE-SIDED LEG PAIN / SWELLING = DVT",
       "BREATHLESS / CHEST PAIN = CLOT ON LUNG (PE)",
       "GET HER UP & WALKING EARLY",
       "EARLY WALKING LOWERS THE CLOT RISK"]

def dvt(d,t):
    rr(d,98,94,184,110,GOWN); rr(d,98,94,184,97,GOWN_H); rr(d,98,107,184,110,GOWN_D)   # gown hem
    # left leg - normal
    rr(d,118,110,128,166,SKIN); el(d,114,162,132,172,SKIN); rr(d,114,170,132,173,SKIN_D)
    TLX.add(102,176,"NORMAL",(170,180,196),'tiny')
    # right leg - swollen + red calf
    rr(d,154,110,166,132,SKIN); el(d,148,130,176,164,REDSKIN); el(d,150,160,174,172,SKIN); rr(d,150,170,174,173,SKIN_D)
    d.line([(182,134),(190,134)],fill=ACCENT); d.line([(182,160),(190,160)],fill=ACCENT)   # size bracket
    d.line([(190,134),(190,160)],fill=ACCENT); TLX.add(150,176,"SWOLLEN / RED",RED,'tiny')
    bz=int(2*math.sin(2*math.pi*4*t/12))
    for a in (200,240,300,340):
        ar=math.radians(a); d.line([(162+int(18*math.cos(ar)),146+int(18*math.sin(ar))),(162+int((22+bz)*math.cos(ar)),146+int((22+bz)*math.sin(ar)))],fill=AMBER)

def pe(d,t):
    # chest with lungs + clot + pain burst + short-breath puffs
    el(d,112,112,140,160,LUNG); el(d,144,112,172,160,LUNG)
    el(d,112,112,140,124,LUNG_D); el(d,144,112,172,124,LUNG_D)
    rr(d,140,104,144,118,(196,110,124))                      # trachea
    for bx in (122,126,130):
        for by in (134,140,146): d.point((bx,by),fill=LUNG_D)
    el(d,150,128,160,140,(70,52,60)); el(d,152,130,158,138,(40,30,36))   # clot in R lung
    pz=0.5+0.5*math.sin(2*math.pi*4*t/12)
    for a in range(0,360,45):
        ar=math.radians(a); d.line([(155+int(8*math.cos(ar)),134+int(8*math.sin(ar))),(155+int((13+pz*3)*math.cos(ar)),134+int((13+pz*3)*math.sin(ar)))],fill=RED,width=2)
    for i,(sx,sy) in enumerate([(176,108),(184,116),(178,124)]):      # short-breath puffs
        d.arc([sx,sy,sx+10,sy+6],200,360,fill=(150,170,196))
    TLX.add(176,96,"SUDDEN SOB",ACCENT,'tiny'); TLX.add(104,164,"PLEURITIC PAIN",RED,'tiny')

def walker(d,cx,fy,t):
    ph=4*math.pi*t/3.0; sw=int(6*math.sin(ph)); asw=int(5*math.sin(ph+math.pi)); hip=fy-32
    d.line([(cx,hip),(cx-sw,fy)],fill=SKIN,width=3); d.line([(cx,hip),(cx+sw,fy)],fill=SKIN,width=3)
    rr(d,cx-sw-4,fy-2,cx-sw+3,fy+2,(60,66,86)); rr(d,cx+sw-3,fy-2,cx+sw+4,fy+2,(60,66,86))
    rr(d,cx-10,fy-58,cx+10,hip+4,GOWN); rr(d,cx-10,fy-58,cx+10,fy-55,GOWN_H); rr(d,cx+6,fy-56,cx+10,hip,GOWN_D)
    d.line([(cx-9,fy-54),(cx-9+asw,fy-34)],fill=SKIN,width=3); d.line([(cx+9,fy-54),(cx+9-asw,fy-34)],fill=SKIN,width=3)
    hy=fy-74
    el(d,cx-9,hy-4,cx+9,hy+14,SCARF); el(d,cx-6,hy,cx+6,hy+13,SKIN); rr(d,cx-7,hy-2,cx+7,hy,SCARF)
    rr(d,cx-9,hy+6,cx-6,hy+16,SCARF); rr(d,cx+6,hy+6,cx+9,hy+16,SCARF); rr(d,cx-5,hy+13,cx+5,hy+18,SCARF)
    d.point((cx-3,hy+6),fill=SKIN_D); d.point((cx+3,hy+6),fill=SKIN_D)
    # tiny motion lines behind her
    for i in range(3): d.line([(cx-16-i*5,fy-20-i*6),(cx-22-i*5,fy-20-i*6)],fill=(70,84,110))

def clot_meter(d,x,ytop,ybot,lvl):
    risk=1-lvl
    rr(d,x-3,ytop-3,x+15,ybot+5,(34,40,58)); d.rectangle([x-3,ytop-3,x+15,ybot+5],outline=(70,78,98))
    fillh=int((ybot-ytop)*risk); col=RED if risk>0.6 else (AMBER if risk>0.3 else GREEN)
    rr(d,x,ybot-fillh,x+12,ybot,col)
    TLX.add(x-4,ytop-12,"CLOT RISK",(206,180,186),'tiny')
    TLX.add(x+19,ytop-1,"HIGH",(236,130,130),'tiny'); TLX.add(x+19,ybot-6,"LOW",(120,210,160),'tiny')
    ax=x+58; d.line([(ax,ytop+8),(ax,ybot-10)],fill=ACCENT,width=2); d.polygon([(ax,ybot-4),(ax-4,ybot-12),(ax+4,ybot-12)],fill=ACCENT)
    if risk<0.25:
        d.line([(x+30,ybot-18),(x+34,ybot-12)],fill=GREEN,width=2); d.line([(x+34,ybot-12),(x+42,ybot-26)],fill=GREEN,width=2)

def note(d,x,y,w):
    rr(d,x,y,x+w,y+40,(40,30,34)); rr(d,x,y,x+w,y+2,(130,70,74))
    TLX.add(x+6,y+3,"RED FLAGS:",(236,150,160),'tiny')
    TLX.add(x+6,y+16,"one swollen calf  *  sudden breathless",(214,180,186),'tiny')
    TLX.add(x+6,y+27,"pleuritic chest pain  ->  call for help",(214,180,186),'tiny')

def panel(d,x,y,w,cur):
    h=23+len(ITEMS)*19+5
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))
    TLX.add(x+6,y+3,"VTE: ASK + MOVE",INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
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
    s=int(t//3)%4
    im=Image.new('RGB',(GW,GH),WALL); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,72,WALL2); rr(d,0,181,GW-1,GH-1,FLOOR); rr(d,0,181,GW-1,183,FLOORH)
    if s==0: dvt(d,t)
    elif s==1: pe(d,t)
    else:
        lvl=smooth((t-6)/6.0); walker(d,146,174,t); clot_meter(d,58,100,172,lvl)
    BR.student(d,300,232,t=t,writing=1.0)
    if t>=2.5:
        if s<2:
            TLX.add(214,88,"ASK",(0,180,196),'small'); hud.speech_bubble(d,TLX,208,96,["ANY LEG OR","CHEST SYMPTOMS?"],300)
        else:
            TLX.add(200,88,"ADVISE",(0,180,196),'small'); hud.speech_bubble(d,TLX,194,96,["LET'S GET YOU","UP & WALKING"],300)
    TLX.add(40,30,"AFTER BIRTH - CLOT RISK",ANSWC,'tiny')
    TLX.add(40,48,ITEMS[s],ACCENT,'small')
    panel(d,338,22,136,s)
    TLX.add(388,13,"VTE",(150,150,162),'small')
    note(d,36,196,236)
    TLX.add(292,246,"WHY IT MATTERS:",(0,180,196),'small')
    TLX.add(292,254,PEARL[s],(206,186,192),'small')
    rr(d,16,18,120,19,ACCENT)
    TLX.add(16.4,5.3,"CLOTS & MOVING",(10,14,24),'body'); TLX.add(16,5,"CLOTS & MOVING",TEXT,'body')
    TLX.add(16.4,21.3,"ASK, THEN GET MOVING",(10,14,24),'small'); TLX.add(16,21,"ASK, THEN GET MOVING",TEXTDIM,'small')
    big=im.resize((GW*SCALE,GH*SCALE),Image.NEAREST); bd=ImageDraw.Draw(big); TLX.flush(bd)
    return np.array(big,np.uint8)

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        Image.fromarray(render(tv)).save(f'D:/Ue/UE_5.8/obgyn_explainer/b13_{tv}.png'); print("ok",tv)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else 'D:/Ue/UE_5.8/obgyn_explainer/beat13_vte_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{GW*SCALE}x{GH*SCALE}','-r',str(FPS),'-i','-',
             '-vf','format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
