# Derive every number used in the slides from files in this repository.
# usage (from repo root): python3 presentation/tools/make_numbers.py
# writes presentation/numbers.json and presentation/NUMBERS.md
import array, collections, io, json, os, re, tarfile

A = "agent_v2"
P = "presentation"
N = {}      # key -> value
SRC = {}    # key -> (source file, how)


def put(key, value, src, how):
    N[key] = value
    SRC[key] = (src, how)


# ---------- 168 recorded games ----------
games = json.load(open(f"{A}/analysis/games.json"))
cls = json.load(open(f"{A}/analysis/classified_exact.json"))
g_src = f"{A}/analysis/games.json"
c_src = f"{A}/analysis/classified_exact.json"
put("games_total", len(games), g_src, "len(list)")
selfplay = [g for g in games if g["opp"] == "weiastraia"]
real = [g for g in games if g["opp"] != "weiastraia"]
put("games_selfplay", len(selfplay), g_src, 'opp == "weiastraia" (Kaggle validation episode)')
put("games_real", len(real), g_src, "games_total - games_selfplay")


def wdl(gs):
    r = collections.Counter({1: "W", 0: "D", -1: "L"}[g["rewards"][g["me"]]] for g in gs)
    return [r["W"], r["D"], r["L"]]


p1 = [g for g in real if g["side"] == 1]
p2 = [g for g in real if g["side"] == 2]
put("p1_games", len(p1), g_src, "side == 1, self-play excluded")
put("p1_wdl", wdl(p1), g_src, "rewards[me] for side == 1")
put("p2_games", len(p2), g_src, "side == 2, self-play excluded")
put("p2_wdl", wdl(p2), g_src, "rewards[me] for side == 2")
put("status_not_done", sum(1 for g in games if g["final_status"] != ["DONE", "DONE"]), g_src,
    "games whose final status is not DONE/DONE")
put("my_min_overage", min(g["my_min_overage"] for g in games), g_src,
    "min remainingOverageTime of our agent over all steps (60 = never used)")
put("opponents_distinct", len({g["opp"] for g in real}), g_src, "distinct opponent names")
p1_len = sorted(len(g["moves"]) for g in p1)
put("p1_win_len_min", p1_len[0], g_src, "shortest first-player game (moves)")
put("p1_win_len_max", p1_len[-1], g_src, "longest first-player game (moves)")

creal = [o for o in cls if o["opp"] != "weiastraia"]
put("my_wdl_errors", sum(len(o["my_errors"]) for o in cls), c_src, "our moves that lowered the win/draw/loss value")
put("my_score_inacc", sum(len(o["my_inacc"]) for o in cls), c_src, "our moves that were not exact-score optimal")
loss2 = [o for o in creal if o["side"] == 2 and o["result"] == "L"]
put("p2_losses", len(loss2), c_src, "side 2, result L")
put("p2_loss_lengths", sorted(set(len(o["moves"]) for o in loss2)), c_src, "set of game lengths of those losses")
put("p2_loss_opp_errors", sum(len(o["opp_errors"]) for o in loss2), c_src,
    "opponent moves that lowered their win/draw/loss value in those losses")
put("p2_loss_opp_inacc", sum(len(o["opp_inacc"]) for o in loss2), c_src,
    "opponent moves that were not the fastest win in those losses")
put("p2_loss_opp_moves", sum((len(o["moves"]) + 1) // 2 for o in loss2), c_src,
    "total opponent moves in those losses")
put("p2_loss_opponents", len({o["opp"] for o in loss2}), c_src, "distinct opponents in those losses")
nonloss2 = [o for o in creal if o["side"] == 2 and o["result"] != "L"]
put("p2_nonloss", len(nonloss2), c_src, "side 2, result W or D")
put("p2_nonloss_with_opp_error", sum(1 for o in nonloss2 if o["opp_errors"]), c_src,
    "of those, games where the opponent made a value-losing move")
put("p2_nonloss_444444", sum(1 for o in nonloss2 if o["moves"].startswith("444444")), c_src,
    "of those, games starting with six stones in the centre column")
put("p2_nonloss_opponents", len({o["opp"] for o in nonloss2}), c_src, "distinct opponents in those games")
first_err = sorted(min(e[0] for e in o["opp_errors"]) + 1 for o in nonloss2)
put("p2_first_error_moves", first_err, c_src, "move number of the opponent's first error in each game")
put("p2_perfect_share_pct", round(100 * len(loss2) / len(p2), 1), c_src, "p2_losses / p2_games")
put("p2_draws", sum(1 for o in nonloss2 if o["result"] == "D"), c_src, "side 2, result D")
put("p2_wins", sum(1 for o in nonloss2 if o["result"] == "W"), c_src, "side 2, result W")

# positions evaluated
ev_src = f"{A}/analysis/eval_exact.txt"
ev_lines = [l for l in open(ev_src) if "WINMOVE" not in l]
put("positions_evaluated", len(ev_lines), ev_src, "lines (one per position of every game)")

# opponent determinism
seen = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for g in real:
    for i, m in enumerate(g["moves"]):
        if i % 2 == 1 - g["me"]:
            seen[g["opp"]][g["moves"][:i]][m] += 1
det = {}
for opp, d in seen.items():
    rep = [v for v in d.values() if sum(v.values()) >= 2]
    det[opp] = (sum(1 for v in rep if len(v) == 1), len(rep))
cnt = collections.Counter(g["opp"] for g in real)
top = cnt.most_common(8)
rows = []
for opp, n in top:
    w1 = wdl([g for g in real if g["opp"] == opp and g["side"] == 1])
    w2 = wdl([g for g in real if g["opp"] == opp and g["side"] == 2])
    rows.append({"opp": opp, "games": n, "p1": w1, "p2": w2, "same": det[opp][0], "rep": det[opp][1]})
put("top_opponents", rows, g_src, "8 most frequent opponents; same/rep = repeated positions on their turn "
    "where they always played the same move")
put("det_same_total", sum(v[0] for v in det.values()), g_src, "sum of 'same' over all opponents")
put("det_rep_total", sum(v[1] for v in det.values()), g_src, "sum of 'rep' over all opponents")
put("opponents_3plus", sum(1 for v in cnt.values() if v >= 3), g_src, "opponents met 3 times or more")


# ---------- opening books ----------
def load_book_bytes(b):
    a = array.array("Q")
    a.frombytes(b)
    return a


def plies(a):
    c = collections.Counter()
    for v in a:
        key = v >> 3
        n = 0
        for col in range(7):
            k = (key >> (col * 7)) & 0x7F
            n += (k + 1).bit_length() - 1
        c[n] += 1
    return c


v1_tar = f"{A}/submission/submission_v1.tar.gz"
v2_tar = f"{A}/submission/submission_v2.tar.gz"
with tarfile.open(v1_tar) as t:
    b1 = t.extractfile("cx_book.bin").read()
    v1_names = sorted(t.getnames())
with tarfile.open(v2_tar) as t:
    b2 = t.extractfile("cx_book.bin").read()
    tr = t.extractfile("cx_traps.bin").read()
    v2_names = sorted(t.getnames())
a1, a2 = load_book_bytes(b1), load_book_bytes(b2)
pl1 = plies(a1)
put("book_v7_entries", len(a1), v1_tar, "cx_book.bin size / 8")
put("book_v7_mb", round(len(b1) / 1e6, 1), v1_tar, "cx_book.bin bytes / 1e6")
put("book_v7_p1_plies", [min(p for p in pl1 if p % 2 == 0), max(p for p in pl1 if p % 2 == 0)], v1_tar,
    "stones on board in entries where the first player moves")
put("book_v7_p2_plies", [min(p for p in pl1 if p % 2 == 1), max(p for p in pl1 if p % 2 == 1)], v1_tar,
    "stones on board in entries where the second player moves")
put("book_v7_p1_entries", sum(n for p, n in pl1.items() if p % 2 == 0), v1_tar, "entries with even stone count")
put("book_v7_p2_entries", sum(n for p, n in pl1.items() if p % 2 == 1), v1_tar, "entries with odd stone count")
put("book_v8_entries", len(a2), v2_tar, "cx_book.bin size / 8")
d1 = {v >> 3: v & 7 for v in a1}
d2 = {v >> 3: v & 7 for v in a2}
common = set(d1) & set(d2)
put("book_changed_moves", sum(1 for k in common if d1[k] != d2[k]), f"{v1_tar} + {v2_tar}",
    "positions in both books whose stored move differs")
put("book_only_v8", len(set(d2) - set(d1)), f"{v1_tar} + {v2_tar}", "positions only in the v8 book")
put("book_only_v7", len(set(d1) - set(d2)), f"{v1_tar} + {v2_tar}", "positions only in the v7 book")
put("traps_entries", len(tr) // 8, v2_tar, "cx_traps.bin size / 8")
put("submission_v7_kb", round(os.path.getsize(v1_tar) / 1000), v1_tar, "file size / 1000")
put("submission_v8_kb", round(os.path.getsize(v2_tar) / 1000), v2_tar, "file size / 1000")
put("submission_v7_files", v1_names, v1_tar, "archive members")
put("submission_v8_files", v2_names, v2_tar, "archive members")


# ---------- result text files ----------
def arena(path):
    out = []
    for l in open(path):
        m = re.search(r"^(\S+) vs (\S+): W/D/L=\[(\d+), (\d+), (\d+)\] as P1=\[(\d+), (\d+), (\d+)\] "
                      r"as P2=\[(\d+), (\d+), (\d+)\] avg_len=([\d.]+) moves=(\d+) mean=([\d.]+)ms max=([\d.]+)ms", l)
        if m:
            g = m.groups()
            out.append({"agent": g[0], "opp": g[1], "all": list(map(int, g[2:5])), "p1": list(map(int, g[5:8])),
                        "p2": list(map(int, g[8:11])), "avg_len": float(g[11]), "mean_ms": float(g[13]),
                        "max_ms": float(g[14])})
    return out


R2 = f"{A}/tests/results_v2"
nv = arena(f"{R2}/new_vs_old.txt")[0]
put("new_vs_old_all", nv["all"], f"{R2}/new_vs_old.txt", "v8 vs v7, 200 games, sides alternate: W/D/L of v8")
put("new_vs_old_p1", nv["p1"], f"{R2}/new_vs_old.txt", "v8 as first player")
put("new_vs_old_p2", nv["p2"], f"{R2}/new_vs_old.txt", "v8 as second player")
put("new_vs_old_avg_len", nv["avg_len"], f"{R2}/new_vs_old.txt", "average game length (moves)")

big_new = [arena(f"{R2}/mix_big_stage_{s}.txt")[0] for s in (101, 202)]
big_old = [arena(f"{R2}/mix_big_old_agent_{s}.txt")[0] for s in (101, 202)]
put("mix_big_v8_p2", [sum(x["p2"][i] for x in big_new) for i in range(3)], f"{R2}/mix_big_stage_101.txt, _202.txt",
    "v8 as second player, 2 runs x 500 games, opponent = perfect solver with 30% depth-10 engine moves")
put("mix_big_v7_p2", [sum(x["p2"][i] for x in big_old) for i in range(3)],
    f"{R2}/mix_big_old_agent_101.txt, _202.txt", "same for v7")
put("mix_big_v8_p1", [sum(x["p1"][i] for x in big_new) for i in range(3)], f"{R2}/mix_big_stage_101.txt, _202.txt",
    "v8 as first player in the same runs")
put("mix_big_v7_p1", [sum(x["p1"][i] for x in big_old) for i in range(3)],
    f"{R2}/mix_big_old_agent_101.txt, _202.txt", "v7 as first player in the same runs")
put("mix_big_p2_games", sum(sum(x["p2"]) for x in big_new), f"{R2}/mix_big_stage_101.txt, _202.txt",
    "second-player games per agent")
eps = arena(f"{R2}/eps015.txt")
put("eps_v8_p2", eps[0]["p2"], f"{R2}/eps015.txt", "v8 as second player, 200 games, opponent = perfect + 15% random")
put("eps_v7_p2", eps[1]["p2"], f"{R2}/eps015.txt", "v7, same")
mix = arena(f"{R2}/mix03.txt")
put("mix400_v8_p2", mix[0]["p2"], f"{R2}/mix03.txt", "v8 as second player, 200 games (first, smaller run)")
put("mix400_v7_p2", mix[1]["p2"], f"{R2}/mix03.txt", "v7, same")
put("v8_arena_max_ms", max(x["max_ms"] for x in big_new + [eps[0], mix[0], nv]), f"{R2}/*.txt",
    "largest 'max=' of v8 over all local arena runs")


def kp(path):
    rows, tot = [], None
    for l in open(path):
        m = re.search(r"^([DL]) ply (\d+) (\d+): old W/D/L=\[(\d+), (\d+), (\d+)\]\s+new W/D/L=\[(\d+), (\d+), (\d+)\]", l)
        if m:
            g = m.groups()
            rows.append({"res": g[0], "ply": int(g[1]), "prefix": g[2], "old": list(map(int, g[3:6])),
                         "new": list(map(int, g[6:9]))})
        m = re.search(r"^TOTAL old W/D/L = \[(\d+), (\d+), (\d+)\]\s+new W/D/L = \[(\d+), (\d+), (\d+)\]", l)
        if m:
            tot = (list(map(int, m.groups()[:3])), list(map(int, m.groups()[3:])))
    return rows, tot


rows, tot = kp(f"{R2}/key_positions_mix.txt")
put("kp_mix_positions", len(rows), f"{R2}/key_positions_mix.txt", "distinct positions where v7 and v8 choose differently")
put("kp_mix_games_each", sum(rows[0]["old"]), f"{R2}/key_positions_mix.txt", "games per position per agent")
put("kp_mix_v7", tot[0], f"{R2}/key_positions_mix.txt", "TOTAL line, old = v7 (W/D/L)")
put("kp_mix_v8", tot[1], f"{R2}/key_positions_mix.txt", "TOTAL line, new = v8 (W/D/L)")
put("kp_mix_rows", rows, f"{R2}/key_positions_mix.txt", "per-position lines")
put("kp_mix_better", sum(1 for r in rows if (r["new"][0], -r["new"][2]) > (r["old"][0], -r["old"][2])
                         or (r["new"][2] < r["old"][2])), f"{R2}/key_positions_mix.txt",
    "positions where v8 has more wins or fewer losses")
put("kp_mix_same", sum(1 for r in rows if r["new"] == r["old"]), f"{R2}/key_positions_mix.txt",
    "positions with identical results")
put("kp_mix_worse", sum(1 for r in rows if r["new"][0] < r["old"][0] and r["new"][2] >= r["old"][2]),
    f"{R2}/key_positions_mix.txt", "positions where v8 has fewer wins and not fewer losses")
ep = f"{P}/results/key_positions_eps.txt"
if os.path.exists(ep) and kp(ep)[1]:
    rows_e, tot_e = kp(ep)
    put("kp_eps_v7", tot_e[0], ep, "TOTAL line, old = v7 (W/D/L); opponent = perfect + 15% random")
    put("kp_eps_v8", tot_e[1], ep, "TOTAL line, new = v8 (W/D/L)")
    put("kp_eps_rows", rows_e, ep, "per-position lines")

# kaggle-environments runs
for tag, path in (("v7", f"{A}/tests/results_v1/result_random.txt"), ("v7n", f"{A}/tests/results_v1/result_negamax.txt")):
    l = open(path).read()
    m = re.search(r"'win': (\d+), 'loss': (\d+), 'draw': (\d+).*max=([\d.]+)ms", l)
    put(f"kenv_{tag}", [int(m.group(1)), int(m.group(3)), int(m.group(2))], path, "W/D/L in kaggle-environments, 100 games")
    put(f"kenv_{tag}_max_ms", float(m.group(4)), path, "longest single move (ms)")
ke = open(f"{R2}/kaggle_env.txt").read().strip().split("\n")
for tag, l in zip(("v8", "v8n"), ke):
    m = re.search(r"'win': (\d+), 'loss': (\d+), 'draw': (\d+).*max=([\d.]+)ms", l)
    put(f"kenv_{tag}", [int(m.group(1)), int(m.group(3)), int(m.group(2))], f"{R2}/kaggle_env.txt",
        "W/D/L in kaggle-environments, 100 games (line order: random, negamax)")
    put(f"kenv_{tag}_max_ms", float(m.group(4)), f"{R2}/kaggle_env.txt", "longest single move (ms)")

# solver verification (re-run for this presentation)
sv = f"{P}/results/solver_verify.txt"
if os.path.exists(sv):
    tot_pos = tot_bad = 0
    sets = []
    for l in open(sv):
        m = re.search(r"tests/(\S+): (\d+) positions, (\d+) mismatches, mean ([\d.]+)s max ([\d.]+)s", l)
        if m:
            sets.append({"set": m.group(1), "n": int(m.group(2)), "bad": int(m.group(3)), "mean_s": float(m.group(4)),
                         "max_s": float(m.group(5))})
            tot_pos += int(m.group(2))
            tot_bad += int(m.group(3))
    put("verify_sets", sets, sv, "one line per benchmark set (Pascal Pons test sets)")
    put("verify_positions", tot_pos, sv, "sum of positions")
    put("verify_mismatches", tot_bad, sv, "sum of mismatches")

# off-book timing (re-run for this presentation)
ob = f"{P}/results/offbook_timing.txt"
if os.path.exists(ob):
    for l in open(ob):
        m = re.search(r"^(\S+) ply>=(\d+): n=(\d+) mean=([\d.]+)ms p99=([\d.]+)ms max=([\d.]+)ms timeouts=(\d+)", l)
        if m:
            tag = m.group(1)
            put(f"offbook_{tag}", {"min_ply": int(m.group(2)), "n": int(m.group(3)), "mean_ms": float(m.group(4)),
                                   "max_ms": float(m.group(6)), "timeouts": int(m.group(7))}, ob,
                f"line starting with {tag}: cold solve of positions outside the book")

# replay comparison (re-run for this presentation)
ra = f"{P}/results/replay_agents.txt"
if os.path.exists(ra):
    t = open(ra).read()
    m = re.search(r"mismatches: (\d+)", t)
    put("replay_v7_mismatch", int(m.group(1)), ra, "positions where v7 does not reproduce the recorded move")
    for res, same, n in re.findall(r"games=(\w) (same|DIFFERENT): (\d+) positions", t):
        put(f"replay_{res}_{same.lower()}", int(n), ra, f"our-turn positions in recorded second-player games with result {res}")
    dj = json.load(open(f"{P}/results/replay_diffs.json"))
    put("replay_diff_positions", len(dj), f"{P}/results/replay_diffs.json", "positions where v8 picks another move")
    put("replay_diff_games", len({d["id"] for d in dj}), f"{P}/results/replay_diffs.json", "games containing such a position")
    put("replay_diff_ply_range", [min(d["ply"] for d in dj), max(d["ply"] for d in dj)], f"{P}/results/replay_diffs.json",
        "move numbers of those positions")
kr = f"{P}/results/key_positions_replies.txt"
if os.path.exists(kr):
    rr = []
    for l in open(kr):
        m = re.search(r"^(\w) (.+?)\s+ply (\d+): old col (\d) score (-?\d+) good/plausible (\d+)/(\d+)\s+\| new col (\d) "
                      r"score (-?\d+) good/plausible (\d+)/(\d+)", l)
        if m:
            g = m.groups()
            rr.append({"res": g[0], "opp": g[1].strip(), "ply": int(g[2]), "old_col": int(g[3]), "old_score": int(g[4]),
                       "old_good": int(g[5]), "old_pl": int(g[6]), "new_col": int(g[7]), "new_score": int(g[8]),
                       "new_good": int(g[9]), "new_pl": int(g[10])})
    put("reply_rows", rr, kr, "per changed position: opponent replies that keep their result / replies that do not "
        "lose at once, after the v7 move and after the v8 move")
    put("reply_score_equal", all(r["old_score"] == r["new_score"] for r in rr), kr, "v7 and v8 moves have the same exact score")

json.dump(N, open(f"{P}/numbers.json", "w"), ensure_ascii=False, indent=1)
with io.open(f"{P}/NUMBERS.md", "w", encoding="utf-8") as f:
    f.write("# 数字来源表\n\n由 `presentation/tools/make_numbers.py` 从仓库里的文件自动算出。"
            "PPT 里的数字都取自这张表。\n\n| 键 | 值 | 来源文件 | 计算方法 |\n|---|---|---|---|\n")
    for k, v in N.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            vs = f"（{len(v)} 行，见 numbers.json）"
        else:
            vs = json.dumps(v, ensure_ascii=False)
        f.write(f"| `{k}` | {vs} | `{SRC[k][0]}` | {SRC[k][1]} |\n")
print("numbers:", len(N))
