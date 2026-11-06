#!/usr/bin/env python3
"""Generate two independent previews: black catalog tile, keyboard in theme APK."""
from pathlib import Path
from PIL import Image, ImageDraw
import sys
decoded=Path(sys.argv[1])
original=Path(sys.argv[2])
output=Path(sys.argv[3])
assert original.is_file() and decoded.is_dir()
output.mkdir(parents=True,exist_ok=True)
img=Image.open(original).convert("RGB")
# Original FlatBlack screenshot has grid lines; remove long straight lines only,
# retaining the actual original key legends and layout as far as possible.
p=img.load()
w,h=img.size
for y in range(h):
    n=sum(1 for x in range(w) if max(p[x,y])-min(p[x,y])<10 and 75<=sum(p[x,y])//3<=215)
    if n>w*0.72:
        for dy in range(max(0,y-1),min(h,y+2)):
            for x in range(w):
                if max(p[x,dy])-min(p[x,dy])<16 and max(p[x,dy])<218: p[x,dy]=(0,0,0)
for x in range(w):
    n=sum(1 for y in range(h) if max(p[x,y])-min(p[x,y])<10 and 75<=sum(p[x,y])//3<=215)
    if n>h*0.63:
        for dx in range(max(0,x-1),min(w,x+2)):
            for y in range(h):
                if max(p[dx,y])-min(p[dx,y])<16 and max(p[dx,y])<218: p[dx,y]=(0,0,0)
# RDR snapshot is supplied as an actual drawable in the theme APK.
snapshot=decoded/"res"/"drawable-nodpi"/"rdr_amoled_keyboard_preview.png"
snapshot.parent.mkdir(parents=True,exist_ok=True)
img.save(snapshot,"PNG",optimize=True)
# Catalog image is deliberately solid black, separately delivered in theme ZIP.
Image.new("RGB",(480,320),(0,0,0)).save(output/"RDR.BLACK.AMOLED.V1.png","PNG",optimize=True)
print("Catalog: solid black; theme snapshot:",snapshot)
