# Opponent determinism: for each opponent, positions (move prefixes) seen 2+ times on their turn.
import json, collections, sys
g = json.load(open(sys.argv[1]))
by = collections.defaultdict(list)
for x in g:
    if x["opp"] != "weiastraia":
        by[x["opp"]].append(x)
rows = []
for opp, gs in sorted(by.items(), key=lambda t: -len(t[1])):
    seen = collections.defaultdict(collections.Counter)
    for x in gs:
        opp_parity = 1 - x["me"]  # opponent moves at plies with this parity
        for i, m in enumerate(x["moves"]):
            if i % 2 == opp_parity:
                seen[x["moves"][:i]][m] += 1
    rep = {k: v for k, v in seen.items() if sum(v.values()) >= 2}
    det = sum(1 for v in rep.values() if len(v) == 1)
    sides = collections.Counter(2 - x["me"] for x in gs)  # opponent's side (1 = first)
    firsts = collections.Counter(x["moves"][:1] if x["me"] == 1 else x["moves"][1:2] for x in gs)
    rows.append((opp, len(gs), dict(sides), len(rep), det, dict(firsts)))
    print(f"{opp[:28]:<28} games={len(gs):>2} opp_side={dict(sides)} repeated_positions={len(rep):>3} "
          f"always_same_move={det:>3} first_moves={dict(firsts)}")
