#!/usr/bin/env python3
"""Filtered Swype emoji logcat analysis. Does not emit user-typed strings."""
import json,re,sys
from pathlib import Path
ADDED=re.compile(r'loadCodePoints: called\s+(.+?)\s+:: added emoji ::\s+([0-9A-Fa-f,]+)')
PAGE=re.compile(r'setItems\s*:\s*called\s*::\s*emojis\.size\(\)\s*(\d+)\s*, cells count::\s*(\d+)\s*, pageNumber\s*:\s*(\d+)')
RESOURCE=re.compile(r'loadCodePoints\(\): called :: arrayType=(\d+)')
TARGETS={'1F970':'🥰','1F929':'🤩','1FAE9':'🫩'}
def analyze(lines):
    counts={};hits={v:[] for v in TARGETS};pages=[];types=[]
    for row in lines:
        m=RESOURCE.search(row)
        if m:types.append(int(m.group(1)))
        m=ADDED.search(row)
        if m:
            cat,seq=m.group(1).strip(),m.group(2).upper().strip()
            counts[cat]=counts.get(cat,0)+1
            for code in TARGETS:
                if code in seq.split(','):
                    hits[code].append({'category':cat,'filtered_ordinal':counts[cat]})
        m=PAGE.search(row)
        if m:
            pages.append({'visible_page_items':int(m.group(1)),
                          'grid_cells':int(m.group(2)),
                          'page_number':int(m.group(3))})
    return {'loaded_count_by_category':counts,
            'target_positions_after_filtering':hits,
            'observed_page_calls':pages,
            'array_types':types,
            'note':'Empty results may mean release logging is disabled. Page logs contain counts, not emoji values.'}
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python analyze_emoji_logcat.py logcat.txt')
    print(json.dumps(analyze(Path(sys.argv[1]).read_text(encoding='utf-8',errors='replace').splitlines()),ensure_ascii=False,indent=2))
