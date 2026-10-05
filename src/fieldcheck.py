import struct,sys
# usage: python3 fieldcheck.py orig.byc new.byc  -> changed field ops must match an original (op,field,X)
FIELD={29,30,31,32,33,125,126,127,79,80,87,88}
d0=open(sys.argv[1],'rb').read(); d1=open(sys.argv[2],'rb').read()
b0=0x897CB; b1=b0+len(d1)-len(d0); N=887737
ok=set()
for i in range(N):
    r=struct.unpack_from('<iii',d0,b0+12+i*20)
    if r[0] in FIELD: ok.add(r)
bad=[]
for i in range(N):
    r1=struct.unpack_from('<iii',d1,b1+12+i*20)
    if r1[0] in FIELD and r1 not in ok: bad.append((i,r1))
print('field-op violations',len(bad),bad[:20])
