# 次の解析の引継ぎ

## 作業場所

このrepoを解析の新しい基点にする。元の /opt/flyover-viewer と別スレッドの取得labは参照用のまま保持している。研究checkpointは research/nativefree-lab-20261013/、独立監査履歴は research/independent-audit/、HUFF中間監査は reports/historical/。

## 主要目標達成後の引継ぎ

主要6条件は対応するR3Dについて達成済み。別Ubuntu24.04/aarch64でもOahu72を再現し、936配列/画像hashとGLB/PLY SHAが一致。証拠はreports/validation-20261014/、成果物はprivate Release linux-explorer-20261014。

Oahuサーバーはユーザー指定で https://ct104.taila8c9c.ts.net:8972/ に稼働中。systemd transient unitなのでshell終了後も動作するが、マシン再起動時の自動起動は未設定。詳細はLINUX_EXPLORER.md。

次に追跡するのは追加目標の公式pixel一致、正確なLOD、Apple独自の累積・色変換。現状のbarycentric alpha/GLB standard blendの差を維持して明記する。未知codec/primary atlas variantやAPI template更新が必要な地域は明示rejectし、代用meshやnative再表示へfallbackしない。

完全経路のコマンドと取得設定/coverage/対応形式の制約は[LINUX_EXPLORER.md](LINUX_EXPLORER.md)。

数値codecと東京223全配列検証は[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)に記録済み。Splatの全3*N頂点と8属性/material20は完全一致、ポリゴンXYZ/UV/全index/primary HEICも一致。法線271個の1 ULP差は個別の数値証拠付きで説明済み。旧`.decoded`の位置は全配列の先頭N頂点だけなので、これを中心点として再利用しない。

## 完了判定

[ACCEPTANCE.md](ACCEPTANCE.md)の6項目をすべて満たす。Linux上でR3D入力だけからtexture＋mesh XYZ/面/UV/normal＋Splat XYZ/8属性/描画用三角形を復元し、東京223の全配列golden比較、新規Oahu72のgeometry/表示検証、座標入力から取得・復号・表示の統合、新しいLinux環境での再現と回帰、GitHub保存・証拠付き報告を完了する。saved native outputsのreplay、ヘッダーcount一致、HUFF中間復号、推定高さmeshだけでは完了としない。公式表示pixel一致・LOD・タイル累積/色変換は追加目標として別途追跡する。

## メモ間の優先度

README / docs/STATUSは整理時点の現状。過去checkpointは発見過程の証拠。HUFF監査の成功はnative中間byte parityを保証しない。複数監査の件数やwrapper count解釈の差を隠さず残している。
