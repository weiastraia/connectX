# Check that numbers spoken in the English script also appear on the same slide (and list the rest).
# usage: python3 presentation/tools/check_consistency.py <slide_text.md from the pptx skill>
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_text import slide_scripts

N = json.load(open("presentation/numbers.json"))
S = slide_scripts(N)
txt = open(sys.argv[1], encoding="utf-8").read()
parts = re.split(r"<!-- Slide number: \d+ -->", txt)[1:]
assert len(parts) == len(S), (len(parts), len(S))
num = lambda t: {x.rstrip(",") for x in re.findall(r"\d[\d,]*(?:\.\d+)?", t)}
bad = 0
for i, (part, sc) in enumerate(zip(parts, S), 1):
    slide_part, _, notes = part.partition("### Notes:")
    if sc["en"] not in notes.replace("\n", " ") and sc["en"] not in notes:
        bad += 1
        print(f"slide {i}: NOTES DIFFER FROM SCRIPT")
    on_slide = num(slide_part)
    spoken = num(sc["en"])
    only_spoken = sorted(spoken - on_slide)
    print(f"slide {i}: spoken numbers {len(spoken)}, not printed on the slide: {only_spoken}")
print("notes mismatches:", bad)
