# Apple Maps R3D / Flyover research

## iOS ネイティブ・視界に応じた直接取得

`ios/R3DExplorer.xcodeproj` に SwiftUI + Metal の iPhone / iPad アプリを追加。Apple Maps の R3D / C3MM を端末から直接取得し、独立 decoder を端末内で実行する。カメラ移動に応じた取得、全高さ、距離別 LOD、視界外モデルの解放、容量制限付きキャッシュ、青空・太陽・雲を実装している。既存の研究用 Web ビューアも保持する。

セットアップ・操作・検証・制約は [IOS_STREAMING.md](docs/IOS_STREAMING.md)。`bash ios/Scripts/bootstrap.sh` 後に Xcode project を開く。標準の配信情報と公開済みの共通定数から端末内で署名し、外部の取得設定や GitHub Secrets なしで起動できる。Actions の `R3DExplorer-unsigned-ipa` artifact にインストール用 IPA を提供する。

Apple Maps iOS 27のR3Dを調査し、**元のテクスチャ付きポリゴンとsoft triangle Splatを復元・表示する研究**の成果をまとめたスナップショットです。2026-10-14 JST時点。

**Linuxの独立decoder、東京223の全配列照合、Oahu72の元配列検証と、全高さ135タイルの元テクスチャ付きポリゴン＋Splat表示、座標入力からの取得・復号・表示・GLB/PLY出力を実装・検証しました。別Ubuntu24.04 ARM Linuxでも再現し、936配列/画像とGLB/PLYのhashが一致しました。GitHub Releaseへ成果物を保存済みで、対応するR3Dについて主要6条件を達成しました。** soft triangle Splatを通常の楕円3D Gaussian Splattingと同一とは断定していません。

主要目標は任意の緯度・経度・範囲からLinuxだけで取得・完全復号・自由移動表示まで実行することです。[6項目の完了条件](docs/ACCEPTANCE.md)をすべて満たした場合に達成と判定します。公式表示とのpixel一致、正確なLOD、タイル累積・色変換の完全再現は別の追加目標として追跡します。

**高層部分の取得漏れを修正済み。** 従来は高さ層h0だけを取得していたため、Oahu72の上部が欠けていました。C3MM占有インデックスから全高さ候補を取得し、Oahuは135タイルへ補完。元72の936配列/画像は完全一致を保持し、上部ポリゴン・SplatとGLB/PLYを再検証しました。[修正仕様・再現手順](docs/HEIGHT_LAYERS.md) / [検証証拠](reports/height-layers-20261014/README.md)。

稼働中のビューア（Tailscale内）：**https://ct104.taila8c9c.ts.net:8972/**。地図で場所と範囲を選び、タイル数を確認してから取得・表示できます。完成成果物は [全高さ修正版Release](https://github.com/nmt3325/apple-maps-r3d-research/releases/tag/linux-explorer-height-layers-20261014)、[6条件の検証証拠](reports/validation-20261014/README.md)、[再現手順](docs/LINUX_EXPLORER.md)。ローカル取得設定、サービスcoverageと対応codecの制約は手順に明記しています。

**Web版の移動中ストリーミングを追加。** Appleからの取得・復号はサーバー側のまま、カメラの移動・回転に合わせて全高さ層のタイルを追加します。近距離z20／遠距離z18・z19の逐次表示、任意座標への移動、キャッシュとモデルの解放に対応します。[操作・設計・検証手順](docs/WEB_STREAMING.md)。

## 現在の成果

| 対象 | 検証結果 | 状態 |
|---|---|---|
| 東京R3D | 223タイル、736,915 Splatレコード | ネイティブ参照データ取得済み |
| Splat描画 | 417,650個のalpha可視三角形、元の頂点/RGBA | ブラウザ表示・GLB出力済み |
| 元のC3Mポリゴン | 223タイル、1,922,693面、223枚の元HEICアトラス | XYZ・面・UV・法線・テクスチャ取得済み |
| ハイブリッド表示 | 元のポリゴン＋Splat、UV上下方向修正、WASD・Q/E飛行 | 動作検証済み |
| Oahu Hilton h0原本の独立復号（従来検証） | 72 R3D、304,527 Splatレコード、581,186元ポリゴン面、216 HEIC | 全数値復号・元テクスチャ付き表示・地理/配列/画像検証済み |
| Oahu全高さ取得・独立復号 | 135 R3D、382,128 Splat、1,064,079元ポリゴン面 | 63上層追加、全配列/画像/位置合わせ/GLB/PLY検証、既存URLへ反映 |
| Linux独立Splat復号 | 東京223、XYZ 6,632,235 float・8属性5,895,320 float・material20 14,738,300 byte | 全配列bit/byte完全一致 |
| Linux独立ポリゴン復号 | 東京223、XYZ・UV・位置/UV/法線index・223 primary HEIC | bit/byte完全一致 |
| Linux独立ポリゴン法線 | 3,175,104 float中271個に1 ULP差 | 全差異をDecimal三角関数で説明、最大絶対誤差5.96e-8 |
| Linux R3Dフレーム解析 | 東京223＋Oahu72、590 BYET/Jストリーム、12,980レーン | 境界・長さ・ヘッダー検証済み |
| HEIC抽出 | 計885画像、東京primary atlas 223件がnative出力と一致 | native-free |
| 過去HUFF中間監査 | 2,659圧縮候補、739,702出力byte、復号reject 0 | 探索履歴。現在の数値decoderは実際のsymbol数を原本から復元 |
| BYET/J kind0..6 | 数値復号とtriangle/属性/mesh全配列照合 | 原点差と3*N byteの意味も解決 |
| C3MM v2 | 6サンプル・36 LZMA区画、タイルz/x/y復元 | 構造解析済み、階層意味は一部未解決 |
| 新規地域のLinuxのみでの完全3D復元 | Oahu72、304,527 Splat、581,186元ポリゴン面 | 地理・全viewer配列・画像照合、ブラウザ15操作チェック通過 |
| 座標から取得・復号・表示・出力 | 東京タワー4、新規ニューヨーク2をLinux HTTPS取得 | 一コマンド経路成功。ローカル取得設定が必要 |
| Web地図から地点選択 | Leaflet/OSM地図、中心座標/範囲、タイル数preview、取得ジョブとシーン切替 | Tailnet Webビューアへ提供中。1回24平面タイル/300m上限、全高さを自動取得 |
| 独立GLB/PLY export | Oahuの全geometry/UV/法線/画像/RGBA、PLYの8属性 | 全出力の読み戻し一致、Khronos GLB検証でerror/warning 0 |

過去のHUFF研究では2,424個の0x24 envelope内で1,462圧縮table＋962 literalを検証しました。上記2,659件とは走査対象・候補検出方法が違い、件数を単純に比較できません。現在の独立decoderは原本から実際のsymbol数を取得し、全配列照合とentropy消費・padding検証を通しています。

## ファイル構成

| 場所 | 内容 |
|---|---|
| [codec/](codec/) | 独立Python実装：R3D/TLV、compact size、HEIC、BYET origin/J directory、HUFF、C3MM |
| [audit/](audit/) | レーン照合・コーパス検証。主要HUFF/ BYET監査はrepo内codecを参照 |
| [viewer/](viewer/) | 現行HTML、依存package情報、vendorライセンス |
| [pipeline/](pipeline/) | Linuxの座標計画・署名取得・独立復号・ハイブリッド表示・GLB/PLY出力 |
| [snapshots/viewer/](snapshots/viewer/) | CT104の元ビューワ・変換・GLB/PLY出力・ブラウザ検証スクリプト |
| [snapshots/apple-maps-region-fetch-lab-20261013/](snapshots/apple-maps-region-fetch-lab-20261013/) | 別作業の取得/計画ツールを読み取り専用で複製 |
| [native-harness/](native-harness/) | Mac iOS Simulatorによる参照復号用Objective-C++と静的解析ツール |
| [research/](research/) | 各作業の解析コード、時刻付きcheckpoint、ARM64/Ghidra資料、履歴 |
| [reports/](reports/) | 過去の検証レポートと今回の検証記録 |
| [docs/](docs/) | 現状、フォーマット、再現方法、次の解析手順 |
| [data/](data/) | Releaseデータのファイル一覧・原本所在・SHA-256 |
| [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) | 元ソースの所在とハッシュ。移植調整は別記 |

元R3D、native golden、以前のビュー用バイナリとGLB/PLY、抽出済み中間データは、**private Release `snapshot-20261014`** に保存済みです。5つのデータアーカイブには計6,338ファイル、圧縮後676,456,931 byte（約645 MiB）を収録しました。

**private Release `linux-explorer-20261014`（旧h0版）** には独立復号したOahuの全配列・完成viewer・GLB/PLY（143,194,860 byteのarchive）と、東京タワー4/ニューヨーク2の新原本・独立出力・ログ（10,078,991 byteのarchive）を保存済みです。別Linuxからダウンロードし、両archiveのSHA-256一致を確認しました。最終確認と数値/表示検証の記録も添付しました。Git cloneだけでは実データは揃いません。認証情報、署名付きURL、通信キャプチャ、インストール済みツール一式は収録しません。

修正版の原本・C3MM・全135タイルの独立出力・viewer・GLB/PLY・ログは **private Release `linux-explorer-height-layers-20261014`**。旧h0版の地域上部の不足を補完しています。

## 最小の実行

**完全経路のセットアップと再現コマンドは [LINUX_EXPLORER.md](docs/LINUX_EXPLORER.md)。** Python 3.12以上、Node/npm、固定requirementsとpackage-lockを使う。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-audit.txt
npm ci --prefix viewer --ignore-scripts --no-audit --no-fund
.venv/bin/python pipeline/r3d_explorer.py --lat 35.6586 --lon 139.7454 \
  --radius-m 15 --config /private/path/maps.credentials.json \
  --out-dir reports/generated/tokyo-tower --export --serve
```

Python 3.10以上。主要codecは標準ライブラリのみです。

```bash
python3 codec/huff816_nativefree.py
PYTHONPATH=codec python3 -c "from audit.test_nativefree_r3d import test_compact_size; test_compact_size(); print('PASS compact-size roundtrip')"
python3 codec/nativefree_r3d_codec_streams.py /path/to/tile.r3d
python3 codec/nativefree_extract_heic.py /path/to/r3d_directory --out-dir /path/to/heic
python3 codec/c3mm_v2_parser.py /path/to/tile.c3mm
python3 codec/nativefree_decode_r3d.py /path/to/r3d_directory --out-dir output/decoded --workers 4
python3 -m unittest audit.test_numeric_codec -v
```

[独立decoderと全配列検証](docs/INDEPENDENT_DECODER.md) / [再現手順](docs/REPRODUCING.md) / [成果と限界](docs/STATUS.md) / [バイナリ形式](docs/FORMAT.md) / [次の作業](docs/CONTINUATION.md) / [元データと保存範囲](docs/PROVENANCE.md)

## 注意する区別

- native-freeヘッダー解析・画像抽出は、圧縮ジオメトリ数値の復号完了を意味しません。
- native-harnessは以前の参照データを得るためのApple依存経路です。Linux codecの最終目標には含めません。
- 過去メモは、その時点の誤解や後に置き換わった仮説も保存しています。現状の判断はこのREADMEとdocs/STATUS.mdを優先します。
- AppleのSplat shaderに由来するalpha式は調査済みですが、公式uniform値・タイル累積・LOD・最終合成のpixel parityは未達です。

リポジトリは研究スナップショットです。コード・第三者由来資料・Apple由来データの出所は[PROVENANCE](docs/PROVENANCE.md)で区別しています。一括でMIT等のライセンスを適用していません。

