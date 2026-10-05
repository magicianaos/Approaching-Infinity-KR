"""어프로칭 인피니티 한글패치 — 배포판 빌드 스크립트

사용법 (저장소 맨 위 폴더에서):
    python make_release.py v1.1.1

미리 준비할 것 (게임 원본 파일은 저장소에 없음, README 참고):
    game/full/bytecode.byc      ← 정식판  media/bytecode.byc
    game/full/Text/             ← 정식판  media/Text 폴더 통째로
    game/demo/bytecode.byc      ← (선택) 데모판 media/bytecode.byc

결과:
    out/release/AI_한글패치_<버전>.zip
"""
import os, sys, shutil, subprocess, zipfile, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'out')
VER = sys.argv[1] if len(sys.argv) > 1 else 'dev'
PY = sys.executable


def run(args, cwd=ROOT, release=True):
    env = dict(os.environ)
    if release: env['RELEASE'] = '1'
    print('>>', ' '.join(args))
    subprocess.run(args, cwd=cwd, env=env, check=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def zipdir(base, out, include=lambda rel: True):
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(base):
            for f in sorted(fs):
                p = os.path.join(r, f); rel = os.path.relpath(p, os.path.dirname(base)).replace('\\', '/')
                if include(rel): z.write(p, rel)


for need in ('game/full/bytecode.byc', 'game/full/Text'):
    if not os.path.exists(os.path.join(ROOT, need)):
        sys.exit('없음: %s  (README의 "빌드 준비" 참고)' % need)
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

# 1) 정식판
full = os.path.join(OUT, 'full')
run([PY, 'build.py', full], cwd=SRC)
shutil.copy(os.path.join(ROOT, 'font', 'Kanit-Regular.ttf'), os.path.join(full, 'media', 'Kanit-Regular.ttf'))
os.makedirs(os.path.join(full, 'media', 'Images'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'logo', 'AI_Logo4Intro.png'), os.path.join(full, 'media', 'Images', 'AI_Logo4Intro.png'))
fbyc = os.path.join(full, 'media', 'bytecode.byc')
run([PY, 'fieldcheck.py', os.path.join(ROOT, 'game', 'full', 'bytecode.byc'), fbyc], cwd=SRC)
run([PY, 'validate2.py', os.path.join(ROOT, 'game', 'full', 'bytecode.byc'), fbyc], cwd=SRC)
KR_FULL = sha(fbyc)

# 2) 데모판 (선택)
KR_DEMO = ''
demo_byc = os.path.join(ROOT, 'game', 'demo', 'bytecode.byc')
if os.path.exists(demo_byc):
    run([PY, os.path.join('demo', 'port_demo.py'), os.path.join(OUT, 'demo_tmp')])
    dmedia = os.path.join(OUT, 'demo', 'media')
    os.makedirs(os.path.join(dmedia, 'Text'))
    run([PY, os.path.join('demo', 'build_demo.py'), os.path.join(dmedia, 'bytecode.byc')])
    for f in os.listdir(os.path.join(ROOT, 'demo', 'text_override')):
        shutil.copy(os.path.join(ROOT, 'demo', 'text_override', f), os.path.join(dmedia, 'Text', f))
    run([PY, os.path.join('demo', 'check_demo.py'), demo_byc, os.path.join(dmedia, 'bytecode.byc')])
    KR_DEMO = sha(os.path.join(dmedia, 'bytecode.byc'))
    for t in ('demo_tmp_fulltmp',):
        shutil.rmtree(os.path.join(OUT, t), ignore_errors=True)
else:
    print('데모판 bytecode 없음 → 정식판만 포장')

# 3) 포장
name = '한글패치_' + VER
pk = os.path.join(OUT, 'release', name)
os.makedirs(pk)
zipdir(os.path.join(full, 'media'), os.path.join(pk, 'AI_KR_common.zip'), include=lambda rel: rel != 'media/bytecode.byc')
with zipfile.ZipFile(os.path.join(pk, 'AI_KR_full.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(fbyc, 'media/bytecode.byc')
if KR_DEMO:
    zipdir(os.path.join(OUT, 'demo', 'media'), os.path.join(pk, 'AI_KR_demo.zip'))
run([PY, os.path.join('installer', 'mkpkg.py'), pk, KR_FULL] + ([KR_DEMO] if KR_DEMO else []), release=False)
for f in ('1_한글패치_설치.bat', '2_원본_복구.bat', 'image_copies.tsv', 'image_delete.txt', '읽어주세요.txt', '글꼴_라이선스_OFL.txt'):
    shutil.copy(os.path.join(ROOT, 'installer', f), os.path.join(pk, f))
final = os.path.join(OUT, 'release', 'AI_%s.zip' % name)
with zipfile.ZipFile(final, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(pk)): z.write(os.path.join(pk, f), name + '/' + f)
print('\n완료:', final)
print('정식판 한글 bytecode SHA256:', KR_FULL)
if KR_DEMO: print('데모판 한글 bytecode SHA256:', KR_DEMO)
