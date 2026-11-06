#!/usr/bin/env python3
"""Generate matching borderless keyboard previews for the catalog and theme APK."""
from pathlib import Path
from PIL import Image
import sys
decoded=Path(sys.argv[1])
original=Path(sys.argv[2])
output=Path(sys.argv[3])
assert original.is_file() and decoded.is_dir()
output.mkdir(parents=True,exist_ok=True)
img=Image.open(original).convert("RGB")
# Pure 2-color RDR preview: eliminate all gray anti-aliasing and accent hues.
# Bright legend pixels become white, every other pixel becomes OLED black.
img=img.convert("L").point(lambda x: 255 if x >= 140 else 0).convert("RGB")
# RDR snapshot is supplied as an actual drawable in the theme APK.
snapshot=decoded/"res"/"drawable-nodpi"/"rdr_amoled_keyboard_preview.png"
snapshot.parent.mkdir(parents=True,exist_ok=True)
img.save(snapshot,"PNG",optimize=True)
# FÅ TEMA must show the same borderless keyboard as MINA TEMAN / preview dialog.
catalog=output/"RDR.BLACK.AMOLED.V1.png"
img.save(catalog,"PNG",optimize=True)
print("Matching borderless keyboard previews:",catalog,snapshot)
