# 2026-10-14 JSTの状態

**macOS実行時解析の追補（2026-10-15）：** 同じVectorKit buildの解析用MapKitホストからSplat drawの定数 `c=1.5 / p=148.16207885742188`、対応GPU配列、function constants、imageblock 32 / BGRA8Unorm_sRGB / Depth32Float_Stencil8のrender passを取得。東京450/900/1800mとOahuの標本を監査し、command dataを含むGPU captureも保存した。純正Mapsの初回sampleによるUUID・footprint取得は成功したが、LLDB attachはtimeout、純正MapsのTraceは対象GPUイベント0件。**純正Maps.appのuniformやiOS runtimeの確認、最終frame一致とは区別する。** [報告と再現手順](../research/macos-maps-20261015/README.md)。以下は前日までの成果と制約。

**高さ層の追補（2026-10-14）：** 旧Oahu72はh0原本の復号・配列検証であり、地域上部の取得が不足していた。高さ占有インデックスから全層を取得する修正で135タイルへ補完し、配列・表示・出力を再検証。旧数値証拠は有効だが、旧72だけで高層部分まで表示できるとは扱わない。[修正後の証拠](../reports/height-layers-20261014/README.md)。

対応するR3Dについて主要目標の6条件を達成。証拠は[validation-20261014](../reports/validation-20261014/README.md)。[ACCEPTANCE.md](ACCEPTANCE.md)の6項目をすべて満たした時点で達成とする。以下の部分的な成果はその判定と区別する。

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

Oahu72も原本だけから304,527 Splatと581,186元ポリゴン面を復号しました。元テクスチャ付きポリゴンとSplatを表示し、全viewer配列・画像・地理範囲・同じR/ECEF→ENUの適用を検証しました。ブラウザの15チェック（WASD/EQ/mouse/Esc/layer toggleを含む）も通過。独立GLB/PLYの全配列読み戻しは一致、Khronos検証器はerror/warning 0です。

過去のHUFF監査は探索履歴として保存します。現在の全配列比較はレーン内compact整数から実際の出力symbol数を取り、word境界・entropy消費・paddingも検証するdecoderで実行しています。

C3MM v2は6つのサンプルで36圧縮区画が宣言長どおり復号でき、元タイルz/x/yをbinaryから復元できています。局所16x16のpacked XYとcoverage照合は実装済みですが、low-bit markerとh1/階層・tag1/tag6の意味は未確定です。

## 再現と保存

別Ubuntu24.04/aarch64でfresh cloneと隔離venvからOahu72と座標入口を再現しました。936配列/画像hash、GLB/PLYのSHAはx86_64と完全一致。原本破損/別座標のrejectと全region/export監査も通過。独立成果物と新しい座標取得原本はprivate Release linux-explorer-20261014へ保存しました。手順は[LINUX_EXPLORER.md](LINUX_EXPLORER.md)。

ユーザー指定でOahuサーバーをsystemdに起動し、Tailscale HTTPS8972で公開。別LinuxからTLS検証付きscene GETも成功。URL：https://ct104.taila8c9c.ts.net:8972/。

## Apple独自Triangle SplatのGPUパリティ研究（2026-10-14）

AppleのmacOS Metal環境でiOS由来のtriangle Splatの描画式を検証し、単一東京Splatの64×64画素alpha比較でRMSE 1.3384e-5（境界1画素差）を得ました。別の実RGBA色サンプルでもM4 GPUの色合成を測定しました。iOS/macOS Metal IRは対象8個中6個が同一、残り2個は異なります。標準Gaussian近似は1個と3個を比較しましたが、Appleの実行時alpha定数や公式iOS最終フレームの一致は**未検証**です。詳細と再現用コードは [GPU Splat研究](../research/ios27-metal-splat-20261014/README.md) を参照してください。

## 残る追加目標・制約

Apple公式pixel parity、正確なLOD、独自tile accumulation/color transferは未達です。ブラウザはbarycentric alpha、GLBは標準alpha blendなので同じ表示にはなりません。取得にはローカル設定が必要で、coverage/API/versionに依存します。decoderは既知のR3D v2/TRICO mesh v3等に対応し、未知variantは明示rejectします。全世界のサービスcoverageを保証するという意味での完了ではありません。

過去メモの未達・部分復号という記述は探索時点の履歴です。現在の判断はREADME、ACCEPTANCEと実証レポートを優先します。
