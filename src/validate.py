import struct,bisect,collections,sys
from functab import parse
def load(path):
    import bcpatch
    d=open(path,'rb').read()
    d0,_,_=bcpatch.load()
    base=0x897CB+len(d)-len(d0); N=887737
    recs,p=parse(d,base,N)
    arr=[struct.unpack_from('<ii',d,base+i*20+12) for i in range(N)]
    return recs,arr
def funcmap(recs):
    starts=sorted((r[1]-1,k) for k,r in enumerate(recs))
    return starts
LOCALOPS={13:1,119:1,75:1,14:2,120:2,15:3,121:3}
def check(path,ops=LOCALOPS):
    recs,arr=load(path)
    st=funcmap(recs); keys=[s for s,k in st]
    bad=[]
    for i,(o,v) in enumerate(arr):
        if o in ops:
            j=bisect.bisect_right(keys,i)-1
            if j<0: continue
            vs=recs[st[j][1]][2]
            if (ops[o],v) not in vs: bad.append((i,o,v,st[j][0]))
    return bad
if __name__=='__main__':
    b=check(sys.argv[1]); print(len(b)); print(b[:40])
