"""Offline fallback: stdlib trace, explicitly not coverage.py."""
import trace,unittest,sys,dis,types,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import profiler
runner=trace.Trace(count=True,trace=False,ignoredirs=[sys.prefix,sys.exec_prefix])
suite=unittest.defaultTestLoader.discover('.',pattern='test_profiler.py')
result=runner.runfunc(unittest.TextTestRunner(verbosity=2).run,suite)
counts=runner.results().counts
filename=str(Path(profiler.__file__).resolve())
def lines(code):
    found={line for _,line in dis.findlinestarts(code) if line>0}
    for constant in code.co_consts:
        if isinstance(constant,types.CodeType): found.update(lines(constant))
    return found
executable=lines(compile(Path(filename).read_text(),filename,'exec'))
# Module import happened before tracing, so distinguish import/definition lines.
covered={n for (f,n),c in counts.items() if str(Path(f).resolve())==filename and c}
print('TOOL: Python standard-library trace (not coverage.py)')
print('Traced test execution; imports occurred before tracing.')
print('Executed workload lines:',sorted(covered))
print('Untraced executable lines:',sorted(executable-covered))
Path('stdlib_trace.json').write_text(json.dumps({'executed':sorted(covered),'untraced':sorted(executable-covered)},indent=2))
sys.exit(not result.wasSuccessful())
