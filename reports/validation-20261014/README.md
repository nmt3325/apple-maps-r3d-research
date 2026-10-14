# Linux独立R3D explorerの検証証拠

実装commit：`fb259cf3577958f8010df5297772e07915f9ffd4`。保存先：[private GitHub Release linux-explorer-20261014](https://github.com/nmt3325/apple-maps-r3d-research/releases/tag/linux-explorer-20261014)。元データ/goldenはRelease `snapshot-20261014`。認証・キャプチャ・署名URLは収録しない。

| 完了条件 | 結果と証拠 |
|---|---|
| 1. 独立完全復号 | `codec/nativefree_decode_r3d.py`は原本だけを入力し、Splat全3頂点/8属性/三角形、polygon XYZ/面/UV/法線/原HEICを復元。runtimeはApple/native golden不要。対応形式とrejectはdocs/INDEPENDENT_DECODER.md |
| 2. 東京223全配列比較 | reports/validation-20261013/のsplat-arrays.json、mesh-arrays.json。件数、3 index配列、画像exact。法線271 floatの1 ULP差は個別の高精度数値証明付き、最大絶対5.96e-8、ほかの全float/byte exact |
| 3. 新規Oahu72 | oahu-region-validation.json。581,186元polygon面、304,527 Splat。全viewer配列/index/UV/PNG画像/地理/共通座標系を照合。browser/の3画像を実視認 |
| 4. 取得→表示の入口 | live-tokyo-tower-{fetch,run}.json（新HTTP4）とlive-new-york-{fetch,run}.json（新HTTP2）。ブラウザbrowser.jsonは15/15チェック、shader/browser error 0。WASD/EQ/mouse/Esc/表示切替を実イベントで検証 |
| 5. 再現・回帰・破損・出力 | linux-arm-reproduction.json：別Ubuntu24.04/aarch64、fresh clone、system-site-packages=falseのvenv、固定依存、Oahu72と座標入口を再現。cross-platform-comparison.json：936配列/画像hashとGLB/PLY全file SHA exact。pipeline-tests.log：truncated原本/別座標原本をreject。numeric-tests.log：元Tokyo fixtureを含む8チェック。oahu-export-validation.json：全GLB/PLY配列/画像/8属性の読み戻しexact。oahu-gltf-validator.json：error/warning 0（70のNPOT image情報は元画像の寸法） |
| 6. 保存・引継ぎ | 実装/仕様/手順/制約/証拠はmain、decoded/viewer/GLB/PLY/新原本は上記Release。RELEASE_ASSETS.jsonとRELEASE_SHA256SUMS。docs/LINUX_EXPLORER.mdが再現コマンド |

Oahuのレイヤー位置合わせは、原本R/ECEF transformと共通ENUを**各頂点に正しく適用した**ことを全配列で検証する。元の二つの異なるgeometryが同じ形状という意味ではない。Splat centroid→近隣polygon三角形の距離は診断値：36,158 samples、median 2.846m、p95 13.997m、最大26.025m。24近隣centroid候補への距離であり全meshの厳密な最短距離でもない。これをdecoder誤差の許容値とは扱わない。

追加目標は引き続き未達：Apple公式pixel一致、正確なLOD、独自tile accumulation/color transfer。ブラウザbarycentric alphaとGLB標準alphaにも差がある。取得はローカル設定とサービスcoverage/versionに依存し、未知形式は明示reject。対応するR3Dの独立復号・可視化について主要6条件を満たす。

再現コマンド：[docs/LINUX_EXPLORER.md](../../docs/LINUX_EXPLORER.md)。東京golden比較：[docs/INDEPENDENT_DECODER.md](../../docs/INDEPENDENT_DECODER.md)。サーバー稼働状態とTailnet確認はviewer-server.json。
