import re,struct,collections,bcpatch
from kostr import loadS
d,S,end=bcpatch.load()
import os as _o
ROOT=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
K=loadS(_o.environ.get('KR_BYC',_o.path.join(ROOT,'out','full','media','bytecode.byc')))
base=0x897CB; N=887737
arr=[struct.unpack_from('<ii',d,base+i*20+12) for i in range(N)]
sites=collections.defaultdict(list)
for i,(o,v) in enumerate(arr):
    if o==7: sites[v].append(i)
pat=re.compile(r"[A-Za-z']{2,} [A-Za-z']{2,}")
out=[]
for i,s in enumerate(S):
    k=K[i]
    if re.search('[가-힣]',k) or not pat.search(k): continue
    if re.search(r'\.(png|txt|jpg|ogg|wav|fif|mdf)\b',k,re.I) and len(k)<90: continue
    st=sites.get(i,[])
    if not st: continue
    logonly=True
    for p in st:
        kind=None
        for j in range(p+1,min(p+25,N)):
            o,v=arr[j]
            if o==36: kind='LOG' if v==876427 else 'X'; break
            if o in (983,): kind='WRITE'; break
        if kind not in ('LOG',): logonly=False
    if logonly: continue
    out.append(f'{i}\t{len(st)}\t{k[:110]!r}')
open('still_en.txt','w').write('\n'.join(out)); print(len(out))
