"""Download the Google Fonts the quiz uses and write fonts-inline.css with base64 data URIs,
so the offline copy (and local screenshots) render with the real typefaces."""
import base64, re, subprocess, sys
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
URL = ("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;600;700"
       "&family=Big+Shoulders+Stencil+Display:wght@700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap")
KEEP = {"latin", "latin-ext"}
def get(url, binary=False):
    out = subprocess.run(["curl", "-sSL", "-A", UA, url], capture_output=True, check=True).stdout
    return out if binary else out.decode()
css = get(URL)
blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*{[^}]*})", css)
cache, parts, total = {}, [], 0
for subset, block in blocks:
    fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
    if subset not in KEEP or (subset == "latin-ext" and fam != "Atkinson Hyperlegible Next"):
        continue
    url = re.search(r"url\((https://[^)]+)\)", block).group(1)
    if url not in cache:
        data = get(url, binary=True)
        total += len(data)
        cache[url] = "data:font/woff2;base64," + base64.b64encode(data).decode()
    parts.append(f"/* {subset} */\n" + block.replace(url, cache[url]))
open("fonts-inline.css", "w").write("\n".join(parts))
print(f"{len(parts)} @font-face blocks, {len(cache)} files, {total/1024:.0f} KB of woff2")
