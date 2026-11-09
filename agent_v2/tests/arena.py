# Fast arena: agent A vs opponent, alternating sides; reports W/D/L per side and A's move times.
# opponent: path/to/main.py | engine:<depth> | random
# usage: arena.py <agentA main.py> <opponent> <games> [seed]
import sys, time, random, ctypes, importlib.util, os


class Struct(dict):
    __getattr__ = dict.get


def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def winner_after(b, col, mark):
    r = max(r for r in range(6) if b[r * 7 + col] == 0)
    b[r * 7 + col] = mark
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        n = 1
        for sgn in (1, -1):
            rr, cc = r + sgn * dr, col + sgn * dc
            while 0 <= rr < 6 and 0 <= cc < 7 and b[rr * 7 + cc] == mark:
                n += 1
                rr += sgn * dr
                cc += sgn * dc
        if n >= 4:
            return True
    return False


def main():
    a_path, opp, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rnd = random.Random(seed)
    A = load_agent(a_path, "agentA")
    cfg = Struct(columns=7, rows=6, inarow=4, actTimeout=2)
    if opp.startswith("engine:"):
        depth = int(opp.split(":")[1])
        lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "opp_engine.so"))
        B = lambda obs, cfg: lib.opp_move((ctypes.c_int * 42)(*obs.board), obs.mark, depth, rnd.getrandbits(31))
    elif opp.startswith("eps:") or opp.startswith("mix:"):
        # near-perfect opponent: old perfect agent, but with prob p a plausible random move (eps)
        # or a depth-d engine move (mix)
        parts = opp.split(":")
        p = float(parts[1])
        P = load_agent(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "old_agent",
                                    "main.py"), "perfect")
        lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "opp_engine.so"))

        def B(obs, cfg):
            if rnd.random() >= p:
                return P(obs, cfg)
            if parts[0] == "mix":
                return lib.opp_move((ctypes.c_int * 42)(*obs.board), obs.mark, int(parts[2]), rnd.getrandbits(31))
            # plausible = does not allow an immediate reply win, unless nothing else
            legal = [c for c in range(7) if obs.board[c] == 0]
            safe = []
            for c in legal:
                bb = list(obs.board)
                if winner_after(bb, c, obs.mark):
                    return c
                if not any(bb[o] == 0 and winner_after(list(bb), o, 3 - obs.mark) for o in range(7)):
                    safe.append(c)
            return rnd.choice(safe or legal)
    elif opp == "random":
        B = lambda obs, cfg: rnd.choice([c for c in range(7) if obs.board[c] == 0])
    else:
        B = load_agent(opp, "agentB")
    res = {1: [0, 0, 0], 2: [0, 0, 0]}  # A's side -> [W, D, L]
    times = []
    lens = []
    for g in range(n):
        a_side = 1 + g % 2
        b = [0] * 42
        result = 1  # draw index
        for ply in range(42):
            mark = 1 + ply % 2
            obs = Struct(board=list(b), mark=mark, remainingOverageTime=60, step=ply)
            if mark == a_side:
                t = time.perf_counter()
                c = A(obs, cfg)
                times.append(time.perf_counter() - t)
            else:
                c = B(obs, cfg)
            if not (isinstance(c, int) and 0 <= c < 7 and b[c] == 0):
                result = 2 if mark == a_side else 0  # illegal move loses
                break
            if winner_after(b, c, mark):
                result = 0 if mark == a_side else 2
                break
        lens.append(ply + 1)
        res[a_side][result] += 1
    times.sort()
    tot = [res[1][i] + res[2][i] for i in range(3)]
    print(f"{os.path.basename(os.path.dirname(a_path))} vs {opp}: W/D/L={tot} as P1={res[1]} as P2={res[2]} "
          f"avg_len={sum(lens)/len(lens):.1f} moves={len(times)} mean={sum(times)/len(times)*1000:.2f}ms "
          f"max={times[-1]*1000:.1f}ms", flush=True)


if __name__ == "__main__":
    main()
