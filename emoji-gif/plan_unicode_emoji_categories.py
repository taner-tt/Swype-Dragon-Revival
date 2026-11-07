#!/usr/bin/env python3
"""Plan official Unicode emoji placement into Swype's original categories.

This is a reviewable plan, not an APK patch. Device glyph validation remains mandatory.
"""
import argparse,collections,json
CATS=('emoji_category_smiley','emoji_category_family','emoji_category_nature','emoji_category_objects','emoji_category_transportation','emoji_category_flag')
FALLBACK={'Smileys & Emotion':'emoji_category_smiley','People & Body':'emoji_category_family','Animals & Nature':'emoji_category_nature','Food & Drink':'emoji_category_nature','Travel & Places':'emoji_category_transportation','Activities':'emoji_category_objects','Objects':'emoji_category_objects','Symbols':'emoji_category_objects','Flags':'emoji_category_flag'}
def rows_from_unicode(path):
    rows=[];group=subgroup=None
    for line in open(path,encoding='utf-8-sig'):
        if line.startswith('# group:'):group=line.split(':',1)[1].strip()
        elif line.startswith('# subgroup:'):subgroup=line.split(':',1)[1].strip()
        elif ';' in line and '#' in line and not line.lstrip().startswith('#'):
            units,status=line.split(';',1)
            if status.split('#',1)[0].strip()!='fully-qualified':continue
            nums=[int(x,16) for x in units.strip().split()]
            rows.append({'code':','.join(f'{x:X}' for x in nums),'unicode_group':group,'unicode_subgroup':subgroup,'emoji':''.join(chr(x) for x in nums)})
    return rows
def build_plan(rows,original):
    membership=collections.defaultdict(set)
    for category in CATS:
        for s in original[category]:membership[s.upper().replace(' ','')].add(category)
    votes=collections.defaultdict(collections.Counter)
    for row in rows:
        for category in membership[row['code']]:votes[(row['unicode_group'],row['unicode_subgroup'])][category]+=1
    result=[];manual=0
    for row in rows:
        found=membership.get(row['code'],set())
        if found:
            result.append(dict(row,categories=sorted(found),action='preserve_original',method='existing_swype'));continue
        counter=votes[(row['unicode_group'],row['unicode_subgroup'])].most_common(2)
        if counter and (len(counter)==1 or counter[0][1]>=counter[1][1]*2):
            cat=counter[0][0];method='existing_swype_subgroup_majority'
        else:
            cat=FALLBACK.get(row['unicode_group']);method='fallback_needs_manual_review';manual+=1
        result.append(dict(row,categories=[cat] if cat else [],action='device_glyph_check_required',method=method))
    return {'version':'Unicode Emoji 18.0','fully_qualified':len(rows),'existing':sum(x['action']=='preserve_original' for x in result),'new_candidates':sum(x['action']!='preserve_original' for x in result),'manual_review_candidates':manual,'ordered':result}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--unicode-file',required=True);ap.add_argument('--swype-arrays',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    original=json.load(open(args.swype_arrays,encoding='utf-8'))
    rows=rows_from_unicode(args.unicode_file)
    assert len(rows)>1000,'Unicode data missing or incomplete'
    result=build_plan(rows,original)
    with open(args.output,'w',encoding='utf-8') as out:json.dump(result,out,ensure_ascii=False,indent=2)
    print({k:v for k,v in result.items() if k!='ordered'})
    print('Output requires device-glyph and manual-category review. No APK changed.')
