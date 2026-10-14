# Linuxの取得・独立復号・表示・出力

入口は `pipeline/r3d_explorer.py`。R3D原本から元ポリゴンとSplatを復元し、静的Webビューアと任意のGLB/PLYを生成する。Appleライブラリ、Simulator、native goldenは実行時に読まない。

## 依存関係

- Python **3.12以上**（数値codec単体は標準ライブラリ、表示ビルダーの固定NumPyは3.12以上）。
- Node.js 18以上とnpm。依存をpackage-lock.jsonで固定。
- `requirements.txt` のNumPy / Pillow / pillow-heif / cryptography。HEICはLinuxのlibheifでRGB PNGに変換する。wheelに必要なlibheifが含まれる。
- 地理・レイヤー監査のみ `requirements-audit.txt` のSciPy。
- 表示はWebGL対応ブラウザ。自動操作の監査はChromiumとplaywright-core。
- HTTPS取得には、使用するendpoint/style/region/versionと署名素材を含む**ローカル設定**が必要。設定・キャプチャ・署名URLはGit/Releaseに含めない。

Ubuntu 24.04でのセットアップ例：

```bash
sudo apt-get update
sudo apt-get install -y python3-venv nodejs npm
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-audit.txt
npm ci --prefix viewer --ignore-scripts --no-audit --no-fund
```

## 緯度・経度・範囲から実行

```bash
.venv/bin/python pipeline/r3d_explorer.py \
  --lat 35.6586 --lon 139.7454 --radius-m 15 \
  --config /private/path/maps.credentials.json \
  --out-dir reports/generated/tokyo-tower --export --serve
```

http://127.0.0.1:8973/ を開く。WASDで水平移動、E/Q（Space/Ctrlでも可）で上下、Shiftで高速、画面クリックでマウス視点、Escで解除。自由移動ボタン/Fで飛行とorbitを切り替える。ポリゴン/Splatはそれぞれ表示切替できる。

`--radius-m` は球面半径を含む緯度経度の矩形を計画し、交差する完全なタイルを取得する。境界の外にもタイル全体のgeometryを表示する。Mercator緯度±85.0511287798066度、経度±180度、半径0より大きく100km以下、既定最大4096タイル。日付変更線はxをwrapする。広い範囲はメモリと時間を要する。`--zoom` は既定20、公式の正確なLOD選択は行わない。`--max-tiles`で件数上限を変更できる。

既存出力のrawタイルはcacheとして使う。`--refresh`で新しい署名によるHTTPS再取得。同じout-dirに別の領域の原本を混ぜるとrejectする。HTTP失敗、非R3D、上限超過、復号失敗、地理原点と要求タイル中心の0.5m超のずれは処理を失敗させる。空白を推定meshで埋めない。

出力は `plan.json`、`raw/*.r3d`、`raw/fetch.json`、`decoded/manifest.json`と全配列、`decode.log`、`viewer/`、`run.json`。`--export`は `export/scene.glb`、`splats.ply`、`export.json`も生成する。run.jsonは失敗時も保存する。

## ローカル取得設定

設定JSONのschema：`endpoint`（queryを含まないHTTPS URL）、`queryParameters`（順序付き `[名前, 値]` ペア。x/y/z/h/styleを含みstyle=98、accessKeyを含めない）、`headers`、`signingParts`（2つの署名素材）。`R3D_FETCH_CONFIG`でも設定パスを指定できる。署名素材そのものをリポジトリへ書かない。

既存の使用許可がある通信記録と署名用Goソースから、一回だけローカル設定を準備するhelperもある。mitmproxyを持つ別Python環境で実行する：

```bash
/path/to/mitmproxy-python pipeline/prepare_fetch_config.py \
  --capture /private/path/session.mitm \
  --signing-source /private/path/main.go \
  --output /private/path/maps.credentials.json
```

helperは成功したstyle98/z20/h0要求からtemplateを抽出し、保存accessKeyを除く。設定はmode 0600、既存ファイルを上書きしない。その後の実行にキャプチャやmitmproxyは不要。設定templateが古い場合、対象地域のFlyoverがない場合、APIが変更された場合はHTTPエラーになり得る。現在の設定は東京、Oahu、ニューヨークで成功した。任意の地理入力を受け付けるが、サービス側の全世界coverageや未知のcodec variantを保証しない。

## 原本だけからOahu72を再現

Release `snapshot-20261014` の `oahu-and-fetch-results.tar.gz` を展開する。これは原本であり、native goldenはOahuの実行に不要。

```bash
gh release download snapshot-20261014 --repo nmt3325/apple-maps-r3d-research \
  --pattern oahu-and-fetch-results.tar.gz --dir release-assets
mkdir -p release-assets/extracted
tar -xzf release-assets/oahu-and-fetch-results.tar.gz -C release-assets/extracted
R3D_OAHU_INPUT="$PWD/release-assets/extracted/fetch-lab/fresh_signed/oahu_hilton_20261013/area_z20"
.venv/bin/python codec/nativefree_decode_r3d.py "$R3D_OAHU_INPUT" \
  --out-dir reports/generated/oahu-decoded --workers 4
.venv/bin/python pipeline/build_viewer.py reports/generated/oahu-decoded \
  --out-dir reports/generated/oahu-viewer --lat 21.2828 --lon -157.8369 --title 'Oahu · Hilton 3D explorer'
.venv/bin/python pipeline/export_scene.py reports/generated/oahu-viewer \
  --decoded reports/generated/oahu-decoded --out-dir reports/generated/oahu-export
.venv/bin/python audit/audit_region_viewer.py reports/generated/oahu-decoded \
  reports/generated/oahu-viewer "$R3D_OAHU_INPUT" --bounds 21.27 -157.85 21.30 -157.82 \
  --report reports/generated/oahu-region-validation.json
.venv/bin/python audit/audit_scene_export.py reports/generated/oahu-viewer \
  --decoded reports/generated/oahu-decoded --exports reports/generated/oahu-export \
  --report reports/generated/oahu-export-validation.json
python3 -m http.server 8972 --bind 127.0.0.1 --directory reports/generated/oahu-viewer
```

別terminalで、Chromiumの実際の操作を検証する：

```bash
CHROMIUM_PATH=/usr/bin/chromium node audit/test_independent_viewer.cjs \
  http://127.0.0.1:8972/ reports/generated/oahu-browser
```

## 出力の意味と制約

GLBは共通east/up/southメートル座標で、元のポリゴン面、UV、法線、PNGテクスチャと全Splat三角形/RGBAを保存する。UVのVをglTFの画像座標に合わせて反転する。PLYは全Splat三角形のXYZ/RGBAと各頂点に元レコードの8属性を保存する。欠損RGBのNaNもbitを保持する。元HEICとraw配列はdecoded出力に残る。

ブラウザは元三角形にbarycentric alphaを付ける。GLBは標準alpha blendで、専用shaderを表現しない。Apple公式のpixel一致・正確なLOD・タイル累積/色変換は未達の追加目標。レイヤーは元の異なるgeometryであり、Splat中心がポリゴン面と完全一致するという意味ではない。原本の同じR/ECEF transformと共通ENUを適用したことを全配列で検証する。

実証は [reports/validation-20261014](../reports/validation-20261014/) に保存。東京全golden比較は [INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)。

## 再現済み環境と配布成果物

実装fb259cfを別Ubuntu24.04/aarch64でfresh cloneし、system-site-packages=falseのvenvと上記依存からOahu72、viewer、GLB/PLY、全region/export監査、原本破損/別座標reject、座標入口のoffline原本経路を再現した。936配列/画像のSHA一覧digestと、完成GLB/PLYのSHAはLinux x86_64と完全一致。[検証証拠](../reports/validation-20261014/linux-arm-reproduction.json) / [環境間照合](../reports/validation-20261014/cross-platform-comparison.json)。ライブ署名取得はCT104 Linuxで東京4/ニューヨーク2を検証している。

完成viewerと出力はprivate Release `linux-explorer-20261014` にある。全依存なしで完成viewerを表示する例：

```bash
gh release download linux-explorer-20261014 --repo nmt3325/apple-maps-r3d-research \
  --dir release-assets/linux-explorer
cd release-assets/linux-explorer
sha256sum -c SHA256SUMS
tar -xzf independent-oahu-viewer-and-exports.tar.gz
python3 -m http.server 8972 --bind 127.0.0.1 --directory oahu-viewer
```

`fresh-coordinate-regressions.tar.gz` は東京タワー4とニューヨーク2の新原本と独立出力を含む。例えば展開後の `live-new-york/raw` を `--source-dir` に指定すれば、同じ座標/半径で入口を再現できる。取得設定は含まれない。

ユーザー指定によりCT104ではsystemdのtransient unit `r3d-oahu-independent-viewer.service` でOahuサーバーを稼働させ、`tailscale serve --bg --yes --https=8972 http://127.0.0.1:8972`でtailnetに公開した。アクセス先は `https://ct104.taila8c9c.ts.net:8972/`。別Tailscale LinuxからTLS検証付きGETで72タイルsceneを確認済み。serviceはshell終了後も動くがマシン再起動時には自動起動しない。状態は `systemctl status r3d-oahu-independent-viewer.service` と `tailscale serve status`、停止は `systemctl stop r3d-oahu-independent-viewer.service` と `tailscale serve --https=8972 off`。
