# Web版の移動中ストリーミング検証

2026-10-14 JST。[iOS版PR #1](https://github.com/nmt3325/apple-maps-r3d-research/pull/1)のカメラ追従・距離別LOD・全高さ・逐次更新を、サーバー経由のWebビューアで検証した。実行コードと手順は[WEB_STREAMING.md](../../docs/WEB_STREAMING.md)。

**東京で450m移動、視点回転、3kmを超える移動での原点更新、ワイキキへの任意座標移動を確認。z18/19/20、上層、両レイヤーを実際に描画した。ブラウザのJavaScript・shaderエラーは0件。**

| 検証 | 結果 | 証拠 |
|---|---|---|
| 稼働サービスのWebGL・カメラ移動・LOD・地域切替・停止再開・レイヤー切替 | 14/14成功 | [desktop-browser.json](desktop-browser.json) |
| モバイル画面・操作パネル・タッチ移動・離した後の停止・視点ドラッグ・モデル予算 | 9/9成功 | [mobile-browser.json](mobile-browser.json) |
| 従来の静的ビューア | 16/16成功 | [static-browser.json](static-browser.json) |
| StreamCache・HTTP API・原本packing・既存codec/pipeline/全高さ | 20/20成功 | [unit-tests.log](unit-tests.log) |
| 日付変更線・高緯度・地理変換・quadtree・全高さ・LODマスク | Nodeテスト成功 | [test_stream_planner.mjs](../../audit/test_stream_planner.mjs) |
| 同時2件・キャンセル後の遅い結果破棄・同時完了時のモデル予算 | Nodeテスト成功 | [test_stream_controller.mjs](../../audit/test_stream_controller.mjs) |

稼働サービスでのdesktop測定サンプル中のモデル見積もり最大は**139.67MiB / 192MiB**、最大同時処理は**2件**、上層モデル最大5件、キャッシュ応答148件。実際のアプリ全体のRSS上限や実機fpsを測定したものではない。[集計とz19の実取得結果](summary.json)。

元の東京上層R3DのSHA-256を保持し、送信用bufferのindexから三角形を再構成して元の位置配列との一致を確認した。違う座標として同じ原本を供給すると失敗し、公開出力を残さない。空応答と403認証失敗の区別、重複要求の1処理化、再起動後のキャッシュ再利用、LRU予算、原本への公開アクセス拒否もテストした。

## 稼働反映とテスト経路

既存の `r3d-oahu-independent-viewer.service` を更新・再起動し、`/api/status` が ready=true / streaming=true / z18,19,20 / workers=2 を返すことを確認。検証した完成キャッシュ731件を再利用し、原本と署名設定は公開せずに保持した。

実データのテストは、最初に別ポート8974で行い、その後、稼働サービス自身の8972で確認した。稼働サービスのブラウザOriginは `https://ct104.taila8c9c.ts.net:8972`。このホストからTailnetのHTTPS入口へ直接接続できなかったため、Playwrightは**アプリ自身への要求だけ**をloopbackの稼働サービスへ転送した。ブラウザが生成したOriginを維持し、サーバーのOriginチェックを通している。AppleへのHTTPS取得・署名・独立復号・キャッシュ・配信は実際の稼働サーバーで実行した。TailnetのTLS入口そのものの疎通確認は含まない。

稼働サービスを同じ経路で確認する場合：

```sh
R3D_TEST_UPSTREAM=http://127.0.0.1:8972 \
node audit/test_web_streaming.cjs https://ct104.taila8c9c.ts.net:8972 reports/generated/production-check
```

モバイルは390×844のChromiumタッチエミュレーション。iOS Safari実機の動作・性能は未検証。任意座標を入力できるが、Appleのcoverage、取得設定のregion/version、対応するcodecに依存する。公式のpixel parityと正確なLODは従来どおり未達。

## 画面

[東京の逐次表示](initial.png) · [450m移動後](moved.png) · [ワイキキへの移動](waikiki.png) · [モバイル](mobile.png)
