# Check the pure-Python fallback solver and the ctypes path against known scores.
import sys, time, importlib.util
spec = importlib.util.spec_from_file_location("cxmain", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ps = m.PySolver(7, 6, 4)
lib = m._STATE["lib"]
import ctypes
for path, n in [("tests/Test_L3_R1", 200), ("tests/Test_L2_R1", 60), ("tests/Test_L2_R2", 15)]:
    bad = 0; tmax = 0; badc = 0
    lines = open(path).read().split("\n")[:n]
    for line in lines:
        seq, exp = line.split(); exp = int(exp)
        cur = mask = 0; moves = 0
        for ch in seq:
            c = int(ch) - 1
            mv = (mask + (1 << (c * 7))) & ps.colmask[c]
            cur ^= mask; mask |= mv; moves += 1
        ps.tt.clear(); ps.deadline = None
        t0 = time.perf_counter()
        s = (43 - moves) // 2 if ps.win_cells(cur, mask) & ps.possible(mask) else ps.solve(cur, mask, moves)
        tmax = max(tmax, time.perf_counter() - t0)
        bad += s != exp
        if lib is not None:
            badc += lib.cx_solve_moves(seq.encode()) != exp
    print(f"{path}: n={len(lines)} py_mismatch={bad} py_max={tmax:.2f}s cpp_mismatch={badc} (lib={'yes' if lib else 'no'})")
