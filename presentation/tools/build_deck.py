# Build the week-4 deck from the lab template. Every number comes from presentation/numbers.json.
# usage (from repo root): python3 presentation/tools/build_deck.py
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from deck_lib import *  # noqa: F401,F403
from script_text import slide_scripts

P = "presentation"
N = json.load(open(f"{P}/numbers.json"))
OUT = f"{P}/ConnectX_week4.pptx"


def fmt(n):
    return f"{n:,}"


def wdl(v):
    return f"{v[0]}勝{v[1]}分{v[2]}敗"


prs = Presentation(f"{P}/template/lab_template.pptx")
clear_slides(prs)
scripts = slide_scripts(N)
slides = []

# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = "Kaggle\vConnect X"
for r in s.shapes.title.text_frame.paragraphs[0].runs:
    r.font.size = Pt(40.5)
    r.font.name = "Meiryo"
sub = s.placeholders[1]
sub.left, sub.top, sub.width, sub.height = Inches(1.67), Inches(4.74), Inches(10.0), Inches(1.81)
tf = sub.text_frame
tf.paragraphs[0].add_run().text = "第4週　チームC"
p = tf.add_paragraph()
p.add_run().text = "岡邊　徐　"
b = p.add_run()
b.text = "余"
b.font.bold = True
p.add_run().text = "　福田"
tf.add_paragraph().add_run().text = "2026年11月＿＿日"
slides.append(s)

# ---------------------------------------------------------------- 2 overview
s = content_slide(prs, "Connect X：2秒以内に列を返すAI対戦(再掲)", 1)
text(s, 0.6, 1.3, 7.3, 0.5, "ルール", size=24, bold=True)
text(s, 0.6, 1.95, 7.3, 2.0, ["・6行×7列の盤面に、交互に石を落とす", "・縦・横・斜めのどれかに4個並べると勝ち",
                               "・1手は2秒以内（予備時間は1局で合計60秒）"], size=22, space_after=6)
text(s, 0.6, 4.05, 7.3, 0.5, "提出するもの", size=24, bold=True)
text(s, 0.6, 4.7, 7.3, 1.4, ["・盤面を受け取り、石を置く列を返す関数", "・提出どうしが対戦し、勝敗でレートが決まる"],
     size=22, space_after=6)
# board drawn from a recorded game (our 15-move win as first player)
games = json.load(open("agent_v2/analysis/games.json"))
ex = sorted((g for g in games if g["side"] == 1 and len(g["moves"]) == N["p1_win_len_min"]), key=lambda g: g["id"])[0]
grid = [[0] * 7 for _ in range(6)]
last = None
for i, ch in enumerate(ex["moves"]):
    c = int(ch) - 1
    r = max(r for r in range(6) if grid[r][c] == 0)
    grid[r][c] = 1 + i % 2
    last = (r, c)
win = set()
for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
    cells = [last]
    for sg in (1, -1):
        rr, cc = last[0] + sg * dr, last[1] + sg * dc
        while 0 <= rr < 6 and 0 <= cc < 7 and grid[rr][cc] == 1:
            cells.append((rr, cc))
            rr += sg * dr
            cc += sg * dc
    if len(cells) >= 4:
        win |= set(cells)
assert win, "example game must end with a four"
bx, by, cell = 8.45, 1.45, 0.58
box(s, bx - 0.12, by - 0.12, 7 * cell + 0.24, 6 * cell + 0.24, fill=LIGHT, line=GREEN, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    name="盤面")
for r in range(6):
    for c in range(7):
        v = grid[r][c]
        fill = {0: WHITE, 1: GREEN, 2: BLUE}[v]
        ring = ORANGE if (r, c) in win else ("C3CAC6" if v == 0 else fill)
        box(s, bx + c * cell + 0.05, by + r * cell + 0.05, cell - 0.1, cell - 0.1, fill=fill, line=ring,
            line_w=3 if (r, c) in win else 0.75, shape=MSO_SHAPE.OVAL, name=f"石 {r}-{c}")
text(s, bx - 0.2, by + 6 * cell + 0.2, 7 * cell + 0.4, 0.9,
     [f"記録した対局の終局図（{N['p1_win_len_min']}手目に先手の勝ち）", "緑：自分（先手）　青灰：相手　橙枠：4個並び"],
     size=14, color=GRAY, align="c")
text(s, 0.6, 6.62, 12.1, 0.35, "出典：Kaggle Connect X　https://www.kaggle.com/competitions/connectx", size=14, color=GRAY)
slides.append(s)

# ---------------------------------------------------------------- 3 solved game
fm = {}
for l in open(f"{P}/results/first_move_values.txt"):
    q = l.split()
    if len(q) == 4 and q[1] == "1":
        fm[int(q[0][1:])] = (int(q[2]), int(q[3]))
assert sorted(fm) == [1, 2, 3, 4], "first-move values missing"
for c in (5, 6, 7):
    fm[c] = fm[8 - c]  # mirror symmetry


def first_move_label(c):
    w, e = fm[c]  # from the second player's view (side to move after one stone)
    if w == 0:
        return "引き分け", "", BLUE, TXT
    stone = 22 - abs(e)
    if w < 0:
        return "先手の勝ち", f"{2 * stone - 1}手目", GREEN, WHITE
    return "後手の勝ち", f"{2 * stone}手目", "D5D9D7", TXT


p1_win_move = first_move_label(4)[1]
# the spoken script states these results in words; fail loudly if the computed values ever differ
assert [first_move_label(c)[:2] for c in range(1, 8)] == [
    ("後手の勝ち", "40手目"), ("後手の勝ち", "42手目"), ("引き分け", ""), ("先手の勝ち", "41手目"),
    ("引き分け", ""), ("後手の勝ち", "42手目"), ("後手の勝ち", "40手目")]
s = content_slide(prs, f"最善を尽くせば先手が{p1_win_move}に勝つ（解決済み）", 2)
text(s, 0.6, 1.25, 12.1, 2.0, ["・1988年に V. Allis が「先手必勝」を証明した", "・ただし先手は中央の列から始め、最善手を続ける必要がある",
                                "・現在は、どの局面でも勝敗と決着までの手数を計算できる"], size=22, space_after=6)
text(s, 0.6, 3.3, 12.1, 0.4, "1手目に置く列と、その後を双方が最善で打ったときの結果", size=20, bold=True)
cw = 1.6
for c in range(1, 8):
    res, mv, fill, fc = first_move_label(c)
    x = 0.75 + (c - 1) * (cw + 0.12)
    box(s, x, 3.9, cw, 1.75, [[(f"{c}列目", {"size": 16})], [(res, {"size": 20, "bold": True})], [(mv, {"size": 16})]],
        color=fc, fill=fill, line=fill, name=f"1手目 {c}列")
text(s, 0.6, 5.85, 12.1, 0.4, "先手が勝てる1手目は中央（4列目）だけ。後手は、相手が最善なら勝てない", size=20, color=GREEN, bold=True)
text(s, 0.6, 6.62, 12.1, 0.35, "出典：V. Allis, A Knowledge-based Approach of Connect-Four (1988)　図：自作ソルバーの計算結果",
     size=14, color=GRAY)
slides.append(s)

# ---------------------------------------------------------------- 4 version history
s = content_slide(prs, "v7から、評価値ではなく読み切りで手を選ぶ", 3)
rows = [["版", "手の選び方", "追加したもの"],
        ["v1〜v3", "中央優先 → 即勝ち・防御 → 4手読み", "Minimax法＋αβ法"],
        ["v4〜v6", "定石 ＋ 評価値を使う探索", "ビットボード、定石、終局優先探索"],
        ["v7", "定石 ＋ 終局までの読み切り", f"C++の完全ソルバー、定石{N['book_v7_entries'] // 10000}万局面"],
        ["v8", "v7 ＋ 同じ評価値の手の選び分け", f"相手の正解が少ない手、罠表{N['traps_entries']}局面"]]
table(s, 0.6, 1.3, 12.1, [1.4, 5.2, 5.5], rows, size=20, row_h=0.72, bold_rows=(3, 4), name="版の表")
text(s, 0.6, 5.2, 12.1, 1.2, [[("今週の報告：", {"bold": True, "color": GREEN}), ("v7 と v8", {"bold": True, "color": GREEN})],
                               f"・v7：Kaggleに提出し、{N['games_total']}局の記録を分析した",
                               "・v8：提出済み。実戦の記録はまだ集めていない"], size=20, space_after=4)
slides.append(s)

# ---------------------------------------------------------------- 5 solver
s = content_slide(prs, "v7①：全局面の勝敗と手数を厳密に計算する", 4)
gx, gy, gc = 0.75, 1.75, 0.52
text(s, gx, 1.25, 7 * gc, 0.4, "ビットボードのビット番号", size=18, bold=True)
for r in range(7):  # r = 0 is the extra top row
    for c in range(7):
        bit = c * 7 + (6 - r)
        box(s, gx + c * gc, gy + r * gc, gc, gc, str(bit), size=13, color=GRAY if r == 0 else TXT,
            fill="D5D9D7" if r == 0 else WHITE, line="9AA3A0", line_w=0.5, name=f"bit {bit}", margin=0)
text(s, gx, gy + 7 * gc + 0.12, 7 * gc + 0.6, 0.9, ["灰色の段：列の区切り（石は置かない）", "1列7ビット × 7列 ＝ 49ビット"], size=14,
     color=GRAY)
items = [("ビットボード", "盤面を64ビット整数2個で表し、4個並びをビット演算で判定する"),
         ("negamax ＋ αβ法", "評価関数を使わず、終局まで読んで勝敗と手数を求める"),
         ("置換表と手の並べ替え", "同じ局面を再計算せず、中央や脅威の多い手から読む")]
for i, (h, d) in enumerate(items):
    y = 1.3 + i * 1.3
    box(s, 5.2, y, 7.5, 1.1, fill=LIGHT, line=None, name=f"要素{i + 1}")
    text(s, 5.4, y + 0.12, 7.1, 0.4, h, size=20, bold=True, color=GREEN)
    text(s, 5.4, y + 0.56, 7.1, 0.45, d, size=16)
text(s, 5.2, 5.3, 7.5, 0.9, [f"検証：正解つきの{fmt(N['verify_positions'])}局面で、不一致は{N['verify_mismatches']}",
                              "C++で実装し、ctypesでPythonから呼び出す"], size=20, bold=True, color=GREEN, space_after=4)
text(s, 0.6, 6.62, 12.1, 0.35, "手法と検証用の局面：P. Pons, Solving Connect 4（blog.gamesolver.org）を参考に自作", size=14, color=GRAY)
slides.append(s)

# ---------------------------------------------------------------- 6 book + integration
s = content_slide(prs, "v7②：序盤は定石、以降は読み切りで2秒に収める", 5)
lx, lw, rx, rw, bh = 0.7, 4.9, 6.9, 5.6, 0.62
ys = [1.3, 2.3, 3.3, 4.3]
left = ["盤面を取得（main.py）", "定石にある局面か", "C++ソルバーで読み切り", "Pythonの予備ソルバー"]
right = [None, "定石の手を返す", "最善手を返す", "必ず合法手を返す"]
lab_r = [None, "はい", "完了", ""]
lab_d = ["", "いいえ", "失敗・時間切れ", None]
for i in range(4):
    box(s, lx, ys[i], lw, bh, left[i], size=19, name=f"流れ{i + 1}")
    if right[i]:
        box(s, rx, ys[i], rw, bh, right[i], size=19, name=f"返す{i}")
        line(s, lx + lw, ys[i] + bh / 2, rx, ys[i] + bh / 2, arrow=True, name=f"右矢印{i}")
        if lab_r[i]:
            text(s, lx + lw + 0.15, ys[i] + 0.02, 1.6, 0.26, lab_r[i], size=13, color=GRAY)
    if lab_d[i] is not None:
        line(s, lx + lw / 2, ys[i] + bh, lx + lw / 2, ys[i + 1], arrow=True, name=f"下矢印{i}")
        if lab_d[i]:
            text(s, lx + lw / 2 + 0.12, ys[i] + bh + 0.06, 2.2, 0.26, lab_d[i], size=13, color=GRAY)
ob = N["offbook_v7"]
l13 = [x for x in N["verify_sets"] if x["set"].startswith("L1_R3")][0]
text(s, 0.7, 5.2, 12.0, 1.5, [
    [("定石：", {"bold": True, "color": GREEN}),
     (f"{fmt(N['book_v7_entries'])}局面（{N['book_v7_mb']}MB）。石が{N['book_v7_p1_plies'][0]}〜{N['book_v7_p1_plies'][1]}個で、自分の手番に現れる局面", {})],
    [("理由：", {"bold": True, "color": GREEN}),
     (f"序盤の読み切りは最長{l13['max_s']:.1f}秒かかった（難しい{l13['n']}局面で計測）", {})],
    [("定石の外：", {"bold": True, "color": GREEN}),
     (f"読み切りは最長{ob['max_ms'] / 1000:.2f}秒（{fmt(ob['n'])}局面で計測、時間切れ{ob['timeouts']}）", {})]],
    size=19, space_after=5)
slides.append(s)

# ---------------------------------------------------------------- 7 v7 result
p1, p2 = N["p1_wdl"], N["p2_wdl"]
s = content_slide(prs, f"v7の結果：先手{p1[0]}戦全勝、後手は{wdl(p2)}", 6)
cd = CategoryChartData()
cd.categories = [f"後手（{N['p2_games']}局）", f"先手（{N['p1_games']}局）"]
cd.add_series("勝ち", (p2[0], p1[0]))
cd.add_series("引き分け", (p2[1], p1[1]))
cd.add_series("負け", (p2[2], p1[2]))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED, Inches(0.5), Inches(1.2), Inches(7.6), Inches(3.9), cd)
gf.name = "先手後手の勝敗"
ch = gf.chart
ch.font.size = Pt(16)
ch.font.name = FONT
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
ch.value_axis.visible = False
ch.value_axis.has_major_gridlines = False
ch.value_axis.maximum_scale = max(sum(p1), sum(p2))
ch.category_axis.format.line.color.rgb = rgb("D4D4D4")
pl = ch.plots[0]
pl.gap_width = 60
pl.overlap = 100
for ser, col, fc in zip(pl.series, (GREEN, BLUE, "C9CECB"), (WHITE, TXT, TXT)):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    dl = ser.data_labels
    dl.show_value = True
    dl.number_format = "0;;"
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.CENTER
    dl.font.size = Pt(18)
    dl.font.bold = True
    dl.font.color.rgb = rgb(fc)
facts = [("0局", "エラー・時間切れ・反則手"), ("0回", "2秒を超えた手"), (f"{N['opponents_distinct']}", "対戦した相手チームの数")]
for i, (big, lab) in enumerate(facts):
    y = 1.35 + i * 1.22
    box(s, 8.5, y, 4.2, 1.05, fill=LIGHT, line=None, name=f"事実{i + 1}")
    text(s, 8.7, y + 0.1, 1.1, 0.85, big, size=26, bold=True, color=GREEN, anchor="m")
    text(s, 9.85, y + 0.1, 2.8, 0.85, lab, size=15, anchor="m")
text(s, 0.6, 5.25, 12.1, 0.4, f"Kaggleの記録{N['games_total']}局 ＝ 対戦{N['games_real']}局 ＋ 提出時の自己対戦{N['games_selfplay']}局",
     size=16, color=GRAY)
text(s, 0.6, 5.85, 12.1, 0.5, "Kaggle提出スコア　v7：＿＿＿＿（発表前に記入）", size=21, bold=True, color=GREEN)
slides.append(s)

# ---------------------------------------------------------------- 8 the losses are forced
s = content_slide(prs, f"後手の{N['p2_losses']}敗は、全手が最善の相手で防げない", 7)
text(s, 0.9, 1.25, 11.5, 0.4, f"後手の{N['p2_games']}局", size=20, bold=True)
tw = 11.5
w1 = tw * N["p2_losses"] / N["p2_games"]
box(s, 0.9, 1.75, w1, 0.95, f"相手が全手で最善 → {N['p2_losses']}敗", size=20, bold=True, color=WHITE, fill=GRAY, line=None,
    name="負けの割合")
box(s, 0.9 + w1, 1.75, tw - w1, 0.95, f"{N['p2_nonloss']}局", size=20, bold=True, color=WHITE, fill=GREEN, line=None,
    name="ミスの割合")
text(s, 0.9 + w1 - 2.6, 2.78, tw - w1 + 2.6, 0.4, f"相手がミス → {N['p2_wins']}勝{N['p2_draws']}分", size=16, color=GREEN,
     bold=True, align="r")
stats = [(f"{N['p2_loss_lengths'][0]}手目", f"{N['p2_losses']}敗のすべてが終局した手数", "双方最善のときの手数と同じ"),
         (f"{N['p2_loss_opp_inacc'] + N['p2_loss_opp_errors']}手", f"相手の{fmt(N['p2_loss_opp_moves'])}手のうち", "最短勝ちでない手"),
         (f"{N['my_score_inacc']}手", f"自分の手のうち（全{N['games_total']}局）", "最善でない手")]
for i, (big, l1, l2) in enumerate(stats):
    x = 0.9 + i * 3.95
    box(s, x, 3.5, 3.6, 2.1, fill=LIGHT, line=None, name=f"数値{i + 1}")
    text(s, x, 3.62, 3.6, 0.8, big, size=36, bold=True, color=GREEN, align="c", anchor="m")
    text(s, x + 0.15, 4.5, 3.3, 1.0, [l1, l2], size=16, align="c")
text(s, 0.9, 5.95, 11.5, 0.5, "相手は完全ソルバー。こちらがどの手を選んでも、結果は変わらない", size=21, bold=True, color=GREEN)
slides.append(s)

# ---------------------------------------------------------------- 9 where is the room
s = content_slide(prs, "伸ばせるのは「ミスをする相手との後手局」だけ", 8)
fe = N["p2_first_error_moves"]
cats = sorted(set(fe))
cd = CategoryChartData()
cd.categories = [f"{m}手目" for m in cats]
cd.add_series("局数", [fe.count(m) for m in cats])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.75), Inches(5.6), Inches(3.9), cd)
gf.name = "最初のミスの手数"
ch = gf.chart
ch.font.size = Pt(16)
ch.font.name = FONT
ch.has_legend = False
ch.has_title = False
ch.value_axis.visible = False
ch.value_axis.has_major_gridlines = False
ch.value_axis.minimum_scale = 0
ch.category_axis.format.line.color.rgb = rgb("D4D4D4")
pl = ch.plots[0]
pl.gap_width = 70
pl.series[0].format.fill.solid()
pl.series[0].format.fill.fore_color.rgb = rgb(GREEN)
pl.has_data_labels = True
dl = pl.data_labels
dl.show_value = True
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size = Pt(18)
dl.font.bold = True
text(s, 0.6, 1.25, 5.6, 0.4, f"相手が最初にミスをした手数（{N['p2_nonloss']}局）", size=18, bold=True)
share = round(100 * N["p2_nonloss"] / N["p2_games"])
det = round(100 * N["det_same_total"] / N["det_rep_total"])
pts = [(f"{N['p2_nonloss']}局", ["相手がミスをした後手局", f"（後手局の{share}%、{N['p2_nonloss_opponents']}チーム）"]),
       (f"{N['p2_wins']}勝{N['p2_draws']}分", ["ミスの後は取りこぼしなし"]),
       (f"{N['p2_nonloss_444444']}局", ["中央列に6個積んだ形から始まった局", f"（{N['p2_nonloss']}局のうち）"]),
       (f"{det}%", ["同じ局面で相手が同じ手を打った割合", "（2回以上現れた局面で集計）"])]
for i, (big, lab) in enumerate(pts):
    y = 1.3 + i * 1.12
    box(s, 6.5, y, 6.2, 0.98, fill=LIGHT, line=None, name=f"要点{i + 1}")
    text(s, 6.65, y + 0.08, 1.75, 0.82, big, size=24, bold=True, color=GREEN, anchor="m")
    text(s, 8.45, y + 0.08, 4.15, 0.82, lab, size=15, anchor="m")
text(s, 0.6, 5.95, 12.1, 0.5, "相手のミスを増やせれば、引き分けを勝ちに、負けを引き分けにできる可能性がある", size=20, bold=True, color=GREEN)
slides.append(s)

# ---------------------------------------------------------------- 10 the v8 rule
rr = [r for r in N["reply_rows"] if r["res"] == "D" and r["old_pl"] == 1 and r["new_pl"] >= 4][0]
s = content_slide(prs, "v8：同じ評価値なら、相手の正解が少ない手を選ぶ", 9)
text(s, 0.6, 1.25, 12.1, 0.4, f"例：{rr['ply']}手目、引き分けの局面（記録した対局から）。どちらの手も評価値は同じ", size=18, bold=True)


def reply_row(y, tag, col, good, pl, note):
    box(s, 0.7, y, 2.9, 0.8, [[(tag, {"bold": True}), (f"（{col}列目）", {})]], size=18, name=f"{tag}")
    line(s, 3.6, y + 0.4, 4.3, y + 0.4, arrow=True, name=f"{tag} 矢印")
    text(s, 4.35, y - 0.32, 3.2, 0.28, "相手の応手", size=13, color=GRAY)
    for k in range(pl):
        ok = k < good
        box(s, 4.4 + k * 0.72, y + 0.12, 0.56, 0.56, fill=GREEN if ok else WHITE, line=GREEN if ok else ORANGE,
            line_w=1 if ok else 2.25, shape=MSO_SHAPE.OVAL, name=f"{tag} 応手{k + 1}")
    text(s, 8.3, y, 4.5, 0.8, note, size=17, anchor="m")


reply_row(2.15, "v7の手", rr["old_col"], rr["old_good"], rr["old_pl"], f"候補{rr['old_pl']}手・正解{rr['old_good']}手（迷う余地がない）")
reply_row(3.45, "v8の手", rr["new_col"], rr["new_good"], rr["new_pl"], f"候補{rr['new_pl']}手・正解は{rr['new_good']}手だけ")
box(s, 0.7, 4.42, 0.3, 0.3, fill=GREEN, line=GREEN, shape=MSO_SHAPE.OVAL, name="凡例 正解")
text(s, 1.1, 4.4, 4.6, 0.35, "正解：引き分けを保つ手", size=14, color=GRAY)
box(s, 5.6, 4.42, 0.3, 0.3, fill=WHITE, line=ORANGE, line_w=2.25, shape=MSO_SHAPE.OVAL, name="凡例 ミス")
text(s, 6.0, 4.4, 6.0, 0.35, "ミス：こちらの勝ちに変わる手（すぐ負ける手は候補から除く）", size=14, color=GRAY)
text(s, 0.6, 5.0, 12.1, 1.5, [
    [("勝ちの局面：", {"bold": True, "color": GREEN}), ("最短で勝つ手（v7と同じ）", {})],
    [("引き分け・負けの局面：", {"bold": True, "color": GREEN}), ("評価値が同じ手の中で、相手の正解が最も少ない手", {})],
    [("罠表：", {"bold": True, "color": GREEN}),
     (f"記録で相手がミスをした手順の{N['traps_entries']}局面では、評価値が同じならその手を選ぶ", {})]],
    size=19, space_after=5)
slides.append(s)

# ---------------------------------------------------------------- 11 validation
s = content_slide(prs, "v8はv7に劣らないが、全体の勝率差は見えない", 10)
replay_total = sum(N[k] for k in ("replay_D_different", "replay_D_same", "replay_L_different", "replay_L_same",
                                  "replay_W_same"))
rows = [["検証の内容", "v7", "v8"],
        [f"v8 対 v7　{sum(N['new_vs_old_all'])}局", "—", "互いに先手番で全勝"],
        ["random・Negamax　各100局", "全勝", "全勝"],
        [f"ミスをする模擬相手　後手{fmt(N['mix_big_p2_games'])}局", wdl(N["mix_big_v7_p2"]), wdl(N["mix_big_v8_p2"])],
        [f"手が変わる{N['kp_mix_positions']}局面から　各{N['kp_mix_games_each']}局", wdl(N["kp_mix_v7"]), wdl(N["kp_mix_v8"])],
        ["Kaggleの実戦", f"{N['games_total']}局を分析", "提出済み・記録は未収集"]]
table(s, 0.6, 1.3, 12.1, [5.3, 3.3, 3.5], rows, size=18, row_h=0.64, bold_rows=(3, 4), name="検証の表")
text(s, 0.6, 5.3, 12.1, 1.4, [
    f"・対局全体では差なし：手が変わるのは、記録した後手局の{fmt(replay_total)}局面のうち{N['replay_diff_positions']}局面だけ",
    f"・{N['kp_mix_positions']}局面の内訳：改善{N['kp_mix_better']}、同じ{N['kp_mix_same']}、わずかに悪化{N['kp_mix_worse']}",
    [("・効果が見えたのは模擬相手だけ。実戦での効果は未確認", {"bold": True, "color": GREEN})]], size=19, space_after=4)
slides.append(s)

# ---------------------------------------------------------------- 12 summary
s = content_slide(prs, "まとめ：先手は完全、後手の改善は実戦で未検証", 11)
text(s, 0.6, 1.25, 12.1, 0.45, "今週の成果", size=24, bold=True)
text(s, 0.6, 1.8, 12.1, 1.5, [f"・v7：完全ソルバーと定石で、先手{p1[0]}戦全勝・エラー0",
                               f"・{N['games_total']}局の分析：後手の{N['p2_losses']}敗は理論どおりの負けで、自分の悪手は0",
                               "・v8：同じ評価値の手の選び分けを実装し、模擬対局で確認"], size=20, space_after=4)
text(s, 0.6, 3.45, 12.1, 0.45, "限界", size=24, bold=True)
text(s, 0.6, 4.0, 12.1, 1.1, ["・後手は、相手が最善なら必ず負ける（ゲームの性質）",
                               f"・記録は1回の提出の{N['games_total']}局だけ。v8の効果は模擬相手でしか見ていない"], size=20, space_after=4)
text(s, 0.6, 5.2, 12.1, 0.45, "今後の課題", size=24, bold=True)
text(s, 0.6, 5.75, 12.1, 1.1, ["・v8の実戦記録を集め、v7と同じ方法で比べる", "・相手のミスの記録を増やし、罠表を広げる"], size=20, space_after=4)
slides.append(s)

# ---------------------------------------------------------------- 13 appendix: rating
s = content_slide(prs, "付録：順位はスキルレートμで決まる", 12)
steps = ["提出", "自己対戦で確認", "μ＝600で開始", ["レートの近い", "相手と対局"], "μとσを更新"]
sw, sg = 2.2, 0.3
for i, t in enumerate(steps):
    x = 0.6 + i * (sw + sg)
    box(s, x, 1.5, sw, 0.95, t, size=17, fill=LIGHT if i < 4 else GREEN, color=TXT if i < 4 else WHITE, name=f"手順{i + 1}")
    if i < 4:
        line(s, x + sw, 1.975, x + sw + sg, 1.975, arrow=True, name=f"手順矢印{i + 1}")
text(s, 0.6, 2.95, 12.1, 3.2, ["・各提出のレートは、正規分布 N(μ, σ²) で表される（μ：強さの推定値、σ：不確かさ）",
                               "・勝つとμが上がり、負けると下がる。引き分けは両者のμが近づく",
                               "・変化の大きさは、対局前のμから見た予想とのずれと、σで決まる",
                               "・対局を重ねるとσは小さくなる",
                               "・リーダーボードには、各チームの最も良い提出のμが載る"], size=20, space_after=8)
text(s, 0.6, 6.62, 12.1, 0.35, "出典：Kaggle Connect X の Evaluation ページ（2026年10月28日に確認）", size=14, color=GRAY)
slides.append(s)

# ---------------------------------------------------------------- 14 appendix: opponents
s = content_slide(prs, "付録：よく当たる相手は、同じ局面で同じ手を打つ", 13)
rows = [["相手（多い順）", "対局", "自分が先手", "自分が後手", "同じ手／重複局面"]]
for o in N["top_opponents"]:
    rows.append([o["opp"], str(o["games"]), wdl(o["p1"]), wdl(o["p2"]), f"{o['same']}／{o['rep']}"])
table(s, 0.6, 1.25, 12.1, [3.6, 1.2, 2.4, 2.4, 2.5], rows, size=16, row_h=0.5, aligns=["l", "c", "c", "c", "c"],
      name="相手の表")
text(s, 0.6, 5.95, 12.1, 0.8, ["重複局面：その相手の手番で2回以上現れた局面。同じ手：毎回同じ列を選んだ局面",
                               f"全相手の合計では {N['det_same_total']}／{N['det_rep_total']}"], size=15, color=GRAY, space_after=3)
slides.append(s)

# ---------------------------------------------------------------- notes
assert len(slides) == len(scripts), (len(slides), len(scripts))
for s, sc in zip(slides, scripts):
    s.notes_slide.notes_text_frame.text = sc["en"] + "\n\n【中文】\n" + sc["zh"]

prs.save(OUT)

# replace the template's stale docProps/app.xml (old slide titles) with a minimal one
import shutil, zipfile
APP = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
       '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
       f'<TotalTime>0</TotalTime><Application>Microsoft Office PowerPoint</Application><Slides>{len(slides)}</Slides>'
       f'<Notes>{len(slides)}</Notes></Properties>')
tmp = OUT + ".tmp"
with zipfile.ZipFile(OUT) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, APP if it.filename == "docProps/app.xml" else zin.read(it.filename))
shutil.move(tmp, OUT)
print("saved", OUT, "slides:", len(slides))
