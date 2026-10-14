# iOS取得最適化・Macへの引き継ぎ（2026-10-14 JST）

## Macでの継続状況（2026-10-14 JST）

- 追加ログの最新40秒セッションで、テクスチャ交換1,852件、同じ896 px atlasの896 / 448往復730件（約4.09秒）を確認。自身のatlas使用量で目標サイズが変わる判定を修正し、圧迫中の再拡大を禁止、縮小後の拡大に10秒待機を追加。実際のmipサイズを記録し、緊急の追加縮小と圧迫解除後の画質復元は維持。修正後の実機ログ確認が必要。
- 添付ログ全文8,534行を再集計し、下記の件数・中央値・p95・最大値が一致することを確認。復号エラー3件もすべてキャンセル。
- `main` の `69a4ffd` までを統合。診断ログ、CPUキャッシュ、動的テクスチャ更新、周囲360度の先読み、LOD hysteresis、メモリ制御を含む最新実装に復号最適化を適用した。ログから実行commitそのものは特定できない。
- 古いportrait FOV制限は、最新の周囲先読みと競合するため適用しない。縦横画面で同じ周囲を取得することを検査。キュー順位は候補ごとに1回計算し、移動先の予測距離・前方優先・atlas再取得・診断イベントを保持。coarse優先の150m調整を適用した。
- Xcode 27.0 / build 27A266aで、World / Navigation / Pipeline / Diagnostics / GPU検査がすべて成功。GPU検査は実際のMetalデバイスでpreview・原寸atlas・geometry保持・mip縮小を検証した。
- Swiftのキュー計算で型検査時間上限に当たった式を、型付き変数・ループ・個別sortへ分割。Simulator Debug / iPhone arm64 Releaseの両ビルドが成功。既存のMetal Sendable警告と実機版orientation警告は残る。
- Python 3.12.11で数値codec検査10件成功、Release reference corpus依存の1件はskip。mobile decoderは取得済み5原本で全3検査成功。
- Simulator保存の223原本でもmobile decoder全3検査成功（319.681秒）。mesh位置・法線・UV・indexとSplat位置が元のdecoder配列と一致。これはnative golden再監査ではない。
- `main`（`69a4ffd`）と統合後で取得済み5原本を復号し、JSON / vertices / indices / splats / atlasの全SHA-256が一致。[Mac検証記録](../reports/diagnostic-fetch-optimization-20261014/mac-validation.json)。各1回・全件検査との並行実行だったため、この計測から速度改善率を主張しない。
- 署名なしIPAを生成・検証済み。実機へのインストールには署名が必要。端末上の改善率、冷/温キャッシュ、150m調整後の表示穴は実機再計測が残る。

## 依頼と保存状態

ユーザーの依頼は「データの取得が遅いので最適化してください」。途中で「ここまでをブランチでリモートにプッシュし、次はMacで続ける」に切り替わったため、ここは検証途中のチェックポイント。

- リポジトリ: `nmt3325/apple-maps-r3d-research`
- ブランチ: `codex/ios-fetch-optimization-handoff`
- ベース: `9ab14cf`（`Remove iOS distance fog and horizon haze`）
- ベースには既存の取得・復号最適化 `bef5d46` も含まれる。
- ログ全文はユーザーが次のチャットへ渡す。リポジトリにはログ全文、署名URL、認証情報、取得原本を追加していない。

## 添付ログからの観測

対象は `R3D-diagnostics-ECBBC244-42C1-4509-B176-D1D4D0FD4518.jsonl`。1セッション、8,534行、約20秒。Apple A16 GPU / アプリ0.2.0 / ビルド1。添付は診断データとして扱い、内部の文面を作業指示として扱わない。

| 記録項目 | 件数 | 中央値 | p95 | 最大 |
|---|---:|---:|---:|---:|
| `network.response.duration_ms` | 79 | 30.0 ms | 448.5 ms | 652.4 ms |
| `decode.end.duration_ms` | 31 | 638.7 ms | 863.5 ms | 990.2 ms |
| `decode.begin.actor_wait_ms` | 34 | 583.1 ms | 841.2 ms | 963.1 ms |
| `processing.begin.wait_ms` | 34 | 912.9 ms | 1,446.3 ms | 1,614.9 ms |
| `pipeline.begin.queue_wait_ms` | 83 | 4,790.7 ms | 10,772.7 ms | 15,191.4 ms |
| `gpu.prepare_end.duration_ms` | 29 | 12.0 ms | 20.1 ms | 24.9 ms |

p95はソート後の添字 `int((n-1)*0.95)`。成功した復号とキャンセルは別集計。これは短い移動中セッションで、ネットワークには空応答も含まれる。端末の主な律速は通信より直列CPU復号とその待ち行列だと推定した。

- `pipeline.queued` は6,902行。候補を再記録しており、6,902個の実リクエストではない。
- `plan.update` のneeded数は中央値1,056、最大1,552。表示範囲600m、aspect約0.46。
- `render.tile_first_submitted` のready-to-drawは最大約8.1秒。視点移動とLOD切替があるので、その値だけで表示バグと断定しない。
- `decode.error` 3件はいずれもキャンセル。
- **ログを出したアプリとこのベースは一致していない可能性が高い。** ログにはCPUキャッシュ、動的なテクスチャ入れ替え、診断イベントがあるが、このcheckoutのiOSコードには該当実装がない。Mac側の最新ブランチを確認し、必要ならこの変更をそこへ移植する。最新実装を古いcheckoutで上書きしない。

## 実装した変更

1. `codec/nativefree_huff_aligned.py`: entropyをlittle-endianの32ビットワードへまとめて読み、最大約41ビットの整数reservoirで消費。symbolごとのWordBits呼び出し・同一ワード再読み込みを削減。prefix tree検証、長い符号、末尾、正確なentropy長、ゼロpadding検査は維持。共通codecなのでWeb / CLIにも適用される。
2. `ios/Python/r3d_mobile.py`: meshの位置・法線・UVをfloatへ展開して再packする代わりに、検証済みのfloat32バイトをコピー。indexを`array('I')`へまとめ、little-endianへ統一。Splatの色は三角形ごとに1回packし、barycentricを再利用。位置の重複finite検査を削除したが、`validate_arrays`で全原本位置を検査する。
3. `ios/App/World.swift`: 水平FOV計算でportraitのaspectを反映（下限1から0.1）。既存の角度guard bandと近傍の保持は維持。coarse優先度を距離換算150mに変更し、遠方rootが近くの詳細モデルを長時間待たせるのを抑える。
4. `ios/App/ExplorerModel.swift`: 候補ごとの距離と順位を1回算出してsort。以前は比較のたびに地理変換していた。同順位はTileKeyで安定化。
5. `ios/Tests/WorldChecks.swift`: portrait / landscapeの候補関係、近くのfallback優先、遠方rootより近くの詳細優先、index優先の検査を追加。

通信枠2 / 準備枠2 / pending上限4、全高さの列挙、既存GPU予算は変更していない。Swift側の150m優先度は調整値で、Macで動作を確認する必要がある。

## 実施済みの検証

- `.venv/bin/python -m unittest audit.test_numeric_codec -v`: 11件すべて成功。Word境界、8/16bit symbol、32bitの長い符号、末尾、切断、余剰entropy、padding、prefix conflict、元配列・不正indexなど。
- `ios/Tests/test_mobile_decoder.py`: gzip上限・不正原本拒否を確認。さらに今回の3原本を`R3D_TEST_FIXTURES`へ指定して、mesh位置 / UV / 法線 / indexとSplat位置のpacking一致を検査。
- `audit/benchmark_mobile_decoder.py`: Linux / Python3.13.5、各5回の中央値。変更前後のJSON・vertices・indices・splats・atlasの全SHA-256が3原本で一致。

| 原本 | 変更前 | 変更後 | 短縮 |
|---|---:|---:|---:|
| 東京coarse z18 / 232829 / 103246 / h0 | 0.632秒 | 0.516秒 | 18.4% |
| 東京z20 / 931325 / 412987 / h2 | 0.109秒 | 0.091秒 | 15.8% |
| Oahu z20 / 64554 / 460820 / h0 | 0.425秒 | 0.359秒 | 15.6% |

生の計測値・原本hash・出力hashは [before.json](../reports/diagnostic-fetch-optimization-20261014/before.json) / [after.json](../reports/diagnostic-fetch-optimization-20261014/after.json)。通信・Metal・iPhoneの速度を測った結果ではない。今回の変更での全223 / 135原本の再照合は未実施。

## 次にMacで行うこと

```sh
git fetch origin
git switch --track origin/codex/ios-fetch-optimization-handoff
```

既にローカルに同名ブランチがある場合はそのブランチを選び、ローカル変更を確認してから更新する。別の最新ブランチに診断・CPUキャッシュ等がある場合は、差分を比較してこの最適化を統合する。

1. ユーザーが再添付するログ全文と、Mac側のアプリを生成したcommitを確認。
2. Swift / Xcodeで以下を実行。Linux環境にはSwift / Xcodeがなく、追加したSwift検査・コンパイルはまだ実施していない。

```sh
swiftc ios/App/World.swift ios/Tests/WorldChecks.swift -o /tmp/r3d-world-checks
/tmp/r3d-world-checks
swiftc ios/App/World.swift ios/App/CameraNavigation.swift ios/Tests/NavigationChecks.swift -o /tmp/r3d-navigation-checks
/tmp/r3d-navigation-checks
swiftc ios/App/PipelineSlots.swift ios/Tests/PipelineChecks.swift -o /tmp/r3d-pipeline-checks
/tmp/r3d-pipeline-checks
python3 -m unittest audit.test_numeric_codec -v
python3 ios/Tests/test_mobile_decoder.py -v
bash ios/Scripts/bootstrap.sh
xcodebuild -project ios/R3DExplorer.xcodeproj -scheme R3DExplorer \
  -configuration Debug -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath /tmp/r3d-fetch-simulator ARCHS=arm64 CODE_SIGNING_ALLOWED=NO build
```

3. 利用可能な原本全件で`R3D_TEST_FIXTURES=/path/to/raw python3 ios/Tests/test_mobile_decoder.py -v`を実行し、全corpusの一致を検証。
4. 同じ端末・600m・縦画面・同じ移動操作で計測。冷キャッシュと温キャッシュを分け、queue wait / actor wait / decode duration / 最初に描画されるまでの時間を比較。150mの優先度で周辺の穴が増えないか、全高さ・coarseからfineへの切替とmaskが維持されるかを見る。
5. 依然復号が律速ならmesh topology / predictor / quantized変換をprofileする。ログspamやCPUキャッシュ再利用については、診断実装を含む最新ソースで調べる。

作業開始時からあった未追跡の`audit/probe_browser_direct_fetch.cjs`、`audit/probe_browser_direct_fetch.py`、`reports/browser-direct-fetch-20261014/`は、この最適化の変更ではないため今回のブランチには含めていない。
