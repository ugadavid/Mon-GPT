[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InnoCompiler,
    [string]$PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-BuildTool([string]$Executable,[string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Échec de $Executable (code $LASTEXITCODE)." }
}
function Remove-BuildTree([string]$Path,[string]$Parent) {
    $absolute = [IO.Path]::GetFullPath($Path)
    $prefix = [IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    if (-not $absolute.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Chemin hors build : $absolute" }
    if (Test-Path -LiteralPath $absolute) { Remove-Item -LiteralPath $absolute -Recurse -Force }
}

$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$PythonExe = (Resolve-Path -LiteralPath $PythonExe).Path
$InnoCompiler = (Resolve-Path -LiteralPath $InnoCompiler).Path
$runtime = Invoke-BuildTool $PythonExe @('-I','-c',"import platform,struct,sys; print(platform.system(),platform.machine(),struct.calcsize('P')*8,platform.python_version())")
if ($runtime -ne 'Windows AMD64 64 3.13.17') { throw "CPython 3.13.17 Windows x64 requis ; trouvé : $runtime" }
$compilerVersion = Invoke-BuildTool $InnoCompiler @('--version')
if ($compilerVersion -ne '7.1.1') { throw "Inno Setup 7.1.1 requis ; trouvé : $compilerVersion" }
$version = Invoke-BuildTool $PythonExe @('-I','-c',"import runpy,sys; print(runpy.run_path(sys.argv[1])['__version__'])",(Join-Path $root 'mon_gpt/__init__.py'))
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw "Version invalide : $version" }
$windowsVersion = "$version.0"
$workRoot = Join-Path $root 'build/windows'
$work = Join-Path $workRoot ([guid]::NewGuid().ToString('N'))
$output = Join-Path $root "dist/windows/$version"
$previousCache = $env:PYINSTALLER_CONFIG_DIR
try {
    New-Item -ItemType Directory -Path $work -Force | Out-Null
    $venv = Join-Path $work 'venv'
    Invoke-BuildTool $PythonExe @('-I','-m','venv',$venv)
    $buildPython = Join-Path $venv 'Scripts/python.exe'
    Invoke-BuildTool $buildPython @('-I','-m','pip','--disable-pip-version-check','install','--only-binary=:all:','--no-deps','-r',(Join-Path $PSScriptRoot 'requirements-build.txt'))
    Invoke-BuildTool $buildPython @('-I','-m','pip','check')
    # Le gel ne doit pas embarquer un Pillow différent de l'application.
    Invoke-BuildTool $buildPython @('-I','-c',"import PIL,sys; from pathlib import Path; assert Path(sys.argv[1]).read_text().strip() == 'Pillow=='+PIL.__version__",(Join-Path $root 'requirements.txt'))
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $work 'cache'
    $stage = Join-Path $work 'output'
    Invoke-BuildTool $buildPython @('-I','-m','PyInstaller','--clean','--noconfirm','--distpath',$stage,'--workpath',(Join-Path $work 'pyinstaller'),(Join-Path $PSScriptRoot 'Mon-GPT.spec'))
    $application = Join-Path $stage 'Mon-GPT'
    Invoke-BuildTool $InnoCompiler @("/DProductVersion=$version","/DWindowsVersion=$windowsVersion","/DSourceDir=$application","/DOutputDir=$stage","/DIconFile=$(Join-Path $root 'missions/MG-015-exe/Mon-GPT-robot.ico')",(Join-Path $PSScriptRoot 'setup.iss'))
    $zip = Join-Path $stage "Mon-GPT-$version-windows-x64.zip"
    $setup = Join-Path $stage "Mon-GPT-$version-windows-x64-setup.exe"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::CreateFromDirectory($application,$zip,[IO.Compression.CompressionLevel]::Optimal,$true)
    Invoke-BuildTool $buildPython @('-I',(Join-Path $PSScriptRoot 'verify_bundle.py'),$application,$setup,$zip)
    $hashes = foreach ($asset in @($zip,$setup)) { "{0}  {1}" -f (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash.ToLowerInvariant(),[IO.Path]::GetFileName($asset) }
    Set-Content -LiteralPath (Join-Path $stage 'SHA256SUMS.txt') -Value $hashes -Encoding ASCII
    New-Item -ItemType Directory -Path $output -Force | Out-Null
    Remove-BuildTree (Join-Path $output 'Mon-GPT') $output
    foreach ($asset in @($application,$zip,$setup,(Join-Path $stage 'SHA256SUMS.txt'),(Join-Path $stage 'verification.json'))) {
        Move-Item -LiteralPath $asset -Destination (Join-Path $output ([IO.Path]::GetFileName($asset))) -Force
    }
    Get-ChildItem -LiteralPath $output | Select-Object Name,Length
}
finally {
    $env:PYINSTALLER_CONFIG_DIR = $previousCache
    Remove-BuildTree $work $workRoot
}
