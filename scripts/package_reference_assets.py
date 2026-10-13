#!/usr/bin/env python3
"""Package local reference corpora and generated 3D outputs; never capture credentials."""
from pathlib import Path
import datetime,hashlib,json,re,tarfile
ROOT=Path(__file__).resolve().parents[1]
VIEWER=Path('/opt/flyover-viewer')
WORK=Path('/root/.desktop-mcp/linux-4ebec5ed/work')
OUT=ROOT/'release-assets'
OUTPUT_EXT={'.r3d','.c3mm','.png','.jpg','.jpeg','.heic','.bin','.decoded','.native-triangle-f32','.native-material20','.glb','.ply','.geojson','.json','.raw','.polybuf','.js','.txt','.trico-soup','.trico-mesh','.byet-j'}
groups={
 'tokyo-r3d':[(VIEWER/'native-r3d','flyover-viewer/native-r3d')],
 'oahu-and-fetch-results':[(WORK/'apple-maps-region-fetch-lab-20261013/fresh_signed','fetch-lab/fresh_signed'),(WORK/'apple-maps-region-fetch-lab-20261013/exports','fetch-lab/exports')],
 'native-goldens':[(VIEWER/'decoded-native','flyover-viewer/decoded-native')],
 'viewer-assets-and-exports':[(VIEWER/'www','flyover-viewer/www')],
 'nativefree-intermediates':[(VIEWER/d,'flyover-viewer/'+d) for d in ['nativefree-regions','nativefree-huff-raw-tokyo','nativefree-huff-raw-oahu','nativefree-trico-tokyo','nativefree-trico-oahu','nativefree-oahu-textures']],
}
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def selected(p):
 # Several intermediates use a nonstandard trailing stream extension.
 return p.suffix in OUTPUT_EXT or '.trico-' in p.name or p.name.endswith('.byet-j')
def check_metadata(p):
 if p.suffix not in {'.json','.geojson'}:return
 t=p.read_text()
 if re.search(r'https?://[^ ]+(?:accessKey|token)=',t,re.I):
  raise ValueError('Signed URL in metadata: '+str(p))
 obj=json.loads(t)
 def walk(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if k.lower() in {'authorization','cookie','password','accesskey','tokenp1','tokenp2','api_key'} and v:
     raise ValueError('Credential metadata key in '+str(p))
    walk(v)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(obj)
def main():
 OUT.mkdir(exist_ok=True)
 inventory=[];assets=[]
 for name,roots in groups.items():
  files=[]
  for src,prefix in roots:
   if not src.exists():continue
   for p in sorted(src.rglob('*')):
    if p.is_file() and selected(p):
     check_metadata(p)
     files.append((p,str(Path(prefix)/p.relative_to(src))))
  asset=OUT/(name+'.tar.gz')
  with tarfile.open(asset,'w:gz',compresslevel=1) as tf:
   for p,arc in files:
    before=p.stat()
    digest=sha(p)
    tf.add(p,arcname=arc,recursive=False)
    after=p.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
     raise RuntimeError('File changed during snapshot: '+str(p))
    inventory.append({'asset':asset.name,'archivePath':arc,'source':str(p),'bytes':before.st_size,'sha256':digest})
  row={'file':asset.name,'files':len(files),'sourceBytes':sum(p.stat().st_size for p,_ in files),'archiveBytes':asset.stat().st_size,'sha256':sha(asset)}
  assets.append(row);print(json.dumps(row),flush=True)
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (ROOT/'data').mkdir(exist_ok=True)
 (ROOT/'data/REFERENCE_INVENTORY.json').write_text(json.dumps({'snapshotUTC':stamp,'files':inventory},indent=2))
 (ROOT/'data/RELEASE_ASSETS.json').write_text(json.dumps({'snapshotUTC':stamp,'assets':assets,'excluded':['Credential-bearing .mitm/.har captures, ingest.token, key stores, installed node_modules/Ghidra/JDK/Unicorn, duplicate source .tar archives.']},indent=2))
 (OUT/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['file']+'\n' for r in assets))
 print('PACKAGING_COMPLETE',len(inventory),sum(r['archiveBytes'] for r in assets),flush=True)
if __name__=='__main__':main()
