#!/usr/bin/env python3
"""Watch a YouTube channel: list uploads, pull transcripts and frames, score stock calls.

Needs on PATH: yt-dlp, ffmpeg, tesseract (optional, for on-screen text), and deno
or node (yt-dlp uses one to solve YouTube's JavaScript challenges).

  python ttf.py list     [--since 20260505] [--max 60]
  python ttf.py new      [--since 20260505] [--frames]   # unseen uploads: transcripts (+ frames)
  python ttf.py captions ID [ID ...]
  python ttf.py frames   ID_OR_FILE [--every 2]
  python ttf.py score    [--calls calls.csv]
"""
import argparse, csv, datetime, json, re, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

CHANNEL = "https://www.youtube.com/@thetradingfraternity"
HERE = Path(__file__).resolve().parent
WORK = HERE / "work"        # media, transcripts, frames (git-ignored)
SEEN = HERE / "seen.txt"    # ids whose transcript has been fetched
PAUSE = 4                   # seconds between YouTube requests; bursts get rate-limited or bot-checked


def ytdlp(*args):
    cmd = ["yt-dlp", "--no-warnings"]
    if not shutil.which("deno") and shutil.which("node"):
        cmd += ["--js-runtimes", "node"]
    return subprocess.run(cmd + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")


def last_error(r):
    lines = [l for l in r.stderr.splitlines() if l.strip()]
    return lines[-1] if lines else "unknown error"


def watch_url(vid):
    return f"https://www.youtube.com/watch?v={vid}"


# ---------- listing ----------

def list_uploads(since, limit):
    rows = []
    for tab in ("videos", "shorts"):
        r = ytdlp("--flat-playlist", "--playlist-end", str(limit), "--print", "%(id)s", f"{CHANNEL}/{tab}")
        ids = r.stdout.split()
        if not ids:
            print(f"[{tab}] nothing listed: {last_error(r)}", file=sys.stderr)
        for vid in ids:
            m = ytdlp("--skip-download", "--print", "%(upload_date)s|%(duration)s|%(title)s", watch_url(vid))
            time.sleep(PAUSE)
            out = m.stdout.strip().splitlines()
            if not out:
                print(f"  {vid}: no metadata ({last_error(m)})", file=sys.stderr)
                continue
            date, dur, title = out[-1].split("|", 2)
            if date != "NA" and date < since:
                break   # tabs are newest-first
            rows.append(dict(date=date, duration=dur, id=vid, tab=tab, title=title))
            print(f"{date}  {tab:6}  {dur:>5}s  {vid}  {title}")
    WORK.mkdir(exist_ok=True)
    with open(WORK / "uploads.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "duration", "id", "tab", "title"])
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------- transcripts ----------

def vtt_to_text(vtt):
    out = []
    for line in re.sub(r"<[^>]+>", "", vtt).splitlines():
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")) or line.isdigit():
            continue
        if not out or out[-1] != line:   # auto-captions repeat each line as it scrolls
            out.append(line)
    return " ".join(out)


def captions(ids):
    tdir = WORK / "transcripts"
    tdir.mkdir(parents=True, exist_ok=True)
    got = []
    for vid in ids:
        # en-orig is YouTube's own speech recognition; en can be a re-translation of it
        for lang in ("en-orig", "en"):
            r = ytdlp("--write-auto-sub", "--write-sub", "--sub-lang", lang, "--skip-download",
                      "--sub-format", "vtt", "-o", str(tdir / f"{vid}.%(ext)s"), watch_url(vid))
            time.sleep(PAUSE)
            vtts = sorted(tdir.glob(f"{vid}.*.vtt"))
            if vtts:
                text = vtt_to_text(vtts[0].read_text(encoding="utf-8", errors="replace"))
                (tdir / f"{vid}.txt").write_text(text, encoding="utf-8")
                print(f"{vid}: {len(text.split())} words")
                got.append(vid)
                break
        else:
            print(f"{vid}: no transcript ({last_error(r)})", file=sys.stderr)
    return got


# ---------- frames ----------

def frames(src, every):
    if Path(src).exists():
        video, name = Path(src), Path(src).stem
    else:
        name = src
        vdir = WORK / "video"
        vdir.mkdir(parents=True, exist_ok=True)
        r = ytdlp("-S", "res:720", "--merge-output-format", "mp4", "-o", str(vdir / f"{name}.%(ext)s"), watch_url(src))
        video = vdir / f"{name}.mp4"
        if not video.exists():
            sys.exit(f"{src}: download failed ({last_error(r)})")
    fdir = WORK / "frames" / name
    shutil.rmtree(fdir, ignore_errors=True)
    (fdir / "full").mkdir(parents=True)
    ff = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    subprocess.run(ff + ["-i", str(video), "-vf", f"fps=1/{every}", str(fdir / "full" / "%04d.jpg")], check=True)
    full = sorted((fdir / "full").glob("*.jpg"))

    # Contact sheets: portrait video (shorts) 5x2, landscape 3x4 -- ten or twelve frames per image.
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", str(video)],
                                   capture_output=True, text=True).stdout.split(",")[:2])
    cols, rows, tw = (5, 2, 300) if h > w else (3, 4, 400)
    subprocess.run(ff + ["-i", str(fdir / "full" / "%04d.jpg"), "-vf",
                         f"scale={tw}:-2,tile={cols}x{rows}:padding=4:color=white",
                         str(fdir / "sheet_%02d.jpg")], check=True)
    per = cols * rows
    sheets = sorted(fdir.glob("sheet_*.jpg"))
    with open(fdir / "index.txt", "w", encoding="utf-8") as f:
        for i, s in enumerate(sheets):
            a, b = i * per * every, ((i + 1) * per - 1) * every
            f.write(f"{s.name}: {a // 60}:{a % 60:02d} - {b // 60}:{b % 60:02d}, frames left-to-right, top-to-bottom\n")

    # On-screen text, so tickers and numbers are captured even from frames nobody looks at.
    if shutil.which("tesseract"):
        prev = None
        with open(fdir / "ocr.txt", "w", encoding="utf-8") as f:
            for i, img in enumerate(full):
                text = " ".join(subprocess.run(["tesseract", str(img), "stdout"], capture_output=True,
                                               text=True, errors="replace").stdout.split())
                if len(re.sub(r"\W", "", text)) >= 4 and text != prev:
                    t = i * every
                    f.write(f"{t // 60}:{t % 60:02d} | {text}\n")
                    prev = text
    print(f"{name}: {len(full)} frames every {every}s -> {len(sheets)} sheets in {fdir}")


# ---------- scoring ----------

def yahoo(ticker, start, end):
    p1 = int(datetime.datetime.combine(start, datetime.time()).timestamp())
    p2 = int(datetime.datetime.combine(end, datetime.time()).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={p1}&period2={p2}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = json.load(urllib.request.urlopen(req, timeout=30))["chart"]["result"][0]
    return [(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).date(), c)
            for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c]


def close_on(ticker, day):
    pts = [c for d, c in yahoo(ticker, day - datetime.timedelta(days=7), day + datetime.timedelta(days=1)) if d <= day]
    return pts[-1]


def latest(ticker):
    today = datetime.date.today()
    return yahoo(ticker, today - datetime.timedelta(days=10), today + datetime.timedelta(days=1))[-1]


def score(calls_file):
    calls = list(csv.DictReader(open(calls_file, encoding="utf-8")))
    spy_day, spy_now = latest("SPY")
    lines = [f"Prices as of {spy_day}. Price return only; dividends excluded.", "",
             "| Ticker | Call | Entry date | Entry | Now | Return | SPY same period | vs SPY |",
             "|---|---|---|---|---|---|---|---|"]
    tot = tot_spy = 0
    for c in calls:
        day = datetime.date.fromisoformat(c["entry_date"])
        entry = float(c["entry_price"]) if c["entry_price"] else close_on(c["ticker"], day)
        now = latest(c["ticker"])[1]
        ret, spy = (now / entry - 1) * 100, (spy_now / close_on("SPY", day) - 1) * 100
        tot, tot_spy = tot + ret, tot_spy + spy
        lines.append(f"| {c['ticker']} | {c['label']} | {day} | {entry:.2f} | {now:.2f} | {ret:+.1f}% | {spy:+.1f}% | {ret - spy:+.1f} |")
        time.sleep(0.3)
    n = len(calls)
    lines.append(f"| **Average** | | | | | **{tot / n:+.1f}%** | **{tot_spy / n:+.1f}%** | **{(tot - tot_spy) / n:+.1f}** |")
    WORK.mkdir(exist_ok=True)
    (WORK / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--since", default="20260505"); p.add_argument("--max", type=int, default=60)
    p = sub.add_parser("new"); p.add_argument("--since", default="20260505"); p.add_argument("--frames", action="store_true")
    p = sub.add_parser("captions"); p.add_argument("ids", nargs="+")
    p = sub.add_parser("frames"); p.add_argument("src"); p.add_argument("--every", type=int, default=2)
    p = sub.add_parser("score"); p.add_argument("--calls", default=str(HERE / "calls.csv"))
    a = ap.parse_args()

    if a.cmd == "list":
        list_uploads(a.since, a.max)
    elif a.cmd == "captions":
        captions(a.ids)
    elif a.cmd == "frames":
        frames(a.src, a.every)
    elif a.cmd == "score":
        score(a.calls)
    elif a.cmd == "new":
        seen = set(SEEN.read_text().split()) if SEEN.exists() else set()
        fresh = [r for r in list_uploads(a.since, 60) if r["id"] not in seen]
        print(f"{len(fresh)} unseen uploads")
        got = captions([r["id"] for r in fresh])
        if a.frames:
            for r in fresh:
                frames(r["id"], 2)
                time.sleep(PAUSE)
        with open(SEEN, "a", encoding="utf-8") as f:
            f.writelines(v + "\n" for v in got)


if __name__ == "__main__":
    main()
