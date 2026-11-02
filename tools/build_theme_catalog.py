#!/usr/bin/env python3
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile

REPO = os.environ.get("GITHUB_REPOSITORY", "taner-tt/Swype-Dragon-Revival")
TAG = os.environ.get("SWYPE_THEME_RELEASE", "themes-v1")
API = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/theme-previews"
PREVIEW_DIR = "theme-previews"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Swype-Dragon-Revival-catalog-builder",
}


def request(url, accept=None):
    headers = dict(HEADERS)
    if accept:
        headers["Accept"] = accept
    return urllib.request.Request(url, headers=headers)


def get_json(url):
    with urllib.request.urlopen(request(url)) as r:
        return json.load(r)


def download(url, path):
    with urllib.request.urlopen(request(url, "application/octet-stream")) as r, open(path, "wb") as f:
        shutil.copyfileobj(r, f)


def display_name(theme_id):
    name = theme_id
    for prefix in ("btm.theme.", "nuance.theme."):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    return name.replace("_", " ").replace("-", " ").strip().title()


def extract_preview(zip_path, theme_id):
    """Extract a real keyboard-art PNG from the theme APK.

    Old Nuance metadata sometimes references a snapshot resource that is absent,
    so the catalog preview is generated from artwork that is physically present
    in the APK instead of trusting that stale metadata.
    """
    with zipfile.ZipFile(zip_path) as outer:
        apk_names = [n for n in outer.namelist() if n.lower().endswith(".apk") and not n.endswith("/")]
        if len(apk_names) != 1:
            raise RuntimeError(f"{theme_id}: expected exactly one APK, found {len(apk_names)}")
        apk_bytes = outer.read(apk_names[0])

    with tempfile.NamedTemporaryFile(suffix=".apk") as tmp:
        tmp.write(apk_bytes)
        tmp.flush()
        with zipfile.ZipFile(tmp.name) as apk:
            pngs = [
                i for i in apk.infolist()
                if i.filename.lower().endswith(".png")
                and not i.filename.lower().endswith(".9.png")
                and "/keyboard_background_" in i.filename.lower()
            ]
            if not pngs:
                # Conservative fallback: use the largest ordinary drawable PNG.
                pngs = [
                    i for i in apk.infolist()
                    if i.filename.lower().endswith(".png")
                    and not i.filename.lower().endswith(".9.png")
                    and i.filename.startswith("res/drawable")
                ]
            if not pngs:
                return None
            chosen = max(pngs, key=lambda i: i.file_size)
            data = apk.read(chosen)

    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out_name = f"{theme_id}.png"
    out_path = os.path.join(PREVIEW_DIR, out_name)
    with open(out_path, "wb") as f:
        f.write(data)
    return f"{RAW_BASE}/{out_name}"


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
with tempfile.TemporaryDirectory() as td:
    for index, a in enumerate(sorted(assets, key=lambda x: x["name"].lower()), 1):
        if not a["name"].lower().endswith(".zip"):
            continue
        theme_id = a["name"][:-4]
        digest = a.get("digest") or ""
        zip_path = os.path.join(td, a["name"])
        print(f"[{index}] {theme_id}")
        download(a["browser_download_url"], zip_path)
        preview = extract_preview(zip_path, theme_id)
        items.append({
            "id": theme_id,
            "name": display_name(theme_id),
            "filename": a["name"],
            "url": a["browser_download_url"],
            "preview": preview,
            "size": a["size"],
            "sha256": digest.removeprefix("sha256:"),
        })

catalog = {
    "schema": 2,
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
print(f"Wrote themes.json with {len(items)} themes and generated previews")
