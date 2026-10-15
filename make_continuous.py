"""One continuous 1080p video. Per topic: ASK (question) -> FOCUS clips (explaining) ->
NEXTQ (answer recorded + bridge). All crossfaded (0.5s), 12 topics joined end to end."""
import glob, subprocess, os, re
PY=r'D:/Ue/UE_5.8/socrates_fix/venv/Scripts/python.exe'
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
FADE=0.5
def run(c): r=subprocess.run(c,capture_output=True,text=True); return r.returncode,r.stderr[-600:]
def mux(v,w,o): return run([FF,'-y','-hide_banner','-loglevel','error','-i',v,'-i',w,'-c:v','copy','-c:a','aac','-b:a','160k','-shortest',o])
def dur(f):
    o=subprocess.run([FF,'-i',f],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',o); h,mi,s=m.groups(); return int(h)*3600+int(mi)*60+float(s)
SEQ=[('02','site'),('03','route'),('04','difficulty'),('06','anaesthesia'),('05','episiotomy'),('07','preop'),
     ('08','intraop'),('09','indications'),('10','recovery'),('11','pph'),('12','wound'),('13','vte')]

def chain(clips,out,scale=False):
    n=len(clips); lines=[];
    if scale:
        for k in range(n): lines.append(f'[{k}:v]scale=1920:1080:flags=bicubic[s{k}]')
        vget=lambda k:f'[s{k}]'
    else:
        vget=lambda k:f'[{k}:v]'
    vcur=vget(0); acur='[0:a]'; L=dur(clips[0])
    for k in range(1,n):
        off=L-FADE; vo=f'[v{k}]' if k<n-1 else '[vo]'; ao=f'[a{k}]' if k<n-1 else '[ao]'
        lines.append(f'{vcur}{vget(k)}xfade=transition=fade:duration={FADE}:offset={off:.3f}{vo}')
        lines.append(f'{acur}[{k}:a]acrossfade=d={FADE}{ao}')
        vcur=vo; acur=ao; L=L+dur(clips[k])-FADE
    fp=f'{D}/_ch.txt'; open(fp,'w').write(';\n'.join(lines))
    cmd=[FF,'-y','-hide_banner','-loglevel','error']
    for c in clips: cmd+=['-i',c]
    cmd+=['-filter_complex_script',fp,'-map','[vo]','-map','[ao]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',out]
    return run(cmd)

print("=== ASK BEATS ===",flush=True)
for c,_ in SEQ:
    rc,err=run([PY,f'{D}/nextq.py',c,'--mode','ask'])
    if rc: print(' ask ERR',c,err,flush=True); continue
    mux(f'{D}/ask_{c}_4K.mp4',f'{D}/bridge3_ambient.wav',f'{D}/ask_{c}_sfx_4K.mp4')
    print(' ask',c,'OK',flush=True)

print("=== SEGMENTS (1080p) ===",flush=True)
segs=[]
for c,name in SEQ:
    focus=sorted(glob.glob(f'{D}/beat{c}_focus_*_sfx_4K.mp4'))
    clips=[f'{D}/ask_{c}_sfx_4K.mp4']+focus+[f'{D}/nextq_{c}_sfx_4K.mp4']
    seg=f'{D}/seg_{c}_1080.mp4'
    rc,err=chain(clips,seg,scale=True)
    print(' seg',c,name,'OK' if rc==0 else 'ERR '+err,flush=True)
    if rc==0: segs.append(seg)

print("=== JOIN ALL ===",flush=True)
rc,err=chain(segs,f'{D}/SLIDE06_continuous_1080p.mp4',scale=False)
print(' continuous', 'OK' if rc==0 else 'ERR '+err, os.path.getsize(f'{D}/SLIDE06_continuous_1080p.mp4') if rc==0 else '',flush=True)
print("ALL DONE",flush=True)
