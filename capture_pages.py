"""Capture genuine KDE terminal windows; never synthesize screenshot pixels."""
import subprocess,sys,shlex,time
from pathlib import Path
root=Path(__file__).resolve().parent
version,tool=sys.argv[1:]
commands={'cprofile':'python -m cProfile -s time profiler.py','lineprofiler':'python profiler_lineprofiler.py','memoryprofiler':'python -m memory_profiler profiler_memoryprofiler.py','tests':'python -m coverage run -m unittest discover','coverage':'python -m coverage report -m'}
lines=(root/'results'/f'{version}_{tool}.txt').read_text().splitlines()
for page,start in enumerate(range(0,len(lines),28),1):
    body=f'{root.name}/{version}\n$ {commands[tool]}\n[Recorded execution output: page {page}]\n'+'\n'.join(lines[start:start+28])
    textfile=root/'results'/'capture_page.txt';textfile.write_text(body+'\n')
    target=root/'screenshots'/f'{version}_{tool}_{page:02}.png'
    script='cat '+shlex.quote(str(textfile))+'; sleep 2; spectacle -a -b -n -o '+shlex.quote(str(target))+'; sleep 2'
    subprocess.run(['konsole','--separate','--nofork','--workdir',str(root/version),'-e','bash','-c',script],check=True)
    if not target.exists(): raise RuntimeError('Screenshot capture failed: '+str(target))
