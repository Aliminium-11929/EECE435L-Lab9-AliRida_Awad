"""Collect real built-in measurements; these do not replace the named lab tools."""
from pathlib import Path
import subprocess,sys,json,timeit,importlib.util,platform,trace,os
ROOT=Path(__file__).resolve().parent
out=ROOT/'results';out.mkdir(exist_ok=True)
summary={'environment':platform.platform(),'python':sys.version,'versions':{}}
for version in ('baseline','optimized'):
    d=ROOT/version
    for name,command in [('cprofile',[sys.executable,'-m','cProfile','-s','time','profiler.py']),('tests',[sys.executable,'-m','unittest','-v','test_profiler'])]:
        result=subprocess.run(command,cwd=d,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/f'{version}_{name}.txt').write_text(f'Project: {ROOT.name}/{version}\n$ '+ ' '.join(command)+'\n'+result.stdout+f'\nExit status: {result.returncode}\n')
        if result.returncode: raise RuntimeError(result.stdout)
    spec=importlib.util.spec_from_file_location('workload',d/'profiler.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    f=m.fast_function if version=='baseline' else m.optimized_fast_function
    samples=timeit.repeat(f,number=100000,repeat=7)
    summary['versions'][version]={'fast_seconds_per_call':[s/100000 for s in samples], 'fast_min_seconds':min(samples)/100000}
    # Standard-library trace records which workload statements tests execute.
    result=subprocess.run([sys.executable,str(ROOT/'trace_tests.py')],cwd=d,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/f'{version}_stdlib_coverage.txt').write_text(result.stdout)
    if result.returncode: raise RuntimeError(result.stdout)
(out/'measurements.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
