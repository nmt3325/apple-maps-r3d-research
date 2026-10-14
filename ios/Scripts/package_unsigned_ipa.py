"""Package the complete device app for the user's signing/install workflow."""
from pathlib import Path
import argparse
import plistlib
import shutil
import subprocess
import tempfile
import zipfile


def package(source, output):
    if not source.is_dir() or source.suffix != '.app':
        raise ValueError('Require an existing device .app bundle')
    info = plistlib.loads((source/'Info.plist').read_bytes())
    executable = info['CFBundleExecutable']
    if not (source/executable).is_file() or info.get('DTPlatformName') != 'iphoneos':
        raise ValueError('Require an iPhone device executable')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r3d-ipa-') as directory:
        root = Path(directory)
        app = root/'Payload'/source.name
        shutil.copytree(source,app,symlinks=True)
        for bundle in list((app/'Frameworks').glob('*.framework'))+[app]:
            status = subprocess.run(['codesign','-d',str(bundle)],capture_output=True)
            if status.returncode == 0:
                subprocess.run(['codesign','--remove-signature',str(bundle)],check=True,capture_output=True)
        for signature in app.rglob('_CodeSignature'):
            if signature.is_dir(): shutil.rmtree(signature)
        (app/'embedded.mobileprovision').unlink(missing_ok=True)
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(root.rglob('*')):
                if file.is_file(): archive.write(file,str(file.relative_to(root)))
    with zipfile.ZipFile(output) as archive:
        prefix = 'Payload/'+source.name+'/'
        required = [prefix+'Info.plist',prefix+executable,prefix+'default.metallib',
                    prefix+'Frameworks/Python.framework/Python',prefix+'app/r3d_mobile.py']
        if any(path not in archive.namelist() for path in required):
            raise ValueError('IPA is missing runtime resources')
        if archive.testzip() is not None:
            raise ValueError('IPA archive integrity failure')
        if any('/_CodeSignature/' in path for path in archive.namelist()):
            raise ValueError('Expected an unsigned IPA')
    print(f'Unsigned IPA verified: {output} ({output.stat().st_size} bytes)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('app',type=Path)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    package(args.app,args.output)
