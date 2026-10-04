"""Parse the plain-text question files into a list of dicts and validate them.

Format (one block per question):
    --- e2-01 | Site scenario
    Q: Question text (may wrap onto following lines)
    A) option
    B)* correct option (asterisk marks the answer)
    C) option
    D) option
    Why: explanation
    Tip: optional assessor's note
    Ref: source reference
"""
import json, re, sys
from collections import Counter
from pathlib import Path

FIELD = re.compile(r"^(Q|Why|Tip|Ref):\s?(.*)$")
OPT = re.compile(r"^([A-D])\)(\*?)\s?(.*)$")

def parse_file(path):
    area = Path(path).stem.split("_", 1)[-1]
    out, cur, last = [], None, None
    for n, raw in enumerate(Path(path).read_text().splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("#") or (not line.strip() and cur is None):
            continue
        if line.startswith("--- "):
            if cur: out.append(cur)
            parts = [x.strip() for x in line[4:].split("|")]
            qid, kind = parts[0], (parts[1] if len(parts) > 1 else "")
            cur = {"id": qid, "area": area, "kind": kind or "Question", "keep": "keep" in parts[2:], "options": [], "answer": None,
                   "q": "", "explain": "", "note": "", "ref": "", "_line": n, "_file": str(path)}
            last = None
            continue
        if cur is None:
            continue
        if not line.strip():
            last = None
            continue
        m = FIELD.match(line)
        if m:
            key = {"Q": "q", "Why": "explain", "Tip": "note", "Ref": "ref"}[m.group(1)]
            cur[key] = m.group(2).strip()
            last = key
            continue
        m = OPT.match(line)
        if m:
            if m.group(2):
                cur["answer"] = len(cur["options"])
            cur["options"].append(m.group(3).strip())
            last = ("opt", len(cur["options"]) - 1)
            continue
        # continuation line
        if isinstance(last, tuple):
            cur["options"][last[1]] += " " + line.strip()
        elif last:
            cur[last] += " " + line.strip()
        else:
            raise SystemExit(f"{path}:{n}: stray line: {line!r}")
    if cur: out.append(cur)
    return out

def load_all(folder):
    qs = []
    for p in sorted(Path(folder).glob("*.txt")):
        qs.extend(parse_file(p))
    errors, seen = [], set()
    for q in qs:
        where = f"{q['_file']}:{q['_line']} {q['id']}"
        if q["id"] in seen: errors.append(f"{where}: duplicate id")
        seen.add(q["id"])
        if len(q["options"]) != 4: errors.append(f"{where}: {len(q['options'])} options")
        if q["answer"] is None: errors.append(f"{where}: no answer marked")
        for k in ("q", "explain", "ref"):
            if not q[k]: errors.append(f"{where}: missing {k}")
        if '"' in q["q"] + q["explain"] + q["note"] + "".join(q["options"]):
            errors.append(f"{where}: straight double quote (use curly quotes)")
    return qs, errors

if __name__ == "__main__":
    qs, errors = load_all(sys.argv[1] if len(sys.argv) > 1 else "questions")
    by_area = Counter(q["area"] for q in qs)
    print("questions:", len(qs), dict(by_area))
    for area in by_area:
        dist = Counter("ABCD"[q["answer"]] for q in qs if q["area"] == area and q["answer"] is not None)
        print(f"  {area:7} answers: " + " ".join(f"{k}{dist.get(k,0)}" for k in "ABCD"))
    if errors:
        print("ERRORS:"); print("\n".join(errors)); sys.exit(1)
