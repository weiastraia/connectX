# Play n games vs an opponent; opponent "noisy" = 30%-random negamax, "perfect_eps" = our agent with 15% random moves.
import sys, importlib.util, random
from kaggle_environments import make
sys.path.insert(0, "tests")
import opponents

agent_path, opp_name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
if opp_name == "noisy":
    opp = opponents.noisy_negamax
elif opp_name == "perfect_eps":
    spec = importlib.util.spec_from_file_location("oppmain", agent_path)
    om = importlib.util.module_from_spec(spec); spec.loader.exec_module(om)
    rnd = random.Random(5)
    def opp(obs, cfg):
        if rnd.random() < 0.15:
            return rnd.choice([c for c in range(7) if obs.board[c] == 0])
        return om.agent(obs, cfg)
else:
    opp = opp_name
res = {"win": 0, "loss": 0, "draw": 0, "error": 0}
by_side = {0: [0, 0, 0], 1: [0, 0, 0]}
worst, durs = 0.0, []
for g in range(n):
    env = make("connectx", debug=False)
    me = g % 2
    env.run([agent_path, opp] if me == 0 else [opp, agent_path])
    st = env.steps[-1][me]
    if st.status != "DONE":
        res["error"] += 1
        print("game", g, "status", st.status)
        continue
    k = "win" if st.reward == 1 else "draw" if st.reward == 0 else "loss"
    res[k] += 1
    by_side[me][["win", "draw", "loss"].index(k)] += 1
    for step in env.logs:
        if len(step) > me and isinstance(step[me], dict) and "duration" in step[me]:
            durs.append(step[me]["duration"])
durs.sort()
print(f"vs {opp_name}: {res}  as P1 [W,D,L]={by_side[0]} as P2 [W,D,L]={by_side[1]}  "
      f"moves={len(durs)} mean={sum(durs)/max(1,len(durs))*1000:.1f}ms p99={durs[int(len(durs)*0.99)]*1000:.1f}ms max={durs[-1]*1000:.1f}ms")
