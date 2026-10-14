# Web版の任意位置・移動中ストリーミング

Web版では、Appleからの署名取得・独立復号・HEIC変換を従来どおりLinuxサーバーで行う。ブラウザは同じサイトから表示用の配列・PNGを受け取り、WebGLで描画する。署名素材、署名付きURL、Appleの原本をブラウザへ渡さない。

[iOS版PR #1](https://github.com/nmt3325/apple-maps-r3d-research/pull/1)のカメラ追従、距離別LOD、全高さ探索、粗いモデルからの逐次更新とモデル保持予算を参考にした。iOSのApple直接取得・Metal描画はWebへ移植していない。

## 操作

既存のTailnet入口：https://ct104.taila8c9c.ts.net:8972/

- 「地図から場所を選ぶ」で任意の緯度・経度を入力し、「対象タイル数を確認」→「この場所から探索」。ページを切り替えず、その位置から読み込みを始める。
- 「自由移動」でWASD、E/Q（Space/Ctrl）、マウス視点を利用。Shiftで高速。タッチ画面には方向・上下ボタンを表示し、ドラッグで視点を回転する。
- スマホでは操作パネルを初期状態で折りたたむ。「操作」で地点選択や描画距離の設定を開く。
- 「移動先を自動で読み込む」は初期状態でON。停止・再開できる。描画距離は80〜600m。
- `/?lat=35.6586&lon=139.7454` のようにURLでも開始位置を指定できる。対象緯度はMercatorの±85.05112878度、経度は±180度。

表示中の座標はカメラ位置であり、端末GPSへの追従ではない。データが存在しない場所・取得設定に対応しない地域は空表示または明示エラーになる。

## 読み込みと描画

250msごとにカメラ位置、方向、視野角からz18の親を選び、近距離200m以内をz19、85m以内をz20へ分割する。距離にはタイルの半対角を含める。視野には回転時の余裕を持たせる。1回の計画は最大192の水平leafで、near/farの重複しないquadtree領域を作る。

高さインデックスはすべてのLODで**z13**。その中のz17占有セルからz18/19/20の高さ子をそれぞれ2/4/8個列挙する。空の下層があっても上層の探索を続ける。インデックスがない・壊れた場合は、h0固定で成功扱いしない。

粗い親タイルを先に準備し、各高さが到着すると表示する。fine leafの全高さが読み込み済みまたは正しく空と判定された時点で詳細を表示する。親の対応するXY範囲を両レイヤーのfragment shaderでマスクし、粗いSplatと細かいSplatの重複を抑える。公式LOD、tile seam、pixel parityの完全再現を意味しない。

元のlocal float32配列とdouble精度のECEF変換をタイルごとに送る。ブラウザで共通east/up/south座標へ変換する。原点から3km移動するとカメラの地理的位置を引き継いで原点を更新し、モデルを再取得・再配置する。地域変更時は世代を更新し、前の取得結果を新しいシーンへ混ぜない。

## 制限とキャッシュ

- ブラウザのサーバー取得ジョブ待ちは同時2件、配列・テクスチャの取得とモデル準備も同時2件。全体を最大4件に制限し、モデル準備中に次のサーバー取得を進める。不要なHTTP要求と準備待機をAbortControllerで取り消し、遅れて生成されたモデルも破棄・解放する。非表示タブでは新規読み込みを停止する。
- サーバーの取得・復号はプロセス2個。全ブラウザ共通の処理待ちは最大8件。同じ設定・タイルへの要求は1処理にまとめる。不要になった処理も、サーバーで実行開始済みなら安全に完了させてキャッシュする。
- ブラウザの保持モデル予算は192MiB、初期幅700px未満では96MiB。不要なモデルを2秒後に解放し、頂点・index・テクスチャ・materialをdisposeする。予算不足時は描画距離を縮める。この予算はGPU用配列とテクスチャの見積もりで、ブラウザ全体のRSS上限ではない。
- サーバーは設定別namespaceの完成キャッシュを1GiBに制限する。原本・表示データは1時間、空応答は60秒、失敗は20秒。LRUで整理し、プロセス再起動後も有効な完成キャッシュを再利用する。処理中の一時ファイルと他namespaceの保存物はこの予算に含めない。
- テクスチャは元HEICからPNGへ変換し、最大1024pxへ縮小する。ジオメトリは元配列を保持し、要求座標とECEF原点の0.5m以内の一致を検証する。
- 429/5xxは最大3回、待ち時間を設けて再試行する。401/403は認証エラーとして停止する。未知の形式・復号失敗を空タイルとして扱わない。

公開するのは専用ルートのmesh/splats/textureだけ。原本、設定、復号途中のファイルは静的Web root外に置く。APIは既存と同じOriginチェックを使い、ブラウザから任意URLを指定する仕組みはない。

## 起動と検証

既存サービスと同じPython環境・取得設定を使う。追加のデータ変換サービスやブラウザ拡張は不要。

```sh
R3D_FETCH_CONFIG=/private/path/maps.credentials.json \
R3D_ALLOWED_ORIGIN=http://127.0.0.1:8974 \
R3D_WEB_PORT=8974 \
R3D_WEB_ROOT=/absolute/path/to/existing/viewer \
R3D_WEB_RUNS=/absolute/private/path/to/runs \
.venv/bin/python pipeline/map_web_server.py

.venv/bin/python -m unittest audit.test_web_streaming -v
node audit/test_stream_planner.mjs
node audit/test_stream_controller.mjs
node audit/test_web_streaming.cjs http://127.0.0.1:8974 reports/generated/web-streaming-browser
node audit/test_web_streaming_mobile.cjs http://127.0.0.1:8974 reports/generated/web-streaming-mobile
```

ライブサービスでは、既に生成したシーンにも現在のHTML/JSと読み込みAPIを提供する。単独の静的ビューアは従来どおり供給済みタイルを表示し、ライブAPIへアクセスしない。従来の範囲一括取得API、offline CLI、GLB/PLY exportは利用可能。

検証記録は[Webストリーミングの検証](../reports/web-streaming-20261014/README.md)。モバイル検証はChromiumのタッチ画面エミュレーションで、iOS Safari実機の性能確認ではない。
