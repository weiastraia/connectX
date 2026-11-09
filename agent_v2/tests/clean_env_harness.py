# Load main.py exactly like kaggle_environments.agent.get_last_callable (no __file__, exec into {})
# and play self-play games, checking legality and timing. Needs only the standard library.
import os, sys, time, random


class Struct(dict):
    __getattr__ = dict.get


def load(path):
    raw = open(path).read()
    env = {}
    sys.path.append(os.path.dirname(path))
    exec(compile(raw, path, "exec"), env)
    sys.path.pop()
    return [v for v in env.values() if callable(v)][-1]


def winner(b, W=7, H=6):
    for r in range(H):
        for c in range(W):
            p = b[r * W + c]
            if not p:
                continue
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if all(0 <= r + i * dr < H and 0 <= c + i * dc < W and b[(r + i * dr) * W + c + i * dc] == p
                       for i in range(4)):
                    return p
    return 0


def main():
    path = sys.argv[1]
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.perf_counter()
    agent = load(path)
    st = agent.__globals__["_STATE"]
    print("agent callable:", agent.__name__, f"load {time.perf_counter() - t0:.3f}s", "lib:", st["lib"] is not None, "book:", 0 if st["book"] is None else len(st["book"]))
    cfg = Struct(columns=7, rows=6, inarow=4, actTimeout=2, timeout=2, agentTimeout=60)
    worst = 0.0
    results = []
    rnd = random.Random(1)
    for g in range(games):
        b = [0] * 42
        # game 0: pure self-play; others: we play side `me`, opponent is 30% random / 70% solver
        me = 1 + g % 2
        for ply in range(42):
            mark = 1 + ply % 2
            t = time.perf_counter()
            if g > 0 and mark != me and rnd.random() < 0.3:
                a = rnd.choice([c for c in range(7) if b[c] == 0])
            else:
                a = agent(Struct(board=list(b), mark=mark, remainingOverageTime=60), cfg)
                if g == 0 or mark == me:
                    worst = max(worst, time.perf_counter() - t)
            assert isinstance(a, int) and 0 <= a < 7 and b[a] == 0, ("illegal", a)
            r = max(r for r in range(6) if b[r * 7 + a] == 0)
            b[r * 7 + a] = mark
            w = winner(b)
            if w:
                results.append("win" if g == 0 or w == me else "LOSS")
                break
        else:
            results.append(0)
    print("winners per game:", results, f"worst move {worst:.3f}s")


main()
