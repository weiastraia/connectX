# Check sampled book entries against an independent full analysis (all 7 children solved).
# usage: verify_book.py <stage_dir> <samples> [min_ply]
import sys, os, array, random, ctypes, collections

d, n = sys.argv[1], int(sys.argv[2])
min_ply = int(sys.argv[3]) if len(sys.argv) > 3 else 0
lib = ctypes.CDLL(os.path.join(d, "cx_solver_v2.so"))
lib.cx_init(25)
book = array.array("Q")
book.frombytes(open(os.path.join(d, "cx_book.bin"), "rb").read())


def decode(key):
    cur = mask = 0
    for c in range(7):
        k = (key >> (c * 7)) & 0x7F
        h = (k + 1).bit_length() - 1
        m = ((1 << h) - 1)
        mask |= m << (c * 7)
        cur |= (k - m) << (c * 7)
    return cur, mask


plies = collections.Counter()
for v in book:
    _, mask = decode(v >> 3)
    plies[bin(mask).count("1")] += 1
print("entries per ply:", dict(sorted(plies.items())))

random.seed(7)
idx = [i for i in range(len(book)) if bin(decode(book[i] >> 3)[1]).count("1") >= min_ply]
sample = random.sample(idx, min(n, len(idx)))
bad = 0
for i in sample:
    v = book[i]
    cur, mask = decode(v >> 3)
    mv = v & 7
    moves = bin(mask).count("1")
    mark = 1 + moves % 2
    board = [0] * 42
    for c in range(7):
        for h in range(6):
            b = 1 << (c * 7 + h)
            if mask & b:
                board[(5 - h) * 7 + c] = mark if cur & b else 3 - mark
    arr = (ctypes.c_int * 42)(*board)
    sc = (ctypes.c_int * 7)()
    lib.cx_analyze(arr, mark, sc)
    best = max(sc)
    if sc[mv] != best:
        bad += 1
        print("BAD ply", moves, "book", mv, "scores", list(sc))
print(f"checked {len(sample)} entries (ply>={min_ply}), wrong={bad}")
sys.exit(1 if bad else 0)
