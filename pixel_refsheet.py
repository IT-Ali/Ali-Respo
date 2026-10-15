"""Pixel-art STYLE/CHARACTER reference sheet to hand to an image model.
480x270 grid -> nearest-neighbor x8 -> 3840x2160 PNG."""
import numpy as np, sys
from PIL import Image, ImageDraw
GW,GH,SCALE=480,270,8

BG=(16,24,40); BG2=(22,32,50); FLOOR=(28,40,60); PANEL=(24,34,54)
SKIN=(242,201,170); SKIN_SH=(214,168,138)
SCARF=(210,118,134); SCARF_SH=(176,88,106); SCARF_HI=(230,150,166)
DRESS=(96,104,170); DRESS_SH=(70,78,134); DRESS_HI=(132,140,200)
SCRUB=(42,162,150); SCRUB_SH=(28,126,118); SCRUB_HI=(86,196,184)
HAIR=(58,42,46); WHITE=(236,240,246); DARK=(28,32,46)
BED=(96,108,130); MAT=(228,232,240); BLANK=(36,150,172)
IV=(120,132,150); BAG=(150,214,180)
MON=(44,54,74); SCREEN=(8,14,22); ECG=(78,230,150)
ROOF=(206,96,86); WALLH=(224,206,170); DOOR=(120,86,70)
BLOOD=(214,70,80); ACCENT=(0,200,214)
BABYB=(244,214,204); BABYB_SH=(214,184,176)
TEXT=(214,224,238); TEXTDIM=(128,144,170)

FONT={
'A':["010","101","111","101","101"],'B':["110","101","110","101","110"],
'C':["011","100","100","100","011"],'D':["110","101","101","101","110"],
'E':["111","100","110","100","111"],'F':["111","100","110","100","100"],
'G':["011","100","101","101","011"],'H':["101","101","111","101","101"],
'I':["111","010","010","010","111"],'J':["001","001","001","101","010"],
'K':["101","101","110","101","101"],'L':["100","100","100","100","111"],
'M':["101","111","111","101","101"],'N':["101","111","111","111","101"],
'O':["010","101","101","101","010"],'P':["110","101","110","100","100"],
'Q':["010","101","101","011","001"],'R':["110","101","110","101","101"],
'S':["011","100","010","001","110"],'T':["111","010","010","010","010"],
'U':["101","101","101","101","011"],'V':["101","101","101","101","010"],
'W':["101","101","111","111","101"],'X':["101","101","010","101","101"],
'Y':["101","101","010","010","010"],'Z':["111","001","010","100","111"],
' ':["000","000","000","000","000"],'/':["001","001","010","100","100"],
'-':["000","000","111","000","000"],'&':["010","101","010","101","011"]}
def rr(d,x0,y0,x1,y1,c): d.rectangle([x0,y0,x1,y1],fill=c)
def el(d,x0,y0,x1,y1,c): d.ellipse([x0,y0,x1,y1],fill=c)
def text(d,s,x,y,c):
    for ch in s.upper():
        g=FONT.get(ch,FONT[' '])
        for ry,row in enumerate(g):
            for rx,v in enumerate(row):
                if v=='1': d.point((x+rx,y+ry),fill=c)
        x+=4

def shadow(d,cx,y,w):
    el(d,cx-w,y-2,cx+w,y+2,(10,16,28))

def patient(d,cx,fy):
    shadow(d,cx,fy,16)
    # dress (flared) via polygon
    d.polygon([(cx-11,120),(cx+11,120),(cx+17,fy-7),(cx-17,fy-7)],fill=DRESS)
    el(d,cx-15,138,cx+15,176,DRESS)          # belly
    rr(d,cx-15,152,cx-11,174,DRESS_SH)       # side shade
    el(d,cx-12,142,cx-2,158,DRESS_HI)        # belly highlight
    # legs/feet
    rr(d,cx-8,fy-8,cx-1,fy,DARK); rr(d,cx+1,fy-8,cx+8,fy,DARK)
    # left arm along side; right hand resting on belly
    rr(d,cx-15,122,cx-11,152,SKIN)
    d.line([(cx+13,124),(cx+5,150)],fill=SKIN,width=3)
    el(d,cx+2,148,cx+10,156,SKIN)
    # ---- HIJAB (clearly a headscarf, no hair) ----
    el(d,cx-13,84,cx+13,120,SCARF)                     # scarf covering whole head
    d.polygon([(cx-13,108),(cx-15,132),(cx-5,130),(cx-6,110)],fill=SCARF)  # left drape
    d.polygon([(cx+13,108),(cx+15,132),(cx+5,130),(cx+6,110)],fill=SCARF)  # right drape
    rr(d,cx-12,112,cx-11,130,SCARF_SH); rr(d,cx+11,112,cx+12,130,SCARF_SH) # fold shade
    rr(d,cx-7,116,cx+7,126,SCARF)                      # neck cover
    el(d,cx-8,96,cx+8,118,SKIN)                        # face opening (forehead covered)
    rr(d,cx-9,93,cx+9,97,SCARF)                        # forehead band
    el(d,cx-13,84,cx+4,95,SCARF_HI)                    # scarf top highlight
    rr(d,cx-5,105,cx-4,107,DARK); rr(d,cx+3,105,cx+4,107,DARK)  # eyes
    d.line([(cx-2,112),(cx+2,112)],fill=SKIN_SH,width=1)        # smile
    el(d,cx-7,109,cx-5,111,(236,160,150)); el(d,cx+5,109,cx+7,111,(236,160,150))  # blush

def doctor(d,cx,fy):
    shadow(d,cx,fy,14)
    # legs (pants)
    rr(d,cx-10,150,cx+10,fy-7,SCRUB_SH); rr(d,cx-1,150,cx+1,fy-7,DARK)
    rr(d,cx-9,fy-8,cx-2,fy,WHITE); rr(d,cx+2,fy-8,cx+9,fy,WHITE)  # white shoes
    # scrubs top
    rr(d,cx-12,116,cx+12,152,SCRUB); rr(d,cx-12,116,cx+12,120,SCRUB_HI)
    rr(d,cx+8,120,cx+12,150,SCRUB_SH)
    # arms
    rr(d,cx-14,118,cx-11,146,SCRUB); rr(d,cx+11,118,cx+14,146,SCRUB)
    rr(d,cx-14,144,cx-11,152,SKIN); rr(d,cx+11,144,cx+14,152,SKIN)
    # head + cap
    el(d,cx-9,92,cx+9,116,SKIN)
    el(d,cx-10,86,cx+10,104,SCRUB)           # surgical cap
    el(d,cx-10,86,cx+5,94,SCRUB_HI)
    rr(d,cx-5,102,cx-4,104,DARK); rr(d,cx+3,102,cx+4,104,DARK)
    d.line([(cx-2,109),(cx+2,109)],fill=SKIN_SH,width=1)
    # stethoscope
    d.line([(cx-6,118),(cx-7,132),(cx-2,140)],fill=(210,218,228),width=1,joint="curve")
    d.line([(cx+6,118),(cx+7,132),(cx+2,140)],fill=(210,218,228),width=1,joint="curve")
    el(d,cx-2,140,cx+2,144,ACCENT)

def baby(d,cx,fy):
    shadow(d,cx,fy,13)
    el(d,cx-13,fy-30,cx+13,fy-2,BABYB)       # swaddle body
    el(d,cx-13,fy-14,cx-5,fy-2,BABYB_SH)
    el(d,cx-7,fy-40,cx+7,fy-24,SKIN)         # face
    rr(d,cx-5,fy-24,cx+5,fy-22,BABYB)        # wrap edge
    # sleeping eyes (arcs) + blush + tuft
    d.line([(cx-4,fy-33),(cx-2,fy-33)],fill=DARK); d.line([(cx+2,fy-33),(cx+4,fy-33)],fill=DARK)
    el(d,cx-6,fy-31,cx-4,fy-29,(236,160,150)); el(d,cx+4,fy-31,cx+6,fy-29,(236,160,150))
    rr(d,cx-1,fy-41,cx+1,fy-39,HAIR)
    d.point((cx+9,fy-34),fill=ACCENT); d.point((cx+11,fy-37),fill=ACCENT)  # sparkle

def mini_bed(d,x,y):
    rr(d,x+2,y+14,x+5,y+22,BED); rr(d,x+34,y+14,x+37,y+22,BED)
    rr(d,x,y+8,x+40,y+15,BED); rr(d,x+2,y+2,x+40,y+9,MAT)
    rr(d,x-2,y-3,x+4,y+15,BED)               # headboard
    rr(d,x+4,y+2,x+14,y+6,(206,222,236))     # pillow
    rr(d,x+16,y+1,x+40,y+8,BLANK); el(d,x+22,y-4,x+34,y+4,BLANK)  # bump

def mini_iv(d,x,y):
    rr(d,x+5,y,x+6,y+34,IV); rr(d,x,y+34,x+12,y+35,IV)
    rr(d,x+1,y,x+11,y+9,BAG)
    d.line([(x+6,y+9),(x+6,y+24)],fill=(170,222,235))

def mini_monitor(d,x,y):
    rr(d,x,y,x+34,y+24,MON); rr(d,x+2,y+2,x+32,y+22,SCREEN)
    pts=[]
    for i in range(30):
        yy=y+13
        if i==14: yy=y+5
        elif i==15: yy=y+19
        pts.append((x+2+i,yy))
    d.line(pts,fill=ECG,width=1)
    rr(d,x+4,y+4,x+6,y+6,(236,96,112))

def house(d,x,y):
    d.polygon([(x,y+8),(x+14,y),(x+28,y+8)],fill=ROOF)
    rr(d,x+3,y+8,x+25,y+26,WALLH); rr(d,x+11,y+15,x+17,y+26,DOOR)

def hospital(d,x,y):
    rr(d,x,y,x+26,y+26,(70,90,120)); rr(d,x+2,y+2,x+26,y+26,(84,104,136))
    rr(d,x+10,y+4,x+16,y+8,BLOOD); rr(d,x+8,y+5,x+18,y+7,BLOOD)  # cross
    for ry in range(12,24,5):
        for rx in range(4,24,6): rr(d,x+rx,y+ry,x+rx+2,y+ry+2,(40,54,78))

def swatches(d,x,y,cols):
    for i,c in enumerate(cols):
        rr(d,x+i*13,y,x+i*13+11,y+11,c); rr(d,x+i*13,y,x+i*13+11,y,(0,0,0))

def build():
    im=Image.new('RGB',(GW,GH),BG); d=ImageDraw.Draw(im)
    rr(d,0,0,GW-1,40,BG2)
    rr(d,0,214,GW-1,GH-1,FLOOR); rr(d,0,214,GW-1,215,(38,52,74))
    # title
    text(d,"PIXEL STYLE REFERENCE",10,10,TEXT)
    text(d,"OBSTETRIC TEACHING - DARK THEME",10,20,TEXTDIM)
    # characters
    import birth_recovery as BR
    patient(d,54,205); doctor(d,114,205); BR.student(d,176,205); baby(d,236,205)
    text(d,"PATIENT",42,220,TEXT); text(d,"MIDWIFE",102,220,TEXT); text(d,"STUDENT",164,220,TEXT); text(d,"NEWBORN",224,220,TEXT)
    # divider
    rr(d,276,44,277,208,PANEL)
    # props
    text(d,"PROPS",300,48,TEXTDIM)
    mini_bed(d,290,150); text(d,"BED",300,176,TEXTDIM)
    mini_iv(d,350,120); text(d,"IV",350,158,TEXTDIM)
    mini_monitor(d,378,120); text(d,"MONITOR",378,148,TEXTDIM)
    house(d,300,70); text(d,"HOME",302,100,TEXTDIM)
    hospital(d,350,70); text(d,"HOSPITAL",346,100,TEXTDIM)
    # blood-loss / drop accent sample
    el(d,430,120,446,140,BLOOD); text(d,"BLOOD",428,146,TEXTDIM)
    # palette
    text(d,"PALETTE",10,228,TEXTDIM)
    swatches(d,10,240,[BG,BG2,DRESS,SCARF,SCRUB,SKIN,BLANK,ECG,BLOOD,ACCENT,WHITE,HAIR])
    return np.array(im,np.uint8)

if __name__=='__main__':
    a=build()
    big=np.array(Image.fromarray(a).resize((GW*SCALE,GH*SCALE),Image.NEAREST))
    out=sys.argv[1] if len(sys.argv)>1 else r'D:/Ue/UE_5.8/obgyn_explainer/pixel_reference_sheet.png'
    Image.fromarray(big).save(out); print("wrote",out)
