#!/bin/sh
# Assemble the submission: main.py + solver libraries + opening book + trap table, at the archive root.
set -e
cd "$(dirname "$0")"
S=build/stage
rm -rf $S && mkdir -p $S submission
cp src/main.py build/cx_solver_v1.so build/cx_solver_v2.so $S/
cp book/cx_book_v2.bin $S/cx_book.bin
cp book/traps.bin $S/cx_traps.bin
tar -C $S -czf submission/submission.tar.gz main.py cx_solver_v1.so cx_solver_v2.so cx_book.bin cx_traps.bin
ls -la submission/submission.tar.gz
tar -tzvf submission/submission.tar.gz
