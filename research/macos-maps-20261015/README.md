# macOS Maps / VectorKit の実行時・メモリ・GPU解析 — 2026-10-15

**今回の到達点：純正MapsでロードされたVectorKitのbuildを特定し、同じVectorKitを使う解析用MapKitアプリから、実際のSplat描画に結び付く透明度定数、GPU頂点・属性・描画順序、関数定数、render passを取得した。** 純正Maps.appへのデバッガ接続・最終フレーム一致は未達。MapKitホストでの観測を、Maps.appそのもののuniform取得とは扱わない。

## 最初に確認した既存成果

調査開始時のHEADは `9d93a5e`（2026-10-14）。README、docs/STATUS、CONTINUATION、FORMAT、独立decoder、native-harness、前日のGPU研究を確認した。

| 段階 | リポジトリ内の到達点 | 今回の扱い |
| --- | --- | --- |
| R3D / BYET / HUFF / TRICO | Linux独立復号、東京223のnative配列比較、法線の微小丸め差の説明 | 実装済み。今回の作業の前提。全原本コーパスは再取得・再監査していない |
| mesh / texture / splat | 元ポリゴン・HEIC・三角形Splat復元、Oahu上層追加、Web/iOS表示・GLB/PLY | 実装済み。新しいdecoder完成を今回の成果として数えない |
| GPU式 | iOS/macOS AIR比較、仮定した `c=1,p=20` で単一三角形の画素実験 | 有効な限定実験。ただし実行時の定数ではなかった |
| 残り | 実行時uniform、正確なLOD、描画順序・合成・色、公式最終フレーム | 今回はmacOS実行時データを優先 |

根拠：[現状](../../docs/STATUS.md)、[独立decoder](../../docs/INDEPENDENT_DECODER.md)、[前日のGPU研究](../ios27-metal-splat-20261014/README.md)。historical/reference資料の「まだ復号できない」などの記述は、それぞれの執筆時点の状態として読んだ。

## バイナリの同定と静的解析

実機は **macOS 27.0.1 / 26A434、Apple M4**。純正Mapsは **Mac Catalyst版 3.0 / 2972.20.6.12.47**。

| 対象 | 今回の識別結果 |
| --- | --- |
| 純正Mapsの稼働slice | UUID `1CA0CC9D-9EE5-3A22-97B7-291C0884651B` |
| 稼働VectorKit | `2043.20.6.12.18`、UUID `118C1225-42FA-3428-AD31-F414C80C326E` |
| ローカル抽出VectorKit | 上記UUIDと一致、SHA-256 `bf432e44cd40bd1330f9e63db5ea71044461047321ea2ec6feb25d648290153c` |
| 現行macOS default.metallib | 2,991,304 bytes、SHA-256 `7cb9244f82b6c273c1e0d9d5dba6c21c8ae5ff18b5d20a88e5b785f4f2601b67` |

純正Mapsの `sample` のロード一覧と抽出Mach-Oの `LC_UUID` を照合した。VectorKitのunslid baseは `0x1c229a000`、純正Mapsでのbaseは `0x1db3aa000`。別のローカルプロセス内でもdyld APIから元のsegment VM addressとslide `0x19110000` を読み、実メモリの `__text` 先頭4 KiBのSHA-256が抽出ファイルと一致することを確認した。[実メモリ上の識別結果](metrics/live_image_identity.json)。抽出ファイルのbase差だけをslideと断定せず、アドレスを別OS/buildへ流用しない。

Mach-Oのload command・symbol・AArch64 BLを再走査し、**22個の対象symbol、63個の対象間直接BL**を記録した。`r3d_world_read_mem=0x1c34588c4`、`createSplats=0x1c3465a7c`、Splat vertex/fragment descriptor `0x1c24217bc / 0x1c2421884` を再確認。BL件数はcodecや描画の意味を単独で証明しない。

現行metallibからreflectionとAIRを再抽出し、SplatConstantsのoffset/size、bindless table、12個のFlyover entryのhash・target triple・function constant番号を保存した。**macOSの解析結果であり、iOS側のアドレスや実行時定数とは区別する。**

証拠：[binary_inventory.json](metrics/binary_inventory.json)。Appleの実行ファイル・AIR本文・逆アセンブル本文はcommitしていない。

## 実際のSplat描画に結び付くデータ

[mapkit_probe.mm](tools/mapkit_probe.mm) は、AppKit + MKMapViewの使い捨てホストを作る。`MKImageryMapConfiguration(realistic)` とpitch 65°で指定した地域を表示し、このプロセス内でMetal APIを観測する。純正Mapsへの注入・再署名やOS保護設定の変更はしない。

pipeline作成時にvertex/fragment名を記録し、**`Flyover::splat_vertex` と `Flyover::splat_fragment` の組でdrawした時だけ**SplatConstantsを解釈する。shared argument bufferのGPU addressを、登録済みMTLBufferの実際のaddress/lengthへ解決し、範囲検証後にCPU可読領域を保存する。別meshのbindingをSplat定数と解釈する初期試行は採用していない。

### 透明度定数

| SplatConstants内 | offset | 観測したfloat32 | bit pattern |
| --- | --- | --- | --- |
| alphaConcentration | 196 | **1.5** | `0x3fc00000` |
| alphaPreFactor | 200 | **148.16207885742188** | `0x4314297e` |

東京のcamera distance 450 / 900 / 1800 mと、Oahu Hilton付近の900 mで同じ組を観測した。これは選んだ条件・最初のinstance・重複排除したrender slotでの標本であり、世界共通defaultや全drawの不変性を証明しない。`splatID` はbindless tableのslotで、地理的tile IDではない。

現行AIRはこのfloat32をvertexから **half** で渡すため、fragmentの係数は **1.5 / 148.125** になる。既存のkernel式 `min(0.99, p * sourceAlpha * (b0*b1*b2)^c)` に実行時の入力が得られたが、最終frameのpixel parityを達成したという意味ではない。

### GPU配列と描画順序

reflectionの3×16384 pointer tableから、対応する3配列を解決できた。

| 配列 | 実メモリ上の形式 | Splatあたり |
| --- | --- | --- |
| positions | 三角形3頂点、各 `ushort4` | 24 bytes |
| properties | packed color 4、normal `ushort2` 4、roughness/specular 2、padding 2 | 12 bytes |
| orders | `int32` のSplat index | 4 bytes |

合計40 bytes/Splat。これは定数・argument buffer・textureなどを除く3配列の値。**native-triangle-f32のvertex-planarな配列順と、このGPU用interleaved ushort4を混同しない。** AIRでの位置復元は `q.xyz / 65535 * posBoundsScale + posBoundsMin`。packed colorのlittle-endian byteは逆順にRGBAへ展開する。

各runで取得した完全な3配列について、同じNを持つことと、ordersが `0..N-1` の欠落・重複のない置換であることを検証した。以下は各runの**最初に取得できた1組**で、シーン全体のSplat数やtile数ではない。

| 条件 | N | 三角形重心のview-z順の小逆転数 | 最大逆転 | 保守的な量子化2段分の幅 |
| --- | ---: | ---: | ---: | ---: |
| 東京450 m | 2,045 | 11 / 2,044 | 0.000358 m | 0.002158 m |
| 東京900 m（capture） | 3,669 | 29 / 3,668 | 0.004835 m | 0.017843 m |
| 東京1800 m | 7,858 | 116 / 7,857 | 0.007116 m | 0.030963 m |
| Oahu900 m | 359 | 4 / 358 | 0.000070 m | 0.000559 m |

**全ての逆転が量子化の幅以内で、概ね手前から奥へのview-z順と整合する。** 幅は `2 * sum(abs(modelView.zRow[i]) * boundsScale[i] / 65535)`。CPU側の正確なsort comparatorやtile間の順序を復元した証明ではない。

### shader specialization / render pass

function constant setter・copy・resetからdescriptorへ渡る値を追跡した。東京1800 m、Oahu、最終東京runで成功したSplat function作成では、宣言されているindex 1は `useMetalBarycentricCoordinate=true`、vertexのindex 2/3/4は `colorAdjustmentEnabled=false / usePbrRendering=false / useClipPlanes=false`。取得できなかったrunの値は推測で埋めていない。

最終東京runでは、Splat drawに属するrender passを取得した。**imageblockSampleLength=32、color=BGRA8Unorm_sRGB (81)、depth=Depth32Float_Stencil8 (260)、sampleCount=1、1920×1440**。tileWidth/Heightの指定値は0であり、実ハードウェアのtileサイズ0を意味しない。前日の実験のRGBA16F・depth32Float・imageblock 28は実験設定で、今回の実行時passとは異なる。

clear → Splat → intermediate resolve → final color/depth resolveに加え、`flyover_bindless_vertex/fragment` によるmesh drawを観測。名前が存在するだけでなく、実際のpipeline bindとdrawが根拠。

証拠：[東京450](metrics/probe-tokyo-near.json)、[900/capture](metrics/probe-tokyo-capture.json)、[1800](metrics/probe-tokyo-far.json)、[Oahu](metrics/probe-oahu.json)、[最終東京](metrics/probe-tokyo-final.json)。

## メモリとGPUキャプチャ

純正Mapsの初回 `sample` は成功し、physical footprint **431.5M**、peak **555.5M** と対象UUIDを記録した。これは短いidle標本のアプリ全体で、3D専用メモリではない。

解析用ホストでは、別runの終了時に `task_info(TASK_VM_INFO)` と `MTLDevice.currentAllocatedSize` を記録。[メモリ標本](metrics/probe-tokyo-memory.json)ではfootprint **346,932,184 bytes**、Metal allocation **146,538,496 bytes**、観測のため保持した399 bufferの合計 **31,687,558 bytes**。プローブは最大512 MiB / 24,000 bufferを保持し、寿命・スケジュールを変える。純正Mapsとの性能・使用量比較には使えない。

`METAL_CAPTURE_ENABLED=1` とMTLCaptureManagerで、**draw差分865、3,588ファイル / 1,282,655,220 bytes** のcommand dataを含む `.gputrace` を取得した。idle状態で開始・終了した初期試行はdraw差分0、capture stream 8 bytesの空記録だった。成功APIやmetadataのframe countだけで成功としないよう監査している。

最終ソースと実行ファイルのhash・コンパイラ・flagsは [probe_build.json](metrics/probe_build.json)。途中のrunは段階的なprobeの版で、イベントとバッファ自体のhashを各レポートに保持した。

生データはローカルの `reports/generated/macos-maps-20261015/` に保存し、Git対象外。特に実キャプチャは `probe-tokyo-capture/mapkit.gputrace`。公開・push・Release追加は行っていない。

## 成功と数えなかった試行・未解決事項

- 純正MapsへのLLDB attachは25秒でtimeout。失敗理由は確定していない。今回の試行が残したdebugserverは終了した。OS保護・署名を変更していない。後続のvmmap/sampleもtimeoutしたので、初回の成功標本と区別する。
- 純正MapsにattachしたMetal System Traceは保存・exportできたが、target PIDで絞ると **0件**。1,784件は対象外プロセスのGPUイベントだった。**純正Mapsの描画キャプチャ成功とは扱わない。** [監査結果](metrics/native_trace_attempt.json)
- MapKitホストと純正Mapsは同じVectorKit buildを使うが、UI・内部設定・feature flag・coverageが同一とは限らない。
- 実uniformを使った同一cameraの最終色・深度比較、正確なLOD、R3D取得tileとrender slotの対応、CPU→GPUの全属性変換、tileを跨ぐsort/accumulationは未解決。
- iOS純正runtimeのuniform取得・最終フレーム一致は今回も未検証。

## 再現

macOS / Xcode / ネット接続が必要。位置はユーザーの現在地を使用せず、引数の固定座標を使う。標準ライブラリのPython以外のPython依存はない。

```bash
mkdir -p reports/generated/macos-maps-20261015
xcrun clang++ -std=c++17 -fobjc-arc -g -O1 -Wall -Wextra \
  -framework AppKit -framework MapKit -framework Metal -framework CoreLocation \
  research/macos-maps-20261015/tools/mapkit_probe.mm \
  -o reports/generated/macos-maps-20261015/mapkit_probe

# 出力先は毎回新しい名前にする。既存events.jsonlは上書きしない。
reports/generated/macos-maps-20261015/mapkit_probe \
  reports/generated/macos-maps-20261015/new-tokyo 16 35.6586 139.7454 900 65

python3 research/macos-maps-20261015/tools/audit_probe.py \
  reports/generated/macos-maps-20261015/new-tokyo \
  --output reports/generated/macos-maps-20261015/new-tokyo.json

# 任意：起動から約8秒間のGPU capture。今回の例は約1.2 GiB。
METAL_CAPTURE_ENABLED=1 MAPS_PROBE_CAPTURE=1 \
  reports/generated/macos-maps-20261015/mapkit_probe \
  reports/generated/macos-maps-20261015/new-capture 16 35.6586 139.7454 900 65

python3 research/macos-maps-20261015/test_audit.py
```

引数順は `OUTPUT_DIR duration_s latitude longitude distance_m pitch_deg`。distanceは450/900/1800、Oahuは `21.2828 -157.8369 900 65` で測定した。今回のdefault 16秒はcoverage/通信遅延によっては十分でない。`map_rendered`、対象pipeline、終了summary、実ファイルの監査で成否を判断する。

抽出済みの**macOS** VectorKitを持っている場合の静的解析：

```bash
python3 research/macos-maps-20261015/tools/inspect_binaries.py \
  --vector-kit /path/to/extracted/macos/VectorKit \
  --native-sample /path/to/successful-maps-sample.txt \
  --raw-dir reports/generated/macos-maps-20261015/static \
  --output reports/generated/macos-maps-20261015/binary-inventory.json
```

`--native-sample` は省略可能。実行時のbuild照合を行う場合は純正Mapsから得た成功したsampleが必要。システムframeworkのパスはdyld cache上のimageで、抽出済みの単独Mach-Oと区別する。

プロセス内でのUUID・slide・実コード先頭のfingerprint照合も再実行できる（Maps.appへのattachは不要）。出力の `live_text_prefix4096_sha256` と静的レポートの `extracted_text_prefix4096_sha256` を比較する。

```bash
xcrun clang++ -std=c++17 -fobjc-arc -Wall -Wextra -framework Foundation \
  research/macos-maps-20261015/tools/image_identity.mm \
  -o reports/generated/macos-maps-20261015/image_identity
reports/generated/macos-maps-20261015/image_identity
```

新規監査テスト6件は全成功。既存codecは10成功・原本必要1件skip、前日のGPU metricsテスト5件も成功。[検証記録](metrics/validation.json)。今回の全コーパスnative配列比較の再実行を意味しない。

APIとenumの解釈は現行Xcode SDKヘッダー、およびApple一次資料の [MTLCaptureManager](https://developer.apple.com/documentation/metal/mtlcapturemanager)、[programmatic capture](https://developer.apple.com/documentation/metal/capturing-metal-commands-programmatically)、[Metal capture in Xcode](https://developer.apple.com/documentation/xcode/capturing-a-metal-workload-in-xcode) に照らした。
