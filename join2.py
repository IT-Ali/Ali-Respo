"""Crossfade-join clip A then clip B (video xfade + audio acrossfade). Measures A's
duration automatically. Usage: join2.py A.mp4 B.mp4 OUT.mp4 [fade]"""
import subprocess, sys, re, os
FF=r'D:/Ue/UE_5.8/socrates_fix/work/bin/ffmpeg.exe'
def dur(f):
    o=subprocess.run([FF,'-i',f],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',o); h,mi,s=m.groups(); return int(h)*3600+int(mi)*60+float(s)
a,b,out=sys.argv[1],sys.argv[2],sys.argv[3]
FADE=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
off=dur(a)-FADE
cmd=[FF,'-y','-hide_banner','-loglevel','error','-i',a,'-i',b,
 '-filter_complex',f'[0:v][1:v]xfade=transition=fade:duration={FADE}:offset={off:.3f}[vo];[0:a][1:a]acrossfade=d={FADE}[ao]',
 '-map','[vo]','-map','[ao]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',out]
r=subprocess.run(cmd,capture_output=True,text=True)
print('OK' if r.returncode==0 else r.stderr[-800:], os.path.getsize(out) if (os.path.exists(out) and r.returncode==0) else '')
