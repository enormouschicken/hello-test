# TTF watcher — handoff

Watches **The Trading Fraternity** (`youtube.com/@thetradingfraternity`): pulls every new video and short, reads both the transcript and the visuals, extracts each stock call, and scores it against the S&P 500.

Started in a cloud session on 5 Nov 2026. That session proved the pipeline, scored eight long-form calls (see **findings.md**), then YouTube bot-checked its datacentre IP before it reached the shorts. **Running from a home connection avoids that** — which is why this now lives in the local session.

## One-time setup

```
pip install -U yt-dlp
```
Plus on PATH: **ffmpeg**, **tesseract** (on-screen text; optional but recommended), and **deno** or **node** (yt-dlp needs one for YouTube's JS challenges).

- macOS: `brew install ffmpeg tesseract deno`
- Windows: `winget install Gyan.FFmpeg UB-Mannheim.TesseractOCR DenoLand.Deno`
- Linux: `apt install ffmpeg tesseract-ocr` + deno or node

## Pick up where it stopped

```
python ttf.py new --since 20260505 --frames
```
Lists the last six months of videos **and** shorts, pulls transcripts, and for each upload builds visuals in `work/frames/<id>/`:

- `sheet_XX.jpg` — contact sheets, one frame every 2 s, 10–12 frames per image (`index.txt` gives each sheet's time range)
- `ocr.txt` — on-screen text from every frame, timestamped
- transcripts in `work/transcripts/<id>.txt`

Then, for each upload, a Claude session should:
1. **Read the transcript and look at every contact sheet.** Charts, tickers and price levels are often only on screen. Use `ocr.txt` to catch text on frames between what you study closely, and open the full-resolution frame in `full/` when a chart's labels are too small on the sheet.
2. **Extract each call:** ticker, direction, entry price if stated, date. Auto-captions garble tickers ("NLR" can arrive as "n l r") — confirm against what's on screen.
3. **Append it to `calls.csv`.** Leave `entry_price` blank to use the close on `entry_date`.
4. **Run `python ttf.py score`** — writes `work/scorecard.md`, each call vs the S&P over the same period.
5. **Note claims that aren't stock calls** (macro predictions, "crash coming") in findings.md, so they can be checked later.

## Going weekly

`python ttf.py new --frames` processes only uploads not yet in `seen.txt`. Run it from a scheduled task in the Claude app, `/loop` in Claude Code, or your OS scheduler.

## Known issues

- **YouTube rate-limits and bot-checks bursts.** The script waits 4 s between requests (`PAUSE`). Don't run copies in parallel — that's what got the cloud session blocked.
- If a bot-check still appears, wait an hour. yt-dlp's documented fallback is `--cookies-from-browser`, which uses your browser's YouTube sign-in.
- Nothing personal is in this folder. Transcripts and video stay in `work/`, which git ignores — keep it that way rather than committing the creator's content.
