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

def resource(root,name):
    candidates=[]
    for p in glob.glob(root+'/res/drawable*/'+name+'.*'):
        if p.endswith('.xml'): continue
        score=0
        for key,value in [('xxxhdpi',4),('xxhdpi',3),('xhdpi',2),('hdpi',1),('mdpi',0)]:
            if key in os.path.dirname(p): score=value
        candidates.append((score,p))
    return max(candidates)[1] if candidates else None

def place(canvas,im,gravity,tile=False):
    im=im.convert('RGBA')
    if tile:
        for y in range(0,H,im.height):
            for x in range(0,W,im.width): canvas.alpha_composite(im,(x,y))
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

def render(root,out):
    xml=root+'/res/drawable/keyboard_background_main.xml'
    if not os.path.isfile(xml): return False
    base=Image.new('RGBA',(W,H),(0,0,0,255))
    for item in ET.parse(xml).getroot():
        for el in item:
            tag=el.tag.split('}')[-1]
            if tag=='shape':
                solid=el.find('solid'); grad=el.find('gradient')
                if solid is not None:
                    ImageDraw.Draw(base).rectangle((0,0,W,H),fill=rgba(solid.attrib[A+'color']))
                elif grad is not None:
                    c1=rgba(grad.attrib[A+'startColor']); c2=rgba(grad.attrib[A+'endColor']); ang=float(grad.attrib.get(A+'angle','0'))%360
                    if ang in (90,270):
                        line=Image.new('RGBA',(1,H)); pix=line.load()
                        for y in range(H):
                            t=(1-y/(H-1)) if ang==90 else y/(H-1); pix[0,y]=tuple(round(c1[i]*(1-t)+c2[i]*t) for i in range(4))
                    else:
                        line=Image.new('RGBA',(W,1)); pix=line.load()
                        for x in range(W):
                            t=(x/(W-1)) if ang==0 else (1-x/(W-1)); pix[x,0]=tuple(round(c1[i]*(1-t)+c2[i]*t) for i in range(4))
                    base.alpha_composite(line.resize((W,H)))
            elif tag in ('bitmap','nine-patch'):
                src=el.attrib.get(A+'src','').split('/')[-1]; path=resource(root,src)
                if not path: continue
                im=Image.open(path).convert('RGBA')
                if '.9.' in path and im.width>2 and im.height>2: im=im.crop((1,1,im.width-1,im.height-1))
                place(base,im,el.attrib.get(A+'gravity'),el.attrib.get(A+'tileMode')=='repeat')
    os.makedirs(os.path.dirname(out) or '.',exist_ok=True)
    base.convert('RGB').save(out,'PNG',optimize=True)
    return True

if __name__=='__main__':
    if len(sys.argv)!=3 or not render(sys.argv[1],sys.argv[2]): raise SystemExit(2)
