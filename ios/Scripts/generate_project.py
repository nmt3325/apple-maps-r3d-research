"""Generate a dependency-free Xcode project; checked-in result opens directly."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
objects = {}
def ident(value): return hashlib.sha1(value.encode()).hexdigest()[:24].upper()
def quote(value): return json.dumps(str(value))
def add(name, body):
    key = ident(name)
    objects[key] = body
    return key
def array(values): return '(' + ','.join(values) + ',)'

sources, references = [], []
for path in sorted((ROOT/'App').iterdir()):
    kind = {'.swift':'sourcecode.swift','.m':'sourcecode.c.objc','.cpp':'sourcecode.cpp.cpp','.h':'sourcecode.c.h',
            '.metal':'sourcecode.metal','.plist':'text.plist.xml'}.get(path.suffix)
    if not kind: continue
    ref = add(str(path.relative_to(ROOT)), f'isa = PBXFileReference; lastKnownFileType = {kind}; path = {quote(path.relative_to(ROOT))}; sourceTree = "<group>";')
    references.append(ref)
    if path.suffix in ('.swift','.m','.cpp','.metal'):
        flags = ' settings = { COMPILER_FLAGS = "-std=c++17 -O3 -ffp-contract=off"; };' if path.suffix == '.cpp' else ''
        sources.append(add('build:'+path.name, f'isa = PBXBuildFile; fileRef = {ref};{flags}'))
xc = add('python', 'isa = PBXFileReference; lastKnownFileType = wrapper.xcframework; path = Vendor/Python.xcframework; sourceTree = "<group>";')
cfg = add('config', 'isa = PBXFileReference; lastKnownFileType = text.xcconfig; path = Build.xcconfig; sourceTree = "<group>";')
link = add('link-python', f'isa = PBXBuildFile; fileRef = {xc};')
embed = add('embed-python', f'isa = PBXBuildFile; fileRef = {xc}; settings = {{ ATTRIBUTES = (CodeSignOnCopy,RemoveHeadersOnCopy,); }};')
product = add('product', 'isa = PBXFileReference; explicitFileType = wrapper.application; path = R3DExplorer.app; sourceTree = BUILT_PRODUCTS_DIR;')
products = add('products', f'isa = PBXGroup; name = Products; children = {array([product])}; sourceTree = "<group>";')
main = add('main', f'isa = PBXGroup; children = {array(references+[xc,cfg,products])}; sourceTree = "<group>";')
sourcephase = add('sources', f'isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = {array(sources)}; runOnlyForDeploymentPostprocessing = 0;')
frameworkphase = add('frameworks', f'isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = {array([link])}; runOnlyForDeploymentPostprocessing = 0;')
resources = add('resources', 'isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0;')
script = add('runtime', 'isa = PBXShellScriptBuildPhase; alwaysOutOfDate = 1; buildActionMask = 2147483647; files = (); inputPaths = (); outputPaths = (); name = "Install embedded decoder"; shellPath = /bin/bash; shellScript = ' + quote('bash "$PROJECT_DIR/Scripts/install_runtime.sh"') + '; runOnlyForDeploymentPostprocessing = 0;')
copyphase = add('embed', f'isa = PBXCopyFilesBuildPhase; buildActionMask = 2147483647; dstPath = ""; dstSubfolderSpec = 10; files = {array([embed])}; name = "Embed Frameworks"; runOnlyForDeploymentPostprocessing = 0;')
def configurations(name, is_target):
    configs=[]
    for mode in ['Debug','Release']:
        settings = 'CLANG_ENABLE_MODULES = YES; CLANG_ENABLE_OBJC_ARC = YES; ENABLE_TESTABILITY = YES;'
        if mode == 'Debug': settings += ' SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG; GCC_PREPROCESSOR_DEFINITIONS = ("$(inherited)","DEBUG=1",);'
        c = add(name+mode, f'isa = XCBuildConfiguration; baseConfigurationReference = {cfg}; buildSettings = {{ {settings} }}; name = {mode};')
        configs.append(c)
    return add(name+'configs', f'isa = XCConfigurationList; buildConfigurations = {array(configs)}; defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;')
targetconfigs = configurations('target',True)
projectconfigs = configurations('project',False)
target = add('target', f'isa = PBXNativeTarget; buildConfigurationList = {targetconfigs}; buildPhases = {array([sourcephase,frameworkphase,resources,script,copyphase])}; buildRules = (); dependencies = (); name = R3DExplorer; productName = R3DExplorer; productReference = {product}; productType = "com.apple.product-type.application";')
project = add('project', f'isa = PBXProject; attributes = {{ LastUpgradeCheck = 2700; }}; buildConfigurationList = {projectconfigs}; compatibilityVersion = "Xcode 14.0"; developmentRegion = ja; hasScannedForEncodings = 0; knownRegions = (ja,en,Base,); mainGroup = {main}; productRefGroup = {products}; projectDirPath = ""; projectRoot = ""; targets = {array([target])};')
directory = ROOT/'R3DExplorer.xcodeproj'
directory.mkdir(exist_ok=True)
pbx = '// !$*UTF8*$!\n{ archiveVersion = 1; classes = {}; objectVersion = 56; objects = {\n'
pbx += '\n'.join(f'{key} = {{ {value} }};' for key,value in objects.items())
pbx += f'\n}}; rootObject = {project}; }}\n'
(directory/'project.pbxproj').write_text(pbx)
scheme = directory/'xcshareddata/xcschemes'
scheme.mkdir(parents=True,exist_ok=True)
(scheme/'R3DExplorer.xcscheme').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="2700" version="1.3">
<BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="R3DExplorer.app" BlueprintName="R3DExplorer" ReferencedContainer="container:R3DExplorer.xcodeproj"/></BuildActionEntry></BuildActionEntries></BuildAction>
<LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="R3DExplorer.app" BlueprintName="R3DExplorer" ReferencedContainer="container:R3DExplorer.xcodeproj"/></BuildableProductRunnable></LaunchAction>
<ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"/>
<AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>''')
print(directory)
