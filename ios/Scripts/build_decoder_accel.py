"""Build the same array accelerator for host-side parity tests and benchmarks."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig


def build(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / ('_r3d_accel' + sysconfig.get_config_var('EXT_SUFFIX'))
    source = Path(__file__).resolve().parents[1] / 'App/NativeCodec.cpp'
    command = shlex.split(os.environ.get('CXX', 'c++')) + [
        '-std=c++17', '-O3', '-ffp-contract=off', '-DR3D_STANDALONE_PYTHON',
        '-I' + sysconfig.get_path('include'), '-shared', '-fPIC', str(source), '-o', str(output)]
    if sys.platform == 'darwin':
        command += ['-undefined', 'dynamic_lookup']
    subprocess.run(command, check=True)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    print(build(parser.parse_args().out))
