# Trap table: our moves on recorded second-player games before the opponent's first error.
# Output entries (canonical_key << 3 | col_in_canonical_frame), little-endian uint64.
import json, sys, array

def key_of(moves):
    cur = mask = 0
    for ch in moves:
        c = int(ch) - 1
        m = (mask + (1 << (c * 7))) & (0x3F << (c * 7))
        cur ^= mask
        mask |= m
    return cur + mask

def mirror(k):
    return sum(((k >> (c * 7)) & 0x7F) << ((6 - c) * 7) for c in range(7))

games = json.load(open(sys.argv[1]))
tr = {}
for g in games:
    if g["side"] != 2 or not g["opp_errors"]:
        continue
    first_err = min(e[0] for e in g["opp_errors"])
    for i in range(1, first_err, 2):  # our plies (odd) before the error
        k = key_of(g["moves"][:i])
        col = int(g["moves"][i]) - 1
        mk = mirror(k)
        ck, cc = (mk, 6 - col) if mk < k else (k, col)
        if ck in tr and tr[ck] != cc:
            print("conflict at", g["moves"][:i])
        tr[ck] = cc
a = array.array("Q", sorted(ck << 3 | cc for ck, cc in tr.items()))
a.tofile(open(sys.argv[2], "wb"))
print("trap entries:", len(a))
