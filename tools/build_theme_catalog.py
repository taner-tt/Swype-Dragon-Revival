#!/usr/bin/env python3
import hashlib
import io
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from PIL import Image, ImageOps

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


def theme_tokens(theme_id):
    s = theme_id.lower()
    for prefix in ("btm.theme.", "nuance.theme."):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return [x for x in s.replace("-", "_").split("_") if len(x) >= 4]


def png_score(info, theme_id):
    n = info.filename.lower()
    score = 0
    if "keyboard_background" in n:
        score += 100
    if "background" in n:
        score += 35
    if "theme" in n:
        score += 25
    if "preview" in n or "snapshot" in n:
        score += 80
    if any(t in n for t in theme_tokens(theme_id)):
        score += 120
    if n.endswith(".9.png"):
        score += 15
    if "ic_launcher" in n:
        score -= 80
    if "icon_primary" in n or "cjk_" in n:
        score -= 120
    score += min(info.file_size // 1024, 50)
    return score


def load_png(apk, info):
    try:
        data = apk.read(info)
        im = Image.open(io.BytesIO(data)).convert("RGBA")
        if info.filename.lower().endswith(".9.png") and im.width > 2 and im.height > 2:
            im = im.crop((1, 1, im.width - 1, im.height - 1))
        return im, data
    except Exception:
        return None, None


def fit(im, size):
    if im.width < 2 or im.height < 2:
        return None
    return ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def extract_preview(zip_path, theme_id):
    """Create a catalog preview from one coherent piece of real theme artwork.

    The previous renderer combined the four highest-scoring drawables. That was
    structurally wrong: a Swype theme APK contains keyboard backgrounds, key
    nine-patches and other UI parts, so the result looked like two unrelated
    images glued together. Prefer the strongest theme/background drawable and
    render only that resource. This keeps the catalog preview coherent and does
    not invent a keyboard composition that Swype itself never renders this way.
    """
    with zipfile.ZipFile(zip_path) as outer:
        apk_names = [n for n in outer.namelist() if n.lower().endswith(".apk") and not n.endswith("/")]
        if len(apk_names) != 1:
            raise RuntimeError(f"{theme_id}: expected exactly one APK, found {len(apk_names)}")
        apk_bytes = outer.read(apk_names[0])

    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as apk:
        candidates = [
            i for i in apk.infolist()
            if i.filename.lower().endswith(".png")
            and i.filename.startswith("res/drawable")
            and i.file_size > 128
        ]
        candidates.sort(key=lambda i: (png_score(i, theme_id), i.file_size), reverse=True)

        selected = None
        seen = set()
        for info in candidates:
            im, data = load_png(apk, info)
            if im is None:
                continue
            digest = hashlib.sha256(data).digest()
            if digest in seen:
                continue
            seen.add(digest)
            selected = (info, im)
            break

    if selected is None:
        return None

    canvas = Image.new("RGBA", (640, 360), (28, 28, 28, 255))
    artwork = fit(selected[1], (640, 360))
    if artwork is None:
        return None
    canvas.alpha_composite(artwork, (0, 0))

    os.makedirs(PREVIEW_DIR, exist_ok=True)
    out_name = f"{theme_id}.png"
    out_path = os.path.join(PREVIEW_DIR, out_name)
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
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
