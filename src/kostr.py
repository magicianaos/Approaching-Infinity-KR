import struct
def loadS(f):
    d=open(f,'rb').read(); p=0x529; n=struct.unpack_from('<i',d,p)[0]; p+=4; S=[]
    for i in range(n):
        L=struct.unpack_from('<i',d,p)[0]; S.append(d[p+4:p+4+L].decode('utf8','replace')); p+=4+L
    return S
import os as _o
ROOT=_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
K=loadS(_o.environ.get('KR_BYC',_o.path.join(ROOT,'out','full','media','bytecode.byc')))
