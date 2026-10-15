"""Lightweight 2D cut-out poser for the student chibi rig (user's avatar).
Loads full-canvas limb PNGs + rig-map pivots; poses by rotating bones about pivots
with parent hierarchy; crops + downscales to the scene's pixel-grid density."""
import numpy as np, json, math, os
from PIL import Image

class ChibiRig:
    def __init__(self, root=r'D:/Ue/UE_5.8/obgyn_explainer/student_rig'):
        self.root=root
        m=json.load(open(os.path.join(root,'rig-map.json')))
        self.W,self.H=m['canvas']['width'],m['canvas']['height']
        self.bones=m['bones']; self.order=m['parts']
        self.parts={p:Image.open(os.path.join(root,'assets',p+'.png')).convert('RGBA') for p in self.order}
        self.heads={}
        for k,f in [('default','hero-head.png'),('serious','hero-head-serious.png'),
                    ('closed','hero-head-closed.png'),('blush','hero-head-blush.png')]:
            fp=os.path.join(root,'assets',f)
            if os.path.exists(fp): self.heads[k]=Image.open(fp).convert('RGBA')
        self.torso_pivot=(182,500)   # hip centre = root rotation point

    def _rot(self,pivot,ang):
        c,s=math.cos(ang),math.sin(ang); px,py=pivot
        return np.array([[c,-s,px-c*px+s*py],[s,c,py-s*px-c*py],[0,0,1]],float)
    def _world(self,bone,pose):
        R=self._rot(self.bones[bone]['pivot'],math.radians(pose.get(bone,0.0)))
        par=self.bones[bone]['parent']
        if par in self.bones: return self._world(par,pose)@R
        return self._rot(self.torso_pivot,math.radians(pose.get('torso',0.0)))@R
    def _apply(self,img,M):
        inv=np.linalg.inv(M)
        return img.transform((self.W,self.H),Image.AFFINE,
                             (inv[0,0],inv[0,1],inv[0,2],inv[1,0],inv[1,1],inv[1,2]),
                             resample=Image.BICUBIC)
    def render(self,pose=None,head='serious'):
        pose=pose or {}
        canvas=Image.new('RGBA',(self.W,self.H),(0,0,0,0))
        Rt=self._rot(self.torso_pivot,math.radians(pose.get('torso',0.0)))
        for p in self.order:
            M=self._world(p,pose) if p in self.bones else Rt
            canvas.alpha_composite(self._apply(self.parts[p],M))
        canvas.alpha_composite(self._apply(self.heads.get(head,self.heads['default']),self._world('head',pose)))
        return canvas
    def sprite(self,pose=None,head='serious',grid_h=132):
        img=self.render(pose,head); bb=img.getbbox()
        if bb: img=img.crop(bb)
        w=max(1,round(img.width*grid_h/img.height))
        return img.resize((w,grid_h),Image.LANCZOS)

# ---- named poses (bone angles in degrees) ----
def pose_idle(t=0.0):
    sw=1.2*math.sin(2*math.pi*t/3.2)
    return {'left_upper_arm':sw,'right_upper_arm':-sw,'head':0.6*math.sin(2*math.pi*t/4)}
def pose_talk(t=0.0):
    g=6+4*math.sin(2*math.pi*t/1.1)
    return {'right_upper_arm':-18,'right_forearm':-40-g,'left_upper_arm':3,'head':2*math.sin(2*math.pi*t/2.2)}
def pose_point(t=0.0):
    return {'right_upper_arm':-62,'right_forearm':-8,'left_upper_arm':4,'head':-3}
def pose_write(t=0.0):
    w=5*math.sin(2*math.pi*t*2.2)
    return {'left_upper_arm':24,'left_forearm':44,'right_upper_arm':18,'right_forearm':34+w,'head':6}
def pose_ask(t=0.0,T=2.4):
    """gentle talking/asking loop, seamless over T seconds."""
    ph=2*math.pi*t/T
    return {'right_upper_arm':-15+3*math.sin(ph),'right_forearm':-34-7*math.sin(2*ph),
            'left_upper_arm':4+2*math.sin(ph+1.0),'left_forearm':3*math.sin(ph),
            'head':2.6*math.sin(ph),'torso':0.5*math.sin(ph)}
def pose_walk(t=0.0):
    a=22*math.sin(2*math.pi*t/0.7)
    return {'left_thigh':a,'left_shin':max(0,-a*0.6),'right_thigh':-a,'right_shin':max(0,a*0.6),
            'left_upper_arm':-a*0.8,'right_upper_arm':a*0.8}

if __name__=='__main__':
    import sys
    rig=ChibiRig()
    poses={'rest':{}, 'idle':pose_idle(0.4),'talk':pose_talk(0.3),'point':pose_point(),'write':pose_write(0.2),'walk':pose_walk(0.3)}
    bg=Image.new('RGBA',(365*len(poses),678),(236,238,244,255)); x=0
    for nm,p in poses.items():
        s=rig.render(p,'serious'); bg.alpha_composite(s,(x,0)); x+=365
    bg.convert('RGB').resize((365*len(poses)*2,678*2),Image.NEAREST).save(r'D:/Ue/UE_5.8/obgyn_explainer/rig_poses.png')
    print("ok")
