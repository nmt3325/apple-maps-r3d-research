# 2026-10-14 JSTの状態

## 完了した経路

東京223タイルは、以前にMac上のiOS 27 Simulator / VectorKitを使って復号しています。Splatの元triangle/material buffer、およびC3Mの位置・UV・法線と各index配列・HEICアトラスが保存されています。

- Splatレコード736,915。createSplats出力は各レコード3頂点、計2,210,745頂点。alpha可視417,650三角形。
- C3Mは1,922,693面。描画用にindexを統合した位置/UV/法線の組合せは1,203,476。
- z19の元meshは21タイル247,750面。z20は201タイル1,660,801面。z18を含め223タイル。
- Three.js TextureLoaderのflipY=trueがnative UV表示に対応。GLB exporterのV変換とは区別する。
- WASD移動、E上昇、Q下降、mouse look、orbit復帰がブラウザ検証済み。
- GLBは元頂点・面・画像を運べるが、Apple専用Splat shaderそのものは含まない。

## Linuxの独立処理

R3Dフレーム、TRICO header、BYET/J directory、compact integer、HEIC抽出、ECEF変換は実装済み。東京223＋Oahu72の計295でフレーム検証済みです。原点検証は座標minの下限/差を確認したもので、XYZ全数値の一致ではありません。

HUFF復号はコード表・MSB-first bit reader・literal branchを実装しました。先行監査は2,659圧縮候補を739,702 byteへ復号しreject 0ですが、指定/推定symbol countを用いた結果です。内部byte-array goldenと一致していることも、BYETの最終floatになったことも未証明です。

別研究の0x24限定の走査は2,424 envelopes、1,462 compressed prefix tables、962 literalsを検証しました。走査対象やheader位置の選び方が違うため先行監査との差は未解消です。どちらの集計も保存しています。

kind0座標レーン21本は入力が3*N byte。先頭N byteだけを既存native XYZの低位byteと比較し20本一致しました。残るZ laneは297点全部で+1、sparse origin headerは0877065cfeff5afefff5ffです。後続2*N byteの解釈とsparse packingは未解決です。

C3MM v2は6つのサンプルで36圧縮区画が宣言長どおり復号でき、元タイルz/x/yをbinaryから復元できています。局所16x16のpacked XYとcoverage照合は実装済みですが、low-bit markerとh1/階層・tag1/tag6の意味は未確定です。

## まだできていないこと

1. 新規R3DのSplat XYZ・8属性をLinuxだけで全数値復号する。
2. TRICO mesh v3の全位置・面・UV・法線をLinuxだけで復号する。
3. Oahuを独立decoderからフル3Dとして描画する。
4. 任意地域fetcherから完全native-free hybrid viewerまでを一体化する。
5. Apple公式renderingとのpixel parity、uniform、tile accumulation、LOD選択。

過去メモの「polygon未取得」「222/223 origin」のような記述は段階的な履歴です。元polygon取得は後に完了しています。一方、native-free geometry未完成という判断は現在も有効です。
