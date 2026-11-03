#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os, glob, sys, xml.etree.ElementTree as ET
A='{http://schemas.android.com/apk/res/android}'
W,H=640,360

def rgba(s):
    s=s.lstrip('#')
    if len(s)==8:
        a,r,g,b=[int(s[i:i+2],16) for i in (0,2,4,6)]
    else:
        r,g,b=[int(s[i:i+2],16) for i in (0,2,4)]; a=255
    return r,g,b,a

def candidates(root,name):
    out=[]
    for p in glob.glob(root+'/res/drawable*/'+name+'.*'):
        score=0
        for key,value in [('xxxhdpi',4),('xxhdpi',3),('xhdpi',2),('hdpi',1),('mdpi',0)]:
            if key in os.path.dirname(p): score=value
        out.append((score,p))
    return sorted(out, reverse=True)

def resource(root,name):
    files=[x for x in candidates(root,name) if not x[1].endswith('.xml')]
    return files[0][1] if files else None

def xml_resource(root,name):
    files=[x for x in candidates(root,name) if x[1].endswith('.xml')]
    return files[0][1] if files else None

def place(canvas,im,gravity,tile=False):
    im=im.convert('RGBA')
    if tile:
        for y in range(0,H,max(1,im.height)):
            for x in range(0,W,max(1,im.width)): canvas.alpha_composite(im,(x,y))
        return
    if not gravity or gravity=='fill':
        canvas.alpha_composite(im.resize((W,H),Image.Resampling.LANCZOS)); return
    if im.width>W or im.height>H:
        scale=min(1,W/im.width,H/im.height)
        im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.Resampling.LANCZOS)
    x=(W-im.width)//2; y=(H-im.height)//2
    if 'left' in gravity: x=0
    if 'right' in gravity: x=W-im.width
    if 'top' in gravity: y=0
    if 'bottom' in gravity: y=H-im.height
    canvas.alpha_composite(im,(x,y))

def gradient(canvas,el):
    c1=rgba(el.attrib[A+'startColor']); c2=rgba(el.attrib[A+'endColor']); ang=float(el.attrib.get(A+'angle','0'))%360
    if ang in (90,270):
        line=Image.new('RGBA',(1,H)); pix=line.load()
        for y in range(H):
            t=(1-y/(H-1)) if ang==90 else y/(H-1); pix[0,y]=tuple(round(c1[i]*(1-t)+c2[i]*t) for i in range(4))
    else:
        line=Image.new('RGBA',(W,1)); pix=line.load()
        for x in range(W):
            t=(x/(W-1)) if ang==0 else (1-x/(W-1)); pix[x,0]=tuple(round(c1[i]*(1-t)+c2[i]*t) for i in range(4))
    canvas.alpha_composite(line.resize((W,H)))

def render_element(root,canvas,el,depth=0):
    if depth>8: return
    tag=el.tag.split('}')[-1]
    if tag=='shape':
        solid=el.find('solid'); grad=el.find('gradient')
        if solid is not None and A+'color' in solid.attrib:
            ImageDraw.Draw(canvas).rectangle((0,0,W,H),fill=rgba(solid.attrib[A+'color']))
        elif grad is not None and A+'startColor' in grad.attrib and A+'endColor' in grad.attrib:
            gradient(canvas,grad)
    elif tag in ('bitmap','nine-patch'):
        src=el.attrib.get(A+'src','').split('/')[-1]; path=resource(root,src)
        if path:
            im=Image.open(path).convert('RGBA')
            if '.9.' in path and im.width>2 and im.height>2: im=im.crop((1,1,im.width-1,im.height-1))
            place(canvas,im,el.attrib.get(A+'gravity'),el.attrib.get(A+'tileMode')=='repeat')
    elif tag in ('layer-list','selector'):
        for child in el:
            render_element(root,canvas,child,depth+1)
    elif tag=='item':
        drawable=el.attrib.get(A+'drawable','')
        if drawable.startswith('@drawable/'):
            name=drawable.split('/')[-1]
            xp=xml_resource(root,name); rp=resource(root,name)
            if xp:
                render_element(root,canvas,ET.parse(xp).getroot(),depth+1)
            elif rp:
                im=Image.open(rp).convert('RGBA'); place(canvas,im,el.attrib.get(A+'gravity'))
        for child in el:
            render_element(root,canvas,child,depth+1)

def direct_keyboard_background(root):
    # Some original Swype families (notably Hues) use a complete density-qualified
    # keyboard_background_<theme>.png instead of keyboard_background_main.xml.
    # Prefer the highest-density complete keyboard background and never HWR assets.
    found=[]
    for p in glob.glob(root+'/res/drawable*/keyboard_background_*'):
        name=os.path.basename(p).lower()
        if name.endswith('.xml') or 'hwr' in name or 'main' in name: continue
        try:
            with Image.open(p) as im:
                area=im.width*im.height
        except Exception:
            continue
        density=0
        d=os.path.dirname(p)
        for key,value in [('xxxhdpi',5),('xxhdpi',4),('xhdpi',3),('hdpi',2),('mdpi',1),('ldpi',0)]:
            if key in d: density=value
        found.append((density,area,p))
    return max(found)[2] if found else None

def render(root,out):
    matches=glob.glob(root+'/res/drawable*/keyboard_background_main.xml')
    os.makedirs(os.path.dirname(out) or '.',exist_ok=True)
    if matches:
        base=Image.new('RGBA',(W,H),(0,0,0,255))
        render_element(root,base,ET.parse(matches[0]).getroot())
        base.convert('RGB').save(out,'PNG',optimize=True)
        return True
    direct=direct_keyboard_background(root)
    if direct:
        im=Image.open(direct).convert('RGB')
        im=im.resize((W,H),Image.Resampling.LANCZOS)
        im.save(out,'PNG',optimize=True)
        return True
    return False

if __name__=='__main__':
    if len(sys.argv)!=3 or not render(sys.argv[1],sys.argv[2]): raise SystemExit(2)
