import sys
from dis import *
from kostr import loadS
import os as _o
ROOT=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
K=loadS(_o.environ.get('KR_BYC',_o.path.join(ROOT,'out','full','media','bytecode.byc')))
def ctx(s,a=25,b=12):
    out=[]
    for i in range(s-a,s+b):
        o,v=ins(i)
        if o==7: out.append(f"{'*' if i==s else ''}[{v}]{K[v]!r}")
        elif o==990: out.append('str()')
        elif o==15: out.append(f'${v}')
        elif o==13: out.append(f'i{v}')
        elif o==31: out.append(f'.f{v}')
        elif o==29: out.append(f'.i{v}')
        elif o==36: out.append({474664:'MSG',876427:'LOG',282506:'FLT',115217:'fmt',30134:'lc',612791:'plural',89083:'cap',360090:'fmtd'}.get(v,f'C{v}'))
        elif o==121: out.append(f'=>${v}')
        elif o in (127,119,125): out.append(f'=>{o}:{v}')
        elif o==112: out.append('+')
    return ' '.join(out)
if __name__=='__main__':
    for s in sys.argv[1:]: print(s, ctx(int(s))); print()
