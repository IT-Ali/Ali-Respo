"""Render all 12 next-question beats, then merge each montage + its next-question beat
(hard cut, no fade) and downscale the result to 1920x1080."""
import subprocess, os
PY=r'D:/Ue/UE_5.8/socrates_fix/venv/Scripts/python.exe'
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
def run(cmd): r=subprocess.run(cmd,capture_output=True,text=True); return r.returncode,r.stderr[-500:]
def mux(v,w,o): return run([FF,'-y','-hide_banner','-loglevel','error','-i',v,'-i',w,'-c:v','copy','-c:a','aac','-b:a','160k','-shortest',o])
MONT={'02':'beat02_site','03':'beat03_route','04':'beat04_difficulty','05':'beat05_episiotomy','06':'beat06_anaesthesia',
      '07':'beat07_preop','08':'beat08_intraop','09':'beat09_indications','10':'beat10_recovery','11':'beat11_pph','12':'beat12_wound','13':'beat13_vte'}
codes=list(MONT)

print("=== NEXT-Q BEATS ===",flush=True)
for c in codes:
    rc,err=run([PY,f'{D}/nextq.py',c])
    if rc: print(' render ERR',c,err,flush=True); continue
    mux(f'{D}/nextq_{c}_4K.mp4',f'{D}/bridge3_ambient.wav',f'{D}/nextq_{c}_sfx_4K.mp4')
    print(' nextq',c,'OK',flush=True)

print("=== MERGE + 1080p ===",flush=True)
SEQ=[('02','site'),('03','route'),('04','difficulty'),('06','anaesthesia'),('05','episiotomy'),('07','preop'),
     ('08','intraop'),('09','indications'),('10','recovery'),('11','pph'),('12','wound'),('13','vte')]
for i,(c,name) in enumerate(SEQ,1):
    mont=f'{D}/{MONT[c]}_sfx_4K.mp4'
    if c=='02':
        rc,err=run([FF,'-y','-hide_banner','-loglevel','error','-i',mont,'-t','9.8','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',f'{D}/_m02.mp4'])
        mont=f'{D}/_m02.mp4'
    nq=f'{D}/nextq_{c}_sfx_4K.mp4'
    out=f'{D}/part{i:02d}_{name}_1080p.mp4'
    rc,err=run([FF,'-y','-hide_banner','-loglevel','error','-i',mont,'-i',nq,'-filter_complex',
        '[0:v]scale=1920:1080:flags=bicubic[v0];[1:v]scale=1920:1080:flags=bicubic[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]',
        '-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out])
    print(f' part{i:02d}',name, 'OK' if rc==0 else 'ERR '+err, os.path.getsize(out) if (os.path.exists(out) and rc==0) else '',flush=True)
print("ALL DONE",flush=True)
