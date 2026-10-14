#!/bin/bash
set -euo pipefail
cd "$PROJECT_DIR"
source Vendor/Python.xcframework/build/utils.sh
export EXPANDED_CODE_SIGN_IDENTITY="${EXPANDED_CODE_SIGN_IDENTITY:--}"
export EXPANDED_CODE_SIGN_IDENTITY_NAME="${EXPANDED_CODE_SIGN_IDENTITY_NAME:-Ad Hoc}"
export PLATFORM_FAMILY_NAME="${PLATFORM_FAMILY_NAME:-iOS}"
mkdir -p "$CODESIGNING_FOLDER_PATH/app"
rsync -a --delete Python/ "$CODESIGNING_FOLDER_PATH/app/" --exclude '__pycache__'
rsync -a ../codec/ "$CODESIGNING_FOLDER_PATH/app/" --exclude '__pycache__'
install_python Vendor/Python.xcframework app
mkdir -p "$CODESIGNING_FOLDER_PATH/ThirdParty"
rsync -a ThirdParty/ "$CODESIGNING_FOLDER_PATH/ThirdParty/"
# Local configuration is never part of the tracked source or release ZIP.
if [[ -n "${R3D_FETCH_CONFIG:-}" && -f "$R3D_FETCH_CONFIG" ]]; then
    cp "$R3D_FETCH_CONFIG" "$CODESIGNING_FOLDER_PATH/maps.credentials.json"
else
    rm -f "$CODESIGNING_FOLDER_PATH/maps.credentials.json"
fi
