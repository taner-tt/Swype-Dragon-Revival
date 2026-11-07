#!/usr/bin/env python3
"""Read-only baseline audit: detect GIF and emoji sharing one keycode in Swype APK."""
import struct, zipfile, sys, json

PATHS = ("res/xml/popup_messaging_return_key.xml", "res/xml/popup_smileys_with_return.xml")

def scan(blob):
    u16 = lambda p: struct.unpack_from("<H", blob, p)[0]
    u32 = lambda p: struct.unpack_from("<I", blob, p)[0]
    strings, keys, at = [], [], 8
    def len8(pos):
        x=blob[pos];pos+=1
        if x&128: x=((x&127)<<8)|blob[pos];pos+=1
        return x,pos
    def len16(pos):
        x=u16(pos);pos+=2
        if x&32768: x=((x&32767)<<16)|u16(pos);pos+=2
        return x,pos
    while at < len(blob):
        kind,header,size=struct.unpack_from("<HHI",blob,at)
        if size <= 0: raise ValueError("Invalid AXML chunk")
        if kind == 1:
            for i in range(u32(at+8)):
                p=at+u32(at+20)+u32(at+header+4*i)
                if u32(at+16)&256:
                    _,p=len8(p);n,p=len8(p)
                    strings.append(blob[p:p+n].decode("utf8","replace"))
                else:
                    n,p=len16(p)
                    strings.append(blob[p:p+n*2].decode("utf-16le","replace"))
        elif kind == 0x102:
            name=strings[u32(at+20)]
            attrs={}
            for i in range(u16(at+28)):
                p=at+16+u16(at+24)+i*20
                _,index,raw,_,_,dtype,value=struct.unpack_from("<IIIHBBI",blob,p)
                attrs[strings[index]]=(strings[raw] if raw!=0xffffffff else
                   strings[value] if dtype==3 else "0x%08x"%value)
            if name == "Key": keys.append(attrs)
        at += size
    return [{"label":k.get("keyLabel"),"codes":k.get("codes"),
             "icon":k.get("keyIcon")} for k in keys]

def main(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError("Corrupt APK")
        result={p:scan(z.read(p)) for p in PATHS}
        result["dex_gif_keycode_defined"] = b"keycode_gif" in z.read("classes.dex")
        dex=z.read("classes.dex")
    for name in PATHS:
        keys=result[name]
        assert len(keys)==3, (name, keys)
        assert keys[1]["label"]=="GIF", (name, keys)
        assert keys[1]["codes"]==keys[2]["codes"], (name,keys)
    result["gif_dispatch_indicators"]={
        "keycode_gif":dex.count(b"keycode_gif"),
        "keycode_emoticon":dex.count(b"keycode_emoticon"),
        "InputContentInfo":dex.count(b"InputContentInfo"),
        "commitContent":dex.count(b"commitContent"),
        "KLIPY":dex.count(b"KLIPY"),
        "GifDecoder":dex.count(b"GifDecoder"),
        "GifView":dex.count(b"GifView"),
    }
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("CHECK: Both popup layouts map GIF to the same keycode as emoji.")
    print("This is a diagnostic; it does not implement GIF search, send, or a new handler.")

if __name__=="__main__":main(sys.argv[1])
