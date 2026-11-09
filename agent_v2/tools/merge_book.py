# Merge raw book entry files into a sorted, de-duplicated cx_book.bin.
# usage: merge_book.py out.bin in1.bin [in2.bin ...]
import sys
import array

out, ins = sys.argv[1], sys.argv[2:]
a = array.array("Q")
for p in ins:
    with open(p, "rb") as f:
        a.frombytes(f.read())
vals = sorted(set(a))
res = array.array("Q")
conflicts = 0
prev = None
for v in vals:
    k = v >> 3
    if k == prev:
        conflicts += 1  # same position, different move: keep the first
        continue
    res.append(v)
    prev = k
with open(out, "wb") as f:
    res.tofile(f)
print(f"raw={len(a)} unique={len(res)} conflicts={conflicts} size={len(res) * 8 / 1e6:.2f} MB")
