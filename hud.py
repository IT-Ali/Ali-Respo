"""History-taking HUD: the OSCE history sheet (the 'record it' panel) + speech bubble
(the 'ask it' line). Shared across all beats. Uses birth_recovery draw helpers."""
import math
from birth_recovery import rr, el, text

CREAM=(240,238,226); CREAM_D=(210,206,190); INK=(52,56,72); INKDIM=(150,150,162)
LINEC=(200,196,180); ACCENT=(0,200,214); HILITE=(252,240,176)
ANSC=(30,120,142); TICK=(40,172,112)
BUB=(246,248,252); BUB_D=(198,204,214); BUBINK=(44,50,66); ASKC=(0,170,185)

def history_sheet(d,tl,x,y,w,h,title,fields,active,fill,t=0.0):
    """Shapes on grid `d`, text via `tl` (4K). fields=[(LABEL,ANSWER)], active=index filling now."""
    d.rectangle([x,y,x+w,y+h],fill=CREAM,outline=CREAM_D)
    rr(d,x+w//2-8,y-3,x+w//2+8,y+1,(150,160,172))          # clip
    tl.add(x+6,y+3,title,INK,'small'); rr(d,x+6,y+18,x+w-6,y+18,ACCENT)
    ry=y+23
    for i,(label,ans) in enumerate(fields):
        if i==active: rr(d,x+3,ry-3,x+w-3,ry+17,HILITE)     # highlight current
        c=INK if i<=active else INKDIM
        tl.add(x+6,ry-2,label,c,'small')
        aw = ans if i<active else (ans[:max(0,round(len(ans)*fill))] if i==active else "")
        tl.add(x+10,ry+8,aw,ANSC if i<=active else INKDIM,'small')
        rr(d,x+8,ry+18,x+w-8,ry+18,LINEC)                   # underline
        if i==active and fill<1.0 and int(t*2)%2==0:
            cx=int(x+10+tl.w(aw,'small')); rr(d,cx,ry+8,cx,ry+16,INK)   # blinking caret
        if i<active:                                        # tick done fields
            d.line([(x+w-15,ry+5),(x+w-10,ry+10)],fill=TICK); d.line([(x+w-10,ry+10),(x+w-3,ry-1)],fill=TICK)
        ry+=21

def speech_bubble(d,tl,x,y,lines,tailx,size='body'):
    w=int(max(tl.w(l,size) for l in lines))+16; h=len(lines)*10+9
    d.rectangle([x,y,x+w,y+h],fill=BUB,outline=BUB_D)
    tx=max(x+6,min(x+w-6,tailx))
    d.polygon([(tx-4,y+h-1),(tx+6,y+h-1),(tx+1,y+h+8)],fill=BUB)
    d.line([(tx-4,y+h),(tx+1,y+h+8)],fill=BUB_D); d.line([(tx+6,y+h),(tx+1,y+h+8)],fill=BUB_D)
    for i,l in enumerate(lines): tl.add(x+8,y+4+i*10,l,BUBINK,size)
    return w,h
