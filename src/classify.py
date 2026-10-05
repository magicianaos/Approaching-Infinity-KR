import numpy as np,json,collections,re
I=np.load('instr.npy'); S=json.load(open('strings.json'))
S=[s.encode('latin1').decode('utf8','replace') for s in S]
M={int(k):v[0] for k,v in json.load(open('opmap.json')).items()}
op=I[:,3]; x=I[:,4]
FILE={'OPENTOREAD','OPENTOWRITE','GETFILEEXISTS','DELETEFILE','LOADIMAGE','LOADSOUND','LOADMUSIC','LOADMUSICOGG','LOADSOUNDOGG','SETFOLDER','OPENBROWSER','RUNAPP','LOADFONT','MAKEFOLDER','GETFOLDEREXISTS','LOADSUBIMAGE','LOADSPRITE','CREATESPRITE','LOADOBJECT','PLAYMUSICOGG','COPYFILE','SETRAWWRITEPATH','LOADSHADER','CHOOSERAWFILE','GETSTEAMSTAT','SETSTEAMSTAT'}
DISP={'SETTEXTSTRING','CREATETEXT','PRINT','PRINTC','MESSAGE','SETWINDOWTITLE','SETEDITBOXTEXT','SETCLIPBOARDTEXT'}
TOK={'COUNTSTRINGTOKENS','GETSTRINGTOKEN','COUNTSTRINGTOKENS2','GETSTRINGTOKEN2','FINDSTRING','FINDSTRINGCOUNT','FINDSTRINGREVERSE','STRIPSTRING','REPLACESTRING','TRIMSTRING','LOWER','UPPER','ASC','MID','LEFT','RIGHT','LEN','VAL','VALFLOAT'}
WRITE={'WRITELINE','WRITESTRING','WRITESTRING2'}
tags=collections.defaultdict(collections.Counter)
def cname(o):
    n=M.get(int(o)); return n.split('_')[0] if n else None
for i in np.where(op==7)[0]:
    s=int(x[i]); o1=int(op[i+1]); o2=int(op[i+2])
    if o1 in (144,145) or (o1==5 and o2==152) or (o1==15 and o2 in (144,145)): tags[s]['CMP']+=1; continue
    # find consumer: skip following pushes of other args (simple: look up to 6 ahead for first command/known op)
    t=None
    for k in range(1,7):
        oo=int(op[i+k]); n=cname(oo)
        if n:
            if n in FILE: t='FILE'
            elif n in DISP: t='DISP'
            elif n in TOK: t='TOK:'+n
            elif n in WRITE: t='WRITE'
            else: t='CMD:'+n
            break
        if oo==36: t='CALL'; break
        if oo==112: t='CONCAT'; break
        if oo in (121,127): t='STORE'; break
        if oo in (144,145): t='CMP2'; break
        if oo==7 or oo==5 or oo==6 or oo in (15,27,31,13,12,20): continue
        t='OP%d'%oo; break
    tags[s][t or 'UNK']+=1
json.dump({k:dict(v) for k,v in tags.items()},open('tags.json','w'))
c=collections.Counter()
for k,v in tags.items():
    for t in v: c[t.split(':')[0]]+=1
print(c.most_common())
