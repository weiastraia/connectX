# For our-turn positions in recorded second-player games: does the new policy pick a different move?
import json, sys, ctypes, time, collections
lib = ctypes.CDLL(sys.argv[1]); lib.cx_init(26)
lib.cx_best_move2.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_double, ctypes.c_int,
                              ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_void_p]
games = json.load(open(sys.argv[2]))
min_ply = int(sys.argv[3])
stats = collections.Counter(); diffs = []; tmax = 0
for g in games:
    if g["side"] != 2 or g["opp"] == "weiastraia":
        continue
    b = [0] * 42
    for i, ch in enumerate(g["moves"]):
        c = int(ch) - 1
        if i % 2 == 1 and i >= min_ply:
            sc, fl = ctypes.c_int(), ctypes.c_int()
            arr = (ctypes.c_int * 42)(*b)
            t = time.perf_counter()
            new = lib.cx_best_move2(arr, 2, 0.0, -1, 1, ctypes.byref(sc), ctypes.byref(fl), None)
            tmax = max(tmax, time.perf_counter() - t)
            cls = "lost" if sc.value < 0 else "draw" if sc.value == 0 else "win"
            stats[(g["result"], cls, "same" if new == c else "diff")] += 1
            if new != c:
                diffs.append((g["id"], g["result"], i, g["moves"][:i], c + 1, new + 1, sc.value))
        r = max(r for r in range(6) if b[r * 7 + c] == 0)
        b[r * 7 + c] = 1 + i % 2
for k, v in sorted(stats.items()):
    print(k, v)
print("max time per position (no limit):", round(tmax, 3), "s")
json.dump(diffs, open(sys.argv[4], "w"))
for d in diffs[:15]:
    print(d)
