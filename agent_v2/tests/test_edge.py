# Edge-case tests for the agent: forced wins/blocks, nearly full board, odd configs, bad input.
import sys, time, importlib.util
from kaggle_environments import utils

spec = importlib.util.spec_from_file_location("cxmain", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
agent = m.agent
S = utils.structify
CFG = S({"columns": 7, "rows": 6, "inarow": 4, "actTimeout": 2})


def board_from_moves(seq, W=7, H=6):
    b = [0] * (W * H)
    for i, ch in enumerate(seq):
        c = int(ch) - 1
        r = max(r for r in range(H) if b[r * W + c] == 0)
        b[r * W + c] = 1 + i % 2
    return b


def board_from_rows(rows):
    return [int(x) for row in rows for x in row]


fails = 0


def check(name, board, mark, expect, cfg=CFG, use_dict=False):
    global fails
    obs = {"board": board, "mark": mark, "remainingOverageTime": 60}
    obs = obs if use_dict else S(obs)
    t0 = time.perf_counter()
    a = agent(obs, cfg if not use_dict else dict(cfg))
    dt = time.perf_counter() - t0
    ok = a in expect if isinstance(expect, (set, list, tuple)) else expect(a)
    fails += not ok
    print(f"{'OK ' if ok else 'BAD'} {name:<40} -> {a} ({m._STATE['last']}, {dt*1000:.1f} ms)")


# 1. we can win now (horizontal) even though other moves look good
check("win now horizontal", board_from_rows([
    "0000000", "0000000", "0000000", "0000000", "0000020", "0111022"]), 1, {0, 4})
# 2. opponent threatens to win: must block
check("block vertical threat", board_from_rows([
    "0000000", "0000000", "0000000", "0200000", "0201000", "1201000"]), 1, {1})
# 3. win now beats blocking
check("win beats block", board_from_rows([
    "0000000", "0000000", "0000000", "0000000", "2220000", "1110000"]), 1, {3})
check("win beats block (as p2)", board_from_rows([
    "0000000", "0000000", "0000000", "0000000", "1110000", "2220001"]), 2, {3})
# 4. diagonal win
check("block diagonal threat", board_from_rows([
    "0000000", "0000000", "0002000", "0021000", "0212000", "0112100"]), 1, {0})
check("diagonal win", board_from_rows([
    "0000000", "0000000", "0002000", "0021000", "0212000", "0112101"]), 2, {0})
# 5. nearly full board: one legal column left
pat = [0, 0, 1, 1, 0, 0, 0]  # column parity pattern -> no 4-in-a-row anywhere
full = [1 + ((pat[c] + (5 - r)) % 2) for r in range(6) for c in range(7)]
full[0 * 7 + 6] = 0  # top of last column empty
check("only one legal column", full, 2, {6})
# 6. opponent has a double threat (we lose anyway) -> still a legal move
check("lost position still legal", board_from_rows([
    "0000000", "0000000", "0000000", "0000000", "0010010", "0222010"]), 1, {0, 4})
# 7. empty board as first player -> center
check("empty board", [0] * 42, 1, {3})
# 8. reply to center as second player -> center (only drawing/slowest-loss move)
check("reply to center", board_from_moves("4"), 2, {3})
# 9. plain dict inputs instead of Struct
check("dict observation", board_from_moves("44"), 1, {3}, use_dict=True)
# 10. malformed board (floating stone) -> any legal move, no crash
bad = [0] * 42
bad[0] = 1
check("malformed board", bad, 2, lambda a: a in range(7) and bad[a] == 0)
# 11. other configurations handled by the Python solver
cfg2 = S({"columns": 5, "rows": 4, "inarow": 3})
check("5x4 connect-3 win now", board_from_rows(["00000", "00000", "00000", "11022"]), 1, {2}, cfg=cfg2)
cfg3 = S({"columns": 8, "rows": 7, "inarow": 5})
check("8x7 connect-5 empty", [0] * 56, 1, lambda a: 0 <= a < 8, cfg=cfg3)
b3 = [0] * 56
for c in range(4):
    b3[6 * 8 + c] = 1
for c in range(5, 8):
    b3[6 * 8 + c] = 2
b3[5 * 8 + 7] = 2
check("8x7 connect-5 win now", b3, 1, {4}, cfg=cfg3)
print("FAILURES:", fails)
sys.exit(1 if fails else 0)
