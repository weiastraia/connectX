# From each changed key position (our turn, we are P2): play N games old vs new with the same
# opponent model (perfect solver + p plausible random), paired seeds. Report W/D/L per agent.
import sys, json, random, importlib.util, os
sys.argv_saved = list(sys.argv)
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

class Struct(dict):
    __getattr__ = dict.get

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.agent

from arena import winner_after  # noqa: E402  (arena.main() is guarded below)

new, old = load(sys.argv[1], "new"), load(sys.argv[2], "old")
perfect = load(os.path.join(here, "..", "build", "old_agent", "main.py"), "perfect")
diffs = json.load(open(sys.argv[3])); n = int(sys.argv[4]); p = float(sys.argv[5])
mode = sys.argv[6] if len(sys.argv) > 6 else "eps"  # eps | mix:<depth>
import ctypes
eng = ctypes.CDLL(os.path.join(here, "..", "build", "opp_engine.so"))
cfg = Struct(columns=7, rows=6, inarow=4)

def opp_move(obs, rnd):
    if rnd.random() >= p:
        return perfect(obs, cfg)
    if mode.startswith("mix"):
        return eng.opp_move((ctypes.c_int * 42)(*obs.board), obs.mark, int(mode.split(":")[1]), rnd.getrandbits(31))
    legal = [c for c in range(7) if obs.board[c] == 0]
    safe = []
    for c in legal:
        bb = list(obs.board)
        if winner_after(bb, c, obs.mark):
            return c
        if not any(bb[o] == 0 and winner_after(list(bb), o, 3 - obs.mark) for o in range(7)):
            safe.append(c)
    return rnd.choice(safe or legal)

def play(agent, prefix, seed):
    rnd = random.Random(seed)
    b = [0] * 42
    for i, ch in enumerate(prefix):
        winner_after(b, int(ch) - 1, 1 + i % 2)
    for ply in range(len(prefix), 42):
        mark = 1 + ply % 2
        obs = Struct(board=list(b), mark=mark)
        c = agent(obs, cfg) if mark == 2 else opp_move(obs, rnd)
        if winner_after(b, c, mark):
            return "W" if mark == 2 else "L"
    return "D"

tot = {"old": [0, 0, 0], "new": [0, 0, 0]}
seen = set()
for d in diffs:
    if d["prefix"] in seen:
        continue
    seen.add(d["prefix"])
    row = {}
    for name, ag in (("old", old), ("new", new)):
        r = [play(ag, d["prefix"], 1000 + k) for k in range(n)]
        row[name] = [r.count("W"), r.count("D"), r.count("L")]
        for i in range(3):
            tot[name][i] += row[name][i]
    print(f"{d['result']} ply {d['ply']} {d['prefix']}: old W/D/L={row['old']}  new W/D/L={row['new']}", flush=True)
print("TOTAL old W/D/L =", tot["old"], " new W/D/L =", tot["new"])
