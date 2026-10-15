# iOS取得最適化・Macへの引き継ぎ（2026-10-14 JST）

## 作業終了・remote保存チェックポイント（2026-10-15 JST）

ユーザーの最新依頼は「高解像度モデルへの切り替えをもっと早く」。調査中に「ここまでで終了して、remoteにコミット」に切り替わったため、追加の高速化は止めて現在の状態を保存する。**高解像度切り替えの高速化も、下記の0.1秒目標も達成済みではない。**

- 進行中だった準備済みキャッシュを含む。`RawCache.swift`へ既存ディスクcacheを分離し、`PreparedTileCache.swift`を追加。設定ごとの別namespace、64MiB上限、形式version、1時間の絶対有効期限、payloadのSHA-256確認、clear後の古い保存job拒否を実装した。高さインデックスと検証済みz16形状、原寸atlas、256pxのlossless PNGを保存・再利用する。
- PNG作成と保存はGPU常駐後に行い、準備枠は先に解放する。pending上限4を維持。キャッシュの不一致・破損はmissとして通常の取得に戻す。新しいキャッシュ経路の起動速度・実通信・破損/失効/clear競合の専用検査は未実施。**効果や安全性を検証済みとは扱わない。**
- 今回のキャッシュ変更についてWorld / Metal GPU検査とSimulator Debugビルドは成功。下記の実機Releaseビルド・IPA・223原本一致・計測値は `d002100` の記録であり、この追加キャッシュの性能証明ではない。追加キャッシュを含む新IPAは生成していない。
- 高解像度の調査では、同じ前回ログのz20初回submitは冷キャッシュ中央値1266.8ms、原本ディスクキャッシュ再起動868.1ms（各19件）。GPU常駐後からsubmitまでは49.3ms / 44.4msで、待ちの大半はその前にある。次は近傍の詳細モデル取得順位と、原寸atlasへの更新順序・待ち時間を調べる。全高さが揃うまでcoarseを残す挙動を、穴やSplat重複が出る変更で置き換えない。
- fetchした `origin/main` は `9d93a5e` まで進んでいるが、この終了チェックポイントへ追加統合はしていない。再開時に差分を確認する。生ログ、取得原本、署名URL、認証情報は追加していない。

## 2026-10-15 JST: 0.1秒目標は継続中

追加依頼は「軽量モデルの読み込み・描画を0.1秒以内」「描画距離は上下位置を無視して水平距離だけで判定」。**水平距離対応は検証済みだが、0.1秒の全経路目標は未達。完了扱いにしない。** 以下の2026-10-14節は過去のチェックポイント。

- 実装commitは `d002100`。独立Python decoderの配列処理をC++ / CPython組込みmoduleに移した。Appleの非公開decoderは使わず、Pythonによるframing・variant確認と配列の検証、source-only fallbackを残す。
- 2つのdecoder workerでC++ループ中のみGILを解放。入力寿命と例外時のGIL復帰を検査。GPU/通信の枠は各2、pending上限4を維持。
- 初期表示はサーバーの原本z16 + 256px atlas。詳細は従来のz18/19/20へ切り替える。高さインデックスはz17の4セルと親高さを集約し、飛び飛びの上層も保持。coarseのmaskは256矩形のGPU bufferへ拡張。
- 軽量atlasを先に抽出して形状復号と画像準備を重ね、検証済みモデルのGPU準備で同じtextureを再利用する。初期化のwarmup、欠けたcoarseの優先、50msごとのplan、キューの末尾popも追加。
- 描画は無限far projection + XZ距離のfragment clipping。CPU可視判定とpickingも水平距離。実際のMetal pixel readbackでMesh/Splatの高度10km/20km、範囲外、256個目のmaskを確認した。
- `needed`時間は水平地点がplanに入った時から取り、高さインデックス取得とキュー待ちを含む。`app.model_init.latency_origin = horizontal_plan` で区別。旧ログは高さ展開後からなので直接比較しない。計画tickまでの待ちやplan前の起動時間は別に残る。
- 223原本すべてのmobile出力dictがPython版とバイト単位で一致。並列原本復号、不正入力、数値codec、Swift World/Navigation/Pipeline/Diagnostics、Metal GPU検査が成功。release reference corpus依存の数値検査1件はskipで、native goldenの再監査ではない。
- Simulator Debug / iPhone arm64 Releaseの両ビルド成功。既存警告は残る。最新IPAは `/tmp/r3d-fetch-device/R3DExplorer-lightweight-native-unsigned.ipa`。署名なしで、実機実行には署名が必要。古いtexture-stable IPAと混同しない。
- 実通信したSimulatorの初回GPU描画完了は、冷キャッシュ中央値253.7ms / p95 302.5ms / 最大385.8ms（6件）、原本ディスクキャッシュ再起動は171.3ms / 218.7ms / 252.6ms（6件）。両方とも100ms以内は0件。画面提示完了の証明ではなく、実機速度でもない。
- どちらも初期設定600mから既存メモリ制御で約120mへ縮小したセッション。固定600mでの性能試験ではない。初回のモデル通信は最大107.4msで、それだけでも100msを超えた。試行開始後だけの温キャッシュ79.8msを目標達成として扱わない。
- 2セッションともtexture交換は57件・各tile1回、非キャンセルエラーなし。前の往復交換修正は保持。生ログ・原本・署名URLはcommitしていない。

詳細・セッション別集計・IPA hashは [2026-10-15検証記録](../reports/ios-lightweight-latency-20261015/README.md)。このMac上の試験用Simulatorは `R3D-Latency-20261015` (`23EF76AC-D8B8-4111-A563-B12FB858D978`)。既存の別Simulatorやユーザーの保存原本を消さない。

次は署名した実機で、未取得地点・原本ディスクキャッシュ・GPU常駐時の移動を分けて再計測する。実機は `render.tile_first_presented`、Simulatorは `render.tile_first_completed`。インデックス発見待ち、準備枠待ち、軽量の準備済みデータ再利用も改善余地がある。初回未取得地点も100msの対象か確認は未回答だが、勝手に条件を温キャッシュへ狭めない。外部通信を含む無条件100msはクライアントだけでは保証できない。

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
