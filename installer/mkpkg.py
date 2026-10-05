"""Generate install/restore scripts supporting full + demo editions.
usage: python3 demo/mkpkg.py OUTDIR KR_FULL_HASH [KR_DEMO_HASH]"""
import sys, os, re
out, KR_FULL = sys.argv[1], sys.argv[2]
KR_DEMO = sys.argv[3] if len(sys.argv) > 3 else ''
ORIG_FULL = '16c66c175341f885e56646fba93449f516d4ae11d975efacd5b0d4d00968a729'
ORIG_DEMO = '7ee7d84b7ba00d8fb2baea5749acc6f902adda4c671e6cb142b81f320fd3ee41'
KNOWN = ['de52bd8d31184fe6af3fda05da1370d0484fcffa01da4fb6eec41ac7a9634f12',   # v1.0 full
         '4e7653033d50b9767938b95697c874548feea1b326267ccea7b15271ada7de98',   # v1.0 sound-diag full
         'cf3c71977d4cdfaed689a011081a65276aad7f0acf1de3e76414b20d60d3359c']   # v1.1 demo
for h in (KR_FULL, KR_DEMO):
    if h and h not in KNOWN: KNOWN.append(h)

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install.ps1'), 'rb').read().decode('utf-8-sig')
a = src.index('function Test-Game')
b = src.index('$game = Find-Game')
finder = src[a:b]

head = '''$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ORIG = @{ "%s" = "full"; "%s" = "demo" }
$KR = @{ "full" = "%s"; "demo" = "%s" }
$KNOWN = @(%s)
$EDNAME = @{ "full" = "정식판"; "demo" = "데모판" }
''' % (ORIG_FULL, ORIG_DEMO, KR_FULL, KR_DEMO, ', '.join('"%s"' % h for h in KNOWN))
common_tail = '''$game = Find-Game
$media = Join-Path $game "media"
$bak = Join-Path $game "한글패치_원본백업"
Write-Host "게임 폴더: $game"
function BakEdition { $f = Join-Path $bak "media\\bytecode.byc"; if (Test-Path -LiteralPath $f) { $h = Hash $f; if ($ORIG.ContainsKey($h)) { return $ORIG[$h] } }; return $null }
'''

install = head + finder + common_tail + r'''
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
  if ((Hash (Join-Path $media "bytecode.byc")) -ne $KR.Keys.ForEach({$_}) -and -not $ORIG.ContainsKey((Hash (Join-Path $media "bytecode.byc")))) { Write-Host "원본 복구에 실패했습니다."; exit 1 }
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
'''
# simplify the post-restore check line (PowerShell): after restoring backup, bytecode must be an original
install = install.replace(
    '''  if ((Hash (Join-Path $media "bytecode.byc")) -ne $KR.Keys.ForEach({$_}) -and -not $ORIG.ContainsKey((Hash (Join-Path $media "bytecode.byc")))) { Write-Host "원본 복구에 실패했습니다."; exit 1 }''',
    '''  if (-not $ORIG.ContainsKey((Hash (Join-Path $media "bytecode.byc")))) { Write-Host "원본 복구에 실패했습니다."; exit 1 }''')

restore = head + finder + common_tail + r'''
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
'''
os.makedirs(out, exist_ok=True)
for n, s in (('install.ps1', install), ('restore.ps1', restore)):
    open(os.path.join(out, n), 'wb').write(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))
print('ok', out)
