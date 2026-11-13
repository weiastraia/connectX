# Speaker script (English + Chinese) and expected questions for each slide.
# Numbers are filled from numbers.json so that slides, notes and the PDF always agree.


def slide_scripts(N):
    p1, p2 = N["p1_wdl"], N["p2_wdl"]
    book_k = N["book_v7_entries"] // 1000
    l13 = [x for x in N["verify_sets"] if x["set"].startswith("L1_R3")][0]
    ob = N["offbook_v7"]
    share = round(100 * N["p2_nonloss"] / N["p2_games"])
    det = round(100 * N["det_same_total"] / N["det_rep_total"])
    rr = [r for r in N["reply_rows"] if r["res"] == "D" and r["old_pl"] == 1 and r["new_pl"] >= 4][0]
    v7m, v8m = N["mix_big_v7_p2"], N["mix_big_v8_p2"]
    k7, k8 = N["kp_mix_v7"], N["kp_mix_v8"]
    replay_total = sum(N[k] for k in ("replay_D_different", "replay_D_same", "replay_L_different", "replay_L_same",
                                      "replay_W_same"))
    fe = N["p2_first_error_moves"]
    n59 = sum(1 for m in fe if 5 <= m <= 9)
    top = N["top_opponents"][0]
    S = []

    S.append(dict(
        title="タイトル",
        en=("Hello everyone. I am Yu from Team C. This is our week 4 report on Kaggle Connect X. "
            "Today I will talk about three things. "
            "First, our new agent, version 7. It is a perfect solver. "
            f"Second, what we learned from {N['games_total']} real games on Kaggle. "
            "Third, a small improvement, version 8, and how I tested it."),
        zh=("大家好，我是C组的余。这是我们 Kaggle Connect X 第4周的报告。"
            "今天讲三件事。"
            "第一，新的智能体 v7，它是一个完美求解器。"
            f"第二，从 Kaggle 上 {N['games_total']} 局真实对局里学到了什么。"
            "第三，一个小改进 v8，以及我是怎么验证它的。"),
        qa=[]))

    S.append(dict(
        title="Connect X：2秒以内に列を返すAI対戦(再掲)",
        en=("First, a short review of the game. "
            "The board has 6 rows and 7 columns. Two players drop stones in turn. "
            "The first player who gets four in a line wins. The line can be vertical, horizontal or diagonal. "
            "Our agent is a function. It gets the board and returns one column. "
            "It must answer within 2 seconds. "
            "The picture on the right is a real game from our records. Green is our agent. "
            f"It won at move {N['p1_win_len_min']}."),
        zh=("先简单回顾一下规则。"
            "棋盘是6行7列，两个人轮流落子。"
            "先把四个子连成一线的人获胜，横、竖、斜都可以。"
            "我们的智能体是一个函数，输入棋盘，返回一个列号。"
            "每一步必须在2秒内回答。"
            "右边的图是记录里的一局真实对局，绿色是我们的智能体，"
            f"它在第{N['p1_win_len_min']}手获胜。"),
        qa=[dict(q_en="What happens if the agent is too slow?",
                 q_zh="如果智能体算得太慢会怎样？",
                 a_en=("Each move has 2 seconds. There are also 60 seconds of extra time for the whole game. "
                       "If the extra time is used up, the agent loses. "
                       f"In our {N['games_total']} games we never used the extra time."),
                 a_zh=("每一步有2秒。整局另外还有60秒的备用时间。备用时间用完就判负。"
                       f"我们的 {N['games_total']} 局里，一次都没有用到备用时间。")),
            dict(q_en="How is the ranking calculated?",
                 q_zh="排名是怎么算的？",
                 a_en=("By a skill rating called mu. A new submission starts at 600. "
                       "A win raises mu and a loss lowers it. "
                       "The leaderboard shows the mu of each team's best submission. "
                       "I have a backup slide about this."),
                 a_zh=("按一个叫 μ 的技能分来排。新提交从600分开始，赢了加分，输了减分。"
                       "排行榜显示每个队最好的那次提交的 μ。我在付录里准备了一页说明。"))]))

    S.append(dict(
        title="最善を尽くせば先手が41手目に勝つ（解決済み）",
        en=("Connect Four is a solved game. "
            "In 1988, Victor Allis proved that the first player can always win. "
            "But the first player must start in the center column, and must play the best move every time. "
            "The figure shows the result of each first move. I computed it with my own solver. "
            "Only the center column wins. The win comes at move 41. "
            "The two columns next to the center give a draw. The other four columns lose. "
            "So the second player cannot win if the first player is perfect. "
            "Please remember this. It is important for today's talk."),
        zh=("四子棋是一个已经被解开的游戏。"
            "1988年，Victor Allis 证明了先手必胜。"
            "但先手必须从中间一列开始，并且每一步都走最优着法。"
            "这张图是第一手下在各列时的结果，是我用自己的求解器算出来的。"
            "只有中间一列能赢，在第41手获胜。"
            "中间两旁的两列是和棋，其余四列是先手输。"
            "所以，只要先手完美，后手就赢不了。"
            "请记住这一点，它对今天的内容很重要。"),
        qa=[dict(q_en="Why must the second player lose?",
                 q_zh="为什么后手一定会输？",
                 a_en=("It is a property of the game, not of our agent. "
                       "With perfect play from both sides, the first player wins at move 41. "
                       "Near the end the board is almost full, and one player is forced to play a bad square. "
                       "This is called zugzwang. The first player can control it if it starts in the center. "
                       f"Our data agrees: in our {N['p2_losses']} losses, the opponent played the best move every time."),
                 a_zh=("这是游戏本身的性质，不是我们智能体的问题。"
                       "双方都完美时，先手在第41手获胜。"
                       "棋盘快满的时候，总有一方被迫下在对自己不利的格子上，这叫 zugzwang（迫移）。"
                       "先手从中间开始，就能控制这件事。"
                       f"我们的数据也一致：输掉的 {N['p2_losses']} 局里，对手每一步都是最优着法。")),
            dict(q_en="Is your solver's result the same as the known result?",
                 q_zh="你的求解器算出的结果和已知结论一致吗？",
                 a_en=("Yes. The values of the seven first moves are the same as the known values. "
                       f"I also tested {N['verify_positions']:,} positions with known answers. There was no mismatch."),
                 a_zh=("一致。七个第一手的结果和已知结论相同。"
                       f"另外我用 {N['verify_positions']:,} 个有标准答案的局面做了测试，没有一个不一致。"))]))

    S.append(dict(
        title="v7から、評価値ではなく読み切りで手を選ぶ",
        en=("This table shows our versions. "
            "Versions 1 to 6 choose a move with search and an evaluation function. "
            "They look some moves ahead and then estimate. "
            "Version 7 is different. It reads the game to the end. So it knows the true result of every position. "
            "Version 8 is version 7 plus one new rule. I will explain it later. "
            f"Version 7 was submitted to Kaggle, and we have {N['games_total']} game records from it. "
            "Version 8 is also submitted, but I have not collected its games yet."),
        zh=("这张表是我们各个版本的变化。"
            "v1 到 v6 用搜索加评估函数来选着法，先往前看几步，再估计局面好坏。"
            "v7 不一样，它一直算到终局，所以知道每个局面真正的结果。"
            "v8 是在 v7 上加了一条新规则，后面会讲。"
            f"v7 已经提交到 Kaggle，我们有它的 {N['games_total']} 局对局记录。"
            "v8 也提交了，但它的对局记录还没有收集。"),
        qa=[dict(q_en="Is version 7 stronger than version 6?",
                 q_zh="v7 比 v6 强吗？",
                 a_en=("In theory version 7 cannot make a mistake, so it should not be weaker. "
                       "But I have not run version 7 against version 6 directly. "
                       "The Kaggle scores are on the result slide."),
                 a_zh=("理论上 v7 不会走错，所以不会更弱。"
                       "但我没有让 v7 和 v6 直接对战过。Kaggle 分数在结果那一页。"))]))

    S.append(dict(
        title="v7①：全局面の勝敗と手数を厳密に計算する",
        en=("This is the solver. It has three parts. "
            "First, a bitboard. The board is stored in two 64-bit integers. "
            "We can check four in a line with bit shifts. It is very fast. "
            "Second, negamax with alpha-beta pruning. We do not use an evaluation function. "
            "We search to the end of the game. So we get the exact result and the number of moves. "
            "Third, a transposition table and move ordering. "
            "We do not solve the same position twice, and we try good moves first. "
            "The method follows the public tutorial by Pascal Pons. The code is written in C++ for this project. "
            f"I tested it on {N['verify_positions']:,} positions with known answers. All answers matched."),
        zh=("这是求解器，由三部分组成。"
            "第一，位棋盘。整个棋盘用两个64位整数表示，用移位运算就能判断四连，非常快。"
            "第二，negamax 加 alpha-beta 剪枝。我们不用评估函数，一直搜索到终局，"
            "所以能得到精确的胜负和手数。"
            "第三，置换表和着法排序。同一个局面不重复计算，并且先试好的着法。"
            "方法参考了 Pascal Pons 的公开教程，代码是为这个项目用 C++ 写的。"
            f"我用 {N['verify_positions']:,} 个有标准答案的局面测试，全部一致。"),
        qa=[dict(q_en="Why not just use an open-source solver?",
                 q_zh="为什么不直接用开源的求解器？",
                 a_en=("The method is not new. I followed the public method by Pascal Pons. "
                       "But we wrote our own code for four reasons. "
                       "One: Kaggle runs a Python file, so we need a small library that Python can call. "
                       "Two: we need a time limit and a backup, so the agent never fails. "
                       "Three: for version 8 we must change how the solver chooses between equal moves. "
                       "Four: the goal of this project is to learn how to build an agent."),
                 a_zh=("方法并不新，我参考的是 Pascal Pons 公开的方法。但我们自己写代码有四个原因。"
                       "一，Kaggle 运行的是 Python 文件，所以需要一个 Python 能调用的小型库。"
                       "二，需要时间限制和兜底，保证智能体不会出错。"
                       "三，v8 要改变求解器在同分着法之间的选择方式，必须能改代码。"
                       "四，这个项目的目的就是学习怎么做智能体。")),
            dict(q_en="Did you write all the code yourself?",
                 q_zh="代码都是你自己写的吗？",
                 a_en=("The code was written with an AI coding tool, Claude Code. "
                       "My part was to set the goal, submit to Kaggle, collect the game records and check the results. "
                       "The solver was checked with public test positions."),
                 a_zh=("代码是用 AI 编程工具 Claude Code 写的。"
                       "我负责定目标、提交 Kaggle、收集对局记录和检查结果。求解器用公开的测试局面验证过。")),
            dict(q_en="What does the exact score mean?",
                 q_zh="精确分数是什么意思？",
                 a_en=("Positive means the player to move wins. A bigger number means a faster win. "
                       "Zero is a draw. Negative means a loss."),
                 a_zh="正数表示轮到走的一方能赢，数字越大赢得越快。零是和棋，负数是输。")]))

    S.append(dict(
        title="v7②：序盤は定石、以降は読み切りで2秒に収める",
        en=("The solver is exact, but the opening is slow. "
            f"Some hard opening positions took up to {l13['max_s']:.1f} seconds. The limit is 2 seconds. "
            "So I computed the opening in advance. This is the opening book. "
            f"It has about {book_k} thousand positions, with "
            f"{N['book_v7_p1_plies'][0]} to {N['book_v7_p1_plies'][1]} stones on the board. "
            "The flow is on the left. First, look in the book. If the position is there, return the book move. "
            "If not, call the C++ solver. After the book, the solver is fast. "
            f"The slowest position took {ob['max_ms'] / 1000:.2f} seconds in my test. "
            "If the C++ library fails, a pure Python solver is used. The agent always returns a legal move."),
        zh=("求解器是精确的，但开局阶段算得慢。"
            f"一些难的开局局面最长要 {l13['max_s']:.1f} 秒，而限制是2秒。"
            "所以我把开局提前算好，这就是开局库。"
            f"它有大约 {book_k / 10:.0f} 万个局面，覆盖棋盘上有 "
            f"{N['book_v7_p1_plies'][0]} 到 {N['book_v7_p1_plies'][1]} 个子的局面。"
            "流程在左边。先查开局库，查到就返回库里的着法。"
            "查不到就调用 C++ 求解器。出了开局库以后求解器很快，"
            f"我测到最慢的局面是 {ob['max_ms'] / 1000:.2f} 秒。"
            "如果 C++ 库出问题，就用纯 Python 的求解器。智能体一定会返回合法的着法。"),
        qa=[dict(q_en="How did you build the opening book?",
                 q_zh="开局库是怎么生成的？",
                 a_en=("I start from the empty board. On our turn I store only the best move. "
                       "On the opponent's turn I try every move. So the book covers every reply of the opponent. "
                       "It took about half an hour on 4 CPU cores."),
                 a_zh=("从空棋盘开始。轮到我们时只存最优的一步，轮到对手时把每一步都展开。"
                       "这样对手的任何应着都在库里。在4核 CPU 上大约算了半小时。")),
            dict(q_en="Is a compiled library allowed on Kaggle?",
                 q_zh="Kaggle 允许提交编译好的库吗？",
                 a_en=("The rules do not say it clearly. "
                       f"The submission passed the validation game and played {N['games_real']} games without any error. "
                       "If the library cannot be loaded, the Python solver works as a backup."),
                 a_zh=("规则没有明确写。"
                       f"这次提交通过了验证局，并且打了 {N['games_real']} 局没有任何报错。"
                       "如果库加载不了，会用 Python 求解器兜底。"))]))

    S.append(dict(
        title=f"v7の結果：先手{p1[0]}戦全勝、後手は{p2[0]}勝{p2[1]}分{p2[2]}敗",
        en=("This is the result of version 7 on Kaggle. "
            f"We have {N['games_total']} game records. One is the self-play check, so there are {N['games_real']} real games. "
            f"As the first player we played {N['p1_games']} games and won all of them. "
            f"As the second player we played {N['p2_games']} games. We won {p2[0]}, drew {p2[1]} and lost {p2[2]}. "
            "There were no errors and no timeouts. "
            f"We played against {N['opponents_distinct']} teams. "
            "The Kaggle score is written at the bottom."),
        zh=("这是 v7 在 Kaggle 上的结果。"
            f"我们有 {N['games_total']} 局记录，其中1局是提交时的自我对弈检查，所以真实对局是 {N['games_real']} 局。"
            f"先手 {N['p1_games']} 局，全部获胜。"
            f"后手 {N['p2_games']} 局，{p2[0]} 胜 {p2[1]} 平 {p2[2]} 负。"
            "没有报错，也没有超时。"
            f"一共遇到 {N['opponents_distinct']} 个队伍。"
            "Kaggle 分数写在最下面。"),
        qa=[dict(q_en=f"Are {N['games_total']} games enough?",
                 q_zh=f"只有 {N['games_total']} 局，样本够吗？",
                 a_en=("It depends on the claim. "
                       "For 'the agent has no errors and no timeouts', it is good evidence, but not a proof. "
                       "For 'the first player always wins', I do not rely on these games. The solver is exact and tested. "
                       f"For 'how often opponents make mistakes', it is a small sample. Only {N['p2_nonloss']} games had a mistake. "
                       "So I do not make strong claims about that."),
                 a_zh=("要看是哪个结论。"
                       "对“智能体不报错、不超时”，这是不错的证据，但不是证明。"
                       "对“先手必胜”，我不依赖这些对局，求解器本身是精确的，并且测试过。"
                       f"对“对手多久犯一次错”，样本很小，只有 {N['p2_nonloss']} 局出现失误，所以这方面我不下强结论。")),
            dict(q_en="Why did a perfect solver lose so many games?",
                 q_zh="完美求解器为什么还输这么多？",
                 a_en="All losses were as the second player. The next slide explains why they could not be avoided.",
                 a_zh="输的全是后手局。下一页解释为什么这些局避免不了。")]))

    S.append(dict(
        title=f"後手の{N['p2_losses']}敗は、全手が最善の相手で防げない",
        en=(f"Why did we lose {N['p2_losses']} games? "
            "I checked every position of every game with the solver. The result is clear. "
            f"All {N['p2_losses']} losses ended at move {N['p2_loss_lengths'][0]}. This is the length of a perfect game. "
            f"In these games the opponents made {N['p2_loss_opp_moves']:,} moves. Every one was the best move. "
            "Our moves were also all best moves. "
            "So these opponents are perfect solvers too. "
            "When a perfect player moves first, the second player always loses. We cannot change these games."),
        zh=(f"为什么输了 {N['p2_losses']} 局？"
            "我用求解器检查了每一局的每一个局面，结果很清楚。"
            f"{N['p2_losses']} 局输棋全部在第 {N['p2_loss_lengths'][0]} 手结束，这正是双方完美对弈时的长度。"
            f"这些局里对手一共走了 {N['p2_loss_opp_moves']:,} 步，每一步都是最优着法。"
            "我们的每一步也都是最优着法。"
            "所以这些对手也是完美求解器。"
            "完美的一方先走，后手一定输。这些局我们改变不了。"),
        qa=[dict(q_en="Could a different move by us change the result?",
                 q_zh="我们换一种走法能改变结果吗？",
                 a_en=("No. In these positions every move loses against perfect play. "
                       f"We can only choose how slowly we lose. We already lose as slowly as possible, at move {N['p2_loss_lengths'][0]}."),
                 a_zh=("不能。这些局面里，面对完美的对手，任何一步都是输。"
                       f"我们只能选择输得多慢，而现在已经是最慢的了，在第 {N['p2_loss_lengths'][0]} 手。")),
            dict(q_en="How do you know these opponents are solvers and not just lucky?",
                 q_zh="怎么知道这些对手是求解器，而不只是运气好？",
                 a_en=(f"{N['p2_loss_opp_moves']:,} moves and not one was worse than the best move. "
                       f"These games were against {N['p2_loss_opponents']} different opponents. Luck cannot explain that."),
                 a_zh=(f"{N['p2_loss_opp_moves']:,} 步里没有一步比最优着法差，"
                       f"而且来自 {N['p2_loss_opponents']} 个不同的对手，运气解释不了。"))]))

    S.append(dict(
        title="伸ばせるのは「ミスをする相手との後手局」だけ",
        en=("So where can we improve? Only in second-player games against opponents who make mistakes. "
            f"There were {N['p2_nonloss']} such games. That is {share} percent of our second-player games. "
            f"After the mistake we did not give the advantage back: {N['p2_wins']} wins and {N['p2_draws']} draws. "
            f"The chart shows when the first mistake came. {n59} of the {N['p2_nonloss']} were between move 5 and move 9. "
            f"{N['p2_nonloss_444444']} of the {N['p2_nonloss']} games started with six stones in the center column. "
            "One more point. Opponents are very repeatable. "
            f"In the same position, they played the same move {det} percent of the time. "
            "So if a line worked once, it may work again."),
        zh=("那么哪里还能提升？只有“对手会犯错的后手局”。"
            f"这样的对局有 {N['p2_nonloss']} 局，占后手局的 {share}%。"
            f"对手失误以后，我们没有把优势还回去：{N['p2_wins']} 胜 {N['p2_draws']} 平。"
            f"图里是对手第一次失误出现在第几手，{N['p2_nonloss']} 局里有 {n59} 局在第5到第9手之间。"
            f"{N['p2_nonloss']} 局里有 {N['p2_nonloss_444444']} 局，开头都是中间一列连下6个子。"
            "还有一点：对手的走法很固定。"
            f"相同的局面下，他们有 {det}% 的情况走同一步。"
            "所以一条路线成功过一次，就可能再成功。"),
        qa=[dict(q_en=f"Could the {N['p2_draws']} draws have been wins?",
                 q_zh=f"那 {N['p2_draws']} 局平局本来能赢吗？",
                 a_en=("In those games the opponent's mistake changed a win into a draw, not into a loss. "
                       "After that, the opponent defended correctly. So the true value was a draw. "
                       "We can only win if the opponent makes one more mistake. Version 8 tries to make that more likely."),
                 a_zh=("这几局里，对手的失误只是把胜局变成了和棋，没有变成输棋。"
                       "之后对手一直防守正确，所以局面的真实价值就是和棋。"
                       "只有对手再犯一次错我们才能赢。v8 就是想让这种情况更容易发生。")),
            dict(q_en=f"Is {N['p2_nonloss']} games enough to say anything?",
                 q_zh=f"{N['p2_nonloss']} 局能说明什么吗？",
                 a_en=("It is a small number. It only shows where to look. "
                       "This is why I tested version 8 with simulated opponents, and why I say the real effect is still unknown."),
                 a_zh=("数量很少，只能告诉我们该往哪里看。"
                       "所以我用模拟对手测试了 v8，并且明确说实战效果还不知道。"))]))

    S.append(dict(
        title="v8：同じ評価値なら、相手の正解が少ない手を選ぶ",
        en=("This is the idea of version 8. Often several moves have the same exact value. "
            "Version 7 just takes the first one. Version 8 asks: which move is harder for the opponent? "
            f"Here is a real example from our records. It is move {rr['ply']} and the position is a draw. "
            f"After the version 7 move, the opponent has only {rr['old_pl']} possible reply. It is forced, and it is correct. "
            f"After the version 8 move, the opponent has {rr['new_pl']} possible replies. Only {rr['new_good']} keeps the draw. "
            f"The other {rr['new_pl'] - rr['new_good']} give us a win. "
            "Both moves are equally safe for us. But the second one gives the opponent more chances to go wrong. "
            f"There is also a small trap table with {N['traps_entries']} positions. "
            "They come from recorded games where the opponent made a mistake later. "
            "The rule never picks a worse move. If we can win, we still win as fast as possible."),
        zh=("这是 v8 的想法。经常有好几步的精确分数是一样的。"
            "v7 直接取第一个。v8 会问：哪一步对对手来说更难？"
            f"这是记录里的一个真实例子，第 {rr['ply']} 手，局面是和棋。"
            f"v7 的着法之后，对手只有 {rr['old_pl']} 个可走的应着，是被迫的，而且是正确的。"
            f"v8 的着法之后，对手有 {rr['new_pl']} 个可走的应着，只有 {rr['new_good']} 个能保住和棋，"
            f"其余 {rr['new_pl'] - rr['new_good']} 个都会让我们赢。"
            "两步对我们来说同样安全，但第二步给了对手更多走错的机会。"
            f"另外还有一个小的陷阱表，共 {N['traps_entries']} 个局面，"
            "来自对手后来犯过错的那些对局。"
            "这条规则不会选更差的着法。能赢的时候，仍然选最快赢的。"),
        qa=[dict(q_en="Does this 'luring' strategy really work?",
                 q_zh="这种“诱敌”策略真的有效吗？",
                 a_en=("My honest answer: partly, and only in simulation so far. "
                       "Against a perfect opponent it changes nothing. "
                       "Against simulated imperfect opponents, it helped in the positions where version 7 and version 8 differ. "
                       "In full games I saw no clear difference, because such positions are rare. "
                       "On Kaggle I have no data yet."),
                 a_zh=("老实说：部分有效，而且目前只在模拟里。"
                       "对完美的对手，它什么都改变不了。"
                       "对模拟的不完美对手，在 v7 和 v8 选着不同的那些局面上有帮助。"
                       "在完整对局里我没看到明显差别，因为这种局面很少出现。"
                       "Kaggle 实战还没有数据。")),
            dict(q_en="Is version 8 more risky than version 7?",
                 q_zh="v8 会不会比 v7 更冒险？",
                 a_en=("No. Version 8 only chooses among moves with the same exact score. "
                       f"I played version 8 against version 7 for {sum(N['new_vs_old_all'])} games. Each side won all its first-player games."),
                 a_zh=("不会。v8 只在精确分数相同的着法里挑。"
                       f"我让 v8 和 v7 对战了 {sum(N['new_vs_old_all'])} 局，双方执先时都全胜。")),
            dict(q_en="What is a 'possible reply'?",
                 q_zh="“可走的应着”指什么？",
                 a_en=("A reply that does not lose at once. Any agent can block an immediate four. "
                       "So I do not count such forced blocks as real chances for a mistake."),
                 a_zh="指不会马上输掉的应着。任何智能体都会堵住马上要成的四连，所以这种被迫的堵，我不算作真正的犯错机会。")]))

    S.append(dict(
        title="v8はv7に劣らないが、全体の勝率差は見えない",
        en=("How did I test version 8? "
            f"First, version 8 against version 7, {sum(N['new_vs_old_all'])} games. Each side won all its first-player games. "
            "So version 8 is not weaker. "
            "Second, against the random and Negamax agents, both versions won every game. "
            "Third, I made a simulated opponent. It is a perfect solver, but 30 percent of its moves come from a weaker search. "
            f"As the second player, over {N['mix_big_p2_games']:,} games, version 7 won {v7m[0]} and version 8 won {v8m[0]}. No difference. "
            f"Fourth, I started games from the {N['kp_mix_positions']} positions where the two versions choose different moves. "
            f"There version 8 was better. Wins went from {k7[0]} to {k8[0]}, and losses from {k7[2]} to {k8[2]}. "
            f"But look at the details: {N['kp_mix_better']} positions improved, {N['kp_mix_same']} were the same, "
            f"and {N['kp_mix_worse']} was slightly worse. "
            "So my conclusion is careful. Version 8 is not worse than version 7. It helps in some special positions. "
            "But these positions are rare, and the opponent is simulated. The effect on Kaggle is not confirmed."),
        zh=("我是怎么测试 v8 的？"
            f"第一，v8 对 v7，{sum(N['new_vs_old_all'])} 局。双方执先时都全胜，所以 v8 没有变弱。"
            "第二，对 random 和 Negamax 智能体，两个版本都是全胜。"
            "第三，我做了一个模拟对手：它是完美求解器，但有30%的着法改用较弱的搜索来走。"
            f"执后 {N['mix_big_p2_games']:,} 局，v7 赢 {v7m[0]} 局，v8 赢 {v8m[0]} 局，没有差别。"
            f"第四，我从两个版本选着不同的 {N['kp_mix_positions']} 个局面出发开始对局。"
            f"在这里 v8 更好：胜局从 {k7[0]} 变成 {k8[0]}，负局从 {k7[2]} 变成 {k8[2]}。"
            f"但要看细节：{N['kp_mix_better']} 个局面变好，{N['kp_mix_same']} 个一样，{N['kp_mix_worse']} 个略差。"
            "所以我的结论比较谨慎：v8 不比 v7 差，在一些特殊局面上有帮助，"
            "但这些局面很少，而且对手是模拟的。在 Kaggle 上的效果还没有确认。"),
        qa=[dict(q_en=f"Why is there no difference in the {N['mix_big_p2_games']:,} games?",
                 q_zh=f"为什么 {N['mix_big_p2_games']:,} 局里看不出差别？",
                 a_en=("The two versions choose the same move in almost all positions. "
                       f"In the recorded second-player games they differ in only {N['replay_diff_positions']} of about {replay_total:,} positions. "
                       "So a full game rarely reaches a position where they differ."),
                 a_zh=("两个版本在几乎所有局面上选的着法都一样。"
                       f"在记录的后手对局里，约 {replay_total:,} 个局面中只有 {N['replay_diff_positions']} 个不同。"
                       "所以完整对局很少会走到两者不同的局面。")),
            dict(q_en="Is the simulated opponent realistic?",
                 q_zh="模拟对手和真实对手像吗？",
                 a_en=("I am not sure. Real opponents made their mistakes early, mostly between move 5 and move 9. "
                       "My simulated opponent can make a mistake at any move. This is a limitation of the test."),
                 a_zh=("我不确定。真实对手的失误出现得早，大多在第5到第9手。"
                       "我的模拟对手在任何一手都可能失误。这是这个测试的局限。"))]))

    S.append(dict(
        title="まとめ：先手は完全、後手の改善は実戦で未検証",
        en=("To sum up. Version 7 is a perfect solver with an opening book. "
            f"As the first player it won all {p1[0]} games, with no errors. "
            f"From {N['games_total']} games we learned that our {N['p2_losses']} losses could not be avoided. "
            "Version 8 adds a rule for equal moves. It works in simulation. "
            "There are limits. The second player loses against a perfect opponent. This is the game itself. "
            f"We only have {N['games_total']} games from one submission. And version 8 is not tested on real games yet. "
            "Next, I will collect real games of version 8 and compare them with version 7 in the same way. "
            "I also want to collect more opponent mistakes and extend the trap table. "
            "That is all. Thank you."),
        zh=("总结一下。v7 是带开局库的完美求解器。"
            f"先手 {p1[0]} 局全胜，没有报错。"
            f"从 {N['games_total']} 局里我们知道，输掉的 {N['p2_losses']} 局是避免不了的。"
            "v8 增加了一条处理同分着法的规则，在模拟里有效。"
            "局限有这些：面对完美的对手，后手一定输，这是游戏本身决定的。"
            f"我们只有一次提交的 {N['games_total']} 局。v8 还没有在实战中验证。"
            "接下来，我会收集 v8 的实战对局，用同样的方法和 v7 比较。"
            "我还想收集更多对手的失误，扩充陷阱表。"
            "以上，谢谢大家。"),
        qa=[dict(q_en="Can the Kaggle score still go up?",
                 q_zh="Kaggle 分数还能再涨吗？",
                 a_en=("As the first player, no. We already win every game. "
                       "As the second player, only against opponents who make mistakes. So the possible gain is small."),
                 a_zh="先手不能，已经全胜了。后手只有面对会犯错的对手才有可能。所以能涨的空间很小。"),
            dict(q_en="What about reinforcement learning?",
                 q_zh="强化学习呢？",
                 a_en=("For the standard board, the exact solver already plays the best move. "
                       "So reinforcement learning cannot play better. "
                       "It may be useful to model how opponents make mistakes. I have not tried it."),
                 a_zh=("对标准棋盘来说，精确求解器已经走的是最优着法，强化学习不可能下得更好。"
                       "它也许可以用来学习对手怎么犯错。这个我还没试过。"))]))

    S.append(dict(
        title="付録：順位はスキルレートμで決まる",
        en=("This slide is for questions about the ranking. "
            "Each submission has a rating. It is a normal distribution with mean mu and uncertainty sigma. "
            "A new submission first plays against itself, to check that it works. Then it starts at mu 600. "
            "It plays against submissions with similar ratings. "
            "A win raises mu, a loss lowers it, and a draw moves the two values closer. "
            "The leaderboard shows the mu of each team's best submission."),
        zh=("这一页是为排名方面的提问准备的。"
            "每个提交有一个评分，用均值 μ 和不确定度 σ 的正态分布表示。"
            "新提交先自己和自己下一局，确认能正常运行，然后从 μ=600 开始。"
            "它会和评分接近的提交对局。"
            "赢了 μ 上升，输了下降，平局则两边的值互相靠近。"
            "排行榜显示每个队最好的那次提交的 μ。"),
        qa=[dict(q_en="Why is a perfect agent not far above the others?",
                 q_zh="完美的智能体为什么没有远远领先？",
                 a_en=("This is my own reading. About half of the games are as the second player. "
                       "The top agents are also perfect. Against them we win as the first player and lose as the second. "
                       "So the ratings of perfect agents stay close to each other."),
                 a_zh=("这是我自己的理解。大约一半的对局是后手。"
                       "排在前面的智能体也是完美的，和它们下，先手赢、后手输。"
                       "所以完美智能体之间的评分会很接近。"))]))

    S.append(dict(
        title="付録：よく当たる相手は、同じ局面で同じ手を打つ",
        en=("This table shows the opponents we met most often. "
            "For each one it shows our results as the first and as the second player. "
            "The last column shows how repeatable the opponent is. "
            f"For example, the first opponent had {top['rep']} repeated positions and played the same move in {top['same']} of them. "
            "Most of these opponents beat us every time when they move first. They are perfect solvers."),
        zh=("这张表是我们遇到次数最多的对手。"
            "每个对手列出了我们执先和执后的成绩。"
            "最后一列是对手走法的固定程度。"
            f"比如第一个对手有 {top['rep']} 个重复出现的局面，其中 {top['same']} 个每次都走同一步。"
            "这些对手大多数在执先时每次都赢我们，它们是完美求解器。"),
        qa=[]))
    return S
