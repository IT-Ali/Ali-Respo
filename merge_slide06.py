"""Merge the whole Slide 06 into one video: hero intro, then per beat the MONTAGE opener
followed by its FOCUS clips, joined with 0.5s crossfades (video xfade + audio acrossfade).
Builds a filter_complex script (too long for the command line) and runs ffmpeg."""
import glob, subprocess, os
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
FADE=0.5; CLIP=12.0

def focus(beat):
    fs=sorted(glob.glob(f'{D}/beat{beat}_focus_*_sfx_4K.mp4'))
    return fs

order=[f'{D}/birth_recovery_sfx_4K.mp4']
MONT={'02':'beat02_site','03':'beat03_route','04':'beat04_difficulty','05':'beat05_episiotomy',
      '06':'beat06_anaesthesia','07':'beat07_preop','08':'beat08_intraop','09':'beat09_indications',
      '10':'beat10_recovery','11':'beat11_pph','12':'beat12_wound','13':'beat13_vte'}
for b in ['02','03','04','05','06','07','08','09','10','11','12','13']:
    order.append(f'{D}/{MONT[b]}_sfx_4K.mp4')
    order += focus(b)

missing=[p for p in order if not os.path.exists(p)]
if missing:
    raise SystemExit("MISSING:\n"+"\n".join(missing))
n=len(order)
print("clips:",n,flush=True)

# build filter_complex
lines=[]
vcur='[0:v]'; acur='[0:a]'
for k in range(1,n):
    voff=k*(CLIP-FADE)
    vout=f'[v{k}]' if k<n-1 else '[vout]'
    aout=f'[a{k}]' if k<n-1 else '[aout]'
    lines.append(f'{vcur}[{k}:v]xfade=transition=fade:duration={FADE}:offset={voff:.2f}{vout}')
    lines.append(f'{acur}[{k}:a]acrossfade=d={FADE}{aout}')
    vcur=vout; acur=aout
fc=';\n'.join(lines)
with open(f'{D}/_merge_filter.txt','w') as f: f.write(fc)

cmd=[FF,'-y','-hide_banner','-loglevel','error']
for p in order: cmd+=['-i',p]
cmd+=['-filter_complex_script',f'{D}/_merge_filter.txt','-map','[vout]','-map','[aout]',
      '-c:v','libx264','-preset','ultrafast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',
      f'{D}/SLIDE06_FULL_crossfade_4K.mp4']
print("running ffmpeg...",flush=True)
r=subprocess.run(cmd,capture_output=True,text=True)
if r.returncode:
    print("ERR",r.stderr[-3000:],flush=True); raise SystemExit(1)
print("OK", os.path.getsize(f'{D}/SLIDE06_FULL_crossfade_4K.mp4'),flush=True)
