import sys,bisect,collections
from validate import load
OPS={13:1,119:1,75:1,14:2,120:2,15:3,121:3}
def viol(path):
    recs,arr=load(path)
    st=sorted((r[1]-1,k) for k,r in enumerate(recs)); keys=[s for s,k in st]
    out=[]
    for i,(o,v) in enumerate(arr):
        if o not in OPS: continue
        j=bisect.bisect_right(keys,i)-1
        if j<0: continue
        vs=recs[st[j][1]][2]
        if v>=0:
            if (OPS[o],v) not in vs: out.append((i,o,v,st[j][0],'pos'))
        else:
            mn=min([x for t,x in vs if x<0],default=0)
            if v<mn-1: out.append((i,o,v,st[j][0],'neg'))
    return out
if __name__=='__main__':
    a=set((x[0],x[1],x[2]) for x in viol(sys.argv[1]))
    b=viol(sys.argv[2])
    new=[x for x in b if (x[0],x[1],x[2]) not in a]
    print('orig viol',len(a),'new viol',len(new)); print(new[:50])
