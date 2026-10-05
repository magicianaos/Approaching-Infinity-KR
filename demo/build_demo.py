"""Build Korean demo bytecode from demo/port.json.  usage: python3 demo/build_demo.py OUT.byc"""
import sys, json, struct, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
import bcpatch
DEMO = os.path.join(ROOT, 'game', 'demo', 'bytecode.byc')
FIELD = {29, 30, 31, 32, 33, 125, 126, 127, 79, 80, 87, 88}
EXTRA = {  # demo-only strings
    3075: '각 옵션을 순서대로 신중하게 설정합니다:` &16 `\t• 함선`\t• 외형`\t• 직종`\t• 스킬`\t• 영구 사망`\t• 난이도`\t• 자금`\t• 치트`\t• 이름;모든 선택을 무작위로 정하지만, 여전히 바꿀 수 있습니다.;',
    3361: '변경 요소 활성화: 무한 산소',
    3362: '변경 요소 활성화: 일일 코드 무제한',
    3363: '변경 요소 활성화: 저항 없음',
    3364: '변경 요소 활성화: 어디서나 설치',
    3365: '변경 요소 활성화: 장교 팀',
    3366: '변경 요소 활성화: 소행성 기지',
    3367: '변경 요소 활성화: 무작위 종족',
    3368: '변경 요소 활성화: 레벨 제한 없음',
    3369: '변경 요소 활성화: 유한 자원',
    3635: '워프 재사용 대기 ',
    5520: ' 이(가) 영원히 우리를 미워할 거예요.``한 번에 끝나지도 않을 거고,`우리를 파괴하려고 함선을 몇 차례나 보내올 거예요.``정말 공격하시겠습니까?',
}

def main(out):
    P = json.load(open(os.path.join(ROOT, 'out', 'port.json'), encoding='utf-8'))
    repl = {int(k): v for k, v in P['repl'].items()}
    repl.update(EXTRA)
    patches = {int(k): v for k, v in P['patches'].items()}
    d = open(DEMO, 'rb').read()
    p = 0x529; n = struct.unpack_from('<i', d, p)[0]; p += 4; S = []
    for i in range(n):
        L = struct.unpack_from('<i', d, p)[0]; S.append(d[p + 4:p + 4 + L]); p += 4 + L
    end = p
    j = d.find(struct.pack('<iiii', 173, 0, 0, 6855), end); base0 = j + 8
    N = struct.unpack_from('<i', d, base0 - 16)[0]
    for i, t in sorted(repl.items()):
        if i < len(S): S[i] = t.encode('utf8')
        else:
            assert i == len(S), (i, len(S)); S.append(t.encode('utf8'))
    b = bytearray(d[:0x529]); b += struct.pack('<i', len(S))
    for s in S: b += struct.pack('<i', len(s)) + s
    b += struct.pack('<I', bcpatch.strhash(S)); b += d[end + 4:]
    base = base0 + len(b) - len(d)
    assert struct.unpack_from('<i', b, base - 16)[0] == N
    for idx, pv in patches.items():
        struct.pack_into('<ii', b, base + idx * 20 + 12, pv[0], pv[1])
        if len(pv) > 2: struct.pack_into('<i', b, base + idx * 20 + 20, pv[2])
        elif pv[0] in FIELD: raise Exception(('field op needs X', idx, pv))
    open(out, 'wb').write(b)
    print('demo KR written', len(b), 'strings', len(S), 'patches', len(patches))

main(sys.argv[1])
