# For each changed position: opponent replies after old vs new move -> (good replies / plausible replies).
import json, sys, importlib.util
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ps = m.PySolver(7, 6, 4)

def play(cur, mask, c):
    mv = (mask + (1 << (c * 7))) & ps.colmask[c]
    return cur ^ mask, mask | mv

def value(cur, mask, moves):  # exact score for side to move
    if moves >= 42: return 0
    if ps.win_cells(cur, mask) & ps.possible(mask): return (43 - moves) // 2
    ps.deadline = None
    return ps.solve(cur, mask, moves)

def stats(cur, mask, moves, col, cls):
    q_cur, q_mask = play(cur, mask, col)
    nl = ps.non_losing(q_cur, q_mask)
    good = pl = 0
    for c in range(7):
        if nl & ps.colmask[c]:
            pl += 1
            r_cur, r_mask = play(q_cur, q_mask, c)
            v = value(r_cur, r_mask, moves + 2)
            good += (v > 0) - (v < 0) <= cls
    return good, pl

seen = set()
for d in json.load(open(sys.argv[2])):
    if d["prefix"] in seen: continue
    seen.add(d["prefix"])
    cur = mask = 0
    for ch in d["prefix"]:
        cur, mask = play(cur, mask, int(ch) - 1)
    n = len(d["prefix"])
    s_old = -value(*play(cur, mask, d["old"] - 1), n + 1)
    s_new = -value(*play(cur, mask, d["new"] - 1), n + 1)
    cls = (s_old > 0) - (s_old < 0)
    go = stats(cur, mask, n, d["old"] - 1, cls); gn = stats(cur, mask, n, d["new"] - 1, cls)
    print(f"{d['result']} {d['opp'][:16]:<16} ply {d['ply']}: old col {d['old']} score {s_old} good/plausible {go[0]}/{go[1]}"
          f"  | new col {d['new']} score {s_new} good/plausible {gn[0]}/{gn[1]}", flush=True)
