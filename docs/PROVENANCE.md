# 保存範囲と出所

- CT104解析本体: /opt/flyover-viewer/
- この会話の独立監査: /root/.desktop-mcp/linux-4ebec5ed/work/apple-r3d-independent-audit-20261013/
- 別スレッド取得lab: /root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/
- Mac参照復号/静的解析: /Users/denken/.desktop-mcp/mac-6dd4602a/work/ios27-vectorkit-analysis/
- ChatGPT作業フォルダ: /workspace/scratch/0cf1e1f0b378/huffman_work/
- 新しいGit checkout: /opt/apple-maps-r3d-research/

SOURCE_MANIFEST.jsonは元ソースのsource path・bytes・SHA-256とrepo内コピー先を記録する。snapshot viewer/researchは原コードを保存し、codecと主要auditには利用用コピーを置く。auditのsys.pathはrepoのcodecへ変更した。test_nativefree_r3dは環境変数でデータパスを指定でき、report出力先をrepo内に変更した。C3MM corpus testもR3D_FETCH_LAB_DIRでデータ場所を指定できる。

Gitにはコード・記録・静的解析の小さな研究資料を収録する。研究資料のGhidra Cはdecompiled pseudocodeで、compilable Cや独立実装とは区別する。ARM64 sliceも同じ研究用途の参照資料。

Releaseには元R3D、native比較配列、viewer用出力、GLB/PLY、取得labのpayload/export、独立抽出の中間結果を収録する。各snapshotはdata/REFERENCE_INVENTORY.jsonに載る。重複したtarを保存し直す代わりに、その中身のデータを保存する。

収録しないもの: 認証情報を含むmitmproxy/HTTP capture、ingest.token、鍵ディレクトリ、個別signed request URL、インストール済みGhidra/JDK/node_modules/Unicorn、派生データの重複tar。既存legacy OSS checkoutは再配布せず、出典参照とする。

元のviewer assetsとnative出力はApple由来の地図データ。Three.js/playwrightのライセンスはviewer/third-party/。legacy参考実装はretroplasma/flyover-reverse-engineeringとApple-3D-RE-Lightweight。独立Python実装と第三者/Apple由来資料を一括で同じライセンスにしていない。新規repoはprivateで保存した。

## 履歴を保った整理

探索段階の推測・誤解を含む過去メモはhistoryとして残す。C3MM record lengthのtag1byteの扱い、過去のproxy polygon、UV上下、原点222/223と後続の検証結果などは現状文書で補足する。canonical C3MM parserはcodec/c3mm_v2_parser.py。古いscan-based parserの見かけの+1 byteを実入力truncationとは扱わない。
