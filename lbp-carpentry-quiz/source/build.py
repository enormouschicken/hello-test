"""Build the LBP Carpentry practice quiz from the question files.

Outputs (in dist/):
  quiz.html                          page body for the hosted artifact (Google Fonts link, no doctype)
  LBP-Carpentry-Practice-Quiz.html   single-file offline copy (fonts embedded, works without internet)
  print.html                         printable booklet, rendered to PDF by render_pdf.js
  questions.json                     the balanced question bank, for reference
"""
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from parse_questions import load_all

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
LETTERS = "ABCDE"

AREAS = [
    {"id": "rbw", "code": "RBW", "name": "Restricted building work & records of work", "focus": True,
     "blurb": "What is and isn't RBW, owner-builders, supervision, and records of work."},
    {"id": "e2", "code": "E2/AS1", "name": "Weathertightness & clearances", "focus": True,
     "blurb": "Ground and roof clearances, the risk matrix, cavities, windows, flashings and decks (4th edition)."},
    {"id": "brace", "code": "NZS 3604 · B", "name": "Bracing", "focus": True,
     "blurb": "Bracing demand, wind and earthquake zones, bracing lines, elements, hold-downs and diaphragms."},
    {"id": "struct", "code": "NZS 3604", "name": "Foundations, framing & timber",
     "blurb": "Good ground, piles, subfloors, slabs, timber grades and treatment, fixings and span tables."},
    {"id": "act", "code": "ACT", "name": "Building Act, Code & consents",
     "blurb": "Building Code clauses, ways to comply, consents, inspections, variations, exemptions and CCCs."},
    {"id": "lbp", "code": "LBP", "name": "Licensing, ethics & discipline",
     "blurb": "Licence classes, the assessment, renewal, skills maintenance, the Code of Ethics and the Board."},
    {"id": "con", "code": "CON", "name": "Contracts & consumer protection",
     "blurb": "Written contracts, disclosure, implied warranties, defect repairs and the Construction Contracts Act."},
    {"id": "hs", "code": "H&S", "name": "Health & safety on site",
     "blurb": "PCBU and worker duties, notifiable events and work, controls, working at height and asbestos."},
    {"id": "mock", "code": "MOCK", "name": "Mixed mock assessment",
     "blurb": "A random round of 25 drawn from every area, like the real assessment conversation."},
]
AREA_ORDER = [a["id"] for a in AREAS if a["id"] != "mock"]


def keeps_order(q):
    opts = q["options"]
    if q.get("keep"):
        return True
    if any(re.search(r"\b(all|none) of the above\b", o, re.I) for o in opts):
        return True
    return all(re.match(r"^[\$\d]", o) for o in opts)


def balance(questions):
    """Swap each free-order question's correct option into the least-used letter for its area."""
    by_area = defaultdict(list)
    for q in questions:
        by_area[q["area"]].append(q)
    for items in by_area.values():
        counts = Counter(q["answer"] for q in items if keeps_order(q))
        for q in items:
            if keeps_order(q):
                continue
            n = len(q["options"])
            h = int(hashlib.md5(q["id"].encode()).hexdigest(), 16)
            target = sorted(range(n), key=lambda i: (counts[i], (i + h) % n))[0]
            a = q["answer"]
            if target != a:
                q["options"][target], q["options"][a] = q["options"][a], q["options"][target]
                q["answer"] = target
            counts[target] += 1
    return questions


def font_css(path):
    """Merge Google Fonts blocks that share one variable-font file into a single weight range."""
    css = Path(path).read_text()
    blocks = re.findall(r"(/\*\s*[\w-]+\s*\*/)\s*@font-face\s*{([^}]*)}", css)
    groups, order = {}, []
    for comment, body in blocks:
        fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        weight = int(re.search(r"font-weight:\s*(\d+)", body).group(1))
        src = re.search(r"src:\s*(url\([^)]+\)\s*format\('woff2'\))", body).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()
        key = (fam, style, src, rng)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(weight)
    out = []
    for fam, style, src, rng in order:
        ws = sorted(groups[(fam, style, src, rng)])
        wcss = str(ws[0]) if len(ws) == 1 else f"{ws[0]} {ws[-1]}"
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wcss};font-display:swap;src:{src};unicode-range:{rng};}}")
    return "\n".join(out)


def page_data(questions):
    qs = [{k: q[k] for k in ("id", "area", "kind", "q", "options", "answer", "explain", "note", "ref")} for q in questions]
    for q in qs:
        if not q["note"]:
            del q["note"]
    areas = [{k: a[k] for k in ("id", "code", "name", "blurb")} | ({"focus": True} if a.get("focus") else {}) for a in AREAS]
    return ("const AREAS = " + json.dumps(areas, ensure_ascii=False) + ";\n  const QUESTIONS = "
            + json.dumps(qs, ensure_ascii=False, separators=(",", ":")) + ";")


def build_pages(questions):
    template = (ROOT / "template.html").read_text()
    n_areas = len(AREA_ORDER)
    page = (template.replace("/*__DATA__*/", page_data(questions))
            .replace("__NQ__", str(len(questions))).replace("__NA__", str(n_areas)))
    (DIST / "quiz.html").write_text(page)

    # Offline single file: real document skeleton, embedded fonts, no external requests.
    body = re.sub(r'<link[^>]+fonts\.(googleapis|gstatic)\.com[^>]*>\n?', "", page)
    title = re.search(r"<title>.*?</title>", body).group(0)
    body = body.replace(title, "", 1)
    offline = ("<!doctype html>\n<html lang=\"en-NZ\">\n<head>\n<meta charset=\"utf-8\">\n"
               "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
               f"{title}\n<style>{font_css(ROOT / 'fonts-inline.css')}</style>\n"
               "<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}"
               ":root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n"
               "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    (DIST / "LBP-Carpentry-Practice-Quiz.html").write_text(offline)


def e(s):
    return html.escape(s, quote=False)


def build_print(questions):
    numbered = []
    n = 0
    for aid in AREA_ORDER:
        for q in (q for q in questions if q["area"] == aid):
            n += 1
            numbered.append((n, q))
    area_of = {a["id"]: a for a in AREAS}
    ranges = {}
    for num, q in numbered:
        lo, hi = ranges.get(q["area"], (num, num))
        ranges[q["area"]] = (min(lo, num), max(hi, num))

    contents = "".join(
        f"<tr><td class='mono'>{e(area_of[a]['code'])}</td><td>{e(area_of[a]['name'])}"
        f"{' <span class=focus>Focus</span>' if area_of[a].get('focus') else ''}</td>"
        f"<td class='mono num'>{ranges[a][0]}–{ranges[a][1]}</td></tr>" for a in AREA_ORDER)

    sections = []
    for aid in AREA_ORDER:
        a = area_of[aid]
        items = []
        for num, q in numbered:
            if q["area"] != aid:
                continue
            opts = "".join(f"<li><span class='box'>{LETTERS[i]}</span><span>{e(o)}</span></li>" for i, o in enumerate(q["options"]))
            items.append(f"<article class='q'><p class='qmeta'><span class='qn'>{num}</span>"
                         f"<span class='kind'>{e(q['kind'])}</span></p><p class='qt'>{e(q['q'])}</p><ol class='opts'>{opts}</ol></article>")
        sections.append(f"<section class='area'><header class='area-head'><p class='mono'>{e(a['code'])}</p>"
                        f"<h2>{e(a['name'])}</h2><p class='blurb'>{e(a['blurb'])} Questions {ranges[aid][0]}–{ranges[aid][1]}.</p></header>"
                        + "".join(items) + "</section>")

    grid = []
    for aid in AREA_ORDER:
        a = area_of[aid]
        cells = "".join(f"<span><b>{num}</b> {LETTERS[q['answer']]}</span>" for num, q in numbered if q["area"] == aid)
        grid.append(f"<div class='grid-area'><p class='mono'>{e(a['code'])} · {e(a['name'])}</p><div class='grid'>{cells}</div></div>")

    keys = []
    for aid in AREA_ORDER:
        a = area_of[aid]
        rows = []
        for num, q in numbered:
            if q["area"] != aid:
                continue
            note = f"<p class='tip'><span>Assessor's note</span> {e(q['note'])}</p>" if q.get("note") else ""
            rows.append(f"<article class='k'><p class='kh'><span class='qn'>{num}</span><b>{LETTERS[q['answer']]}.</b> {e(q['options'][q['answer']])}</p>"
                        f"<p class='kx'>{e(q['explain'])}</p>{note}<p class='kr'>Ref: {e(q['ref'])}</p></article>")
        keys.append(f"<section class='key-area'><h3><span class='mono'>{e(a['code'])}</span> {e(a['name'])}</h3>{''.join(rows)}</section>")

    fonts = font_css(ROOT / "fonts-inline.css")
    doc = f"""<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><title>LBP Carpentry practice assessment</title>
<style>{fonts}</style>
<style>
@page {{ size: A4; margin: 15mm 14mm 17mm; }}
* {{ box-sizing: border-box; }}
:root {{ --ink:#17201C; --muted:#55625C; --rule:#CBD3CE; --tape:#F2C230; --accent:#1D5FA6; --good:#22744A; }}
body {{ margin:0; color:var(--ink); font-family:"Atkinson Hyperlegible Next", Arial, sans-serif; font-size:9.6pt; line-height:1.38; }}
.mono {{ font-family:"IBM Plex Mono", monospace; letter-spacing:.06em; text-transform:uppercase; font-size:7.6pt; color:var(--muted); margin:0; }}
h1, h2, .display {{ font-family:"Big Shoulders Stencil Display", "Arial Narrow", sans-serif; font-weight:800; text-transform:uppercase; letter-spacing:.01em; }}
.cover {{ page-break-after: always; padding-top: 18mm; }}
.cover h1 {{ font-size:46pt; line-height:.9; margin:4mm 0 5mm; }}
.cover .lede {{ font-size:12pt; max-width:150mm; margin:0 0 8mm; }}
.tape {{ height:9mm; background:var(--tape); margin:0 0 9mm; border-radius:1mm;
  background-image:repeating-linear-gradient(90deg, var(--ink) 0 .3mm, transparent .3mm 4mm); background-size:100% 2.6mm; background-repeat:no-repeat; }}
.cover h2 {{ font-size:15pt; margin:7mm 0 2.5mm; }}
.cover ol, .cover ul {{ margin:0; padding-left:5mm; }}
.cover li {{ margin-bottom:1.4mm; }}
table.contents {{ border-collapse:collapse; width:100%; font-size:10pt; }}
table.contents td {{ padding:1.6mm 2mm; border-bottom:.3mm solid var(--rule); }}
table.contents td.num {{ text-align:right; white-space:nowrap; }}
.focus {{ font-family:"IBM Plex Mono", monospace; font-size:6.8pt; letter-spacing:.06em; text-transform:uppercase; background:var(--tape); padding:.3mm 1.4mm; border-radius:.6mm; margin-left:1.5mm; }}
.small {{ font-size:8.4pt; color:var(--muted); }}
.area {{ page-break-before: always; }}
.area-head {{ border-bottom:.6mm solid var(--ink); padding-bottom:2.5mm; margin-bottom:3.5mm; }}
.area-head h2 {{ font-size:24pt; margin:1mm 0 1mm; line-height:1; }}
.blurb {{ margin:0; color:var(--muted); font-size:9pt; }}
.q {{ break-inside: avoid; padding:2.6mm 0 2.8mm; border-bottom:.25mm solid var(--rule); }}
.qmeta {{ margin:0 0 .8mm; display:flex; gap:2.5mm; align-items:baseline; }}
.qn {{ font-family:"IBM Plex Mono", monospace; font-weight:600; font-size:9pt; min-width:7mm; }}
.kind {{ font-family:"IBM Plex Mono", monospace; font-size:7pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); }}
.qt {{ margin:0 0 1.6mm; font-weight:700; }}
.opts {{ list-style:none; margin:0; padding:0 0 0 7mm; display:grid; gap:1mm; }}
.opts li {{ display:grid; grid-template-columns:6mm 1fr; gap:2mm; align-items:start; }}
.box {{ display:inline-grid; place-items:center; width:4.6mm; height:4.6mm; border:.3mm solid var(--ink); border-radius:.8mm;
  font-family:"IBM Plex Mono", monospace; font-size:7.4pt; font-weight:600; }}
.key-start {{ page-break-before: always; }}
.key-start h2 {{ font-size:30pt; margin:0 0 2mm; }}
.grid-area {{ break-inside: avoid; margin:0 0 4mm; }}
.grid {{ display:grid; grid-template-columns:repeat(10, 1fr); gap:.8mm; margin-top:1.2mm; }}
.grid span {{ border:.25mm solid var(--rule); border-radius:.6mm; padding:.8mm 1.2mm; font-family:"IBM Plex Mono", monospace; font-size:8pt; }}
.grid b {{ font-weight:600; color:var(--muted); margin-right:.8mm; }}
.key-area {{ margin-top:5mm; }}
.key-area h3 {{ font-family:"Big Shoulders Stencil Display", sans-serif; font-weight:800; text-transform:uppercase; font-size:15pt; margin:0 0 1.5mm;
  border-bottom:.5mm solid var(--ink); padding-bottom:1.2mm; break-after: avoid; }}
.key-area h3 .mono {{ font-size:8pt; margin-right:2mm; }}
.k {{ break-inside: avoid; padding:2mm 0 2.2mm; border-bottom:.25mm solid var(--rule); }}
.kh {{ margin:0 0 .8mm; }}
.kh .qn {{ display:inline-block; min-width:9mm; }}
.kh b {{ color:var(--good); margin-right:1mm; }}
.kx {{ margin:0 0 .8mm; }}
.tip {{ margin:0 0 .8mm; padding:1.2mm 2mm; background:#EDF0ED; border-radius:.8mm; font-size:8.8pt; }}
.tip span {{ font-family:"IBM Plex Mono", monospace; font-size:6.8pt; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); margin-right:1mm; }}
.kr {{ margin:0; font-family:"IBM Plex Mono", monospace; font-size:7.2pt; color:var(--muted); }}
</style></head><body>
<section class="cover">
  <p class="mono">Licensed Building Practitioner · New Zealand</p>
  <h1>LBP Carpentry<br>practice assessment</h1>
  <div class="tape"></div>
  <p class="lede">{len(questions)} multiple-choice questions in {len(AREA_ORDER)} study areas, written the way an assessor asks them. The answer key with explanations is at the back.</p>
  <h2>How to use this booklet</h2>
  <ol>
    <li>Pick a study area and answer every question in it. Tick a box: A, B, C or D.</li>
    <li>Mark your answers with the quick answer grid at the start of the answer key.</li>
    <li>Read the explanation for every question you missed or guessed. The reference tells you where to look it up.</li>
    <li>Mark the questions you want to go over and bring them to a study session or to Claude.</li>
  </ol>
  <h2>Contents</h2>
  <table class="contents"><tbody>{contents}<tr><td class="mono">Key</td><td>Answer key: quick grid, then explanations</td><td class="mono num">1–{len(questions)}</td></tr></tbody></table>
  <h2>Sources</h2>
  <p class="small">The LBP Handbook (MBIE), Carpentry licence class competencies (LBP Rules Schedule 1), Building Act 2004, NZS 3604:2011 as cited by B1/AS1 2nd edition, E2/AS1 4th edition, B2/AS1 3rd edition, H1/AS1 6th edition, the Building Product Specifications, GIB EzyBrace guidance, the Construction Contracts Act 2002 and WorkSafe guidance. Checked October 2026. Where the LBP Handbook is out of date (for example, the Board's maximum fine is $10,000 under s318, not $50,000), the questions follow the Act. Rules change, so check the current documents on building.govt.nz and lbp.govt.nz before your assessment.</p>
</section>
{''.join(sections)}
<section class="key-start">
  <p class="mono">Answer key</p>
  <h2>Quick answer grid</h2>
  {''.join(grid)}
</section>
{''.join(keys)}
</body></html>"""
    (DIST / "print.html").write_text(doc)
    return len(numbered)


def main():
    questions, errors = load_all(ROOT / "questions")
    if errors:
        raise SystemExit("\n".join(errors))
    order = {aid: i for i, aid in enumerate(AREA_ORDER)}
    questions.sort(key=lambda q: (order[q["area"]], q["_file"], q["_line"]))
    balance(questions)
    for q in questions:
        q.pop("_file", None); q.pop("_line", None)
    (DIST / "questions.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1))
    build_pages(questions)
    build_print(questions)
    dist = defaultdict(Counter)
    for q in questions:
        dist[q["area"]][LETTERS[q["answer"]]] += 1
    for aid in AREA_ORDER:
        print(f"{aid:7} {sum(dist[aid].values()):3}  " + " ".join(f"{k}{dist[aid].get(k, 0)}" for k in "ABCD"))
    print("total", len(questions))
    for f in ("quiz.html", "LBP-Carpentry-Practice-Quiz.html", "print.html"):
        print(f"{f}: {(DIST / f).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
