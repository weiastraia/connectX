# Classify games using exact per-position evaluations (WDL + exact score from ply>=10).
import json, sys, collections
games = {str(x["id"]): x for x in json.load(open(sys.argv[1]))}
ev = collections.defaultdict(dict)
for line in open(sys.argv[2]):
    p = line.split()
    if p[2] == "WINMOVE":
        continue
    ev[p[0]][int(p[1])] = (int(p[2]), int(p[3]))
out = []
for gid, x in games.items():
    e = ev[gid]
    mv = x["moves"]
    n = len(mv)
    # P1-view WDL before each move
    v1 = [e[i][0] * (1 if i % 2 == 0 else -1) for i in range(n) if i in e]
    errs = []  # (ply, mover, P1-view before, after)
    inacc = []  # same WDL but worse exact score
    for i in range(n - 1):
        if i + 1 not in e:
            continue
        mover = 1 + i % 2
        b, a = v1[i], v1[i + 1]
        if (mover == 1 and a < b) or (mover == 2 and a > b):
            errs.append((i, mover, b, a))
        sb, sa = e[i][1], e[i + 1][1]
        if sb != 99 and sa != 99 and sa != -sb and (b == v1[i + 1]):
            inacc.append((i, mover, sb, -sa))
    my = x["side"]
    out.append({"id": int(gid), "side": my, "opp": x["opp"], "moves": mv,
                "result": {1: "W", -1: "L", 0: "D"}[x["rewards"][x["me"]]],
                "my_errors": [t for t in errs if t[1] == my], "opp_errors": [t for t in errs if t[1] != my],
                "my_inacc": [t for t in inacc if t[1] == my], "opp_inacc": [t for t in inacc if t[1] != my],
                "start_v1": v1[0]})
json.dump(out, open(sys.argv[3], "w"), indent=0)
c = collections.Counter()
for o in out:
    if o["opp"] == "weiastraia":
        continue
    k = (o["side"], o["result"], "opp_erred" if o["opp_errors"] else "opp_perfect")
    c[k] += 1
for k, v in sorted(c.items()):
    print(k, v)
print("our WDL errors:", sum(len(o["my_errors"]) for o in out), " our exact-score inaccuracies:", sum(len(o["my_inacc"]) for o in out))
for o in out:
    if o["side"] == 2 and o["opp_errors"]:
        print(o["id"], o["result"], o["opp"][:20], "opp errors (ply,mover,before,after):", o["opp_errors"], "moves:", o["moves"])
