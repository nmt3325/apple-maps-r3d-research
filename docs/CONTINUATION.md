# 次の解析の引継ぎ

## 作業場所

このrepoを解析の新しい基点にする。元の /opt/flyover-viewer と別スレッドの取得labは参照用のまま保持している。研究checkpointは research/nativefree-lab-20261013/、独立監査履歴は research/independent-audit/、HUFF中間監査は reports/historical/。

## 次の順番

1. Oahu72の表示・地理/全viewer配列・GLB/PLY・ブラウザ15操作検証は完了。座標入力による東京4/ニューヨーク2のLinux HTTPS取得→独立復号→表示生成も完了。
2. 別Linux（Ubuntu 24.04 aarch64）の隔離venvで、固定依存から全経路を再現する。
3. 最終の実装・検証証拠・viewer/export成果物をGitHubへ保存し、README/ACCEPTANCEと6条件の監査を揃える。
4. 追加目標の公式pixel一致、正確なLOD、Apple独自の累積・色変換は未達として追跡する。

完全経路のコマンドと制約は[LINUX_EXPLORER.md](LINUX_EXPLORER.md)。新しい証拠はreports/validation-20261014/。

数値codecと東京223全配列検証は[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)に記録済み。Splatの全3*N頂点と8属性/material20は完全一致、ポリゴンXYZ/UV/全index/primary HEICも一致。法線271個の1 ULP差は個別の数値証拠付きで説明済み。旧`.decoded`の位置は全配列の先頭N頂点だけなので、これを中心点として再利用しない。

## 完了判定

[ACCEPTANCE.md](ACCEPTANCE.md)の6項目をすべて満たす。Linux上でR3D入力だけからtexture＋mesh XYZ/面/UV/normal＋Splat XYZ/8属性/描画用三角形を復元し、東京223の全配列golden比較、新規Oahu72のgeometry/表示検証、座標入力から取得・復号・表示の統合、新しいLinux環境での再現と回帰、GitHub保存・証拠付き報告を完了する。saved native outputsのreplay、ヘッダーcount一致、HUFF中間復号、推定高さmeshだけでは完了としない。公式表示pixel一致・LOD・タイル累積/色変換は追加目標として別途追跡する。

## メモ間の優先度

README / docs/STATUSは整理時点の現状。過去checkpointは発見過程の証拠。HUFF監査の成功はnative中間byte parityを保証しない。複数監査の件数やwrapper count解釈の差を隠さず残している。
