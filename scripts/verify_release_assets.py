#!/usr/bin/env python3
"""Verify every release archive against the source-file SHA-256 inventory."""
from pathlib import Path
import hashlib,json,tarfile,datetime
ROOT=Path(__file__).resolve().parents[1]
def digest_stream(f):
 h=hashlib.sha256()
 for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 assets=json.loads((ROOT/'data/RELEASE_ASSETS.json').read_text())['assets']
 rows=json.loads((ROOT/'data/REFERENCE_INVENTORY.json').read_text())['files']
 results=[]
 for spec in assets:
  path=ROOT/'release-assets'/spec['file']
  with path.open('rb') as f:assert digest_stream(f)==spec['sha256'],path
  expected={r['archivePath']:r for r in rows if r['asset']==spec['file']}
  seen=set()
  with tarfile.open(path,'r|gz') as tf:
   for member in tf:
    assert member.isfile(),member.name
    assert member.name in expected and member.name not in seen,member.name
    row=expected[member.name]
    assert member.size==row['bytes'],member.name
    with tf.extractfile(member) as f:assert digest_stream(f)==row['sha256'],member.name
    seen.add(member.name)
  assert seen==set(expected)
  result={'archive':spec['file'],'filesVerified':len(seen),'sha256Matched':True}
  results.append(result);print(json.dumps(result),flush=True)
 assert sum(r['archivePath'].endswith('.polybuf') for r in rows)==223
 assert sum(r['archivePath'].startswith('flyover-viewer/www/vendor/') for r in rows)==3
 report={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allPassed':True,'archives':results,'totalFilesVerified':len(rows),'viewerPolybufCount':223,'viewerVendorCount':3}
 (ROOT/'reports/RELEASE_VALIDATION.json').write_text(json.dumps(report,indent=2))
 print('PASS all archive contents verified',len(rows),flush=True)
if __name__=='__main__':main()
