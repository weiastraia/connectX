# Parse Kaggle ConnectX replays into a compact games.json (move list, sides, result, timing signals).
import json, os, sys, glob

ME = "weiastraia"
src, out = sys.argv[1], sys.argv[2]
games = []
for p in sorted(glob.glob(os.path.join(src, "*.json"))):
    d = json.load(open(p))
    names = d["info"]["TeamNames"]
    me = names.index(ME)
    steps = d["steps"]
    boards = [s[0]["observation"]["board"] for s in steps]
    moves = []
    for i in range(1, len(boards)):
        diff = [k for k in range(42) if boards[i][k] != boards[i - 1][k]]
        if len(diff) != 1:
            break
        moves.append(diff[0] % 7)
    # who moved at step i: the agent ACTIVE in steps[i-1]
    actors = [[j for j in range(2) if steps[i - 1][j]["status"] == "ACTIVE"] for i in range(1, len(steps))]
    overage = [min(s[me]["observation"].get("remainingOverageTime", 60) for s in steps)]
    games.append({
        "id": d["info"]["EpisodeId"], "me": me, "side": me + 1, "opp": names[1 - me],
        "moves": "".join(str(m + 1) for m in moves), "rewards": d["rewards"], "statuses": d["statuses"],
        "final_status": [steps[-1][j]["status"] for j in range(2)],
        "my_min_overage": overage[0],
        "opp_min_overage": min(s[1 - me]["observation"].get("remainingOverageTime", 60) for s in steps),
        "my_actions": [steps[i][me]["action"] for i in range(1, len(steps)) if me in actors[i - 1]],
        "nsteps": len(steps) - 1,
    })
json.dump(games, open(out, "w"))
print("games:", len(games))
