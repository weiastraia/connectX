# Build the bilingual speaker script (English left, Chinese right) as HTML, then print to PDF with Chromium.
# usage (from repo root): python3 presentation/tools/build_script_pdf.py <dir with slide-NN.jpg>
import base64, html, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_text import slide_scripts

P = "presentation"
N = json.load(open(f"{P}/numbers.json"))
S = slide_scripts(N)
img_dir = sys.argv[1]
WPM = 110  # slow, clear pace

e = html.escape


def img(i):
    p = os.path.join(img_dir, f"slide-{i:02d}.jpg")
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()


words = [len(s["en"].split()) for s in S]


def onslide(i):
    # the template counts the title slide as 0, so the number printed on a slide is one less
    return "" if i == 1 else f"（number on the slide / 幻灯片上的页码：{i - 1}）"

main = sum(words[:12])
rows = []
rows.append(f"""
<section class="cover">
<h1>Kaggle Connect X — Week 4 — Speaker Script</h1>
<h1 class="zh">Kaggle Connect X 第4周 讲稿</h1>
<table class="two"><tr>
<td><p>Left side: English. Right side: Chinese.</p>
<p>The English text is the same as the speaker notes in the PowerPoint file.</p>
<p>Main slides 1–12: about {main} words. At a slow pace ({WPM} words per minute) this is about {round(main / WPM)} minutes.</p>
<p>Slides 13–14 are backup slides for questions.</p>
<p>All numbers come from <code>presentation/numbers.json</code>.</p>
<p>"Slide 5" here means the 5th slide in the file. The number printed on that slide is 4, because the title slide is counted as 0.</p></td>
<td class="zh"><p>左边是英文，右边是中文。</p>
<p>英文内容和 PPT 演讲者备注里的英文相同。</p>
<p>正文第1–12页约 {main} 个英文单词，按较慢的语速（每分钟 {WPM} 词）大约 {round(main / WPM)} 分钟。</p>
<p>第13–14页是付録，用来回答提问。</p>
<p>所有数字都来自 <code>presentation/numbers.json</code>。</p>
<p>这里的“第5页”指文件里的第5张幻灯片。那张幻灯片上印的页码是4，因为模板把封面算作第0页。</p></td></tr></table>
<h2>Five questions to prepare / 重点准备的五个问题</h2>
<table class="two idx">
<tr><td>Why not just use an open-source solver? → slide 5</td><td class="zh">为什么不直接用开源求解器？→ 第5页</td></tr>
<tr><td>Why must the second player lose? → slides 3 and 8</td><td class="zh">后手为什么必输？→ 第3页、第8页</td></tr>
<tr><td>Does the "luring" strategy really work? → slides 10 and 11</td><td class="zh">“诱敌”策略真的有效吗？→ 第10页、第11页</td></tr>
<tr><td>Are {N['games_total']} games enough? → slides 7 and 9</td><td class="zh">{N['games_total']} 局样本够吗？→ 第7页、第9页</td></tr>
<tr><td>How is the ranking calculated? → slides 2 and 13</td><td class="zh">排名怎么算？→ 第2页、第13页</td></tr>
</table>
</section>""")

for i, s in enumerate(S, 1):
    qa = ""
    for k, q in enumerate(s["qa"], 1):
        qa += f"""
<tr class="q"><td><b>Q{k}.</b> {e(q['q_en'])}</td><td class="zh"><b>问{k}：</b>{e(q['q_zh'])}</td></tr>
<tr class="a"><td><b>A.</b> {e(q['a_en'])}</td><td class="zh"><b>答：</b>{e(q['a_zh'])}</td></tr>"""
    qa_block = f"""<h3>Expected questions / 预计的提问</h3><table class="two qa">{qa}</table>""" if qa else ""
    en_sent = f"<p>{e(s['en'])}</p>"
    rows.append(f"""
<section class="slide">
<div class="head"><img src="{img(i)}"><div><div class="num">Slide {i} / 第{i}页{onslide(i)} · about {max(5, round(words[i - 1] / WPM * 60 / 5) * 5)} s</div>
<div class="ja">{e(s['title'])}</div></div></div>
<table class="two script"><tr><th>Script (English)</th><th class="zh">讲稿（中文）</th></tr>
<tr><td>{en_sent}</td><td class="zh"><p>{e(s['zh'])}</p></td></tr></table>
{qa_block}
</section>""")

css = """
@page { size: A4; margin: 14mm 12mm; }
body { font-family: Arial, 'DejaVu Sans', 'WenQuanYi Zen Hei', sans-serif; font-size: 11pt; color: #141414; line-height: 1.5; }
.zh { font-family: 'WenQuanYi Zen Hei', sans-serif; }
.ja { font-family: 'IPAPGothic', 'IPAGothic', sans-serif; font-size: 12pt; font-weight: bold; color: #005732; }
h1 { font-size: 17pt; margin: 0 0 4px; color: #005732; }
h2 { font-size: 12pt; margin: 16px 0 6px; }
h3 { font-size: 10.5pt; margin: 10px 0 4px; color: #47534C; }
section { break-inside: avoid; margin-bottom: 14px; }
section.cover { break-after: page; }
.head { display: flex; gap: 12px; align-items: center; margin-bottom: 6px; }
.head img { width: 62mm; border: 1px solid #C3CAC6; }
.num { font-size: 9.5pt; color: #47534C; margin-bottom: 3px; }
table.two { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.two td, table.two th { width: 50%; vertical-align: top; padding: 5px 8px; border: 1px solid #C3CAC6; }
table.two th { background: #E6EBE8; text-align: left; font-size: 9.5pt; }
table.qa tr.q td { background: #F4F6F5; }
table.two p { margin: 0 0 4px; }
code { font-size: 9pt; }
"""
doc = f"<!doctype html><html><head><meta charset='utf-8'><title>ConnectX week 4 script</title><style>{css}</style></head><body>{''.join(rows)}</body></html>"
os.makedirs(f"{P}/build", exist_ok=True)
hp = os.path.abspath(f"{P}/build/script.html")
open(hp, "w", encoding="utf-8").write(doc)
out = os.path.abspath(f"{P}/ConnectX_week4_script_EN_ZH.pdf")
js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://{hp}');
  await p.pdf({{ path: '{out}', format: 'A4', printBackground: true }});
  await b.close();
}})();
"""
subprocess.run(["node", "-e", js], check=True)
print("saved", out, "main words:", main, "minutes:", round(main / WPM, 1))
