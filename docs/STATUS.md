# 2026-10-14 JSTの状態

主要目標は未達。[ACCEPTANCE.md](ACCEPTANCE.md)の6項目をすべて満たした時点で達成とする。以下の部分的な成果はその判定と区別する。

## 完了した経路

東京223タイルは、以前にMac上のiOS 27 Simulator / VectorKitを使って復号しています。Splatの元triangle/material buffer、およびC3Mの位置・UV・法線と各index配列・HEICアトラスが保存されています。

- Splatレコード736,915。createSplats出力は各レコード3頂点、計2,210,745頂点。alpha可視417,650三角形。
- C3Mは1,922,693面。描画用にindexを統合した位置/UV/法線の組合せは1,203,476。
- z19の元meshは21タイル247,750面。z20は201タイル1,660,801面。z18を含め223タイル。
- Three.js TextureLoaderのflipY=trueがnative UV表示に対応。GLB exporterのV変換とは区別する。
- WASD移動、E上昇、Q下降、mouse look、orbit復帰がブラウザ検証済み。
- GLBは元頂点・面・画像を運べるが、Apple専用Splat shaderそのものは含まない。

## Linuxの独立処理

R3D原本からSplatの3頂点XYZ・8属性・material20と、元ポリゴンのXYZ・UV・法線・3種類の面index・HEICを復元する標準Python実装ができています。Appleライブラリ、Simulator、native golden、参照命令列は実行時に不要です。入口は`codec/nativefree_decode_r3d.py`です。

東京223でSplat XYZ 6,632,235 float、8属性5,895,320 float（NaNも含む）、material20 14,738,300 byteが完全一致しました。ポリゴンXYZ 3,172,779 float、UV 2,405,452 float、3種類のindex各5,768,079個、223 primary HEICも完全一致です。法線3,175,104 float中271個には1 ULP、最大絶対5.960464477539063e-8の差があります。全差異について90桁Decimal三角関数とnative側の隣接float32丸めで説明・検証しています。[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)に詳細と再現コマンドを記録しました。

kind0の3*N byteはSplatの3頂点分です。旧`.decoded` goldenは位置配列の先頭N頂点だけを保存しており、全3*N頂点は`.native-triangle-f32`にあります。原点の+1差はint32境界をまたぐbyteの繰り返しで説明でき、タイル固有の例外を除去しました。

Oahu72も原本だけから304,527 Splatと581,186元ポリゴン面を復号しました。元テクスチャ付きポリゴンとSplatのハイブリッド表示・位置合わせ検証はまだ完了していません。

過去のHUFF監査は探索履歴として保存します。現在の全配列比較はレーン内compact整数から実際の出力symbol数を取り、word境界・entropy消費・paddingも検証するdecoderで実行しています。

C3MM v2は6つのサンプルで36圧縮区画が宣言長どおり復号でき、元タイルz/x/yをbinaryから復元できています。局所16x16のpacked XYとcoverage照合は実装済みですが、low-bit markerとh1/階層・tag1/tag6の意味は未確定です。

## まだできていないこと

1. Oahuを独立decoderから元テクスチャ付きポリゴン＋Splatとして描画し、地理位置・レイヤー位置合わせまで検証する。
2. 任意の緯度・経度・範囲から取得、完全独立復号、自由移動表示を一体化する。
3. 独立復号出力のGLB/PLY等のexport、新しいLinux環境での完全経路の再現を揃える。
4. 最終の実装・検証・制約をGitHubに保存し、主要目標達成時に再現コマンドと証拠を提示する。
5. 追加目標：Apple公式表示のpixel parity、uniform、tile accumulation、color transfer、正確なLOD選択。

過去メモの「polygon未取得」「222/223 origin」「native-free geometry未完成」は、その時点の履歴です。独立した数値復号は今回実装・照合済みですが、取得から表示までの主要目標は引き続き未達です。
