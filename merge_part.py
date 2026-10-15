"""Merge ONE section per beat = that beat's montage opener + its focus clips, joined with
0.5s crossfades. Usage: merge_part.py 02 03 ...  -> beatNN_section_crossfade_4K.mp4"""
import glob, subprocess, os, sys
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
D='D:/Ue/UE_5.8/obgyn_explainer'
FADE=0.5; CLIP=12.0
MONT={'02':'beat02_site','03':'beat03_route','04':'beat04_difficulty','05':'beat05_episiotomy',
      '06':'beat06_anaesthesia','07':'beat07_preop','08':'beat08_intraop','09':'beat09_indications',
      '10':'beat10_recovery','11':'beat11_pph','12':'beat12_wound','13':'beat13_vte'}
def clips(b):
    return [f'{D}/{MONT[b]}_sfx_4K.mp4'] + sorted(glob.glob(f'{D}/beat{b}_focus_*_sfx_4K.mp4'))
for b in sys.argv[1:]:
    order=clips(b); n=len(order)
    miss=[p for p in order if not os.path.exists(p)]
    if miss: print(b,"MISSING",miss,flush=True); continue
    lines=[]; vcur='[0:v]'; acur='[0:a]'
    for k in range(1,n):
        voff=k*(CLIP-FADE)
        vout=f'[v{k}]' if k<n-1 else '[vout]'; aout=f'[a{k}]' if k<n-1 else '[aout]'
        lines.append(f'{vcur}[{k}:v]xfade=transition=fade:duration={FADE}:offset={voff:.2f}{vout}')
        lines.append(f'{acur}[{k}:a]acrossfade=d={FADE}{aout}')
        vcur=vout; acur=aout
    fp=f'{D}/_part_{b}.txt'; open(fp,'w').write(';\n'.join(lines))
    out=f'{D}/beat{b}_section_crossfade_4K.mp4'
    cmd=[FF,'-y','-hide_banner','-loglevel','error']
    for p in order: cmd+=['-i',p]
    cmd+=['-filter_complex_script',fp,'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out]
    r=subprocess.run(cmd,capture_output=True,text=True)
    ok = r.returncode==0 and os.path.exists(out)
    print(b, n,'clips', 'OK' if ok else 'ERR', (os.path.getsize(out) if ok else r.stderr[-700:]), flush=True)
