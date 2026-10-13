import sys, glob
sys.path.insert(0, '/opt/flyover-viewer')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
for f in sorted(glob.glob('/opt/flyover-viewer/native-r3d/*.r3d'))[:2]:
    b = open(f, 'rb').read()
    s = dissect(b)['splatStream']
    print(f)
    for frame in s['blocks']:
        spec = frame['byet']
        p = s['offset'] + spec['compressedPayloadRelativeOffset']
        whole = b[p:p+spec['compressedPayloadBytes']]
        lay = split_j(whole, 12 if frame['index']==0 else 32)
        for d in lay['descriptors']:
            if d['compressedBytes']:
                raw = whole[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
                print(frame['index'], d['lane'], d['kind'], len(raw), raw[:20].hex())
