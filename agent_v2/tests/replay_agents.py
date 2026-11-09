# Replay recorded second-player games: compare old vs new agent choice at every our-turn position.
import json, sys, importlib.util, collections

class Struct(dict):
    __getattr__ = dict.get

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.agent

new, old = load(sys.argv[1], "new"), load(sys.argv[2], "old")
games = json.load(open(sys.argv[3]))
cfg = Struct(columns=7, rows=6, inarow=4)
stat = collections.Counter(); diffs = []; recorded_mismatch = 0
for g in games:
    if g["side"] != 2 or g["opp"] == "weiastraia":
        continue
    b = [0] * 42
    for i, ch in enumerate(g["moves"]):
        c = int(ch) - 1
        if i % 2 == 1:
            obs = Struct(board=list(b), mark=2)
            a_old, a_new = old(obs, cfg), new(obs, cfg)
            recorded_mismatch += a_old != c
            stat[(g["result"], a_new == a_old)] += 1
            if a_new != a_old:
                diffs.append({"id": g["id"], "result": g["result"], "opp": g["opp"], "ply": i + 1,
                              "prefix": g["moves"][:i], "old": a_old + 1, "new": a_new + 1})
        r = max(r for r in range(6) if b[r * 7 + c] == 0)
        b[r * 7 + c] = 1 + i % 2
print("old agent reproduces recorded moves; mismatches:", recorded_mismatch)
for (res, same), n in sorted(stat.items()):
    print(f"games={res} {'same' if same else 'DIFFERENT'}: {n} positions")
json.dump(diffs, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
for d in diffs:
    print(d)
