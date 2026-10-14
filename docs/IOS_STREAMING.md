# iOS ネイティブの直接取得・視界ストリーミング

`ios/R3DExplorer.xcodeproj` は SwiftUI の操作画面と Metal の描画を備えた iPhone / iPad アプリ。既存 Web ビューアと研究用 pipeline は保持する。

## 動作

アプリが調査済みの取得テンプレートからリクエストごとに SHA-256 / AES-256-CBC 署名を作り、Apple の HTTPS 配信先へ直接接続する。Linux の地形配信・復号サーバー、WKWebView、全地域の事前ダウンロードは不要。実行中の問い合わせ先は取得設定の Apple ホストだけで、サーバーへのフォールバックはない。

原本 R3D を端末内の独立 Python decoder で復号する。Python は BeeWare の iOS 用 XCFramework と標準ライブラリとしてアプリに同梱し、C API で呼び出す。プロセス起動や外部 Python 環境は使わない。UI / 移動 / ネットワーク / 描画は Swift / UIKit / Metal、元の数値 codec はこのリポジトリの `codec/` を共有する。HEIC は ImageIO / MetalKit で端末内変換する。

250 ms ごとにカメラ位置・方向・視野角から表示候補を更新する。水平範囲は z18 / z19 / z20 の quadtree leaves で分割し、近くを細かく、遠くを粗くする。対応する範囲の coarse モデルを先に表示し、各 fine leaf の全高さが揃うごとに切り替える。coarse の同じ XY 範囲を fragment shader でマスクして、Splat の重複合成を防ぐ。実際のタイル境界付近の差や LOD 継ぎ目は公式と同一とは保証しない。

この取得テンプレートで C3MM を提供するのは **z13**。z18 に対して z11 を問い合わせる方法では空応答になるため、各 LOD とも z13 index 内の z17 占有セルを参照する。z18 / z19 / z20 でそれぞれ 2 / 4 / 8 の高さ子を列挙し、途中の空層では探索を止めない。インデックスの座標を検証し、未知の形式や認証失敗を空タイルとして扱わない。h0 固定の取得は行わない。

## 負荷管理

- ネットワーク・復号・GPU 準備を含むタイル処理は同時最大 2 件。Python 復号は actor 内で直列化し、メインスレッドでは行わない。
- 不要になったリクエストを取り消し、復号中の結果も世代番号・キャンセル確認で破棄する。Python 数値処理自体は途中で強制停止せず、完了後に結果を破棄する。
- GPU のモデル・テクスチャ見積もりは標準 192 MiB、軽量 / メモリ警告時は 96 MiB。実際の 3D frustum に入らないモデルは 2 秒の保持期間後に解放し、軽量な境界情報だけを保持する。視点が変わると原本キャッシュから再生成する。上限に届くと描画距離を短縮する。これは**常駐モデルの予算**であり、Python、復号途中の配列、Metal ドライバー、アプリ全体の RSS の上限ではない。
- テクスチャは最大 1024 / 512 px に縮小し mipmap を生成。描画解像度を最大 1.5 倍、GPU の処理中フレームを最大 3 件に制限する。実際の 3D sphere / frustum 判定で描画を除外する。
- 原本の LRU ディスクキャッシュは取得設定ごとの namespace で最大 384 MiB、モデルは原本から再生成する。HTTP 空応答は 60 秒、最大 4096 件。対応するインデックスも必要範囲を中心に整理する。
- バックグラウンドでは描画・新規取得・移動を停止する。発熱時には軽量化し、低電力モードでは 30 fps に抑える。
- 429 / 5xx は最大 3 回、待ち時間を設けて再試行。401 / 403 は取得を停止して設定更新を示す。取得失敗は 20 秒の cooldown を設ける。レスポンス / gzip 展開は 16 MB に制限する。

空は Metal shader で青空・太陽・薄い雲・地平線の霞を生成し、遠方モデルを霧へ滑らかに接続する。

## ビルドと利用

Xcode と iOS SDK を用意し、リポジトリの root から実行する。

```sh
bash ios/Scripts/bootstrap.sh
open ios/R3DExplorer.xcodeproj
```

bootstrap は SHA-256 を固定して Python 3.13-b13 の iOS support package を取得する。`Vendor/` は git 管理しない。生成済みの Xcode project と shared scheme を収録している。

実機では Xcode の Signing & Capabilities で本人の Development Team を選び、接続した iPhone / iPad を Run 対象にする。iOS 17 以上、Metal 対応端末が必要。実機向けの Release / arm64 コンパイルと simulator の実行は別の検証であり、実機での fps やメモリ挙動は未検証。

初回起動から標準設定で Apple の配信先へ接続する。外部 JSON、Apple ID、個人用 API キー、GitHub Secrets は不要。配信先・データ版・共通の署名定数から iOS 内で `FetchConfiguration` を組み立て、各リクエストの nonce・有効期限・AES 署名を端末内で生成する。

共通定数は MIT ライセンスで公開済みの [Apple-3D-RE-Lightweight](https://github.com/SynArchive/Apple-3D-RE-Lightweight/blob/df3e354d1c0f2dc7a35ecb425b0f49973b7d46ee/main.go) と一致することを確認して使用する。個人の認証情報や保存済み accessKey ではない。配信先 `gspe11-ssl.ls.apple.com/tile`、style 98 / 100、v714、region0 は現在の調査で取得・復号を確認した値であり、Apple のサービス変更で更新が必要になることがある。

GitHub Actions の `iOS native build` の Artifacts から `R3DExplorer-unsigned-ipa` をダウンロードし、ZIP 内の `R3DExplorer-unsigned.ipa` を利用中の方法で署名・インストールする。起動すると東京タワーの取得が始まる。「取得設定を更新」は標準値を上書きするための追加機能で、通常起動には使わない。以前の設定が残っている場合は「標準の接続設定に戻す」で復帰できる。

独自設定を同梱して開発する場合だけ、git 管理しない `ios/Local.xcconfig` に次の値を指定する。

```xcconfig
R3D_FETCH_CONFIG = /absolute/private/path/maps.credentials.json
```

個別に読み込んだ設定は Keychain に保存する。設定を読み込まず、Keychain が利用できない環境でも標準設定で起動できる。個別の設定ファイル・保存済み署名 URL・取得済み実データは git に含めない。

画面ドラッグで視点を回転、左のスティックで前後左右移動、右のボタンで上昇 / 下降、ピンチで前後移動。設定画面から東京タワー・ワイキキ・任意の緯度経度へ移動できる。端末 GPS の現在地への追従ではなく、アプリ内のカメラ位置を追従する。

## 検証

```sh
swiftc ios/App/World.swift ios/Tests/WorldChecks.swift -o /tmp/r3d-world-checks
/tmp/r3d-world-checks
python3.13 ios/Tests/test_mobile_decoder.py -v
# 原本の頂点 / UV / 法線 / Splat の配列一致を検証する場合
R3D_TEST_FIXTURES=/private/path/raw-fixtures python3.13 ios/Tests/test_mobile_decoder.py -v
```

Debug アプリを `-streaming-validation` 引数で起動すると、東京での回転・450 m 移動・メモリ警告・ワイキキへの移動を 120 秒で実行し、Documents の `streaming-validation.json` に記録する。通常起動・Release ではこの自動操作を行わない。公開のダミー設定による署名 test vector も、既存 Python acquisition と照合する。

```sh
python3 ios/Tests/check_validation.py /private/path/streaming-validation.json
```

この検査は実行完了、署名一致、同時処理上限、モデルのメモリ予算、複数 LOD、上層、移動先での表示を確認する。fps は測定値として報告し、端末ごとの結果を区別する。

## 対応範囲

Apple の公式 mesh export API や MapKit への置換ではなく、調査済みの R3D v2 / TRICO v3 / BYET / C3MM v2 経路を端末内で利用する研究アプリ。地域の coverage、取得テンプレートの region / version、有効な署名素材に依存する。未対応 codec / index は明示エラーとなる。公式 pixel parity、正確な Apple LOD 選択、公式 Splat 累積は未達のまま。App Store 配布の確認はこの実装検証に含まない。

参考: [Python の iOS 組み込み](https://docs.python.org/3.13/using/ios.html)、[BeeWare Python Apple Support](https://github.com/beeware/Python-Apple-support)。元コードとデータの出所は [PROVENANCE.md](PROVENANCE.md) に従う。
