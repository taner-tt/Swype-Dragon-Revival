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
# The original preview encodes separators at an exact RGB value.
# Remove those line pixels, retaining white legends and original keyboard geometry.
for y in range(h):
    for x in range(w):
        if p[x,y] == (153,153,153):
            p[x,y] = (0,0,0)
# RDR snapshot is supplied as an actual drawable in the theme APK.
snapshot=decoded/"res"/"drawable-nodpi"/"rdr_amoled_keyboard_preview.png"
snapshot.parent.mkdir(parents=True,exist_ok=True)
img.save(snapshot,"PNG",optimize=True)
# Catalog image is deliberately solid black, separately delivered in theme ZIP.
Image.new("RGB",(480,320),(0,0,0)).save(output/"RDR.BLACK.AMOLED.V1.png","PNG",optimize=True)
print("Catalog: solid black; theme snapshot:",snapshot)
