"""Labour & Delivery -> Recovery: one cinematic pixel room that transforms.
480x270 grid -> nearest-neighbor x8 -> 3840x2160. 24fps.
  --still N  : save one 4K PNG at t=N
  (default)  : render full MP4
"""
import numpy as np, math, subprocess, sys, os
from PIL import Image, ImageDraw
_WINFF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
FFMPEG=os.environ.get('FFMPEG', _WINFF if os.path.exists(_WINFF) else 'ffmpeg')
GW,GH,SCALE=480,270,8
FPS,DUR=24,12.0

# ---------- palette ----------
def lerp(a,b,t):
    t=max(0,min(1,t)); return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
WALL_C=(16,24,40); WALL_W=(40,30,46)         # cool->warm wall
WALL2_C=(22,32,50); WALL2_W=(54,40,58)
FLOOR_C=(26,38,58); FLOOR_W=(46,38,56)
SKY_C=(18,28,52); SKY_W=(74,52,66); STAR=(150,170,210); DAWN=(240,180,120)
TRIM=(30,44,66)
FRAME=(96,108,130); FRAME_D=(70,80,100)
MAT=(228,232,240); MAT_D=(198,206,220); PILLOW=(206,222,236); PILLOW_D=(176,196,214)
BLANK=(36,150,172); BLANK_D=(26,120,142); BLANK_H=(72,186,204)
GOWN=(96,104,170); GOWN_D=(70,78,134); GOWN_H=(132,140,200)
SKIN=(242,201,170); SKIN_D=(214,168,138); SKIN_SH=(196,150,120)
SCARF=(210,118,134); SCARF_D=(176,88,106); SCARF_H=(230,150,166)
SCRUB=(42,162,150); SCRUB_D=(28,126,118); SCRUB_H=(86,196,184)
WHITE=(236,240,246); DARK=(28,32,46)
IV=(120,132,150); BAG=(150,214,180); DRIP=(180,226,238)
MON=(44,54,74); SCREEN=(8,14,22); ECG=(78,230,150); MONR=(236,96,112)
BABYB=(244,214,204); BABYB_D=(214,184,176)
ROOFR=(206,96,86); WALLH=(224,206,170); DOORC=(120,86,70)
HEART=(236,96,120); SWEAT=(150,210,235); CROSSR=(214,70,80)
ACCENT=(0,200,214); TEXT=(214,224,238); TEXTDIM=(130,145,170)
FLOWER=[(236,120,150),(240,180,110),(150,210,180)]

FONT={'A':["010","101","111","101","101"],'B':["110","101","110","101","110"],'C':["011","100","100","100","011"],
'D':["110","101","101","101","110"],'E':["111","100","110","100","111"],'F':["111","100","110","100","100"],
'G':["011","100","101","101","011"],'H':["101","101","111","101","101"],'I':["111","010","010","010","111"],
'J':["001","001","001","101","010"],'K':["101","101","110","101","101"],'L':["100","100","100","100","111"],
'M':["101","111","111","101","101"],'N':["101","111","111","111","101"],'O':["010","101","101","101","010"],
'P':["110","101","110","100","100"],'Q':["010","101","101","011","001"],'R':["110","101","110","101","101"],
'S':["011","100","010","001","110"],'T':["111","010","010","010","010"],'U':["101","101","101","101","011"],
'V':["101","101","101","101","010"],'W':["101","101","111","111","101"],'X':["101","101","010","101","101"],
'Y':["101","101","010","010","010"],'Z':["111","001","010","100","111"],' ':["000","000","000","000","000"],
'/':["001","001","010","100","100"],'-':["000","000","111","000","000"],'!':["010","010","010","000","010"],
'.':["000","000","000","000","010"],"'":["010","010","000","000","000"],'&':["010","101","010","101","011"],
'?':["110","001","010","000","010"],':':["000","010","000","010","000"]}
def rr(d,x0,y0,x1,y1,c): d.rectangle([x0,y0,x1,y1],fill=c)
def el(d,x0,y0,x1,y1,c): d.ellipse([x0,y0,x1,y1],fill=c)
def text(d,s,x,y,c,alpha=1.0):
    if alpha<=0: return
    for ch in s.upper():
        g=FONT.get(ch,FONT[' '])
        for ry,row in enumerate(g):
            for rx,v in enumerate(row):
                if v=='1': d.point((x+rx,y+ry),fill=c)
        x+=4
def smooth(u): u=max(0.,min(1.,u)); return u*u*(3-2*u)

def dome(d,cx,baseY,topY,halfw,c,hi=None,sh=None):
    for y in range(int(topY),int(baseY)+1):
        frac=(y-topY)/max(1,(baseY-topY)); w=int(halfw*math.sin(frac*math.pi/2))
        if w<=0: continue
        rr(d,cx-w,y,cx+w,y,c)
        if hi and y<topY+3: rr(d,cx-max(0,w-2),y,cx+max(0,w-2),y,hi)
        if sh and w>3 and y>topY+2: rr(d,cx+w-2,y,cx+w,y,sh)

# ---------- background ----------
def background(d,t,warmth):
    wall=lerp(WALL_C,WALL_W,warmth); wall2=lerp(WALL2_C,WALL2_W,warmth)
    floor=lerp(FLOOR_C,FLOOR_W,warmth)
    rr(d,0,0,GW-1,GH-1,wall); rr(d,0,0,GW-1,70,wall2)
    rr(d,0,150,GW-1,151,TRIM); rr(d,0,181,GW-1,GH-1,floor); rr(d,0,181,GW-1,182,lerp((38,52,74),(60,50,66),warmth))
    # window with sky (night -> dawn)
    sky=lerp(SKY_C,SKY_W,warmth)
    rr(d,28,26,112,92,(60,68,86)); rr(d,31,29,109,89,sky)
    if warmth>0.3:
        el(d,86,58,104,76,lerp(sky,DAWN,warmth))      # soft sun
    else:
        for sx,sy in [(44,40),(60,52),(78,36),(94,62),(52,70)]:
            d.point((sx,sy),fill=STAR)
    rr(d,69,29,70,89,(60,68,86)); rr(d,31,58,109,59,(60,68,86))  # window cross
    # wall clock
    ccx,ccy=250,46
    el(d,ccx-12,ccy-12,ccx+12,ccy+12,(222,226,234)); el(d,ccx-10,ccy-10,ccx+10,ccy+10,(30,40,60))
    # hands: 'time' advances; faster during transition handled by caller via t param already baked
    ha=t*0.9; ma=t*0.9*12
    d.line([(ccx,ccy),(ccx+int(6*math.sin(ha)),ccy-int(6*math.cos(ha)))],fill=WHITE,width=1)
    d.line([(ccx,ccy),(ccx+int(9*math.sin(ma)),ccy-int(9*math.cos(ma)))],fill=ACCENT,width=1)
    el(d,ccx-1,ccy-1,ccx+1,ccy+1,WHITE)
    # medical cross plaque
    rr(d,150,30,164,44,(236,240,246)); rr(d,155,32,159,42,CROSSR); rr(d,152,35,162,39,CROSSR)

# ---------- props ----------
def iv_pole(d,x,t):
    rr(d,x,98,x+1,210,IV); rr(d,x-6,210,x+8,211,IV); rr(d,x-6,96,x+2,98,IV)
    rr(d,x-6,100,x+6,116,BAG); rr(d,x-5,110,x+5,116,lerp(BAG,(120,190,160),0.5))
    dp=(t%1.4)/1.4; dy=116+int(dp*8)
    if dp<0.7: rr(d,x,dy,x,dy+1,DRIP)
    rr(d,x,116,x,168,DRIP)

def monitor(d,x,y,t,calm):
    rr(d,x+8,y+26,x+10,y+70,FRAME_D); rr(d,x,y+68,x+20,y+70,FRAME_D)
    rr(d,x-14,y,x+22,y+26,MON); rr(d,x-11,y+3,x+19,y+23,SCREEN)
    base=y+13; prev=None
    spd=0.9 if calm else 1.8
    for sx in range(x-10,x+18):
        ph=((sx-(x-10))/28 + t*spd)%1.0; yy=base
        if 0.45<ph<0.5: yy=base-(6 if calm else 9)
        elif 0.5<=ph<0.55: yy=base+(3 if calm else 5)
        elif 0.40<ph<0.45: yy=base-2
        if prev is not None:
            a,b=sorted((prev,yy)); rr(d,sx,a,sx,b,ECG)
        d.point((sx,yy),fill=ECG); prev=yy
    beat=(t*(2.0 if calm else 2.6))%1.0
    if beat<0.14: rr(d,x-9,y+3,x-6,y+6,MONR)
    text(d,"140" if calm else "150",x+9,y+3,ECG)

def nightstand(d,x,y,flowers):
    rr(d,x,y,x+26,y+22,FRAME); rr(d,x+1,y+1,x+25,y+9,lerp(FRAME,(120,130,150),.4))
    rr(d,x+2,y+11,x+24,y+20,FRAME_D)
    if flowers>0.02:
        a=flowers
        rr(d,x+10,int(y-6*a),x+11,y,(70,140,90))                 # stem
        for i,(dx,dy) in enumerate([(-3,-7),(3,-7),(0,-10),(-2,-3),(2,-3)]):
            if a> i/6:
                c=FLOWER[i%3]; px,py=x+10+dx,int(y-6*a)+dy
                el(d,px-1,py-1,px+1,py+1,c)

def bed(d):
    rr(d,66,210,72,230,FRAME_D); rr(d,250,210,256,230,FRAME_D)      # legs
    rr(d,60,196,262,212,FRAME)                                      # base
    rr(d,62,170,260,196,MAT); rr(d,62,193,260,196,MAT_D)            # mattress
    rr(d,56,150,64,212,FRAME)                                       # headboard
    rr(d,66,160,104,176,PILLOW); rr(d,66,172,104,176,PILLOW_D)      # pillow

# ---------- characters ----------
def mother(d,t,ctr,breath,eye,sweat,warmth,holdbaby):
    # ctr: contraction 0..1 (labour), eye: 0 open..1 shut, breath: px rise, holdbaby 0..1
    mx=96; sh=int(breath); bf=1-holdbaby
    # pillow / backrest behind upper body (propped up in bed)
    rr(d,60,122,114,176,PILLOW); rr(d,60,122,114,126,WHITE); rr(d,60,172,114,176,PILLOW_D)
    rr(d,110,126,114,172,PILLOW_D)
    # upper gown — only shoulders / upper chest show above the blanket
    rr(d,mx-16,148-sh,mx+14,166,GOWN); rr(d,mx-16,148-sh,mx+14,151-sh,GOWN_H)
    rr(d,mx+10,150-sh,mx+14,166,GOWN_D)
    # ---- blanket actually covering her lower body ----
    rr(d,92,170,258,196,BLANK); rr(d,92,170,258,172,BLANK_H); rr(d,92,193,258,196,BLANK_D)   # over legs
    rr(d,mx-18,160,mx+34,196,BLANK); rr(d,mx-18,160,mx+34,162,BLANK_H)                         # pulled up over lap/waist
    for fx in range(132,256,24): rr(d,fx,176,fx,192,BLANK_D)                                   # folds
    # belly mound rising from the blanket in front of her (labour only)
    if bf>0.15:
        bw=int(34*bf); bh=int(30*bf); bcx=mx+34; btop=172-bh-int(3*ctr)
        el(d,bcx-bw,btop,bcx+bw,184,BLANK)
        if bw>12:
            el(d,bcx-bw+4,btop+2,bcx-2,btop+bh-2,BLANK_H)
            el(d,bcx+bw-10,btop+bh-6,bcx+bw-2,182,BLANK_D)
    # hands resting on top of the pregnant bump (natural labour pose)
    if holdbaby<0.35:
        d.line([(mx-9,151-sh),(mx+13,153)],fill=SKIN,width=4)   # left forearm draped onto bump
        d.line([(mx+13,151-sh),(mx+29,152)],fill=SKIN,width=4)  # right forearm draped onto bump
        el(d,mx+8,149,mx+19,158,SKIN)                           # left hand on belly
        el(d,mx+23,148,mx+34,157,SKIN)                          # right hand on belly
        rr(d,mx+10,156,mx+17,157,SKIN_D); rr(d,mx+25,155,mx+32,156,SKIN_D)   # finger shade
    # ---- head + HIJAB (snug wrap framing the face, no hair) ----
    hy=124-sh
    el(d,mx-10,hy-3,mx+10,hy+17,SCARF)                 # cap covering hair
    rr(d,mx-10,hy+6,mx-7,hy+18,SCARF); rr(d,mx+7,hy+6,mx+10,hy+18,SCARF)  # cheek sides
    rr(d,mx-9,hy+15,mx+9,hy+21,SCARF)                  # chin wrap
    rr(d,mx-6,hy+20,mx+6,hy+27,SCARF)                  # neck/shoulder cover
    rr(d,mx-9,hy+19,mx+9,hy+21,SCARF_H)                # chin fabric edge
    rr(d,mx-10,hy+6,mx-8,hy+18,SCARF_D); rr(d,mx+8,hy+6,mx+10,hy+18,SCARF_D)  # side shade
    el(d,mx-7,hy+2,mx+7,hy+16,SKIN)                    # face opening
    rr(d,mx-8,hy,mx+8,hy+3,SCARF); el(d,mx-10,hy-3,mx+2,hy+4,SCARF_H)  # forehead band + hilite
    cyf=hy+8
    if eye<0.5:
        rr(d,mx-4,cyf,mx-3,cyf+2,DARK); rr(d,mx+2,cyf,mx+3,cyf+2,DARK)
        d.line([(mx-2,cyf+6),(mx+2,cyf+6)],fill=SKIN_D)
    else:
        d.line([(mx-5,cyf+1),(mx-2,cyf+1)],fill=SKIN_SH); d.line([(mx+1,cyf+1),(mx+4,cyf+1)],fill=SKIN_SH)
        rr(d,mx-2,cyf+5,mx+2,cyf+7,SKIN_SH)
    el(d,mx-7,cyf+3,mx-5,cyf+5,lerp(SKIN,HEART,.35)); el(d,mx+5,cyf+3,mx+7,cyf+5,lerp(SKIN,HEART,.35))
    if sweat>0.3:
        sy=hy+6+int((t*10)%8); d.point((mx+9,sy),fill=SWEAT); d.point((mx+9,sy+1),fill=SWEAT)
    # ---- baby cradled (recovery) ----
    if holdbaby>0.3:
        a=smooth((holdbaby-0.3)/0.7); bx,by=mx+8,hy+30
        sc=1
        el(d,bx-9,by-6,bx+9,by+8,BABYB); el(d,bx-9,by+2,bx-3,by+8,BABYB_D)
        el(d,bx-5,by-9,bx+5,by+1,SKIN); rr(d,bx-4,by-1,bx+4,by+1,BABYB)
        d.line([(bx-3,by-6),(bx-1,by-6)],fill=DARK); d.line([(bx+1,by-6),(bx+3,by-6)],fill=DARK)
        rr(d,bx-1,by-10,bx+1,by-9,(60,42,46))
        # mother's arms wrap the baby
        rr(d,mx-14,hy+28,mx-6,by+6,SKIN); rr(d,mx+12,hy+26,mx+18,by+4,SKIN)
        el(d,bx-12,by+2,bx-4,by+9,SKIN)

def midwife(d,t,pose,breath,warmth):
    cx=312; fy=232; sh=int(breath*0.6)
    lean = -4 if pose=='support' else 0
    cx+=lean
    # shadow
    el(d,cx-14,fy,cx+14,fy+3,(10,16,28))
    # legs
    rr(d,cx-10,fy-40,cx+10,fy-6,SCRUB_D); rr(d,cx-1,fy-40,cx+1,fy-6,DARK)
    rr(d,cx-9,fy-7,cx-2,fy,WHITE); rr(d,cx+2,fy-7,cx+9,fy,WHITE)
    # torso scrubs
    rr(d,cx-12,fy-74-sh,cx+12,fy-38,SCRUB); rr(d,cx-12,fy-74-sh,cx+12,fy-70-sh,SCRUB_H)
    rr(d,cx+8,fy-70,cx+12,fy-40,SCRUB_D)
    # arms by pose
    if pose=='support':
        rr(d,cx-16,fy-72,cx-12,fy-50,SCRUB); rr(d,cx-20,fy-54,cx-12,fy-50,SCRUB)  # left arm reaching toward mother
        rr(d,cx-22,fy-54,cx-16,fy-50,SKIN)
        rr(d,cx+12,fy-72,cx+16,fy-48,SCRUB); rr(d,cx+12,fy-50,cx+16,fy-46,SKIN)
    elif pose=='cheer':
        # gentle: one hand raised in a little wave near the head, other relaxed at side
        wv=int(2*math.sin(t*6))
        rr(d,cx-16,fy-78,cx-12,fy-60,SCRUB); rr(d,cx-18+wv,fy-86,cx-13+wv,fy-78,SCRUB)
        rr(d,cx-19+wv,fy-90,cx-13+wv,fy-86,SKIN)                 # waving hand up
        rr(d,cx+12,fy-72,cx+15,fy-50,SCRUB); rr(d,cx+12,fy-52,cx+15,fy-48,SKIN)
    else:
        rr(d,cx-15,fy-72,cx-12,fy-48,SCRUB); rr(d,cx+12,fy-72,cx+15,fy-48,SCRUB)
        rr(d,cx-15,fy-50,cx-12,fy-46,SKIN); rr(d,cx+12,fy-50,cx+15,fy-46,SKIN)
    # head + cap
    hy=fy-96-sh
    el(d,cx-8,hy,cx+8,hy+20,SKIN)
    el(d,cx-9,hy-4,cx+9,hy+10,SCRUB); el(d,cx-9,hy-4,cx+4,hy+4,SCRUB_H)
    rr(d,cx-4,hy+8,cx-3,hy+10,DARK); rr(d,cx+2,hy+8,cx+3,hy+10,DARK)
    if pose=='cheer': rr(d,cx-2,hy+14,cx+2,hy+16,SKIN_SH)       # open happy
    else: d.line([(cx-2,hy+15),(cx+2,hy+15)],fill=SKIN_D)
    # stethoscope
    d.line([(cx-5,hy+18),(cx-6,fy-60),(cx-1,fy-54)],fill=(210,218,228))
    d.line([(cx+5,hy+18),(cx+6,fy-60),(cx+1,fy-54)],fill=(210,218,228))
    el(d,cx-2,fy-56,cx+1,fy-53,ACCENT)

def student(d,cx,fy,t=0.0,writing=0.0):
    """Medical student / examinee taking the history: neat hair, white coat over blue shirt, lanyard, clipboard + pen."""
    COAT=(226,230,236); COAT_D=(198,204,214); SHIRT=(86,148,198); SHIRT_D=(62,118,166)
    TROUS=(58,64,84); SHOE=(34,38,52); HAIR=(58,44,46); CLIP=(150,110,74); PAPER=(238,240,246); PEN=(40,44,60); LAN=(220,90,104); CLAW=(46,48,56)
    bob=int(1*math.sin(2*math.pi*t/3.5))
    el(d,cx-13,fy,cx+13,fy+3,(10,16,28))                               # shadow
    rr(d,cx-9,fy-38,cx+9,fy-6,TROUS); rr(d,cx-1,fy-38,cx+1,fy-6,(44,48,66))
    rr(d,cx-9,fy-7,cx-2,fy,SHOE); rr(d,cx+2,fy-7,cx+9,fy,SHOE)
    rr(d,cx-10,fy-72-bob,cx+10,fy-36,SHIRT); rr(d,cx+6,fy-70,cx+10,fy-38,SHIRT_D)
    d.polygon([(cx-2,fy-71-bob),(cx+2,fy-71-bob),(cx+3,fy-60),(cx,fy-55),(cx-3,fy-60)],fill=(32,54,110))   # navy tie
    rr(d,cx-13,fy-74-bob,cx-6,fy-34,COAT); rr(d,cx+6,fy-74-bob,cx+13,fy-34,COAT)
    rr(d,cx-13,fy-74-bob,cx-11,fy-34,COAT_D); rr(d,cx+11,fy-74-bob,cx+13,fy-34,COAT_D)
    rr(d,cx-13,fy-74-bob,cx+13,fy-72-bob,COAT)
    d.polygon([(cx-6,fy-72-bob),(cx-2,fy-72-bob),(cx-5,fy-58)],fill=COAT)
    d.polygon([(cx+6,fy-72-bob),(cx+2,fy-72-bob),(cx+5,fy-58)],fill=COAT)
    d.line([(cx-4,fy-71-bob),(cx-2,fy-56)],fill=LAN); d.line([(cx+4,fy-71-bob),(cx+2,fy-56)],fill=LAN)
    rr(d,cx-3,fy-56,cx+3,fy-48,PAPER); rr(d,cx-3,fy-56,cx+3,fy-54,ACCENT)
    rr(d,cx-14,fy-72-bob,cx-11,fy-52,COAT)                             # left sleeve
    clx,cly=cx-20,fy-56
    rr(d,clx-1,cly-1,clx+15,cly+17,CLIP); rr(d,clx+1,cly+1,clx+13,cly+15,PAPER)
    rr(d,clx+4,cly-3,clx+10,cly+1,(120,130,150))
    for ly in range(cly+4,cly+14,3): rr(d,clx+3,ly,clx+11,ly,(176,186,200))
    rr(d,clx-3,cly+10,clx+2,cly+16,CLAW)                              # left claw
    pw=int(2*math.sin(t*9)) if writing>0.5 else 0
    rr(d,cx+11,fy-72-bob,cx+14,fy-56,COAT); rr(d,cx+9,fy-58,cx+14,fy-52,CLAW)
    d.line([(cx+11,fy-54),(clx+9+pw,cly+8)],fill=PEN)
    el(d,clx+8+pw,cly+7,clx+10+pw,cly+9,ACCENT)
    hy=fy-94-bob
    PIG=(80,82,92); PIG_D=(56,58,68); PIG_H=(108,110,122); BEAK=(94,90,84); BEAK_D=(66,62,58); CERE=(238,240,244); EYEO=(242,172,60)
    # stethoscope draped at the collar
    d.line([(cx-5,fy-76-bob),(cx-8,fy-64),(cx-5,fy-57)],fill=(44,48,58),width=1)
    d.line([(cx+5,fy-76-bob),(cx+8,fy-62),(cx+5,fy-57)],fill=(44,48,58),width=1)
    el(d,cx-7,fy-58,cx-3,fy-54,(196,202,212))
    # pigeon head (faces left, toward the patient)
    el(d,cx-8,hy-2,cx+8,hy+18,PIG); el(d,cx-7,hy-2,cx+5,hy+5,PIG_H); el(d,cx-8,hy+11,cx+8,hy+18,PIG_D)
    d.polygon([(cx-7,hy+7),(cx-16,hy+9),(cx-7,hy+12)],fill=BEAK); d.polygon([(cx-7,hy+10),(cx-14,hy+9),(cx-7,hy+12)],fill=BEAK_D)
    el(d,cx-10,hy+5,cx-6,hy+8,CERE)
    el(d,cx-4,hy+4,cx+1,hy+9,EYEO); el(d,cx-3,hy+5,cx,hy+8,(30,24,18)); d.point((cx-2,hy+5),fill=(255,255,255))

# ---------- overlays ----------
def hearts(d,t,amt):
    if amt<=0.02: return
    for i in range(6):
        seed=i*1.7; life=(t*0.4+seed)%1.0
        if life> amt: continue
        x=150+int(28*math.sin(seed*3)) + int(6*math.sin(t*2+seed))
        y=150-int(life*70); a=1-life
        c=lerp((40,30,46),HEART,a)
        d.point((x,y),fill=c); d.point((x+1,y),fill=c); d.point((x,y+1),fill=c); d.point((x+2,y+1),fill=c)
        d.point((x+1,y+2),fill=c)

def phase_label(d,t,txt,a):
    if a<=0.02: return
    c=lerp((40,50,70),TEXT,a); text(d,txt,20,236,c)

# ---------- timeline ----------
def timeline(t):
    # beats: labour 0-4.2, birth 4.2-5.8, recovery 5.8-10.6, hold 10.6-12
    p={}
    labour = t<4.4
    warmth = smooth((t-4.2)/2.2)
    p['warmth']=warmth
    p['holdbaby']=smooth((t-5.0)/1.6)
    # contraction waves in labour
    ctr=0.0
    if t<4.6:
        ctr=max(0.0, math.sin(2*math.pi*(t+0.5)/2.1))**3
    p['ctr']=ctr
    # breathing: fast/strong in labour, calm later
    if t<4.6:
        p['breath']=2.4*(0.5+0.5*math.sin(2*math.pi*t/1.5)) + 2.0*ctr
    else:
        p['breath']=1.4*(0.5+0.5*math.sin(2*math.pi*t/4.0))
    p['eye']= (0.85*ctr + (0.3 if t<4.6 else 0.0)) if t<5.0 else 0.0
    p['sweat']= 1.0 if (t<4.6 and ctr>0.25) else 0.0
    p['calm']= t>5.0
    p['mw']='support' if t<5.6 else ('cheer' if t<9.6 else 'idle')
    p['hearts']= smooth((t-6.0)/1.2)*(1.0 if t<11.6 else 1.0)
    p['flowers']= smooth((t-6.4)/1.5)
    # birth flash
    p['flash']= max(0.0, 1-abs(t-4.9)/0.5) if 4.4<t<5.4 else 0.0
    # labels
    if t<4.2: p['label']=("LABOUR", smooth(t/0.6)*smooth((4.2-t)/0.5))
    elif t<5.8: p['label']=("A HEALTHY BABY!", smooth((t-4.6)/0.4)*smooth((5.8-t)/0.4))
    elif t<10.0: p['label']=("RECOVERY", smooth((t-6.0)/0.5))
    else: p['label']=("RECOVERY", 1.0)
    # red contraction vignette
    p['redv']=ctr*0.5 if t<4.6 else 0.0
    return p

def render(t):
    im=Image.new('RGB',(GW,GH),WALL_C); d=ImageDraw.Draw(im)
    P=timeline(t)
    background(d,t,P['warmth'])
    iv_pole(d,44,t)
    bed(d)
    nightstand(d,266,188,P['flowers'])
    monitor(d,352,90,t,P['calm'])
    mother(d,t,P['ctr'],P['breath'],P['eye'],P['sweat'],P['warmth'],P['holdbaby'])
    midwife(d,t,P['mw'],P['breath'],P['warmth'])
    hearts(d,t,P['hearts'])
    # title
    text(d,"LABOUR & DELIVERY",14,12,TEXT)
    rr(d,14,22,150,22,lerp(SCRUB,HEART,smooth((t-5)/3)))
    lbl,la=P['label']; phase_label(d,t,lbl,la)
    arr=np.array(im,np.uint8).astype(np.float32)
    # red contraction vignette
    if P['redv']>0.01:
        ov=np.zeros_like(arr); ov[:,:,0]=120
        m=np.zeros((GH,GW),np.float32); m[:30]=1; m[-30:]=1; m[:,:30]=1; m[:,-30:]=1
        arr=arr*(1-(m[:,:,None]*P['redv']*0.4))+ov*(m[:,:,None]*P['redv']*0.4)
    # birth white flash (soft)
    if P['flash']>0.01:
        arr=arr*(1-P['flash']*0.5)+np.array([245,245,250])*(P['flash']*0.5)
    return np.clip(arr,0,255).astype(np.uint8)

def up(a): return np.array(Image.fromarray(a).resize((GW*SCALE,GH*SCALE),Image.NEAREST))

if __name__=='__main__':
    if '--still' in sys.argv:
        tv=float(sys.argv[sys.argv.index('--still')+1])
        out=rf'D:/Ue/UE_5.8/obgyn_explainer/still_{tv}.png'
        Image.fromarray(up(render(tv))).save(out); print("wrote",out)
    else:
        OUT=sys.argv[1] if (len(sys.argv)>1 and not sys.argv[1].startswith('--')) else r'D:/Ue/UE_5.8/obgyn_explainer/birth_recovery_4K.mp4'
        cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{GW}x{GH}','-r',str(FPS),'-i','-',
             '-vf',f'scale={GW*SCALE}:{GH*SCALE}:flags=neighbor,format=yuv420p',
             '-an','-c:v','libx264','-preset','medium','-crf','16','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(render(i/FPS).tobytes())
        p.stdin.close(); err=p.stderr.read(); p.wait()
        if p.returncode: raise RuntimeError(err.decode(errors='ignore'))
        print(OUT, os.path.getsize(OUT))
