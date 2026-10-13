from pathlib import Path
p=Path('/opt/flyover-viewer/www/index.html')
s=p.read_text()
repls=[
 ('三角Splatの重ね合わせ強度（近似）','Apple式 alphaPreFactor（係数は未特定）'),
 ('id="splatOpacityVal">3.0×','id="splatOpacityVal">81'),
 ('id="splatOpacity" min="0.5" max="8" step="0.5" value="3"','id="splatOpacity" min="1" max="400" step="1" value="81"'),
 ('三角Splatの縁の柔らかさ（近似）','Apple式 alphaConcentration（係数は未特定）'),
 ('Appleの独自合成処理とは異なるため、透明度を見やすさ優先で調整します。','Metalの原式を使い、係数AとCの実際の値は未特定のため手動調整できます。'),
 ('alphaScale:{value:3.0}','alphaPreFactor:{value:81.0}'),
 ('uniform float alphaScale;','uniform float alphaPreFactor;'),
 ('pow(clamp(27.0*prod,0.0,1.0),splatExponent)','pow(prod,splatExponent)'),
 ('min(0.995,vRGBA.a*coverage*alphaScale)','min(0.99,vRGBA.a*coverage*alphaPreFactor)'),
 ("nativeTriangleMat.uniforms.alphaScale.value=+e.target.value;document.getElementById('splatOpacityVal').textContent=(+e.target.value).toFixed(1)+'×';","nativeTriangleMat.uniforms.alphaPreFactor.value=+e.target.value;document.getElementById('splatOpacityVal').textContent=String(+e.target.value);")
]
for src,dst in repls:
 if s.count(src)!=1:raise ValueError(f'{src[:30]} count={s.count(src)}')
 s=s.replace(src,dst)
p.write_text(s)
print('Installed exact native fragment equation and two clearly estimated parameters.')
