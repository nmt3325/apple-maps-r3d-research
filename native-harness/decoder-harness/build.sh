#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
SDK="$(xcrun --sdk iphonesimulator --show-sdk-path)"
OUT="./TestR3d.app"
mkdir -p "$OUT"
cp Info.plist "$OUT/Info.plist"
cp test-tile.r3d "$OUT/test-tile.r3d"
if [[ -f r3d_offset.txt ]]; then cp r3d_offset.txt "$OUT/r3d_offset.txt"; fi
xcrun clang++ -std=c++17 -arch arm64 -target arm64-apple-ios27.0-simulator -isysroot "$SDK" -fobjc-arc -fmodules \
 -framework Foundation -framework UIKit -framework MapKit -framework CoreGraphics \
 -Wno-deprecated-declarations main.mm -o "$OUT/R3dTester"
codesign --force --sign - --timestamp=none "$OUT"
echo "SIMULATOR APP BUILT: $(pwd)/TestR3d.app"
