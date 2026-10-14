# Runtime notices

The app embeds CPython 3.13 and the BeeWare Python Apple Support build.
Their license texts are included here and copied into the app bundle.
Python's bundled standard library also contains its own license.

The support archive is pinned to release `3.13-b13`, SHA-256
`d1f95f95137a4b91dc0cbe9b99ddfc0a78918dde883c7fbe7147074a5e715274`.
Source and build metadata: https://github.com/beeware/Python-Apple-support/tree/3.13.

The default service profile uses the published shared signing constants from
SynArchive/Apple-3D-RE-Lightweight, commit
`df3e354d1c0f2dc7a35ecb425b0f49973b7d46ee`, `main.go`.
Its MIT license is included in `Apple-3D-RE-Lightweight-LICENSE.txt`.
The reference source SHA-256 is
`e6104f3beef83ca2f15e6afbfa5ee6a1478b53e83e912b2f8207c5a2811f0398`.

This notice does not apply a new license to the repository's researched code
or Apple-derived map data. See `../../docs/PROVENANCE.md` for their provenance.
