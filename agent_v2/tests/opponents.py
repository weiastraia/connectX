# Extra opponents. Kaggle's negamax is deterministic, so these add variety.
import random, time, os, sys
_rnd = random.Random(int(time.time() * 1000) % 100000 + os.getpid())

def noisy_negamax(obs, cfg):
    # 30% random move, otherwise kaggle's built-in negamax
    from kaggle_environments.envs.connectx.connectx import negamax_agent
    if _rnd.random() < 0.3:
        return _rnd.choice([c for c in range(cfg.columns) if obs.board[c] == 0])
    return negamax_agent(obs, cfg)
