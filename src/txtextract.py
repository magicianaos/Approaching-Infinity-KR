import glob,re,os,json,collections
import os as _o
SKIPFILES={'RecipeItemsAndAmounts.txt','StringList.txt','StringList2.txt','stringlist17.txt','stringlist18.txt','TempleOfASCII_9x9_B.txt','TempleRoomsASCII.txt','zlistofnumbersandcommas.txt','AddImg.txt','CharSelImg.txt','quadrantstructure.txt','newbuttonlocations.txt','Sounds.txt','TrackList.txt','pdswl2-list.txt','PDSWs.txt','treesbynumber.txt','ArtCol.txt',
 # generated proper-name lists: keep English by default
 'BunchaNames.txt','Names_All.txt','NamGenNeu.txt','NamSpac.txt','NamSur.txt','NamesBoring.txt','OfficerFirstFemale.txt','OfficerFirstMale.txt','OfficerLast.txt','PlanetNames.txt','pirate names.txt','pn1230n1.txt','pn1230n2.txt','ShipNames.txt','shipnameenders.txt','BossShipNames.txt','VillainNames.txt','name fodder for planet words.txt','names-of-plants.txt','names-of-plants2.txt','EarthCityCountry.txt','Greek Letters.txt','HumanEnders.txt','ion words.txt','FiraxNumbers.txt'}
WORD=re.compile(r"[A-Za-z][A-Za-z'\-]*")
def readlines(f):
    b=open(f,'rb').read()
    try: t=b.decode('utf8'); enc='utf8'
    except UnicodeDecodeError: t=b.decode('cp1252'); enc='cp1252'
    nl='\r\n' if '\r\n' in t else '\n'
    return t.split(nl),enc,nl
def looks_text(v):
    v=v.strip()
    if not v or '/' in v and ' ' not in v: return False
    if re.search(r'\.(png|txt|jpg|ogg|wav)\b',v,re.I): return False
    ws=WORD.findall(v)
    if not ws: return False
    long=[w for w in ws if len(w)>=2]
    if len(long)>=2 and ' ' in v.strip(): return True
    # single word: capitalized alpha name-like
    if len(ws)==1 and re.fullmatch(r"[A-Z][a-z'\-]{2,}[!?.]?",v): return True
    return False
def pieces(line):
    """yield (start,end) spans of candidate value text inside a line"""
    out=[]; pos=0
    for part in line.split('^'):
        s=pos; e=pos+len(part); pos=e+1
        p=part
        m=re.match(r"^(\s*[#~]?)",p); off=m.end()
        body=p[off:]
        # choice '#Text=target'
        if p[:off].strip()=='#' and '=' in body:
            k=body.rfind('='); out.append((s+off,s+off+k)); continue
        m=re.match(r"^([^:=`]{1,14})([:=])",body)
        if m and not re.search(r"[.!?]\s",m.group(1)) and (m.group(2)==':' or re.fullmatch(r"[\w$#& ]+",m.group(1))):
            lab=m.group(1)
            # label must look like a field label: short, no sentence
            if len(lab.split())<=3:
                vs=off+m.end()
                # skip extra colons like ':D E S C:::'
                while vs<len(p) and p[vs]==':': vs+=1
                out.append((s+vs,e,lab.strip())); continue
        out.append((s+off,e,''))
    return [o if len(o)==3 else (o[0],o[1],'#') for o in out]
EXCL_LABELS={'image','img name','ev','Parse$','Trnsfrm','Mon_Where','Ship Img','NuSpawnMt','Stuff$','Theme','SkVchang','SklVal*'}
def labfreq(L):
    c=collections.Counter()
    for line in L:
        for s,e,lab in pieces(line):
            if lab not in ('','#'): c[lab]+=1
    return c
def main():
    segs=[]
    for f in sorted(glob.glob(_o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))),'game','full','Text')+'/**/*.txt',recursive=True)):
        rel=os.path.relpath(f,_o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))),'game','full','Text')).replace('\\','/')
        if os.path.basename(rel) in SKIPFILES: continue
        L,enc,nl=readlines(f)
        LF=labfreq(L)
        for i,line in enumerate(L):
            if not line.strip() or line.lstrip().startswith('`') and not re.search(r'[A-Za-z]{3,} [A-Za-z]{2,}',line[:3]) and line.startswith('`'): 
                continue
            for s,e,lab in pieces(line):
                if lab not in ('','#') and not (LF[lab]>=3 or re.fullmatch(r'\d+',lab)):
                    # not a real label: take whole '^' piece
                    ps=line.rfind('^',0,s)+1; s=ps; lab=''
                    while s<e and line[s] in ' #~': s+=1
                if lab in EXCL_LABELS: continue
                v=line[s:e]
                m=re.match(r'^\s*-?\d+\s*[/]',v)
                if m: s+=m.end(); v=line[s:e]
                if re.match(r'^\s*-?\d+\s*;',v): continue
                # trim trailing inline comment "   ` blah" (2+ spaces then backtick)
                m=re.search(r"\s{2,}`",v)
                if m: e=s+m.start(); v=line[s:e]
                vs=v.strip()
                if looks_text(vs):
                    ls=s+len(v)-len(v.lstrip()); le=ls+len(vs)
                    segs.append({'file':rel,'line':i,'s':ls,'e':le,'label':lab,'en':vs})
    json.dump(segs,open('txt_segs.json','w'),ensure_ascii=False)
    c=collections.Counter(x['file'] for x in segs)
    print(len(segs), sum(len(x['en']) for x in segs), len(c))
    labs=collections.Counter((x['file'],x['label']) for x in segs)
    print(labs.most_common(40))


if __name__=='__main__': main()
