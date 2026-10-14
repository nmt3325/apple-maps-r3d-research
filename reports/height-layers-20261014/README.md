# 高さ層の取得漏れ修正の証拠

`h=0` 固定取得により旧Oahu72の上部が欠けていた。元72原本の数値復号は正しく、地域全体の取得が不足していた。現在はC3MMの全占有高さ候補を収集する。[仕様と再現コマンド](../../docs/HEIGHT_LAYERS.md)。

- [Oahuの応答/高さ監査](oahu-height-coverage.json)：576候補＝135非空＋441空、h0〜h3、既存936配列/画像hash完全一致。全135原本hashを確認。
- [全配列/画像/地理/レイヤー配置](oahu-region.json)：1,064,079面、382,128 Splat、全geometry有限、UV/index/画像exact、共通R/ECEF→ENU配置を全頂点で確認。
- [GLB/PLY読み戻し](oahu-export.json)：全XYZ・UV・法線・index・画像・RGBA・8属性bit一致。[GLB validator](oahu-gltf.json) はerror/warning 0。
- [Oahuブラウザ](oahu-browser/browser.json) / [東京タワーブラウザ](tokyo-browser/browser.json)：それぞれ135/18タイル、16操作チェック、error 0。両レイヤーの屋上、WASD/EQ/mouse/Esc/resetを実ブラウザ操作で確認。
- [ライブWebジョブ](tokyo-live-run.json) / [新規HTTPS応答](tokyo-live-fetch.json)：東京タワー2平面タイルを18の高さ層タイルへ展開し、新しい原本の取得→独立復号→表示が成功。h4〜7の空応答の後にも上部がある。
- [高さ回帰/破損検出](height-layer-tests.log)：実Oahu index/h1原本、空の下層の後の上層、offlineのh1保持、実Splat-only h3、破損した空mesh拒否、原本破損/別座標の拒否。6/6。[数値回帰](numeric-tests.log)は8/8。
- [東京223 mesh再照合](tokyo-223-mesh.json) / [Splat再照合](tokyo-223-soup.json)：件数・XYZ・UV・全index・primary HEIC・Splat全属性/materialはexact。法線271 floatの既知1 ULP差はすべて個別説明付き。未説明差異0。

[修正前のポリゴン](oahu-before-polygons.png) / [修正後のポリゴン](oahu-browser/polygons.png) / [修正後のSplat](oahu-browser/splats.png)。比較画像は同じ地域の全体表示で、scene bounds変更により初期カメラの高さも変わる。

修正版成果物はprivate Release [linux-explorer-height-layers-20261014](https://github.com/nmt3325/apple-maps-r3d-research/releases/tag/linux-explorer-height-layers-20261014)。Oahu原本・C3MM・全配列・viewer・GLB/PLY・ログを収録する。旧ReleaseのOahu72とARM間の936配列照合はh0コーパスの履歴として保持する。今回の全135タイル出力について新たなARM間照合は行っていない。

[REVIEW.json](REVIEW.json)に要点。公式pixel一致・正確なLOD・独自累積/色変換は未達の追加目標のまま。元Splatだけの上層にポリゴンを捏造しない。
