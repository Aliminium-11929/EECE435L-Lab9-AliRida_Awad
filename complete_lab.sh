#!/usr/bin/env bash
# Run from a normal KDE desktop session with Internet access.
set -euo pipefail
cd -- "$(dirname -- "$0")"
project_root="$PWD"
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
py="$project_root/.venv/bin/python"
mkdir -p results screenshots
"$py" -m pip freeze > results/package_versions.txt
"$py" collect_available.py
for version in baseline optimized; do
  cd "$project_root/$version"
  "$py" -m cProfile -o profile.pstats profiler.py
  "$py" -m cProfile -s time profiler.py > "../results/${version}_cprofile.txt" 2>&1
  "$py" profiler_lineprofiler.py > "../results/${version}_lineprofiler.txt" 2>&1
  # This traces twenty million loop events and may take several minutes.
  "$py" -m memory_profiler profiler_memoryprofiler.py > "../results/${version}_memoryprofiler.txt" 2>&1
  "$py" -m coverage run -m unittest discover > "../results/${version}_tests.txt" 2>&1
  "$py" -m coverage report -m > "../results/${version}_coverage.txt"
  "$py" -m coverage html
  "$py" -m coverage json -o coverage.json
  cd "$project_root"
done
if command -v konsole >/dev/null && command -v spectacle >/dev/null; then
  for version in baseline optimized; do
    for tool in cprofile lineprofiler memoryprofiler tests coverage; do
      # A real Konsole displays the recorded command and its authentic output.
      # Capture multiple pages for reports that exceed the terminal height.
      "$py" capture_pages.py "$version" "$tool"
    done
  done
else
  echo 'Open the results in a terminal and capture screenshots; Konsole/Spectacle are unavailable.'
fi
"$py" make_report.py
