#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -d Vendor/Python.xcframework ]]; then
    mkdir -p Vendor
    archive="Vendor/python-ios.tar.gz"
    curl -fL --retry 2 'https://github.com/beeware/Python-Apple-support/releases/download/3.13-b13/Python-3.13-iOS-support.b13.tar.gz' -o "$archive"
    echo 'd1f95f95137a4b91dc0cbe9b99ddfc0a78918dde883c7fbe7147074a5e715274  Vendor/python-ios.tar.gz' | shasum -a 256 -c -
    tar -xzf "$archive" -C Vendor
    rm "$archive"
fi
python3 Scripts/generate_project.py
