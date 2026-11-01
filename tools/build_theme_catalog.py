#!/usr/bin/env python3
import json
import os
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "taner-tt/Swype-Dragon-Revival")
TAG = os.environ.get("SWYPE_THEME_RELEASE", "themes-v1")
API = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"

def get_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"Swype-Dragon-Revival-catalog-builder"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

release = get_json(API)
assets = []
page = 1
while True:
    batch = get_json(release["assets_url"] + f"?per_page=100&page={page}")
    if not batch:
        break
    assets.extend(batch)
    page += 1

items = []
for a in sorted(assets, key=lambda x: x["name"].lower()):
    if not a["name"].lower().endswith(".zip"):
        continue
    digest = a.get("digest") or ""
    items.append({
        "id": a["name"][:-4],
        "filename": a["name"],
        "url": a["browser_download_url"],
        "size": a["size"],
        "sha256": digest.removeprefix("sha256:"),
    })

catalog = {
    "schema": 1,
    "repository": REPO,
    "release": TAG,
    "count": len(items),
    "themes": items,
}
with open("themes.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
    f.write("\n")

if len(items) != 270:
    raise SystemExit(f"Expected 270 theme ZIPs, got {len(items)}")
print(f"Wrote themes.json with {len(items)} themes")
