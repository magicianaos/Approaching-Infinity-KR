import struct
def parse(d,base,N):
    p=base+N*20-4   # name len of first record at p-4? we'll locate: count at base+N*20-8
    cnt=struct.unpack_from('<i',d,base+N*20-8)[0]
    p=base+N*20-4
    recs=[]
    for f in range(cnt):
        L=struct.unpack_from('<i',d,p)[0]; p+=4; name=d[p:p+L]; p+=L
        a,nv=struct.unpack_from('<ii',d,p); p+=8
        vs=[]
        for k in range(nv):
            L=struct.unpack_from('<i',d,p)[0]; p+=4; nm=d[p:p+L]; p+=L
            t,idx=struct.unpack_from('<ii',d,p); p+=8
            vs.append((t,idx))
        recs.append((name,a,vs))
    return recs,p
