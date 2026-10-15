"""Full parts: focus(explaining) clips -> montage(asking), crossfaded (0.5s), then a HARD
CUT into the next-question bridge. Output 1920x1080. partNN_<topic>_full_1080p.mp4"""
import glob, subprocess, os, re
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
FADE=0.5
def run(c): r=subprocess.run(c,capture_output=True,text=True); return r.returncode,r.stderr[-500:]
def dur(f):
    o=subprocess.run([FF,'-i',f],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',o); h,mi,s=m.groups(); return int(h)*3600+int(mi)*60+float(s)
MONT={'02':'beat02_site','03':'beat03_route','04':'beat04_difficulty','05':'beat05_episiotomy','06':'beat06_anaesthesia',
      '07':'beat07_preop','08':'beat08_intraop','09':'beat09_indications','10':'beat10_recovery','11':'beat11_pph','12':'beat12_wound','13':'beat13_vte'}
SEQ=[('02','site'),('03','route'),('04','difficulty'),('06','anaesthesia'),('05','episiotomy'),('07','preop'),
     ('08','intraop'),('09','indications'),('10','recovery'),('11','pph'),('12','wound'),('13','vte')]

def xfade_chain(clips,out):
    n=len(clips); lines=[]; vcur='[0:v]'; acur='[0:a]'; L=dur(clips[0])
    for k in range(1,n):
        off=L-FADE; vo=f'[v{k}]' if k<n-1 else '[vo]'; ao=f'[a{k}]' if k<n-1 else '[ao]'
        lines.append(f'{vcur}[{k}:v]xfade=transition=fade:duration={FADE}:offset={off:.3f}{vo}')
        lines.append(f'{acur}[{k}:a]acrossfade=d={FADE}{ao}')
        vcur=vo; acur=ao; L=L+dur(clips[k])-FADE
    fp=f'{D}/_xf.txt'; open(fp,'w').write(';\n'.join(lines))
    cmd=[FF,'-y','-hide_banner','-loglevel','error']
    for c in clips: cmd+=['-i',c]
    cmd+=['-filter_complex_script',fp,'-map','[vo]','-map','[ao]','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',out]
    return run(cmd)

for i,(c,name) in enumerate(SEQ,1):
    focus=sorted(glob.glob(f'{D}/beat{c}_focus_*_sfx_4K.mp4'))
    mont=f'{D}/{MONT[c]}_sfx_4K.mp4'
    if c=='02':
        run([FF,'-y','-hide_banner','-loglevel','error','-i',mont,'-t','9.8','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',f'{D}/_m02.mp4']); mont=f'{D}/_m02.mp4'
    clips=focus+[mont]
    seg=f'{D}/_seg_{c}.mp4'
    rc,err=xfade_chain(clips,seg)
    if rc: print(f'part{i:02d} {name} XFADE ERR',err,flush=True); continue
    nq=f'{D}/nextq_{c}_sfx_4K.mp4'
    out=f'{D}/part{i:02d}_{name}_full_1080p.mp4'
    rc,err=run([FF,'-y','-hide_banner','-loglevel','error','-i',seg,'-i',nq,'-filter_complex',
        '[0:v]scale=1920:1080:flags=bicubic[v0];[1:v]scale=1920:1080:flags=bicubic[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]',
        '-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out])
    os.path.exists(seg) and os.remove(seg)
    print(f'part{i:02d}',name,'OK' if rc==0 else 'ERR '+err, os.path.getsize(out) if (os.path.exists(out) and rc==0) else '',flush=True)
print("ALL DONE",flush=True)
