# LBP Carpentry practice assessment

A multiple-choice practice quiz for the New Zealand Licensed Building Practitioner (LBP) **Carpentry** licence assessment: 237 questions in 8 study areas, with an answer key and explanations. The questions lean on site scenarios for restricted building work, E2/AS1 weathertightness and clearances, and NZS 3604 bracing.

| File | Use it for |
| --- | --- |
| `LBP-Carpentry-Practice-Quiz.html` | The interactive quiz in one file. Save it to your laptop or phone and open it in a browser. It works without internet. |
| `LBP-Carpentry-Practice-Quiz.pdf` | A printable booklet: questions by area, then a quick answer grid and full explanations at the back. |
| `source/` | The question bank (`source/questions/*.txt`) and the scripts that build the two files above. |

## Study areas

| Code | Area | Questions |
| --- | --- | --- |
| RBW | Restricted building work & records of work | 37 |
| E2/AS1 | Weathertightness & clearances | 48 |
| NZS 3604 · B | Bracing | 36 |
| NZS 3604 | Foundations, framing & timber | 30 |
| ACT | Building Act, Code & consents | 32 |
| LBP | Licensing, ethics & discipline | 25 |
| CON | Contracts & consumer protection | 14 |
| H&S | Health & safety on site | 15 |

The quiz also has a mixed mock round (25 random questions), pinning for questions to go over later, and an optional "check each answer straight away" mode.

## Sources

Checked in October 2026 against the LBP Handbook (MBIE), the Carpentry licence class competencies (LBP Rules Schedule 1), the Building Act 2004, NZS 3604:2011 as cited by B1/AS1 2nd edition, E2/AS1 4th edition, B2/AS1 3rd edition, H1/AS1 6th edition, the Building Product Specifications, GIB EzyBrace guidance, the Construction Contracts Act 2002 and WorkSafe guidance. Where the LBP Handbook is out of date (for example, the Board's maximum fine is $10,000 under s318, not the $50,000 the handbook states), the questions follow the Act.

Rules change. Check the current documents on building.govt.nz and lbp.govt.nz before your assessment.

## Rebuilding

Edit the question files in `source/questions/`, then from `source/`:

```sh
python3 build.py       # validates the questions, balances answer letters, writes dist/
node render_pdf.js     # renders dist/print.html to dist/LBP-Carpentry-Practice-Quiz.pdf (needs Playwright)
```

Each question block looks like this. The asterisk marks the correct option, and `| keep` stops the build reordering options that are in a deliberate order:

```
--- e2-01 | Site scenario
Q: What's the minimum clearance from a paved surface to the bottom of the cladding?
A) 35 mm
B) 50 mm
C)* 100 mm
D) 175 mm
Why: Explanation shown in the answer key.
Tip: Optional assessor's note.
Ref: E2/AS1 Table 9.1.2.1
```
