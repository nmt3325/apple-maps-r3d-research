# 次の解析の引継ぎ

## 作業場所

このrepoを解析の新しい基点にする。元の /opt/flyover-viewer と別スレッドの取得labは参照用のまま保持している。研究checkpointは research/nativefree-lab-20261013/、独立監査履歴は research/independent-audit/、HUFF中間監査は reports/historical/。

## 次の順番

1. `codec/nativefree_decode_r3d.py`のOahu72出力からハイブリッドviewerを生成する。Splat/ポリゴンは同じ原本の回転とECEF並進でENUへ移す。元HEICをLinuxでPNG等へ変換して表示する。
2. Oahuの全配列・地理位置・UV/index・有限値・欠損RGB・レイヤー位置合わせを記録し、WASD、上下、マウス、レイヤー切替をブラウザで検証する。
3. 既存取得labの署名処理を座標/範囲入力の入口へ統合する。認証はローカル設定とし、ログ・表示・Gitには含めない。任意地域でタイルの有無とstyle versionを検証する。
4. 原本取得→独立復号→viewer生成を一コマンドにし、GLB/PLY出力、失敗ログ、破損入力検出、別Linux環境での再現を揃える。
5. 実装・仕様・全検証証拠をGitHubへ保存し、READMEを実態に合わせて6条件の完了監査を行う。
6. 追加目標のshader uniform・tile accumulation・color transfer・LOD・公式pixel一致を別途追跡する。

数値codecと東京223全配列検証は[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)に記録済み。Splatの全3*N頂点と8属性/material20は完全一致、ポリゴンXYZ/UV/全index/primary HEICも一致。法線271個の1 ULP差は個別の数値証拠付きで説明済み。旧`.decoded`の位置は全配列の先頭N頂点だけなので、これを中心点として再利用しない。

## 完了判定

[ACCEPTANCE.md](ACCEPTANCE.md)の6項目をすべて満たす。Linux上でR3D入力だけからtexture＋mesh XYZ/面/UV/normal＋Splat XYZ/8属性/描画用三角形を復元し、東京223の全配列golden比較、新規Oahu72のgeometry/表示検証、座標入力から取得・復号・表示の統合、新しいLinux環境での再現と回帰、GitHub保存・証拠付き報告を完了する。saved native outputsのreplay、ヘッダーcount一致、HUFF中間復号、推定高さmeshだけでは完了としない。公式表示pixel一致・LOD・タイル累積/色変換は追加目標として別途追跡する。

## メモ間の優先度

README / docs/STATUSは整理時点の現状。過去checkpointは発見過程の証拠。HUFF監査の成功はnative中間byte parityを保証しない。複数監査の件数やwrapper count解釈の差を隠さず残している。
