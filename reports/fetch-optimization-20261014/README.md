# 取得・復号の最適化（2026-10-14）

## 改善

- iOS と Web の取得待ちを、復号・GPU / モデル準備から分離。通信 / サーバー取得ジョブ待ちは最大2件、準備は最大2件、待機を含む全体は最大4件。準備中にも次の取得を進める。Python の直列復号、既存のモデル予算、世代チェックは維持する。
- iOS の粗いモデルは、到着した高さ層から表示する。空層を含む全高さの取得完了まで初回表示を待たない。詳細モデルへの切り替えと重複領域のマスクは従来どおり全高さの準備完了を確認する。Web は既にこの逐次表示に対応している。
- 準備待ちはキャンセル可能。準備が失敗した場合も枠を解放し、古い地点で生成されたモデルは破棄する。iOS の追加待機は復号前の原本（1件最大16 MB）、Web の追加待機は表示資産のURLなどのメタデータだけを保持する。
- 共通の Huff816 decoder は32ビットワードをまとめて読み、最大10ビット / 1024項目のprefix表を使う。長い符号と末尾は検証済みtreeで復号する。厳密な出力数、entropy長、ゼロpadding、prefix衝突の検査は維持する。
- 共通の BYET decoder は16ビット対のbyte planeをスライスで配置し、レコードごとのPythonループと一時sliceを削減する。
- iOS の設定JSONをキー順で正規化してキャッシュnamespaceを計算。設定が同じなら辞書の順序や再起動によってキャッシュが別namespaceへ分散しない。旧方式とはnamespaceが変わるため、更新直後は原本の再取得が必要になる場合がある。

共通codecの改善は、iOSの端末内復号、Webサーバーの表示資産生成、CLIの復号・export準備に適用される。原本の数値や画像を変更する最適化ではない。

## 計測

Linux / Python 3.13で、原本読み込み後の `r3d_mobile.decode_tile`（数値復号＋Metal用配列へのpacking）を各5回計測し、中央値を比較した。変更前はcommit `307de11` のコード。実行環境の詳細・全測定値・全出力SHA-256は [baseline.json](baseline.json) と [optimized.json](optimized.json)。

| 原本 | 変更前 | 変更後 | 時間短縮 |
|---|---:|---:|---:|
| Oahu z20 / 64554 / 460820 / h0（179,388 bytes） | 0.777秒 | 0.473秒 | 39.1% |
| 東京タワー z20 / 931325 / 412987 / h0（157,192 bytes） | 0.487秒 | 0.279秒 | 42.8% |

両タイルのJSON・頂点・index・Splat・HEIC全出力のSHA-256は変更前後で一致。これは**CPU復号・packingの計測**であり、Appleへの通信時間、Metalの準備時間、iPhone上の取得完了時間の計測ではない。先行取得の効果は、通信・準備をそれぞれ意図的に止めたcontrollerテストで検証した。

取得設定・署名URL・原本はこのレポートに含めない。

## 検証

- 東京223原本をnative goldenと再照合。Splat XYZ / 8属性 / material20は全件bit / byte一致。mesh位置 / UV / 全index / primary HEIC 223画像も一致。法線は従来の271個の1 ULP差のみで、既存の丸め説明を満たす。[監査サマリー](array-audits.json)。
- 数値codecの11テスト：ワード境界、8 / 16ビットsymbol、32ビットまでの長い符号、末尾、constant / literal、切断、余剰entropy、非ゼロpadding、prefix衝突、予測器、元配列。
- Web / CLI / 全高さの12テスト：空層と上層、元配列、誤った座標、キャッシュ・重複取得・予算・認証区別・HTTPルート。
- Oahu72原本すべてでiOS packingテストを実行し、元のmesh位置 / 法線 / UVとSplat位置が維持されることを確認。gzip上限と不正原本の拒否も通過。
- Web controller / plannerテスト：準備を止めても次の2件を取得し、全体は4件以内。遅い通信は同時2件以内、準備は同時2件以内。キャンセルされた準備待ちは実行されず、遅延結果はdisposeされる。予算超過時もモデルを解放する。
- iOSの `PipelineChecks.swift` と取得 / 準備件数の検査をmacOS CI / simulator検証へ追加。このLinux環境にはSwift / Xcodeがないため、今回のSwiftコンパイル・iOS実行は未実施。端末上の速度は実機で別途確認が必要。

## 再計測

原本がある環境でCPU時間と出力一致を比較できる。`--source-root` は比較対象のcheckout（またはcodecとios/Pythonを展開したディレクトリ）を指定する。

```sh
.venv/bin/python audit/benchmark_mobile_decoder.py /private/path/tile.r3d \
  --source-root /private/path/baseline-checkout --out /tmp/r3d-before.json
.venv/bin/python audit/benchmark_mobile_decoder.py /private/path/tile.r3d \
  --baseline /tmp/r3d-before.json --out /tmp/r3d-after.json

.venv/bin/python -m unittest audit.test_numeric_codec audit.test_web_streaming audit.test_pipeline audit.test_height_layers -v
node audit/test_stream_planner.mjs
node audit/test_stream_controller.mjs
swiftc ios/App/PipelineSlots.swift ios/Tests/PipelineChecks.swift -o /tmp/r3d-pipeline-checks
/tmp/r3d-pipeline-checks
```

原本fixtureを省いた環境では、対応するテストはskipとなる。全配列監査の個別記録はローカルの `reports/generated/fetch-optimization/{soup,mesh}.json`。
