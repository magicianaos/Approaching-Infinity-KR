"""Port the full-game Korean patch (strings + instruction patches) onto the demo bytecode.
usage: RELEASE=1 python3 demo/port_demo.py OUTDIR   (run from repo root)
"""
import sys, os, struct, bisect, difflib, json, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
os.chdir(os.path.join(ROOT, 'src'))
import bcpatch
from functab import parse

FULL = os.path.join(ROOT, 'game', 'full', 'bytecode.byc')
DEMO = os.path.join(ROOT, 'game', 'demo', 'bytecode.byc')
FIELD = {29, 30, 31, 32, 33, 125, 126, 127, 79, 80, 87, 88}
JUMP = {36, 146, 147, 148}
LOCALOPS = {13: 1, 119: 1, 75: 1, 14: 2, 120: 2, 15: 3, 121: 3}


def load(path):
    d = open(path, 'rb').read()
    p = 0x529; n = struct.unpack_from('<i', d, p)[0]; p += 4; S = []
    for i in range(n):
        L = struct.unpack_from('<i', d, p)[0]; S.append(d[p + 4:p + 4 + L]); p += 4 + L
    end = p
    j = d.find(struct.pack('<iiii', 173, 0, 0, 6855), end)  # first instruction record signature
    base = j + 8
    N = struct.unpack_from('<i', d, base - 16)[0]
    I = [struct.unpack_from('<iii', d, base + 12 + i * 20) for i in range(N)]
    R, _ = parse(d, base, N)
    return dict(d=d, S=S, end=end, base=base, N=N, I=I, R=R)


def funcs(G):
    st = sorted((r[1] - 1, r[0], k) for k, r in enumerate(G['R']))
    G['fkeys'] = [s for s, _, _ in st]; G['flist'] = st
    G['fbyname'] = {n: (s, k) for s, n, k in st}


def fof(G, i):
    j = bisect.bisect_right(G['fkeys'], i) - 1
    s, n, k = G['flist'][j]
    e = G['fkeys'][j + 1] if j + 1 < len(G['fkeys']) else G['N']
    return s, e, n, k


# ---- capture full-game repl/patches from build.py
cap = {}
real_build = bcpatch.build
def fake_build(repl, out, patches=None):
    cap['repl'] = dict(repl); cap['patches'] = dict(patches or {})
    return real_build(repl, out, patches)
bcpatch.build = fake_build
import build as B
outdir = sys.argv[1]
B.build(outdir + '_fulltmp')
repl, patches = cap['repl'], cap['patches']

F = load(FULL); D = load(DEMO); funcs(F); funcs(D)
S0, S1 = F['S'], D['S']
print('full strings', len(S0), 'demo strings', len(S1), 'full N', F['N'], 'demo N', D['N'])

# ---- string map full id -> demo id
smap = {}
sm = difflib.SequenceMatcher(None, S0, S1, autojunk=False)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): smap[a + k] = b + k
first1 = {}
for i, s in enumerate(S1): first1.setdefault(s, i)
for i, s in enumerate(S0):
    if i not in smap and s in first1: smap[i] = first1[s]
demo_only = [i for i in range(len(S1)) if i not in set(smap.values())]

nfull = len(S0)
newids = sorted(k for k in repl if int(k) >= nfull)
for k, i in enumerate(newids): smap[i] = len(S1) + k

repl_d = {}
unm = []
for i, t in repl.items():
    i = int(i)
    if i in smap: repl_d[smap[i]] = t
    else: unm.append(i)
print('repl', len(repl), 'mapped', len(repl_d), 'unmapped', [(i, S0[i][:50]) for i in unm])
print('demo-only strings', [(i, S1[i][:70]) for i in demo_only])

# ---- instruction map
def norm(ins, S):
    o, v, x = ins
    if o == 7 and 0 <= v < len(S): return (o, S[v], x)
    if o in JUMP: return (o, 'J')
    return ins

fnmap_cache = {}
def func_align(name):
    if name in fnmap_cache: return fnmap_cache[name]
    s0, e0, _, _ = fof(F, F['fbyname'][name][0])
    s1, k1 = D['fbyname'][name]
    e1 = fof(D, s1)[1]
    A = [norm(F['I'][i], S0) for i in range(s0, e0)]
    Bq = [norm(D['I'][i], S1) for i in range(s1, e1)]
    m = {}
    if A == Bq:
        m = {k: k for k in range(len(A))}
    else:
        sm = difflib.SequenceMatcher(None, A, Bq, autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): m[a + k] = b + k
    fnmap_cache[name] = (s0, s1, m, A == Bq)
    return fnmap_cache[name]

def imap(i):
    s0, e0, name, _ = fof(F, i)
    s0, s1, m, same = func_align(name)
    off = i - s0
    if off in m: return s1 + m[off]
    return None

pd = {}
bad = []
for site, pv in sorted(patches.items()):
    t = imap(site)
    if t is None: bad.append((site, pv, 'site')); continue
    o, v = pv[0], pv[1]
    if o == 7:
        if v not in smap: bad.append((site, pv, 'str')); continue
        v = smap[v]
    elif o in JUMP:
        tt = imap(v - 1)
        if tt is None: bad.append((site, pv, 'target')); continue
        v = tt + 1
    elif o in FIELD:
        # take type index from the demo's own instruction with same op/field in the same function if possible
        x = pv[2] if len(pv) > 2 else None
        bad.append((site, pv, 'field-check')) if x is None else None
    new = [o, v] + (list(pv[2:]) if len(pv) > 2 else [])
    pd[t] = new
print('patches', len(patches), 'ported', len(pd), 'bad', bad)

# local var sanity: for local ops in patches, demo host function must declare var
viol = []
for t, pv in pd.items():
    if pv[0] in LOCALOPS and pv[1] >= 0:
        s, e, n, k = fof(D, t)
        if (LOCALOPS[pv[0]], pv[1]) not in D['R'][k][2]: viol.append((t, pv))
print('local var violations', viol)

json.dump({'repl': {str(k): v for k, v in repl_d.items()}, 'patches': {str(k): v for k, v in pd.items()},
           'demo_only': [[i, S1[i].decode('latin1')] for i in demo_only]},
          open(os.path.join(ROOT, 'out', 'port.json'), 'w', encoding='utf-8'), ensure_ascii=False)
