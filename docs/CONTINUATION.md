# 次の解析の引継ぎ

## 作業場所

このrepoを解析の新しい基点にする。元の /opt/flyover-viewer と別スレッドの取得labは参照用のまま保持している。研究checkpointは research/nativefree-lab-20261013/、独立監査履歴は research/independent-audit/、HUFF中間監査は reports/historical/。

## 次の順番

1. kind0の3*N byteをnative triangle buffer全3頂点と比較する。先頭N byte以外をすぐmetadataと決めつけない。このtriangle仮説自体は未検証であり、createSplatsが生成した頂点である可能性も確認する。
2. sparse origin0877065cfeff5afefff5ffの+1を、mode/bitmap/low-byte復元規則から説明する。goldenだけに合わせた補正はしない。
3. _bytes_decompressのkind0..6とHUFF callsiteを追い、output-count register/stackの由来を確定する。researchのcodec-slice-arm64.b64、callsite/count-constructor/count-tail資料を利用する。
4. embedded次HUFF stream、bitmap、payload、paired laneを区別し、整数再構成・quantizationを実装する。
5. 東京223でXYZと8属性の全数値・並び・必要ならfloat bit parityを検証する。
6. TRICO mesh v3 topology・position・UV・normalをnative arraysと照合する。
7. Oahu72でnative-free全geometryを生成し、任意地域fetcherとhybrid viewerを統合する。
8. shader uniform・tile accumulation・color transfer・LODを詰める。

## 完了判定

Linux上でR3D入力だけからtexture＋mesh XYZ/面/UV/normal＋Splat XYZ/materialを復元し、東京native goldenとの全数値比較と新規Oahu表示を通す。saved native outputsのreplayやヘッダーcount一致だけでは完了としない。

## メモ間の優先度

README / docs/STATUSは整理時点の現状。過去checkpointは発見過程の証拠。HUFF監査の成功はnative中間byte parityを保証しない。複数監査の件数やwrapper count解釈の差を隠さず残している。
