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

Add-Type -AssemblyName System.IO.Compression.FileSystem
$h = Hash (Join-Path $media "bytecode.byc")
$bakEd = BakEdition
if ($ORIG.ContainsKey($h)) {
  $ed = $ORIG[$h]
  if (-not $KR[$ed]) { Write-Host "이 패키지는 $($EDNAME[$ed])을 지원하지 않습니다."; exit 1 }
  Write-Host "[1/4] $($EDNAME[$ed]) 원본 파일 백업 중... (한글패치_원본백업 폴더)"
  if (Test-Path -LiteralPath $bak) { Remove-Item -LiteralPath $bak -Recurse -Force }
  New-Item -ItemType Directory -Path $bak | Out-Null
  $newFiles = @()
  foreach ($zn in @("AI_KR_common.zip", "AI_KR_$ed.zip")) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead((Join-Path $here $zn))
    foreach ($e in $zip.Entries) {
      if ($e.FullName.EndsWith("/")) { continue }
      $rel = $e.FullName -replace "/", "\"
      $src = Join-Path $game $rel
      $dst = Join-Path $bak $rel
      if (Test-Path -LiteralPath $dst) { continue }
      if (Test-Path -LiteralPath $src) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $dst) -Force | Out-Null
        Copy-Item -LiteralPath $src -Destination $dst -Force
      } else { $newFiles += $rel }
    }
    $zip.Dispose()
  }
  Set-Content -LiteralPath (Join-Path $bak "new_files.txt") -Value $newFiles -Encoding UTF8
} elseif (($KNOWN -contains $h) -and $bakEd) {
  $ed = $bakEd
  Write-Host "[1/4] 이전 한글패치를 백업 원본($($EDNAME[$ed]))으로 되돌리는 중..."
  Copy-Item -Path (Join-Path $bak "media") -Destination $game -Recurse -Force
  if (-not $ORIG.ContainsKey((Hash (Join-Path $media "bytecode.byc")))) { Write-Host "원본 복구에 실패했습니다."; exit 1 }
} elseif ($KNOWN -contains $h) {
  Write-Host "한글패치가 설치되어 있지만 원본 백업이 없습니다. 스팀에서 '게임 파일 무결성 확인' 후 다시 설치해 주세요."; exit 1
} else {
  Write-Host ""
  Write-Host "이 게임 버전은 한글패치가 만들어진 버전과 다릅니다. (게임 업데이트, 다른 패치 등)"
  Write-Host "패치를 설치하지 않고 멈춥니다. 스팀에서 '게임 파일 무결성 확인'을 해도 같다면, 새 버전용 패치를 기다려 주세요."
  exit 1
}
Write-Host "[2/4] 한글 파일 설치 중... ($($EDNAME[$ed]))"
Expand-Archive -Path (Join-Path $here "AI_KR_common.zip") -DestinationPath $game -Force
Expand-Archive -Path (Join-Path $here "AI_KR_$ed.zip") -DestinationPath $game -Force
Write-Host "[3/4] 한글 이름 그림 사본 만드는 중..."
$ok = 0; $miss = 0
Get-Content -LiteralPath (Join-Path $here "image_copies.tsv") -Encoding UTF8 | ForEach-Object {
  $p = $_.Trim([char]0xFEFF).Split("`t")
  if ($p.Length -eq 2) {
    $src = Join-Path $media $p[0]; $dst = Join-Path $media $p[1]
    if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $dst -Force; $ok++ } else { $miss++ }
  }
}
Write-Host "그림 사본 $ok 개 완료 (원본 없음 $miss 개)"
Write-Host "[4/4] 필요 없는 그림 정리 중..."
Get-Content -LiteralPath (Join-Path $here "image_delete.txt") -Encoding UTF8 | ForEach-Object {
  $f = $_.Trim([char]0xFEFF).Trim()
  if ($f) { $t = Join-Path $media $f; if (Test-Path -LiteralPath $t) { Remove-Item -LiteralPath $t -Force } }
}
if ((Hash (Join-Path $media "bytecode.byc")) -ne $KR[$ed]) { Write-Host "설치 확인 실패: bytecode.byc 가 예상과 다릅니다."; exit 1 }
Write-Host ""
Write-Host "설치 끝 ($($EDNAME[$ed])). 게임을 실행해 보세요."
