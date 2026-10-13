from pathlib import Path
p=Path('/opt/flyover-viewer/www/index.html')
s=p.read_text()
replace=[
 ('<label for="scale">高さの表示倍率</label><strong id="scaleVal">2.0×','<label for="scale">補助メッシュの高さ倍率（R3D校正済み）</label><strong id="scaleVal">1.0×'),
 ('id="scale" type="range"','id="scale" type="range"'),
 ('val*2;verts[3*v+2]','51.68+val*0.788;verts[3*v+2]'),
 ('p.setY(i,h[i]*m);','p.setY(i,51.68+h[i]*0.788*m);'),
]
for src,dst in replace:
 if s.count(src)<1:print('missing',src)
 else:s=s.replace(src,dst,1)
# Slider order may differ, inspect after replacement
p.write_text(s)
print('Calibrated heights to captured R3D roof heights; backup preserved.')
