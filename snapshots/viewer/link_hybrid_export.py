from pathlib import Path
p=Path('/opt/flyover-viewer/www/index.html')
s=p.read_text()
key='<a href="./Apple-Flyover-iOS27-native-417650-triangles.glb" download>純正三角Splat 417,650面のGLBモデルを取得（25.1 MB）</a>'
assert s.count(key)==1
s=s.replace(key,key+'</div>\n  <div class="tiny" style="margin-top:7px"><a href="./Apple-Flyover-hybrid-native-splats-calibrated-proxy.glb" download>2レイヤーのハイブリッドGLB（27.6 MB）</a></div>\n  <div class="tiny">ポリゴン側は校正した高さPNGの代替メッシュです。Apple純正C3Mモデルではありません。',1)
p.write_text(s)
print('Linked two-layer hybrid GLB in viewer')
