#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REPO=os.environ.get('GITHUB_REPOSITORY','taner-tt/Swype-Dragon-Revival')
TAG=os.environ.get('SWYPE_THEME_RELEASE','themes-v1')
API=f'https://api.github.com/repos/{REPO}/releases/tags/{TAG}'
RAW_BASE=f'https://raw.githubusercontent.com/{REPO}/main/theme-previews'
PREVIEW_DIR='theme-previews'
APKTOOL=os.environ.get('APKTOOL_JAR','/tmp/apktool.jar')
HEADERS={'Accept':'application/vnd.github+json','User-Agent':'Swype-Dragon-Revival-catalog-builder'}

def request(url,accept=None):
    h=dict(HEADERS)
    if accept: h['Accept']=accept
    return urllib.request.Request(url,headers=h)

def get_json(url):
    with urllib.request.urlopen(request(url)) as r: return json.load(r)

def download(url,path):
    with urllib.request.urlopen(request(url,'application/octet-stream')) as r,open(path,'wb') as f: shutil.copyfileobj(r,f)

def display_name(theme_id):
    name=theme_id
    for p in ('btm.theme.','nuance.theme.'):
        if name.startswith(p): name=name[len(p):]; break
    if theme_id == 'Flat_Black_v3_REBUILT_UPLOAD': return 'Flat Black v3'
    return name.replace('_',' ').replace('-',' ').strip().title()

def extract_preview(zip_path,theme_id,work):
    """Render keyboard_background_main exactly as a layered Android drawable.

    Swype theme backgrounds are compositions: gradients, solid colors, bitmaps,
    nine-patches and positioned overlays. Selecting one arbitrary PNG loses
    layers and produced the incorrect catalog images. Decode the resource XML
    and render the same layer-list contract instead; the inner APK is untouched.
    """
    with zipfile.ZipFile(zip_path) as outer:
        apks=[n for n in outer.namelist() if n.lower().endswith('.apk') and not n.endswith('/')]
        if len(apks)!=1: raise RuntimeError(f'{theme_id}: expected exactly one APK, found {len(apks)}')
        apk_path=os.path.join(work,theme_id+'.apk')
        with open(apk_path,'wb') as f: f.write(outer.read(apks[0]))
    # Flat Black v3 uses a full keyboard screenshot, not a plain background.
    # The generic renderer produces a solid black square for this theme.
    if theme_id in ('Flat_Black_v3', 'Flat_Black_v3_REBUILT_UPLOAD'):
        with zipfile.ZipFile(apk_path) as inner:
            candidate='assets/flat_black_v3_original_keyboard_preview.png'
            if candidate in inner.namelist():
                out_name=theme_id+'.png'
                out_path=os.path.join(PREVIEW_DIR,out_name)
                with open(out_path,'wb') as preview_file:
                    preview_file.write(inner.read(candidate))
                os.remove(apk_path)
                return f'{RAW_BASE}/{out_name}'
    decoded=os.path.join(work,theme_id+'-decoded')
    subprocess.run(['java','-Xmx384m','-jar',APKTOOL,'d','-f','-s',apk_path,'-o',decoded],check=True,stdout=subprocess.DEVNULL)
    out_name=theme_id+'.png'; out_path=os.path.join(PREVIEW_DIR,out_name)
    subprocess.run(['python3','tools/render_theme_background.py',decoded,out_path],check=True)
    shutil.rmtree(decoded,ignore_errors=True)
    os.remove(apk_path)
    return f'{RAW_BASE}/{out_name}'

release=get_json(API)
assets=[]; page=1
while True:
    batch=get_json(release['assets_url']+f'?per_page=100&page={page}')
    if not batch: break
    assets.extend(batch); page+=1

os.makedirs(PREVIEW_DIR,exist_ok=True)
items=[]
with tempfile.TemporaryDirectory() as td:
    zips=[a for a in sorted(assets,key=lambda x:x['name'].lower()) if a['name'].lower().endswith('.zip')]
    for index,a in enumerate(zips,1):
        theme_id=a['name'][:-4]; zip_path=os.path.join(td,a['name'])
        print(f'[{index}/{len(zips)}] {theme_id}',flush=True)
        download(a['browser_download_url'],zip_path)
        preview=extract_preview(zip_path,theme_id,td)
        digest=a.get('digest') or ''
        if not digest:
            with open(zip_path,'rb') as payload:
                h=hashlib.sha256()
                for block in iter(lambda:payload.read(1024*1024),b''): h.update(block)
                digest='sha256:'+h.hexdigest()
        items.append({'id':theme_id,'name':display_name(theme_id),'filename':a['name'],'url':a['browser_download_url'],'preview':preview,'size':a['size'],'sha256':digest.removeprefix('sha256:')})

catalog={'schema':2,'repository':REPO,'release':TAG,'count':len(items),'themes':items}
with open('themes.json','w',encoding='utf-8',newline='\n') as f:
    json.dump(catalog,f,ensure_ascii=False,indent=2); f.write('\n')
if len(items)<270: raise SystemExit(f'Expected at least 270 theme ZIPs, got {len(items)}')
print(f'Wrote themes.json with {len(items)} layer-rendered previews')
