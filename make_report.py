"""Build a Word report from actual logs using only the Python standard library."""
from pathlib import Path
import zipfile,html,json,struct,datetime
R=Path(__file__).resolve().parent
E=lambda s:html.escape(str(s),quote=True)
parts=[];images=[]
def para(s,style=None):
 parts.append('<w:p>'+('<w:pPr><w:pStyle w:val="'+style+'"/></w:pPr>' if style else '')+'<w:r><w:t xml:space="preserve">'+E(s)+'</w:t></w:r></w:p>')
def heading(s):para(s,'Heading1')
def page():parts.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
def log(path):
 if not path.exists():para('NOT COLLECTED: required package or desktop access unavailable.');return
 for line in path.read_text().splitlines():para(line,'Code')
def picture(p):
 data=p.read_bytes(); width,height=struct.unpack('>II',data[16:24]);cx=5943600;cy=int(cx*height/width)
 i=len(images)+1;images.append((p,data))
 parts.append(f'<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{i}" name="{E(p.name)}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{i}" name="{E(p.name)}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rId{i}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
para('EECE 435L • Software Tools Lab','Subtitle');para('Lab 9 — Profiling Python','Title')
para('Ali Rida Awad','Subtitle');para(R.name,'Subtitle');para('Fall 2026–2027 | '+str(datetime.date.today()))
complete=all((R/'results'/f'{v}_{t}.txt').exists() for v in ['baseline','optimized'] for t in ['lineprofiler','memoryprofiler','coverage'])
heading('Submission status')
para('Measured results and implementation are included below. '+('Required tool logs have been collected.' if complete else 'This report is incomplete for submission: line_profiler, memory_profiler, coverage.py HTML reports, and genuine terminal screenshots could not be collected in this sandbox. Package installation failed due to unavailable network/DNS; desktop capture failed because the display is inaccessible. No outputs or screenshots are invented.'))
if 'FirstName' in R.name:para('Student name remains a placeholder; rename the project folder before running complete_lab.sh. The generated report uses the folder name.')
heading('Objective and implementation')
para('The baseline preserves the handout workloads: slow_function sleeps for two seconds and sums 10,000 squares; fast_function sums 100 squares; memory_intensive_function sums 10,000,000 squares. Formatting, duplicate fragments, indentation, and the __main__ guard were corrected. Baseline and optimized versions each include all four requested Python files.')
para('The optimized version replaces only fast_function with optimized_fast_function in the workload, line profiler, memory profiler, and tests. It uses n(n−1)(2n−1)/6 for n=100, giving the same exact integer result, 328350. This changes O(n) iterations to a fixed number of integer operations for this workload. The handout’s generator-based sum is an alternative, but still performs 100 squarings. The sleep and large loop remain intact so their measured contribution is comparable.')
heading('Test design and handout corrections')
para('Tests verify exact results 333283335000, 328350, and 333333283333335000000. They also check the two-second sleep, the handout’s one-second and five-second budgets, and that main calls each workload once. main orchestration uses mocks to avoid repeating the expensive operations.')
para('The handout’s strict RSS-after > RSS-before assertion is invalid for an accumulator loop: it does not retain ten million values. The tests instead require absolute RSS change below 20 MiB, a coarse regression guard, and print the observed measurements. This does not prove peak memory or replace memory_profiler. When memory_profiler is unavailable, a clearly documented Linux /proc/self/statm fallback lets tests run. Timing uses the monotonic perf_counter clock. The five-second budget is not asserted under sys.settrace instrumentation, since tracing caused an approximately 8.6-second run during validation; correctness and memory assertions still execute.')
heading('Environment and measurement method')
p=R/'results'/'measurements.json'
if p.exists():
 m=json.loads(p.read_text());para(m['environment']);para(m['python'])
 a=m['versions']['baseline']['fast_min_seconds'];b=m['versions']['optimized']['fast_min_seconds']
 heading('Measured comparison')
 para(f'Fast function: best of seven batches, 100,000 calls per batch. Baseline {a*1e6:.6f} µs/call; optimized {b*1e6:.6f} µs/call; ratio {a/b:.2f}×. Every sample is preserved in results/measurements.json. These unprofiled microbenchmarks isolate the short function, which cProfile rounds to 0.000 seconds.')
para('cProfile is the actual standard-library profiler. Tests were run in separate Python processes. The supplementary trace output comes from Python’s standard-library trace module and is explicitly not a coverage.py report. Imports occur before tracing; therefore untraced import/definition lines are not evidence of missing function tests. Cross-process RSS baselines can differ because of interpreter allocation and address layout.')
para('The sleep sets a two-second lower bound. Removing a few microseconds from fast_function cannot materially reduce overall runtime. Single-run total differences should be treated as noise rather than attributed to this optimization. Both versions use constant auxiliary space for the accumulator; no meaningful RSS reduction is expected from removing a loop of only 100 iterations.')
for tool,label in [('cprofile','cProfile'),('tests','Unit tests'),('lineprofiler','Line profiler'),('memoryprofiler','Memory profiler'),('coverage','coverage.py'),('stdlib_coverage','Supplementary standard-library trace')]:
 page();heading(label+' — before and after')
 if tool=='cprofile':para('Interpret tottime as time in the function itself and cumtime as time including called functions. time.sleep dominates elapsed time; the large loop dominates Python computation. A zero displayed for the short function reflects output rounding.')
 if tool=='lineprofiler':para('When collected, compare time.sleep and the repeated total += i ** 2 lines. Expect 10,000,000 hits in the large-loop body. The optimized short function evaluates a fixed expression. Profiling overhead makes these durations unsuitable for direct comparison with unprofiled timings.')
 if tool=='memoryprofiler':para('When collected, compare RSS and increments line by line. The large loop repeatedly replaces its accumulator; it does not create a retained list. Small or zero increments are consistent with constant-space behavior. The default full workload is preserved and may take several minutes under line-by-line memory tracing.')
 if tool=='coverage':para('The coverage.py configuration measures profiler.py only. Individual workload tests exercise each function body, and the mocked main test covers orchestration. Import-based tests do not enter the final __main__ invocation, so the main() line under the guard is expected to be missing. Exact missing lines and percentages must come from the collected report; no percentage is claimed before it exists. Each htmlcov folder must be kept intact, including its CSS and JavaScript.')
 for v in ['baseline','optimized']:
  para(v.upper(),'Heading2');log(R/'results'/f'{v}_{tool}.txt')
  shots=sorted((R/'screenshots').glob(f'{v}_{tool}_*.png'))
  for shot in shots:picture(shot);para(shot.name,'Caption')
  if not shots and tool!='stdlib_coverage':para('Terminal screenshot: not captured in the sandbox.')
page();heading('Reproduction and remaining work')
para('From a normal KDE desktop with Internet access: run bash complete_lab.sh from this project folder. It installs the required tools into a local environment, collects both versions at the full original workload size, produces both coverage HTML directories, captures genuine Konsole windows with Spectacle, and rebuilds this Word report. Inspect the output and report before uploading. The screenshots show recorded authentic execution output and the corresponding command; long outputs are split across pages.')
para('Submit both code directories, this Word document, screenshots, and both complete htmlcov directories. Do not submit the virtual environment or __pycache__. The current results/index.html is an evidence viewer, not a replacement for coverage.py’s index.html.')
para('The scripts do not infer missing profiler timings, memory deltas, or coverage percentages. Required captures remain outstanding until complete_lab.sh runs successfully on a suitable host.')
ns='xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
doc='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document '+ns+'><w:body>'+''.join(parts)+'<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:bottom="900" w:left="900" w:right="900"/></w:sectPr></w:body></w:document>'
styles='<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="140"/></w:pPr></w:pPrDefault></w:docDefaults>'
for id,size,color in [('Title',40,'17365D'),('Subtitle',26,'526579'),('Heading1',30,'17365D'),('Heading2',25,'28727A'),('Code',14,'222222'),('Caption',18,'526579')]:
 styles+=f'<w:style w:type="paragraph" w:styleId="{id}"><w:name w:val="{id}"/><w:rPr><w:rFonts w:ascii="'+('Consolas' if id=='Code' else 'Calibri')+f'"/><w:sz w:val="{size}"/><w:color w:val="{color}"/></w:rPr></w:style>'
styles+='</w:styles>'
rel='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
for i,(p,data) in enumerate(images,1):rel+=f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{i}.png"/>'
rel+='</Relationships>'
with zipfile.ZipFile(R/(R.name+'.docx'),'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
 z.writestr('word/document.xml',doc);z.writestr('word/styles.xml',styles);z.writestr('word/_rels/document.xml.rels',rel)
 for i,(p,data) in enumerate(images,1):z.writestr(f'word/media/image{i}.png',data)
entries=[]
for p in sorted((R/'results').glob('*.txt')):entries.append('<h2>'+E(p.name)+'</h2><pre>'+E(p.read_text())+'</pre>')
(R/'results'/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Lab 9 measured evidence</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto}pre{background:#eef2f6;padding:20px;overflow:auto}</style><h1>Lab 9 — measured evidence</h1><p>This evidence viewer is not a coverage.py HTML report. See the Word report for limitations.</p>'+''.join(entries))
print('Created',R/(R.name+'.docx'))
