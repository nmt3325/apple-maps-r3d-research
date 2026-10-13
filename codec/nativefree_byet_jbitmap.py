#!/usr/bin/env python3
"""Legacy exploratory module name. Correct J bitmap schema is per-byte-lane
(12 XYZ / 32 attributes), not per point. See nativefree_byet_jdescriptor.py.
"""
from nativefree_byet_jdescriptor import split_j

if __name__ == "__main__":
    raise SystemExit("Replaced by nativefree_byet_jdescriptor.py: use that script.")
