# R3D codec research checkpoint — 2026-10-14

New static audit: arm64_count_tail.py and arm64-count-tail-audit.json.

Four instruction windows were checked independently against captured data: 25/25 checks passed. 1024/1024 synthetic arithmetic vectors agree. The seven-byte tail has the form little_endian_u56(fragment) shifted left eight bits. The low-fragment source and per-lane output counts remain unresolved.

Python module execution was blocked; no Python test pass is claimed. No new numeric Splat or mesh parity. Existing viewer, source data, goldens, and downloader unchanged.

Next: trace low-fragment provenance and caller output counts, then decode lane transforms and validate Tokyo golden numbers before Oahu and viewer integration.

Completion criteria not met; continue later.
