"""Render the 7 section title cards (Pre-op onward), prepend each to its section with a
0.5s crossfade, and output at 1920x1080 (replacing those SLIDE06_1080 clips)."""
import subprocess, os
PY=r'D:/Ue/UE_5.8/socrates_fix/venv/Scripts/python.exe'
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
def run(c): r=subprocess.run(c,capture_output=True,text=True); return r.returncode,r.stderr[-500:]
TOPIC={'07':'preop','08':'intraop','09':'indications','10':'recovery','11':'pph','12':'wound','13':'vte'}
for c in ['07','08','09','10','11','12','13']:
    rc,err=run([PY,f'{D}/title_card.py',c])
    if rc: print('title ERR',c,err,flush=True); continue
    run([FF,'-y','-hide_banner','-loglevel','error','-i',f'{D}/title_{c}_4K.mp4','-i',f'{D}/bridge3_ambient.wav','-c:v','copy','-c:a','aac','-b:a','160k','-shortest',f'{D}/title_{c}_sfx_4K.mp4'])
    sec=f'{D}/beat{c}_section_crossfade_4K.mp4'
    out=f'{D}/SLIDE06_1080/{c}_{TOPIC[c]}_1080p.mp4'
    rc,err=run([FF,'-y','-hide_banner','-loglevel','error','-i',f'{D}/title_{c}_sfx_4K.mp4','-i',sec,'-filter_complex',
        '[0:v]scale=1920:1080:flags=bicubic[v0];[1:v]scale=1920:1080:flags=bicubic[v1];[v0][v1]xfade=transition=fade:duration=0.5:offset=3.0[v];[0:a][1:a]acrossfade=d=0.5[a]',
        '-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out])
    print(c,TOPIC[c],'OK' if rc==0 else 'ERR '+err, os.path.getsize(out) if (os.path.exists(out) and rc==0) else '',flush=True)
print("ALL DONE",flush=True)
