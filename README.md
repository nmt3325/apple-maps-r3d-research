# Apple Maps R3D / Flyover research

Apple Maps iOS 27のR3Dを調査し、**元のテクスチャ付きポリゴンとsoft triangle Splatを復元・表示する研究**の成果をまとめたスナップショットです。2026-10-14 JST時点。

**東京のネイティブ復号済みハイブリッド表示は実現済みです。Linuxだけで新規R3Dからポリゴン・Splat数値を完全復号する処理は未完成です。** soft triangle Splatを通常の楕円3D Gaussian Splattingと同一とは断定していません。

## 現在の成果

| 対象 | 検証結果 | 状態 |
|---|---|---|
| 東京R3D | 223タイル、736,915 Splatレコード | ネイティブ参照データ取得済み |
| Splat描画 | 417,650個のalpha可視三角形、元の頂点/RGBA | ブラウザ表示・GLB出力済み |
| 元のC3Mポリゴン | 223タイル、1,922,693面、223枚の元HEICアトラス | XYZ・面・UV・法線・テクスチャ取得済み |
| ハイブリッド表示 | 元のポリゴン＋Splat、UV上下方向修正、WASD・Q/E飛行 | 動作検証済み |
| Oahu Hilton取得 | 72 R3D、304,527 Splatレコード、216 HEIC | 新規取得・ヘッダー/画像抽出済み |
| Linux R3Dフレーム解析 | 東京223＋Oahu72、590 BYET/Jストリーム、12,980レーン | 境界・長さ・ヘッダー検証済み |
| HEIC抽出 | 計885画像、東京primary atlas 223件がnative出力と一致 | native-free |
| HUFF復号 | 2,659圧縮候補、739,702出力byte、復号reject 0 | 指定/推定出力長による中間復号。native中間byteとの一致は未証明 |
| BYET kind 0 | 21座標レーン中20で先頭N byteがnative低位byteと一致 | 残り2N byteと1つのZ原点差は未解決 |
| C3MM v2 | 6サンプル・36 LZMA区画、タイルz/x/y復元 | 構造解析済み、階層意味は一部未解決 |
| 新規地域のLinuxのみでの完全3D復元 | Splat XYZ/属性、TRICO mesh XYZ/面/UV | 未完成 |

HUFFの別研究では2,424個の0x24 envelope内で1,462圧縮table＋962 literalを検証しています。上記2,659件とは走査対象・候補検出方法が違い、件数を単純に比較できません。出力長の意味・呼び出し元からの値は引き続き要検証です。

## ファイル構成

| 場所 | 内容 |
|---|---|
| [codec/](codec/) | 独立Python実装：R3D/TLV、compact size、HEIC、BYET origin/J directory、HUFF、C3MM |
| [audit/](audit/) | レーン照合・コーパス検証。主要HUFF/ BYET監査はrepo内codecを参照 |
| [viewer/](viewer/) | 現行HTML、依存package情報、vendorライセンス |
| [snapshots/viewer/](snapshots/viewer/) | CT104の元ビューワ・変換・GLB/PLY出力・ブラウザ検証スクリプト |
| [snapshots/apple-maps-region-fetch-lab-20261013/](snapshots/apple-maps-region-fetch-lab-20261013/) | 別作業の取得/計画ツールを読み取り専用で複製 |
| [native-harness/](native-harness/) | Mac iOS Simulatorによる参照復号用Objective-C++と静的解析ツール |
| [research/](research/) | 各作業の解析コード、時刻付きcheckpoint、ARM64/Ghidra資料、履歴 |
| [reports/](reports/) | 過去の検証レポートと今回の検証記録 |
| [docs/](docs/) | 現状、フォーマット、再現方法、次の解析手順 |
| [data/](data/) | Releaseデータのファイル一覧・原本所在・SHA-256 |
| [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) | 元ソースの所在とハッシュ。移植調整は別記 |

元R3D、native golden、ビュー用バイナリ、GLB/PLY、抽出済み中間データは、**private Release `snapshot-20261014`** の添付に保存します。Git cloneだけでは実データは揃いません。5つのデータアーカイブには計6,338ファイル、圧縮後676,456,931 byte（約645 MiB）を収録しました。認証情報、署名付きURL、通信キャプチャ、インストール済みツール一式は収録しません。

## 最小の実行

Python 3.10以上。主要codecは標準ライブラリのみです。

```bash
python3 codec/huff816_nativefree.py
PYTHONPATH=codec python3 -c "from audit.test_nativefree_r3d import test_compact_size; test_compact_size(); print('PASS compact-size roundtrip')"
python3 codec/nativefree_r3d_codec_streams.py /path/to/tile.r3d
python3 codec/nativefree_extract_heic.py /path/to/r3d_directory --out-dir /path/to/heic
python3 codec/c3mm_v2_parser.py /path/to/tile.c3mm
```

[再現手順](docs/REPRODUCING.md) / [成果と限界](docs/STATUS.md) / [バイナリ形式](docs/FORMAT.md) / [次の作業](docs/CONTINUATION.md) / [元データと保存範囲](docs/PROVENANCE.md)

## 注意する区別

- native-freeヘッダー解析・画像抽出は、圧縮ジオメトリ数値の復号完了を意味しません。
- native-harnessは以前の参照データを得るためのApple依存経路です。Linux codecの最終目標には含めません。
- 過去メモは、その時点の誤解や後に置き換わった仮説も保存しています。現状の判断はこのREADMEとdocs/STATUS.mdを優先します。
- AppleのSplat shaderに由来するalpha式は調査済みですが、公式uniform値・タイル累積・LOD・最終合成のpixel parityは未達です。

リポジトリは研究スナップショットです。コード・第三者由来資料・Apple由来データの出所は[PROVENANCE](docs/PROVENANCE.md)で区別しています。一括でMIT等のライセンスを適用していません。
