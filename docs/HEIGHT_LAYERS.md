# 高層部分の取得漏れの修正（2026-10-14）

従来の座標入口はR3D要求を `h=0` に固定していた。元データは高さ方向にも分かれているため、Oahu72では高層建物の上部がポリゴン・Splatとも欠けていた。72原本そのものの復号・golden照合は正しかったが、地域全体の取得としては不足していた。カメラのclip変更では直らない取得漏れである。

現在のライブ入口はstyle100のC3MM v2占有インデックスをLinuxで取得し、指定XY範囲の全高さ候補を列挙する。z20ではz13のインデックスにあるz17の占有セルを使い、3段分の高さの子を保守的にすべて要求する。局所XYは `(x//8)%16`, `15-(y//8)%16`、高さ候補は各セルの `8*h + [0..7]`。インデックスの座標と原本hashを保存・検証する。旧C3MMの子XYZの2倍関係は[一次資料の実装](https://github.com/retroplasma/flyover-reverse-engineering/blob/master/pkg/fly/c3mm/util.go)にも記述されている。現在形式の検証は下記の取得原本・候補応答一覧に基づく。

空のHTTP 200/204または404は、保守的な候補に実データがない場合として記録する。途中の空層で探索を止めない。東京タワーでは `h=4..7` が空でも `h=8` 以上に上部があり、単に連続層を下から探索する方法でも不足する。認証/通信失敗、壊れた非空R3D、未知インデックスは成功扱いしない。インデックスが取得できない場合もh0へ退行しない。空応答のcacheは同じインデックスhashに限って再使用し、`--refresh`はインデックス・非空原本・空応答をすべて再取得する。

一部上層は**元からSplatだけで、ポリゴン0面・テクスチャなし**。空TRICO topologyのmagic・件数・UV/normal不在・全stream消費を厳密に検証し、0長の配列を保存する。表示・GLB出力では空ポリゴンを省略し、元Splatを保持する。架空の面・テクスチャを補わない。hに推定メートルoffsetを加えず、各R3D原本のR/ECEFをそのまま共通フレームへ変換する。

| 検証 | 修正前 | 修正後 |
|---|---:|---:|
| Oahuの非空R3D | h0の72 | h0〜h3の135（追加63） |
| 元ポリゴン面 | 581,186 | 1,064,079 |
| Splatレコード | 304,527 | 382,128 |
| 最大ポリゴン高さ（共通ENU） | 74.36m | 131.12m |
| 最大可視Splat高さ（共通ENU） | 75.96m | 160.36m |
| 東京タワーの同じ平面範囲 | h0の2 | 全高さの18 |

Oahuでは576候補を135非空・441空に分け、全候補の応答を記録。従来72タイルの936配列/画像hashはすべて完全一致。全135タイルの表示配列・UV・画像・地理・位置合わせ、GLB/PLY読み戻し、GLB validatorを確認した。高さはscene原点からのENU上方向のメートルであり、建築物の公称高さではない。

証拠：[reports/height-layers-20261014](../reports/height-layers-20261014/README.md)。新規Linux HTTPSのWebジョブでも東京タワー18を復号・表示。東京223のSplat全配列/材質は完全一致、ポリゴンXYZ/UV/全index/画像は一致、法線271 floatの1 ULP差は従来と同じ個別の説明付き。公式pixel一致・正確なLOD・Apple固有の累積/色変換は引き続き追加目標。

ライブ再現：

```bash
.venv/bin/python pipeline/r3d_explorer.py \
  --lat 21.2828 --lon -157.8369 --radius-m 130 --max-tiles 100 \
  --max-height-requests 2048 --config /private/path/maps.credentials.json \
  --out-dir reports/generated/oahu-full-height --export --serve
```

修正版Release `linux-explorer-height-layers-20261014` の `oahu-full-height.tar.gz` はraw R3D、C3MMインデックス、独立全配列、viewer、GLB/PLY、実行ログを含む。認証設定は含まない。

```bash
gh release download linux-explorer-height-layers-20261014 \
  --repo nmt3325/apple-maps-r3d-research --dir release-assets/height-layers
cd release-assets/height-layers
sha256sum -c SHA256SUMS
tar -xzf oahu-full-height.tar.gz
python3 -m http.server 8972 --bind 127.0.0.1 --directory oahu-full-height/viewer
```

Linux独立復号から再生成する場合は、展開した `oahu-full-height/raw` を `--source-dir` に指定する。offline入口は同じXYの全h原本を選ぶが、入力原本にない高さ層までは補えない。旧h0原本だけを入力すれば旧h0表示になる。

```bash
.venv/bin/python pipeline/r3d_explorer.py \
  --lat 21.2828 --lon -157.8369 --radius-m 130 --max-tiles 100 \
  --source-dir release-assets/height-layers/oahu-full-height/raw \
  --out-dir reports/generated/oahu-height-reproduction --export
R3D_HEIGHT_FIXTURES=release-assets/height-layers/oahu-full-height \
  .venv/bin/python -m unittest audit.test_height_layers audit.test_pipeline -v
```

Webの上限24は平面XYタイルの数。全高さ候補には別途1536要求の上限があり、これを超える範囲は明示rejectする。CLIライブの自動高さ探索はzoom 7以上の対応C3MM v2に限る。地域coverage、API template、未知codecの制約は従来と同じ。
