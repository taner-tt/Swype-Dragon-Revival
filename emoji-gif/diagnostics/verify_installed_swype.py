#!/usr/bin/env python3
"""Read-only ADB verification of installed Swype APK, no private app data access."""
import argparse,hashlib,re,subprocess,tempfile
from pathlib import Path
def adb(*args):
 p=subprocess.run(['adb',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr.strip())
 return p.stdout
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def packages(text):
 return sorted(m.group(1) for line in text.splitlines() if (m:=re.fullmatch(r'package:([\w.]+)',line.strip())) and 'swype' in m.group(1).lower())
def verify(path):
 if not path.is_file():raise FileNotFoundError(path)
 p=packages(adb('shell','pm','list','packages'))
 if len(p)!=1:raise RuntimeError('Expected one Swype package; found '+repr(p))
 lines=adb('shell','pm','path',p[0]).splitlines()
 base=[x[8:].strip() for x in lines if x.startswith('package:') and x.strip().endswith('/base.apk')]
 if len(base)!=1:raise RuntimeError('Cannot identify single base APK; check for split install.')
 with tempfile.TemporaryDirectory() as tmp:
  pulled=Path(tmp)/'base.apk'
  adb('pull',base[0],str(pulled))
  installed=sha(pulled)
 expected=sha(path)
 print('Package:',p[0]);print('Reference APK SHA256:',expected)
 print('Installed APK SHA256:',installed)
 print('Byte-identical to reference:',installed==expected)
 if len(lines)>1:print('Warning: installation includes split APKs, comparison checks base only.')
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('reference_apk',type=Path)
 verify(a.parse_args().reference_apk)
