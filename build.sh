#!/bin/bash
mkdir -p dist

for file in "src/"*; do
  if [[ -f "$file" ]]; then
    outfile="dist/$(basename $file .co).py"
    echo "$file -> $outfile"
    python bootstrap/coastc.py $file $outfile
  fi
done