# 어프로칭 인피니티 한글패치 (Approaching Infinity Korean Patch)

스팀 게임 **Approaching Infinity**의 비공식 한글패치입니다.
정식판(v2.2.1)과 데모판(v2.2.0jk-DEMO)을 지원합니다.

> 이 저장소에는 **게임 원본 파일이 들어 있지 않습니다.**
> 번역 데이터, 빌드 도구, 설치 스크립트만 있습니다. 게임은 스팀에서 구매해 설치해야 합니다.

---

## 설치 (일반 사용자)

1. [Releases](../../releases)에서 최신 `AI_한글패치_vX.X.X.zip`을 받습니다.
2. 압축을 풉니다. (게임 폴더 안에 풀어 두는 것을 권장)
3. `1_한글패치_설치.bat`을 더블클릭합니다.
   - 게임 폴더를 자동으로 찾습니다. 못 찾으면 경로를 물어봅니다.
   - 정식판/데모판을 알아서 판별합니다.
   - 바뀌는 원본 파일은 게임 폴더의 `한글패치_원본백업`에 보관됩니다.
4. 영어로 되돌리려면 `2_원본_복구.bat`을 실행하거나, 스팀에서 "게임 파일 무결성 확인"을 합니다.

게임이 업데이트되면 설치 프로그램이 "버전이 다르다"며 멈춥니다. 새 버전용 패치를 기다려 주세요.

## 알려진 한계

- **클래식 모드(Approaching Infinity Classic)**: 옛 엔진(AGK v1)의 그림 글꼴이 1바이트 문자(최대 224자)만 지원해 한글 표시 불가 → 영어 유지
- 외계 문자 전용 그림 글꼴로 표시되는 줄(불러오기 화면 둘째 줄, 일부 외계 종족 통신문)은 영어/외계 문자 유지
- 그림 안에 그려진 영어, 스팀 상품 이름은 번역하지 않음
- 가끔 효과음이 모두 멈추는 현상은 영어 원본에서도 생기는 엔진 쪽 증상

---

## 빌드 (개발자용)

### 준비

- Python 3.10 이상
- 게임 원본 파일을 `game/` 폴더에 복사 (방법은 [game/README.md](game/README.md))

### 실행

```
python make_release.py v1.1.1
```

결과물: `out/release/AI_한글패치_v1.1.1.zip`

빌드 과정:

1. `src/build.py` — 번역 메모리(`ai_tm*.csv`)와 각종 덮어쓰기 표로 `bytecode.byc` 문자열 표와 `Text/*.txt`를 한글로 바꾸고, 명령어 패치(`instr_patches.json`, 글꼴 번호·메뉴 등)를 적용
2. `src/fieldcheck.py`, `src/validate2.py` — 게임이 시작할 때 하는 bytecode 검사(필드 형 번호, 지역 변수 번호)를 미리 확인
3. `demo/port_demo.py`, `demo/build_demo.py` — 정식판 패치를 데모판 bytecode로 이식 (함수 이름 기준 위치 대응)
4. `installer/mkpkg.py` — 해시를 넣은 설치/복구 스크립트 생성 후 zip으로 포장

### 폴더 구조

| 폴더 | 내용 |
|---|---|
| `src/` | 빌드 도구(Python)와 번역 데이터 (`ai_tm.csv` 번역 메모리, `ai_rows.csv` 문자열 분류, `*_override` 수동 수정 표, `full_ko/` 통째 번역 파일, `nm/work_5/story_ko/` 오프닝 이야기) |
| `demo/` | 데모판 이식 도구, 데모판 전용 텍스트 2개 |
| `installer/` | 설치/복구 스크립트(PowerShell + bat), 그림 사본 목록, 배포용 안내문 |
| `font/` | 한글 글꼴 (Kanit + Noto Sans CJK KR 합본, 내부 이름 "AI Hangul", SIL OFL 1.1) |
| `logo/` | 한글 타이틀 로고 |
| `docs/기술노트.md` | 작업 기록 — bytecode 구조, 버그 원인과 수정 이력, 지켜야 할 규칙 |
| `game/` | (git 제외) 빌드에 쓰는 게임 원본 파일 |

### 꼭 지킬 규칙 (자세한 내용은 기술노트)

- **고정 길이 머리말은 번역 금지**: 게임이 줄 앞 N글자를 건너뛰고 읽는 파일이 있음
  (예: `DeviceEffectDescriptions.txt`의 `Full Effect Desc:` 17글자)
- **필드 명령 패치는 형 번호(X)까지** `[op, 필드, X]`로 적을 것 — 빠지면 게임 시작 시 "Bytecode error"
- 코드 끼워 넣기(동굴)는 숙주 함수에 선언된 지역 변수 번호만 사용

---

## 저작권

- **Approaching Infinity**의 모든 권리는 원 개발자에게 있습니다. 이 패치는 비공식 팬 번역입니다.
- 글꼴: Kanit (Copyright (c) 2015, Cadson Demak), Noto Sans CJK KR (Copyright 2014-2021 Adobe) — 둘 다 SIL Open Font License 1.1. 합친 글꼴도 같은 라이선스 ([font/OFL.txt](font/OFL.txt))

## 만든 사람

- 한글화: AOS
