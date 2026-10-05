import sys,struct,bisect
import os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'src'))
from functab import parse
FIELD={29,30,31,32,33,125,126,127,79,80,87,88}
LOCALOPS={13:1,119:1,75:1,14:2,120:2,15:3,121:3}
def load(path):
    d=open(path,'rb').read()
    p=0x529; n=struct.unpack_from('<i',d,p)[0]; p+=4; S=[]
    for i in range(n):
        L=struct.unpack_from('<i',d,p)[0]; S.append(d[p+4:p+4+L]); p+=4+L
    j=d.find(struct.pack('<iiii',173,0,0,6855),p); base=j+8; N=struct.unpack_from('<i',d,base-16)[0]
    I=[struct.unpack_from('<iii',d,base+12+i*20) for i in range(N)]
    R,_=parse(d,base,N); return d,S,I,R,N
d0,S0,I0,R0,N0=load(sys.argv[1]); d1,S1,I1,R1,N1=load(sys.argv[2])
assert N0==N1 and len(R0)==len(R1)
print('func table same', [(r[0],r[1],r[2]) for r in R0]==[(r[0],r[1],r[2]) for r in R1])
okf=set(r for r in I0 if r[0] in FIELD)
st=sorted((r[1]-1,k) for k,r in enumerate(R1)); keys=[s for s,k in st]
chg=0; bad=[]
for i in range(N0):
    if I0[i]!=I1[i]:
        chg+=1; o,v,x=I1[i]
        if o in FIELD and I1[i] not in okf: bad.append(('field',i,I1[i]))
        if o in LOCALOPS and v>=0:
            j=bisect.bisect_right(keys,i)-1; vs=R1[st[j][1]][2]
            if (LOCALOPS[o],v) not in vs: bad.append(('local',i,I1[i]))
        if o==7 and not (0<=v<len(S1)): bad.append(('str',i,I1[i]))
        if o in (36,146,147,148) and not (0<v<=N1): bad.append(('jump',i,I1[i]))
# global: all string pushes valid
badpush=[i for i,(o,v,x) in enumerate(I1) if o==7 and not (0<=v<len(S1))]
print('changed',chg,'bad',bad[:10],'bad pushes',len(badpush),'strings',len(S0),'->',len(S1))
