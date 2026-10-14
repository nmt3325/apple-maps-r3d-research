# 再現と検証

独立復号からハイブリッド表示・GLB/PLY出力までの完全経路は [LINUX_EXPLORER.md](LINUX_EXPLORER.md)。以下のsaved native viewerの復元とは区別する。

現在の全数値decoderは[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)のコマンドで実行する。以下のフレーム/HUFF中間検証と区別する。東京全配列golden比較は`audit_soup_arrays.py`と`audit_mesh_arrays.py`。Oahu72は`nativefree_decode_r3d.py`で原本から出力できる。

## データ不要のcheck

```bash
python3 -m compileall -q codec audit native-harness snapshots research
python3 codec/huff816_nativefree.py
PYTHONPATH=codec python3 -c "from audit.test_nativefree_r3d import test_compact_size; test_compact_size(); print('PASS compact-size roundtrip')"
```

スナップショットの探索用scriptはimport時に外部ファイルを読むものがあるため、compileallは構文確認だけ。全script実行とは違う。

## Releaseの取得

```bash
gh release download snapshot-20261014 --repo nmt3325/apple-maps-r3d-research --dir release-assets
cd release-assets
sha256sum -c SHA256SUMS
mkdir -p extracted
for f in *.tar.gz; do tar -xzf "$f" -C extracted; done
```

archive内部はflyover-viewer/とfetch-lab/。全ファイルのbytes/SHA-256はdata/REFERENCE_INVENTORY.json。cloneしたrepoとReleaseのsnapshot tagを揃える。

## 295タイルのフレーム回帰

CT104では既存パスを使ってそのまま実行する。

```bash
python3 audit/test_nativefree_r3d.py
python3 audit/audit_huff816_nativefree.py /opt/flyover-viewer/native-r3d /root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/fresh_signed/oahu_hilton_20261013/area_z20 --report reports/generated/huff816.json
python3 audit/audit_byet_kind0.py /opt/flyover-viewer/native-r3d /opt/flyover-viewer/decoded-native/all-223 --report reports/generated/byet-kind0.json
python3 audit/test_c3mm_v2.py
```

別環境の展開済みデータを使う例：

```bash
export R3D_REFERENCE_ROOT="$PWD/release-assets/extracted/flyover-viewer"
export R3D_FETCH_LAB_DIR="$PWD/release-assets/extracted/fetch-lab"
export R3D_OAHU_DIR="$PWD/release-assets/extracted/fetch-lab/fresh_signed/oahu_hilton_20261013/area_z20"
python3 audit/test_nativefree_r3d.py
python3 audit/test_c3mm_v2.py
python3 audit/audit_huff816_nativefree.py "$R3D_REFERENCE_ROOT/native-r3d" "$R3D_OAHU_DIR" --report reports/generated/huff816.json
python3 audit/audit_byet_kind0.py "$R3D_REFERENCE_ROOT/native-r3d" "$R3D_REFERENCE_ROOT/decoded-native/all-223" --report reports/generated/byet-kind0.json
```

HUFFのreject 0とBYET first-N低位byte一致は限定的な検証。完全なnative-free geometry比較とは区別する。

## viewerの復元

Releaseのviewer-assets-and-exports.tar.gzを展開すると、元のwww配下data/native/c3m-geometry/c3m-textures/vendorとGLB/PLYが戻る。current HTMLはrepoのviewer/www/index.html。ReleaseにHTML自体は含まれない。

```bash
cp viewer/www/index.html release-assets/extracted/flyover-viewer/www/index.html
python3 -m http.server 8891 --bind 127.0.0.1 --directory release-assets/extracted/flyover-viewer/www
```

http://127.0.0.1:8891/ を開く。データ量の大きいz20全表示はメモリを多く使う。CT104既存viewerのHTTP serviceやTailscale設定はこの保存作業では変更していない。

viewerの依存はThree.jsとplaywright-core。Pythonのgeometry buildersはnumpy/Pillow/trimeshを使う。取得toolにはmitmproxy/cryptographyが必要で、実際の認証template/署名素材は別途ローカル入力となる。snapshot scriptのCT104絶対パスは保存したままなので、他環境ではパス調整が必要。

Mac native-harnessはiOS27 Simulator/VectorKit private interfacesに依存する。現在のcodec検証はsaved goldenを読み、Apple decoderを呼び出さない。

## 今回のcheck記録

reports/PACKAGING_VALIDATION.json に各commandのexit codeと結果を保存する。historical/は以前の測定であり、今回の再検証とは区別する。
