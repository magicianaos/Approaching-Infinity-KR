$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ORIG = @{ "16c66c175341f885e56646fba93449f516d4ae11d975efacd5b0d4d00968a729" = "full"; "7ee7d84b7ba00d8fb2baea5749acc6f902adda4c671e6cb142b81f320fd3ee41" = "demo" }
$KR = @{ "full" = "de52bd8d31184fe6af3fda05da1370d0484fcffa01da4fb6eec41ac7a9634f12"; "demo" = "cf3c71977d4cdfaed689a011081a65276aad7f0acf1de3e76414b20d60d3359c" }
$KNOWN = @("de52bd8d31184fe6af3fda05da1370d0484fcffa01da4fb6eec41ac7a9634f12", "4e7653033d50b9767938b95697c874548feea1b326267ccea7b15271ada7de98", "cf3c71977d4cdfaed689a011081a65276aad7f0acf1de3e76414b20d60d3359c")
$EDNAME = @{ "full" = "정식판"; "demo" = "데모판" }
function Test-Game($p) { return ($p -and (Test-Path -LiteralPath (Join-Path $p "media\bytecode.byc")) -and (Test-Path -LiteralPath (Join-Path $p "media\Text"))) }
function Find-Game {
  $p = $here
  for ($i = 0; $i -lt 4; $i++) { if (Test-Game $p) { return $p }; $p = Split-Path -Parent $p; if (-not $p) { break } }
  $roots = @()
  foreach ($k in @("HKCU:\Software\Valve\Steam", "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam", "HKLM:\SOFTWARE\Valve\Steam")) {
    try { $v = Get-ItemProperty -Path $k -ErrorAction Stop; if ($v.SteamPath) { $roots += $v.SteamPath }; if ($v.InstallPath) { $roots += $v.InstallPath } } catch {}
  }
  $roots += "C:\Program Files (x86)\Steam"
  $libs = @()
  foreach ($r in $roots) {
    $r = $r -replace "/", "\"
    $libs += $r
    $vdf = Join-Path $r "steamapps\libraryfolders.vdf"
    if (Test-Path -LiteralPath $vdf) {
      foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) { $libs += ($m.Groups[1].Value -replace "\\\\", "\") }
    }
  }
  foreach ($l in ($libs | Select-Object -Unique)) { $g = Join-Path $l "steamapps\common\Approaching Infinity"; if (Test-Game $g) { return $g } }
  Write-Host "게임 폴더를 자동으로 찾지 못했습니다."
  $g = Read-Host "Approaching Infinity 설치 폴더 경로를 붙여 넣고 Enter (예: D:\SteamLibrary\steamapps\common\Approaching Infinity)"
  $g = $g.Trim('"', ' ')
  if (Test-Game $g) { return $g }
  Write-Host "그 폴더에서 media\bytecode.byc 를 찾지 못했습니다."; exit 1
}
function Hash($f) { return (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLower() }
$game = Find-Game
$media = Join-Path $game "media"
$bak = Join-Path $game "한글패치_원본백업"
Write-Host "게임 폴더: $game"
function BakEdition { $f = Join-Path $bak "media\bytecode.byc"; if (Test-Path -LiteralPath $f) { $h = Hash $f; if ($ORIG.ContainsKey($h)) { return $ORIG[$h] } }; return $null }

if (-not (BakEdition)) { Write-Host "원본 백업(한글패치_원본백업)이 없습니다. 스팀에서 '게임 파일 무결성 확인'으로 복구해 주세요."; exit 1 }
$h = Hash (Join-Path $media "bytecode.byc")
if ($ORIG.ContainsKey($h)) { Write-Host "이미 원본(영어) 상태입니다."; exit 0 }
if (-not ($KNOWN -contains $h)) { Write-Host "지금 게임 파일이 한글패치 버전이 아닙니다. (게임 업데이트, 데모판/정식판 전환 등)"; Write-Host "예전 백업을 덮어쓰면 게임이 망가질 수 있어 멈춥니다. 스팀에서 '게임 파일 무결성 확인'을 해 주세요."; exit 1 }
Write-Host "[1/2] 원본 파일 되돌리는 중..."
Copy-Item -Path (Join-Path $bak "media") -Destination $game -Recurse -Force
$nf = Join-Path $bak "new_files.txt"
if (Test-Path -LiteralPath $nf) {
  Get-Content -LiteralPath $nf -Encoding UTF8 | ForEach-Object { $f = $_.Trim([char]0xFEFF).Trim(); if ($f) { $t = Join-Path $game $f; if (Test-Path -LiteralPath $t) { Remove-Item -LiteralPath $t -Force } } }
}
Write-Host "[2/2] 한글 이름 그림 사본 지우는 중..."
$n = 0
Get-Content -LiteralPath (Join-Path $here "image_copies.tsv") -Encoding UTF8 | ForEach-Object {
  $p = $_.Trim([char]0xFEFF).Split("`t")
  if ($p.Length -eq 2) { $dst = Join-Path $media $p[1]; if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force; $n++ } }
}
Write-Host "그림 사본 $n 개 삭제"
if ($ORIG.ContainsKey((Hash (Join-Path $media "bytecode.byc")))) { Write-Host "원본 복구 끝. 영어 원본 상태입니다." } else { Write-Host "주의: bytecode.byc 가 원본과 다릅니다. 스팀에서 '게임 파일 무결성 확인'을 해 주세요." }
