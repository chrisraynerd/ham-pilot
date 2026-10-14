param(
    [Parameter(Mandatory=$true)][string]$Port,
    [ValidateSet(115200,460800,921600)][int]$Baud = 460800,
    [string]$Python = 'py',
    [string]$EsptoolPath = '',
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
$firmwareFiles = @('bootloader.bin','partitions.bin','boot_app0.bin','ham-pilot.bin')
$expectedHashes = @{}
foreach ($line in Get-Content -LiteralPath (Join-Path $PSScriptRoot 'SHA256SUMS')) {
    if ($line -match '^([0-9a-fA-F]{64})  ([a-z0-9_.-]+)$') { $expectedHashes[$Matches[2]]=$Matches[1] }
    elseif ($line.Trim()) { throw 'Malformed SHA256SUMS file.' }
}
foreach ($name in $firmwareFiles) {
    $path = Join-Path $PSScriptRoot $name
    if (-not (Test-Path -LiteralPath $path) -or -not $expectedHashes.ContainsKey($name)) { throw "Missing firmware or checksum: $name" }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $expectedHashes[$name]) { throw "Checksum failed: $name" }
}
Write-Output 'All four firmware checksums verified.'
if ($VerifyOnly) { return }
$flashArguments = @('--chip','esp32','--port',$Port,'--baud',[string]$Baud,'--before','default-reset','--after','hard-reset',
    'write-flash','--flash-mode','dio','--flash-freq','80m','--flash-size','4MB',
    '0x1000',(Join-Path $PSScriptRoot 'bootloader.bin'),'0x8000',(Join-Path $PSScriptRoot 'partitions.bin'),
    '0xe000',(Join-Path $PSScriptRoot 'boot_app0.bin'),'0x10000',(Join-Path $PSScriptRoot 'ham-pilot.bin'))
if ($EsptoolPath) { & $EsptoolPath @flashArguments }
else { & $Python -m esptool @flashArguments }
if ($LASTEXITCODE -ne 0) { throw 'Firmware upload failed.' }
Write-Output 'Ham Pilot installed. Existing Ham Pilot settings were not erased.'
