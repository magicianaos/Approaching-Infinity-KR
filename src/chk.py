import sys,subprocess,ctx,struct,bcpatch,collections
from kostr import loadS
d,S,end=bcpatch.load()
import os as _o
ROOT=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
K=loadS(_o.environ.get('KR_BYC',_o.path.join(ROOT,'out','full','media','bytecode.byc'))); ctx.K=K
ids=[int(x) for x in sys.argv[1:]]
base=0x897CB; N=887737
arr=[struct.unpack_from('<ii',d,base+i*20+12) for i in range(N)]
ctx.ins=lambda i: arr[i]
sites=collections.defaultdict(list)
for i,(o,v) in enumerate(arr):
    if o==7 and v in ids: sites[v].append(i)
for k in ids:
    en=S[k].decode()
    g=subprocess.run(['grep','-rlF',en.strip(),_o.path.join(ROOT,'game','full','Text')],capture_output=True,text=True).stdout.split()
    print(f'### {k} {en!r} files={g[:5]}')
    for s in sites[k][:6]: print('   ',s,ctx.ctx(s,5,4)[:220])
