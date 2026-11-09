# Play games in kaggle-environments, report results and per-move timing of our agent.
import sys, time, json, random
from kaggle_environments import make, utils
import kaggle_environments.agent as kagent

agent_path, opp, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
res = {"win": 0, "loss": 0, "draw": 0, "error": 0}
worst = 0.0
for g in range(n):
    env = make("connectx", debug=True)
    me = g % 2  # alternate first/second player
    agents = [agent_path, opp] if me == 0 else [opp, agent_path]
    env.run(agents)
    st = env.steps[-1][me]
    r = st.reward
    if st.status != "DONE":
        res["error"] += 1; print("game", g, "status", st.status, env.logs[-1] if env.logs else "")
    elif r == 1: res["win"] += 1
    elif r == 0: res["draw"] += 1
    else: res["loss"] += 1
    for step in env.logs:
        for i, a in enumerate(step):
            if i == me and isinstance(a, dict) and "duration" in a:
                worst = max(worst, a["duration"])
print(opp, res, f"worst_move={worst:.3f}s")
