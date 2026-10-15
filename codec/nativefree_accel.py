"""Optional compiled array loops, sharing the independent Python format parser."""
import os

try:
    if os.environ.get('R3D_DISABLE_ACCEL') == '1':
        raise ImportError
    import _r3d_accel as accelerator
except ImportError:
    accelerator = None
