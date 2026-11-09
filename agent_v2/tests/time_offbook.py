# Worst-case live solve time: cold TT, full best-move search, positions beyond the book depth.
import sys, ctypes, time
lib = ctypes.CDLL(sys.argv[1]); lib.cx_init(23)
lib.cx_best_move.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double,
                             ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_void_p]
min_ply = int(sys.argv[2])
ts = []; timeouts = 0
for path in sys.argv[3:]:
    for line in open(path):
        seq = line.split()[0]
        if len(seq) < min_ply:
            continue
        b = [0] * 42
        for i, ch in enumerate(seq):
            c = int(ch) - 1
            r = max(r for r in range(6) if b[r * 7 + c] == 0)
            b[r * 7 + c] = 1 + i % 2
        mark = 1 + len(seq) % 2
        lib.cx_clear()
        fl = ctypes.c_int(0)
        t0 = time.perf_counter()
        lib.cx_best_move((ctypes.c_int * 42)(*b), mark, 0.8, None, ctypes.byref(fl), None)
        ts.append(time.perf_counter() - t0); timeouts += fl.value == 2
ts.sort()
print(f"ply>={min_ply}: n={len(ts)} mean={sum(ts)/len(ts)*1000:.2f}ms p99={ts[int(len(ts)*.99)]*1000:.1f}ms max={ts[-1]*1000:.1f}ms timeouts={timeouts}")
