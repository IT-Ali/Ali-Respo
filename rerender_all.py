"""Re-render everything with the new pigeon-doctor character: montages (+mux), focus
clips (+mux), then per-section crossfade merges."""
import subprocess, glob, os
PY=r'D:/Ue/UE_5.8/socrates_fix/venv/Scripts/python.exe'
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
MONT={'02':'beat02_site','03':'beat03_route','04':'beat04_difficulty','05':'beat05_episiotomy',
      '06':'beat06_anaesthesia','07':'beat07_preop','08':'beat08_intraop','09':'beat09_indications',
      '10':'beat10_recovery','11':'beat11_pph','12':'beat12_wound','13':'beat13_vte'}
codes=list(MONT)
def run(cmd): r=subprocess.run(cmd,capture_output=True,text=True); return r.returncode, r.stderr[-400:]
def mux(vid,wav,out): return run([FF,'-y','-hide_banner','-loglevel','error','-i',vid,'-i',wav,'-c:v','copy','-c:a','aac','-b:a','160k','-shortest',out])

print("=== MONTAGES ===",flush=True)
for c in codes:
    name=MONT[c]
    rc,err=run([PY,f'{D}/{name}.py'])
    if rc: print('  render ERR',name,err,flush=True); continue
    rc,err=mux(f'{D}/{name}_4K.mp4',f'{D}/beat{c}_ambient.wav',f'{D}/{name}_sfx_4K.mp4')
    print('  montage',name,'OK' if rc==0 else 'MUXERR '+err,flush=True)

print("=== FOCUS ===",flush=True)
for c in codes:
    rc,err=run([PY,f'{D}/beat{c}_focus.py'])
    if rc: print('  render ERR',c,err,flush=True); continue
    n=0
    for v in sorted(glob.glob(f'{D}/beat{c}_focus_*_4K.mp4')):
        if v.endswith('_sfx_4K.mp4'): continue
        mux(v,f'{D}/focus_ambient.wav',v[:-7]+'_sfx_4K.mp4'); n+=1
    print('  focus',c,n,'clips OK',flush=True)

print("=== SECTIONS ===",flush=True)
rc,err=run([PY,f'{D}/merge_part.py']+codes)
print('  sections', 'OK' if rc==0 else err,flush=True)
print("ALL DONE",flush=True)
