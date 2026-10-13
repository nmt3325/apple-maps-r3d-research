# 独立した数値復号

2026-10-13 UTCの実装。`codec/nativefree_decode_r3d.py`は、R3D原本だけを入力に、元のポリゴンとSplatを復元する。Python標準ライブラリのみで動き、Appleライブラリ・iOS Simulator・native golden・ARM64参照資料を実行時に読まない。

## 出力と実行

```bash
python3 codec/nativefree_decode_r3d.py /path/to/r3d_directory \
  --out-dir output/decoded --workers 4
```

入力の各タイルについて出力ディレクトリを作る。

| 出力 | 型・shape |
|---|---|
| splat-xyz-f32le.bin | N三角形 × 3頂点 × XYZ、float32 LE |
| splat-attributes-f32le.bin | N × 8属性、float32 LE |
| splat-material20.bin | N × 20 byte：RGBA uint8、後続4属性 float32 LE |
| mesh-xyz-f32le.bin | 位置数 × XYZ、float32 LE |
| mesh-uv-f32le.bin | UV数 × UV、float32 LE、元アトラスで正規化 |
| mesh-normals-f32le.bin | 法線数 × XYZ、float32 LE |
| mesh-position-indices-u32le.bin | 面数 × 3位置index、uint32 LE |
| mesh-uv-indices-u32le.bin | 面数 × 3 UV index、uint32 LE |
| mesh-normal-indices-u32le.bin | 面数 × 3法線index、uint32 LE |
| mesh-face-materials-u32le.bin | 面ごとのアトラス番号、uint32 LE |
| atlas-0.heic / atlas-1.heic / atlas-2.heic | R3D内の元画像そのまま |
| tile.json / manifest.json | shape・SHA-256・原本の座標変換・検証結果・実行コマンド |

XYZと法線は元タイルのローカル座標。表示時は同じR3D内の回転とECEF並進をポリゴン/Splatの両方に適用する。

## 東京223の数値照合

```bash
python3 audit/audit_soup_arrays.py "$R3D_REFERENCE_ROOT/native-r3d" \
  "$R3D_REFERENCE_ROOT/decoded-native/all-223" \
  --report reports/generated/splat-arrays.json --workers 4
python3 audit/audit_mesh_arrays.py "$R3D_REFERENCE_ROOT/native-r3d" \
  "$R3D_REFERENCE_ROOT/decoded-native/c3m-all-223" \
  --report reports/generated/mesh-arrays.json --workers 4
python3 -m unittest audit.test_numeric_codec -v
```

goldenを読むのはaudit側だけ。decoderは原本から生成する。各タイル・各配列の比較総数、不一致数、ハッシュとfloat bit比較を記録する。

| 配列 | 比較総数 | 結果 |
|---|---:|---|
| Splat XYZ | 6,632,235 float | bit完全一致 |
| Splat 8属性 | 5,895,320 float | bit完全一致。canonical NaN 33,958個も一致 |
| Splat material20 | 14,738,300 byte | 完全一致 |
| ポリゴンXYZ | 3,172,779 float | bit完全一致 |
| ポリゴンUV | 2,405,452 float | bit完全一致 |
| ポリゴン法線 | 3,175,104 float | 271個に1 ULPの説明済み差、残りはbit一致 |
| 位置/UV/法線index | 各5,768,079 index | 3配列とも完全一致 |
| 元primary HEIC | 223画像、12,402,125 byte | 完全一致 |

native goldenに保存された画像はタイルごとにprimary atlas 1枚。原本にはほかに2画像があり、decoderはそれらも元byteのまま抽出する。goldenのない画像との比較を実施済みとは扱わない。

### 法線の許容誤差と原因

法線は元のpacked spherical値から復元する。全271個の差はY成分のみで、入力packed値は`0x002d0025`または`0x00430020`。保存済み命令列はfloat32角度計算、paired sine/cosine呼び出し、float32積を使う。独立実装はPythonの倍精度三角関数をfloat32に丸める。

`audit/normal_math_evidence.py`は90桁のDecimal Taylor展開で独立にsin/cosを計算する。各不一致について、独立実装の値がこの計算と一致し、goldenの値がsin(phi)の隣接float32を使った積と一致することを検証する。全271個の入力値・角度bit・出力bit・互換になるnative側sin(phi) bitをレポートに残す。native三角関数の近似丸めによる差という説明は、命令列とこの数値証拠に基づく。

許容する差は法線に限り最大1 ULP、絶対誤差最大`5.960464477539063e-8`。XYZ、UV、Splat属性、件数、index、画像には許容誤差を設けない。法線差を説明できなかった場合はauditが失敗する。goldenに合わせた補正表はdecoderに入れない。

### 欠損属性

BYET quantized deltaの`-1`は原点加算前にcanonical NaN `0x7fc00000`へ戻す。`-2`は負の無限大、`-3`は正の無限大。東京の実入力ではNaNはRGB 3属性に限られ、描画materialのRGB変換は0になる。生の8属性を改変して有限値にすることはしない。出力検証は予期しない非有限値を拒否し、既知の欠損RGBの個数と扱いを明記する。

## 対応範囲

R3D v2、TRICO soup v1、TRICO mesh v3、BYET/J kind0..6、single/chained Huff8/16、primary atlas番号0で検証している。別バージョン、複数primary atlas、未対応BYETフラグ、複数ispeを持つHEICは明示的に拒否する。正常に復号できる地域でもタイルの有無・取得用認証・バージョン選択は取得側の課題として残る。

HUFFはレーン内compact整数から出力symbol数を取得し、表とentropyをword境界で区別する。symbol消費後のentropy長とゼロpaddingを検証する。各BYET/TLVブロックの長さ、meshの全index範囲、XYZ/UV/法線の有限値、法線長、UV範囲を検証する。

参照命令列とGhidra出力は`research/static-codec/`の解析資料であり、実装とは別物。実行時には不要。全体の完了判定は[ACCEPTANCE.md](ACCEPTANCE.md)による。Oahuの表示、取得から表示への統合、GLB/PLY出力、新しいLinux環境での完全経路の再現は引き続き必要。
