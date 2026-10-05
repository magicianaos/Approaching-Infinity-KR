import struct,sys
from bcpatch import load
d,S,end=load()
base=0x897CB; N=887737
def ins(i): return struct.unpack_from('<ii',d,base+i*20+12)
def s(i):
    try: return S[i].decode('utf8','replace')
    except: return '?'
def show(a,b):
    for i in range(a,b):
        o,v=ins(i); x=f'  "{s(v)[:60]}"' if o==7 and 0<=v<len(S) else ''
        print(i,o,v,x)
def find(sid):
    return [i for i in range(N) if ins(i)==(7,sid)]
