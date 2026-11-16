# Lab 9: Python profiling

The baseline and optimized implementations are complete. The Word report contains
real cProfile, unittest, microbenchmark, and standard-library trace results.

**Not submission-ready:** the sandbox has no network access to install
line_profiler, memory_profiler, or coverage, and cannot access the desktop for
screenshots. The required profiler results, coverage.py HTML, and terminal
screenshots remain outstanding. No synthetic screenshots are supplied.

Student: **Ali Rida Awad**. Project: `lab9_AliRida_Awad`.

## Finish collecting the required evidence

1. Open this project folder in a normal desktop terminal.
2. From a normal KDE desktop session with Internet access, run:

   ```bash
   bash complete_lab.sh
   ```

   The memory profiler preserves all 10,000,000 iterations and may take several
   minutes. Konsole and Spectacle are used to capture actual terminal windows
   showing authentic recorded execution output; long outputs use multiple pages.
3. Inspect the regenerated Word report and screenshots. Open
   `baseline/htmlcov/index.html` and `optimized/htmlcov/index.html`.
4. Submit both code folders, the Word report, screenshots, and both complete
   htmlcov folders. Exclude the virtual environment and `__pycache__` folders.

## Files

- `baseline/`: original workloads with corrected handout formatting.
- `optimized/`: the short loop replaced with the exact sum-of-squares formula.
- `results/`: actual measurements and an HTML evidence viewer. Its index.html
  is explicitly **not** coverage.py output.
- `collect_available.py`: offline cProfile, tests, microbenchmark, stdlib trace.
- `make_report.py`: generates the Word report from logs and available screenshots.
- `complete_lab.sh`: collects the required installed-tool outputs and screenshots.

Run offline verification with `python collect_available.py`; rebuild the report
with `python make_report.py`. Python 3.14 was used here.

## Deliberate corrections

The handout's strict memory-increase test is unsuitable for a constant-space
accumulator. The test checks exact output and a 20 MiB RSS-change bound instead.
RSS is measured with memory_profiler when installed, otherwise with Linux procfs.
The five-second timing budget is disabled under sys.settrace instrumentation,
whose overhead would otherwise cause false failures. This is stated in the
report. The trace fallback does not claim to be coverage.py.
