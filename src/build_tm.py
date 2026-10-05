import json,re,collections,csv
S=json.load(open('strings.json')); S=[s.encode('latin1').decode('utf8','replace') for s in S]
T=json.load(open('tags.json')); segs=json.load(open('txt_segs.json'))
NAMEGEN={'SHIPWRECKENDERS.txt','SHIPWRECKSTARTERS.txt','BossStarters.txt'}
KEEPNAMES={'Planam_xenocouncil.txt'}
def namelike(s): return len(s)<=40 and len(s.split())<=5 and not re.search(r'[.!?`:]$',s) and '`' not in s
def bc_class(i,s):
    tags=T.get(str(i),{})
    st=s.strip()
    if ('CMP' in tags or 'OP152' in tags) and re.search(r'[A-Za-z]{2}',s) and not re.search(r'\.(txt|png)',s,re.I): return 'CMPKEY','cmp'
    if not re.search(r'[A-Za-z]{2}',s): return 'KEEP','noletters'
    if 'FILE' in tags or re.search(r'\.(txt|png|jpg|ogg|wav|agc|aic|exe|bld|byc|sec|snx|huh|csv|json)\b',s,re.I) or re.match(r'https?://',st) or re.search(r'\w/\w',st) and ' ' not in st: return 'KEEP','file'
    if ' ' not in st:
        if re.search(r'[\d_$#@{}=<>|\\]',st) and not re.fullmatch(r"[A-Za-z'\-]+[!?.,]?",st): return 'KEEP','code'
        if re.fullmatch(r'[a-z][a-z0-9]*',st) : return 'KEEP','lowerword'
        if re.fullmatch(r'[a-z]+[A-Z]\w*',st): return 'KEEP','camel'
        if re.fullmatch(r'[A-Z]{1,4}\d*',st): return 'KEEP','caps'
    if re.match(r"^(i |i'm |i am |im |numo|in this case|this captain does not)",st) or re.search(r'[a-z]=$|=\s*$',st): return 'DEBUG','dbg'
    if set(tags)=={'WRITE'}: return 'DEBUG','writeonly'
    if 'CMP' in tags: return 'CMPKEY','cmp'
    return 'TEXT',''
rows=[]
for i,s in enumerate(S):
    c,why=bc_class(i,s); rows.append({'src':'bc','id':i,'en':s,'cat':c,'why':why,'tags':','.join(sorted(T.get(str(i),{})))})
for x in segs:
    f=x['file']; c='NAMEGEN' if f in NAMEGEN else ('KEEP' if f in KEEPNAMES else 'TEXT')
    rows.append({'src':'txt','id':'%s:%d:%d'%(f,x['line'],x['s']),'en':x['en'],'cat':c,'why':x['label'],'tags':''})
# translation memory: unique en for TEXT/NAMEGEN; CMPKEY included only if its text (case-insens) appears among TEXT strings or txt segs
txtset=collections.Counter(r['en'] for r in rows if r['cat'] in ('TEXT','NAMEGEN'))
lower={k.lower():k for k in txtset}
for r in rows:
    if r['cat']=='CMPKEY':
        r['cat']='TEXT_LINKED' if r['en'].lower() in lower else 'CMPKEY'
tm=collections.OrderedDict()
for r in rows:
    if r['cat'] in ('TEXT','NAMEGEN','TEXT_LINKED'):
        k=r['en'] if r['cat']!='TEXT_LINKED' else lower[r['en'].lower()]
        e=tm.setdefault(k,{'en':k,'ko':'','n':0,'src':set(),'cat':r['cat']})
        e['n']+=1; e['src'].add(r['src'] if r['src']=='bc' else r['id'].split(':')[0])
        if r['cat']=='TEXT' : e['cat']='TEXT'
c=collections.Counter(r['cat'] for r in rows if r['src']=='bc'); print('bytecode',c)
c=collections.Counter(r['cat'] for r in rows if r['src']=='txt'); print('txt',c)
print('TM unique',len(tm),'chars',sum(len(k) for k in tm), 'TEXT only chars',sum(len(k) for k,v in tm.items() if v['cat']=='TEXT'))
with open('ai_rows.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['src','id','cat','why','tags','en']); w.writeheader(); [w.writerow(r) for r in rows]
with open('ai_tm.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f); w.writerow(['no','cat','count','sources','en','ko'])
    for n,(k,v) in enumerate(tm.items()): w.writerow([n,v['cat'],v['n'],';'.join(sorted(v['src']))[:80],k,''])
