# 検証した形式

独立した全数値復号の現在の仕様・配列検証は[INDEPENDENT_DECODER.md](INDEPENDENT_DECODER.md)。以下の以前の未解決事項はBYET/JとTRICO v3の実装で解決済み。

## R3D v2 / TRICO / BYET

- R3D magic: 3d 96 59 2e、u32 LE version2、bytes8..10は01 02 00。byte11からULEB tag,lengthのTLV。
- 外側tags [1,2,3]。Splat group内[1,1,4,2,3]、mesh group内[1,1,2,3]。
- TRICO soup: d1 22 c9 07、version1、+8 u64 record count、+16 u32 channels8、+20 float32 scale9個。
- TRICO mesh: e1 21 66 24、version3、+8 float32 scale3個。CLERS topology・整数XYZ予測・UV seam・spherical法線はnativefree_mesh.pyで復号する。
- soup +56から2つのcompact-length BYET block。XYZと8属性。BYETは25 00、compact origin byte length、origin、80＋u16 marker004a、J payload。
- compact sizeはULEBとは別物。先頭byteの下位1連続数でLE byte幅を決め、幅分右shift。ffの場合は続く8byteをLE整数として読む。
- originは12byteなら3 signed int32。mode08はbyte遷移bitmapによる前byteの繰り返し、mode04は前byteをキーにした256-entry予測表。int32境界で状態をリセットしない。
- Jは12 XYZ byte lanes /32 attribute byte lanes。bitmap A、active countに基づく2bit token bitmap B、種類/圧縮長directory、lane payloadの順。
- kind0はraw、kind1はbyte遷移、kind2はbyte予測表、kind3は符号付きdelta、kind4は16-bit遷移、kind5は16-bit予測表、kind6は16-bit符号付きdelta。kind4/6は直前laneとのpairを宣言する。bit/sign predictorの意味は実装と全配列比較で確認済み。

## HUFF

0x61000002のtable/payloadはLE u32 wordをMSB-firstに読み、表の後でword境界へ揃える。0xe1000002はliteral dispatch。0x24にはsingle streamとentropyを複数段で圧縮するchainがある。chain中間段はHuff16でも8-bit復号。出力symbol数はBYET各lane内のcompact整数から得る。`nativefree_huff_aligned.py`と`nativefree_bytes.py`が現在の数値decoder。以前の非aligned/推定count実装は探索用として残す。

## 既存native golden

- *.decoded: u32 LE header4個 magic31443352、N、8、reserved。続けてN*3 float32 XYZ、その後N*8 float32 attributes。全長16+44*N。
- .decodedのXYZは元の3*N頂点配列の先頭N頂点だけ。各Splatの中心座標ではなく、完全な位置配列でもない。
- *.native-triangle-f32: N*3*3 float32、36*N byte。
- *.native-material20: N*20 byte、先頭4byte RGBA、後続16byteは4 float32 properties。
- C3M native arraysは位置/UV/法線とそれぞれのtriangle indexを分離している。
- viewerのC3M geometry: 16byte header、12*N XYZ、8*N UV、12*N normals、12*F triangle indices。

## C3MM v2

C3MM＋u16 version2＋u16 subtype3＋u32 section count6/7。各recordはu8 tagとu32 LE total bytesでtagを長さに含む。通常tags [0,8,9,1,5,6]、optional tag4 inlineを先頭に置く場合あり。圧縮recordはcodec flag1、u32 decoded length、LZMA-alone stream。EOSがない場合も宣言長で停止する。

tag0 headerはsubZoom、flippedYOrigin、xOrigin、leafZoom、N。subZoom=z+4、leafZoom=z+7、xOrigin=16*x、flippedYOrigin=2^subZoom-16*(y+1)。N packed u32 indexesの局所XYは(value>>8)&15と(value>>20)&15。low bitsの階層意味は未確定。

高さ層の取得ではtag0の占有セルを保守的に全高さの子へ展開する。h0固定要求は地域上部を欠く。Splat-only上層の空mesh/textureなしの検証も含め、現行の取得・復号仕様は[HEIGHT_LAYERS.md](HEIGHT_LAYERS.md)。
