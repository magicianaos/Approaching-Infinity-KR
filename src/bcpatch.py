import struct,json,sys
import os as _o
ROOT=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
SRC=_o.path.join(ROOT,'game','full','bytecode.byc')
TAB=0x529
def load():
    d=open(SRC,'rb').read()
    p=TAB; n=struct.unpack_from('<i',d,p)[0]; p+=4; S=[]
    for i in range(n):
        L=struct.unpack_from('<i',d,p)[0]; S.append(d[p+4:p+4+L]); p+=4+L
    return d,S,p
def strhash(S):
    t=0
    for s in S:
        for j,c in enumerate(s):
            c=c-256 if c>127 else c
            t+=c*j*(1 if j%2 else -1)
    return t & 0xffffffff
def build(repl,out,patches=None):
    d,S,end=load()
    for i,t in sorted(repl.items(),key=lambda x:int(x[0])):
        i=int(i)
        if i<len(S): S[i]=t.encode('utf8')
        else:
            assert i==len(S),(i,len(S)); S.append(t.encode('utf8'))
    b=bytearray(d[:TAB]); b+=struct.pack('<i',len(S))
    for s in S: b+=struct.pack('<i',len(s))+s
    b+=struct.pack('<I',strhash(S)); b+=d[end+4:]
    if patches:
        delta=len(b)-len(d); base=0x897CB+delta
        assert struct.unpack_from('<i',b,base-16)[0]==887737
        FIELD={29,30,31,32,33,125,126,127,79,80,87,88}
        for idx,pv in patches.items():
            o,v=pv[0],pv[1]
            struct.pack_into('<ii',b,base+idx*20+12,o,v)
            if len(pv)>2: struct.pack_into('<i',b,base+idx*20+20,pv[2])
            elif o in FIELD:
                ox=struct.unpack_from('<ii',d,base-delta+idx*20+12) if False else None
                raise Exception(('field op needs type index',idx,pv))
    open(out,'wb').write(b); return len(b)
if __name__=='__main__':
    repl=json.load(open(sys.argv[1],encoding='utf8'))
    print(build(repl,sys.argv[2]))
