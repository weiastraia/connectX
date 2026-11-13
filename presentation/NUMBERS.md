# 数字来源表

由 `presentation/tools/make_numbers.py` 从仓库里的文件自动算出。PPT 里的数字都取自这张表。

| 键 | 值 | 来源文件 | 计算方法 |
|---|---|---|---|
| `games_total` | 168 | `agent_v2/analysis/games.json` | len(list) |
| `games_selfplay` | 1 | `agent_v2/analysis/games.json` | opp == "weiastraia" (Kaggle validation episode) |
| `games_real` | 167 | `agent_v2/analysis/games.json` | games_total - games_selfplay |
| `p1_games` | 76 | `agent_v2/analysis/games.json` | side == 1, self-play excluded |
| `p1_wdl` | [76, 0, 0] | `agent_v2/analysis/games.json` | rewards[me] for side == 1 |
| `p2_games` | 91 | `agent_v2/analysis/games.json` | side == 2, self-play excluded |
| `p2_wdl` | [9, 4, 78] | `agent_v2/analysis/games.json` | rewards[me] for side == 2 |
| `status_not_done` | 0 | `agent_v2/analysis/games.json` | games whose final status is not DONE/DONE |
| `my_min_overage` | 60 | `agent_v2/analysis/games.json` | min remainingOverageTime of our agent over all steps (60 = never used) |
| `opponents_distinct` | 52 | `agent_v2/analysis/games.json` | distinct opponent names |
| `p1_win_len_min` | 15 | `agent_v2/analysis/games.json` | shortest first-player game (moves) |
| `p1_win_len_max` | 41 | `agent_v2/analysis/games.json` | longest first-player game (moves) |
| `my_wdl_errors` | 0 | `agent_v2/analysis/classified_exact.json` | our moves that lowered the win/draw/loss value |
| `my_score_inacc` | 0 | `agent_v2/analysis/classified_exact.json` | our moves that were not exact-score optimal |
| `p2_losses` | 78 | `agent_v2/analysis/classified_exact.json` | side 2, result L |
| `p2_loss_lengths` | [41] | `agent_v2/analysis/classified_exact.json` | set of game lengths of those losses |
| `p2_loss_opp_errors` | 0 | `agent_v2/analysis/classified_exact.json` | opponent moves that lowered their win/draw/loss value in those losses |
| `p2_loss_opp_inacc` | 0 | `agent_v2/analysis/classified_exact.json` | opponent moves that were not the fastest win in those losses |
| `p2_loss_opp_moves` | 1638 | `agent_v2/analysis/classified_exact.json` | total opponent moves in those losses |
| `p2_loss_opponents` | 32 | `agent_v2/analysis/classified_exact.json` | distinct opponents in those losses |
| `p2_nonloss` | 13 | `agent_v2/analysis/classified_exact.json` | side 2, result W or D |
| `p2_nonloss_with_opp_error` | 13 | `agent_v2/analysis/classified_exact.json` | of those, games where the opponent made a value-losing move |
| `p2_nonloss_444444` | 10 | `agent_v2/analysis/classified_exact.json` | of those, games starting with six stones in the centre column |
| `p2_nonloss_opponents` | 9 | `agent_v2/analysis/classified_exact.json` | distinct opponents in those games |
| `p2_first_error_moves` | [1, 5, 5, 7, 7, 7, 9, 9, 9, 9, 9, 15, 15] | `agent_v2/analysis/classified_exact.json` | move number of the opponent's first error in each game |
| `p2_perfect_share_pct` | 85.7 | `agent_v2/analysis/classified_exact.json` | p2_losses / p2_games |
| `p2_draws` | 4 | `agent_v2/analysis/classified_exact.json` | side 2, result D |
| `p2_wins` | 9 | `agent_v2/analysis/classified_exact.json` | side 2, result W |
| `positions_evaluated` | 6429 | `agent_v2/analysis/eval_exact.txt` | lines (one per position of every game) |
| `top_opponents` | （8 行，见 numbers.json） | `agent_v2/analysis/games.json` | 8 most frequent opponents; same/rep = repeated positions on their turn where they always played the same move |
| `det_same_total` | 581 | `agent_v2/analysis/games.json` | sum of 'same' over all opponents |
| `det_rep_total` | 619 | `agent_v2/analysis/games.json` | sum of 'rep' over all opponents |
| `opponents_3plus` | 22 | `agent_v2/analysis/games.json` | opponents met 3 times or more |
| `book_v7_entries` | 313040 | `agent_v2/submission/submission_v1.tar.gz` | cx_book.bin size / 8 |
| `book_v7_mb` | 2.5 | `agent_v2/submission/submission_v1.tar.gz` | cx_book.bin bytes / 1e6 |
| `book_v7_p1_plies` | [0, 18] | `agent_v2/submission/submission_v1.tar.gz` | stones on board in entries where the first player moves |
| `book_v7_p2_plies` | [1, 17] | `agent_v2/submission/submission_v1.tar.gz` | stones on board in entries where the second player moves |
| `book_v7_p1_entries` | 111312 | `agent_v2/submission/submission_v1.tar.gz` | entries with even stone count |
| `book_v7_p2_entries` | 201728 | `agent_v2/submission/submission_v1.tar.gz` | entries with odd stone count |
| `book_v8_entries` | 312349 | `agent_v2/submission/submission_v2.tar.gz` | cx_book.bin size / 8 |
| `book_changed_moves` | 10 | `agent_v2/submission/submission_v1.tar.gz + agent_v2/submission/submission_v2.tar.gz` | positions in both books whose stored move differs |
| `book_only_v8` | 565 | `agent_v2/submission/submission_v1.tar.gz + agent_v2/submission/submission_v2.tar.gz` | positions only in the v8 book |
| `book_only_v7` | 1256 | `agent_v2/submission/submission_v1.tar.gz + agent_v2/submission/submission_v2.tar.gz` | positions only in the v7 book |
| `traps_entries` | 7 | `agent_v2/submission/submission_v2.tar.gz` | cx_traps.bin size / 8 |
| `submission_v7_kb` | 915 | `agent_v2/submission/submission_v1.tar.gz` | file size / 1000 |
| `submission_v8_kb` | 916 | `agent_v2/submission/submission_v2.tar.gz` | file size / 1000 |
| `submission_v7_files` | ["cx_book.bin", "cx_solver_v1.so", "cx_solver_v2.so", "main.py"] | `agent_v2/submission/submission_v1.tar.gz` | archive members |
| `submission_v8_files` | ["cx_book.bin", "cx_solver_v1.so", "cx_solver_v2.so", "cx_traps.bin", "main.py"] | `agent_v2/submission/submission_v2.tar.gz` | archive members |
| `new_vs_old_all` | [100, 0, 100] | `agent_v2/tests/results_v2/new_vs_old.txt` | v8 vs v7, 200 games, sides alternate: W/D/L of v8 |
| `new_vs_old_p1` | [100, 0, 0] | `agent_v2/tests/results_v2/new_vs_old.txt` | v8 as first player |
| `new_vs_old_p2` | [0, 0, 100] | `agent_v2/tests/results_v2/new_vs_old.txt` | v8 as second player |
| `new_vs_old_avg_len` | 41.0 | `agent_v2/tests/results_v2/new_vs_old.txt` | average game length (moves) |
| `mix_big_v8_p2` | [828, 73, 99] | `agent_v2/tests/results_v2/mix_big_stage_101.txt, _202.txt` | v8 as second player, 2 runs x 500 games, opponent = perfect solver with 30% depth-10 engine moves |
| `mix_big_v7_p2` | [828, 72, 100] | `agent_v2/tests/results_v2/mix_big_old_agent_101.txt, _202.txt` | same for v7 |
| `mix_big_v8_p1` | [1000, 0, 0] | `agent_v2/tests/results_v2/mix_big_stage_101.txt, _202.txt` | v8 as first player in the same runs |
| `mix_big_v7_p1` | [1000, 0, 0] | `agent_v2/tests/results_v2/mix_big_old_agent_101.txt, _202.txt` | v7 as first player in the same runs |
| `mix_big_p2_games` | 1000 | `agent_v2/tests/results_v2/mix_big_stage_101.txt, _202.txt` | second-player games per agent |
| `eps_v8_p2` | [125, 25, 50] | `agent_v2/tests/results_v2/eps015.txt` | v8 as second player, 200 games, opponent = perfect + 15% random |
| `eps_v7_p2` | [124, 26, 50] | `agent_v2/tests/results_v2/eps015.txt` | v7, same |
| `mix400_v8_p2` | [161, 13, 26] | `agent_v2/tests/results_v2/mix03.txt` | v8 as second player, 200 games (first, smaller run) |
| `mix400_v7_p2` | [167, 11, 22] | `agent_v2/tests/results_v2/mix03.txt` | v7, same |
| `v8_arena_max_ms` | 42.5 | `agent_v2/tests/results_v2/*.txt` | largest 'max=' of v8 over all local arena runs |
| `kp_mix_positions` | 8 | `agent_v2/tests/results_v2/key_positions_mix.txt` | distinct positions where v7 and v8 choose differently |
| `kp_mix_games_each` | 200 | `agent_v2/tests/results_v2/key_positions_mix.txt` | games per position per agent |
| `kp_mix_v7` | [7, 793, 800] | `agent_v2/tests/results_v2/key_positions_mix.txt` | TOTAL line, old = v7 (W/D/L) |
| `kp_mix_v8` | [64, 908, 628] | `agent_v2/tests/results_v2/key_positions_mix.txt` | TOTAL line, new = v8 (W/D/L) |
| `kp_mix_rows` | （8 行，见 numbers.json） | `agent_v2/tests/results_v2/key_positions_mix.txt` | per-position lines |
| `kp_mix_better` | 3 | `agent_v2/tests/results_v2/key_positions_mix.txt` | positions where v8 has more wins or fewer losses |
| `kp_mix_same` | 4 | `agent_v2/tests/results_v2/key_positions_mix.txt` | positions with identical results |
| `kp_mix_worse` | 1 | `agent_v2/tests/results_v2/key_positions_mix.txt` | positions where v8 has fewer wins and not fewer losses |
| `kp_eps_v7` | [67, 831, 702] | `presentation/results/key_positions_eps.txt` | TOTAL line, old = v7 (W/D/L); opponent = perfect + 15% random |
| `kp_eps_v8` | [106, 907, 587] | `presentation/results/key_positions_eps.txt` | TOTAL line, new = v8 (W/D/L) |
| `kp_eps_rows` | （8 行，见 numbers.json） | `presentation/results/key_positions_eps.txt` | per-position lines |
| `kenv_v7` | [100, 0, 0] | `agent_v2/tests/results_v1/result_random.txt` | W/D/L in kaggle-environments, 100 games |
| `kenv_v7_max_ms` | 12.6 | `agent_v2/tests/results_v1/result_random.txt` | longest single move (ms) |
| `kenv_v7n` | [100, 0, 0] | `agent_v2/tests/results_v1/result_negamax.txt` | W/D/L in kaggle-environments, 100 games |
| `kenv_v7n_max_ms` | 11.1 | `agent_v2/tests/results_v1/result_negamax.txt` | longest single move (ms) |
| `kenv_v8` | [100, 0, 0] | `agent_v2/tests/results_v2/kaggle_env.txt` | W/D/L in kaggle-environments, 100 games (line order: random, negamax) |
| `kenv_v8_max_ms` | 9.5 | `agent_v2/tests/results_v2/kaggle_env.txt` | longest single move (ms) |
| `kenv_v8n` | [100, 0, 0] | `agent_v2/tests/results_v2/kaggle_env.txt` | W/D/L in kaggle-environments, 100 games (line order: random, negamax) |
| `kenv_v8n_max_ms` | 9.5 | `agent_v2/tests/results_v2/kaggle_env.txt` | longest single move (ms) |
| `verify_sets` | （6 行，见 numbers.json） | `presentation/results/solver_verify.txt` | one line per benchmark set (Pascal Pons test sets) |
| `verify_positions` | 5020 | `presentation/results/solver_verify.txt` | sum of positions |
| `verify_mismatches` | 0 | `presentation/results/solver_verify.txt` | sum of mismatches |
| `offbook_v7` | {"min_ply": 17, "n": 1678, "mean_ms": 0.42, "max_ms": 26.7, "timeouts": 0} | `presentation/results/offbook_timing.txt` | line starting with v7: cold solve of positions outside the book |
| `offbook_v8` | {"min_ply": 17, "n": 1678, "mean_ms": 0.57, "max_ms": 98.3, "timeouts": 0} | `presentation/results/offbook_timing.txt` | line starting with v8: cold solve of positions outside the book |
| `replay_v7_mismatch` | 0 | `presentation/results/replay_agents.txt` | positions where v7 does not reproduce the recorded move |
| `replay_D_different` | 5 | `presentation/results/replay_agents.txt` | our-turn positions in recorded second-player games with result D |
| `replay_D_same` | 79 | `presentation/results/replay_agents.txt` | our-turn positions in recorded second-player games with result D |
| `replay_L_different` | 7 | `presentation/results/replay_agents.txt` | our-turn positions in recorded second-player games with result L |
| `replay_L_same` | 1553 | `presentation/results/replay_agents.txt` | our-turn positions in recorded second-player games with result L |
| `replay_W_same` | 161 | `presentation/results/replay_agents.txt` | our-turn positions in recorded second-player games with result W |
| `replay_diff_positions` | 12 | `presentation/results/replay_diffs.json` | positions where v8 picks another move |
| `replay_diff_games` | 10 | `presentation/results/replay_diffs.json` | games containing such a position |
| `replay_diff_ply_range` | [22, 38] | `presentation/results/replay_diffs.json` | move numbers of those positions |
| `reply_rows` | （8 行，见 numbers.json） | `presentation/results/key_positions_replies.txt` | per changed position: opponent replies that keep their result / replies that do not lose at once, after the v7 move and after the v8 move |
| `reply_score_equal` | true | `presentation/results/key_positions_replies.txt` | v7 and v8 moves have the same exact score |
