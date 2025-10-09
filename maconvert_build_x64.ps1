# Declaration of variables
$projectPath = "C:\maconvert"
$specFile = Join-Path $projectPath "maconvert.spec"
$dllTargetDir = Join-Path $projectPath "dlls"

# Install Python
Write-Host "Downloading Python..."
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
Write-Host "Installing Python..."
Start-Process "$env:TEMP\python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

# Add Python Scripts to PATH
$env:Path += ";C:\Program Files\Python311\Scripts"

# Update python pip
Write-Host "Updating Python pip..."
python.exe -m pip install --upgrade pip

# Install Git
Write-Host "Downloading Git..."
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe" -OutFile "$env:TEMP\git-installer.exe"
Write-Host "Installing Git..."
Start-Process "$env:TEMP\git-installer.exe" -ArgumentList "/VERYSILENT" -Wait

# Add Git to PATH (if needed)
$env:Path += ";C:\Program Files\Git\bin"

# Install Python modules
Write-Host "Installing additional Python modules...(1/4)"
pip install setuptools wheel
Write-Host "Installing additional Python modules...(2/4)"
pip install pyinstaller

Write-Host "Downloading VC++ Redistributable..."
# Download the latest VC++ Redistributable (Visual Studio 2015-2022)
$vcUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
$vcInstaller = "$env:TEMP\vc_redist.x64.exe"
Invoke-WebRequest -Uri $vcUrl -OutFile $vcInstaller

Write-Host "Starting silent installation of VC++ Redistributable..."
Start-Process -FilePath $vcInstaller -ArgumentList "/install", "/quiet", "/norestart" -Wait

# Clone the Git repository
Write-Host "Cloning Git repository maconvert..."
git.exe clone https://github.com/skruszka/maconvert.git C:\maconvert

# Create DLL target folder
Write-Host "Create DLL target folder..."
if (!(Test-Path $dllTargetDir)) {
    New-Item -ItemType Directory -Path $dllTargetDir | Out-Null
}

# Navigate to the project directory
Set-Location $projectPath

# Install dependencies
Write-Host "Installing additional Python modules...(3/4)"
pip install -r requirements.txt
Write-Host "Installing additional Python modules...(4/4)"
pip install pyinstaller

# Create a new .spec file
Write-Host "Create a new .spec file..."
$specContent = @"
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('wx')

a = Analysis(
    ['maconvert.pyw'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='maconvert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='maconvert'
)
"@

# Save the .spec file
$specContent | Set-Content ".\maconvert.spec" -Encoding UTF8

# Search for VC++ DLLs and add them
Write-Host "Locate VC++ DLLs..."
$dllTargetDir = Join-Path $projectPath "dlls"
if (!(Test-Path $dllTargetDir)) { New-Item -ItemType Directory -Path $dllTargetDir | Out-Null }
$dllNames = @("MSVCP140.dll", "VCRUNTIME140.dll", "VCRUNTIME140_1.dll")
Write-Host "Copy VC++ DLLs to target folder..."
foreach ($dll in $dllNames) {
    $dllPath = Get-ChildItem -Path "C:\Windows\System32" -Filter $dll -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($dllPath) {
        Copy-Item $dllPath.FullName -Destination $dllTargetDir -Force
    }
}

# Add DLLs to the spec file
Write-Host "Add VC++ DLLs to .spec file..."
$dllEntries = $dllNames | ForEach-Object { "    (r'$dllTargetDir\$_', '.')," }
Add-Content $specFile "`r`n# Additional DLLs"
Add-Content $specFile "binaries += ["
$dllEntries | ForEach-Object { Add-Content $specFile $_ }
Add-Content $specFile "]"


# Build the EXE
Write-Host "Building the EXE with PyInstaller..."
pyinstaller maconvert.spec --clean

Write-Host "Installation and build completed successfully."

