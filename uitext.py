"""Crisp 4K UI text layer using a readable pixel TTF (Pixelify Sans).
Text is collected in grid coords during scene build, then drawn at full 4K after
upscale — so it's sharp & readable while the art stays chunky-pixel."""
from PIL import ImageFont
FONT_PATH=r'D:/Ue/UE_5.8/obgyn_explainer/fonts/Poppins-SemiBold.ttf'

class TL:
    SIZES={'title':76,'body':60,'small':52,'tiny':46}
    def __init__(self, fontpath=FONT_PATH, scale=8):
        self.fp=fontpath; self.scale=scale; self._f={}; self.cmds=[]
    def _px(self,size): return self.SIZES.get(size,size) if isinstance(size,str) else size
    def font(self,size):
        px=self._px(size)
        if px not in self._f: self._f[px]=ImageFont.truetype(self.fp,px)
        return self._f[px]
    def w(self,s,size='body'):            # text width in GRID px
        return self.font(size).getlength(s)/self.scale
    def add(self,gx,gy,s,color,size='body'):
        if s!="": self.cmds.append((gx,gy,s,color,self._px(size)))
    def flush(self,draw4k):
        for gx,gy,s,color,px in self.cmds:
            draw4k.text((round(gx*self.scale),round(gy*self.scale)),s,
                        font=self.font(px),fill=color,anchor="lt")
        self.cmds=[]
