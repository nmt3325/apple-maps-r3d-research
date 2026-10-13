# 検証した形式

## R3D v2 / TRICO / BYET

- R3D magic: 3d 96 59 2e、u32 LE version2、bytes8..10は01 02 00。byte11からULEB tag,lengthのTLV。
- 外側tags [1,2,3]。Splat group内[1,1,4,2,3]、mesh group内[1,1,2,3]。
- TRICO soup: d1 22 c9 07、version1、+8 u64 record count、+16 u32 channels8、+20 float32 scale9個。
- TRICO mesh: e1 21 66 24、version3、+8 float32 scale3個。topology/数値は未復号。
- soup +56から2つのcompact-length BYET block。XYZと8属性。BYETは25 00、compact origin byte length、origin、80＋u16 marker004a、J payload。
- compact sizeはULEBとは別物。先頭byteの下位1連続数でLE byte幅を決め、幅分右shift。ffの場合は続く8byteをLE整数として読む。
- originは12byteなら3 signed int32。10/11byteではmode04/08＋presence bitmap＋sparse bytes。符号拡張やrepeat規則には未解決ケースあり。
- Jは12 XYZ byte lanes /32 attribute byte lanes。bitmap A、active countに基づく2bit token bitmap B、種類/圧縮長directory、lane payloadの順。
- kind4/6は直前laneとのmulti-byte grouping。種類0..6の数値再構成は未完成。

## HUFF

0x61000002のtable/payloadはLE u32 wordをMSB-firstに読む。8/16bit symbol widthに対応する実装があるが、実コーパス監査は主に8bit。0xe1000002はliteral dispatch。0x24 envelopeの解釈と出力count provenanceは調査継続中。codecの指定output_symbolsは呼び出し側に依存する。

## 既存native golden

- *.decoded: u32 LE header4個 magic31443352、N、8、reserved。続けてN*3 float32 XYZ、その後N*8 float32 attributes。全長16+44*N。
- *.native-triangle-f32: N*3*3 float32、36*N byte。
- *.native-material20: N*20 byte、先頭4byte RGBA、後続16byteは4 float32 properties。
- C3M native arraysは位置/UV/法線とそれぞれのtriangle indexを分離している。
- viewerのC3M geometry: 16byte header、12*N XYZ、8*N UV、12*N normals、12*F triangle indices。

## C3MM v2

C3MM＋u16 version2＋u16 subtype3＋u32 section count6/7。各recordはu8 tagとu32 LE total bytesでtagを長さに含む。通常tags [0,8,9,1,5,6]、optional tag4 inlineを先頭に置く場合あり。圧縮recordはcodec flag1、u32 decoded length、LZMA-alone stream。EOSがない場合も宣言長で停止する。

tag0 headerはsubZoom、flippedYOrigin、xOrigin、leafZoom、N。subZoom=z+4、leafZoom=z+7、xOrigin=16*x、flippedYOrigin=2^subZoom-16*(y+1)。N packed u32 indexesの局所XYは(value>>8)&15と(value>>20)&15。low bitsの階層意味は未確定。
