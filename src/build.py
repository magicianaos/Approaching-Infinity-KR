import json,csv,re,os,sys,collections,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bcpatch
ORIG_TEXT=os.path.join(bcpatch.ROOT,'game','full','Text')+'/'
from txtextract import readlines
TM={}
for r in csv.DictReader(open(os.environ.get('TMFILE','ai_tm.csv'),encoding='utf-8-sig')):
    if r['ko'].strip(): TM[r['en']]=r['ko']
import os as _os
TMS={'bc':dict(TM),'txt':dict(TM)}
if _os.path.exists('ai_tm_extra.csv'):
    for r in csv.DictReader(open('ai_tm_extra.csv',encoding='utf-8-sig')):
        sc=(r.get('scope') or 'bc').strip()
        for k in (('bc','txt') if sc=='all' else (sc,)):
            if r['ko'].strip(): TMS[k][r['en']]=r['ko']
TMLS={k:{a.lower():b for a,b in v.items()} for k,v in TMS.items()}
rows=list(csv.DictReader(open('ai_rows.csv',encoding='utf-8-sig')))
LINK_ALLOW={'done','quit','help','options','inventory','officers','quests','crafting','infinipedia','keybinds','tooltip','shipyards'}
def tr(en,cat,src='bc'):
    TM=TMS[src]; TMl=TMLS[src]
    if cat in ('TEXT_LINKED','CMPKEY'):
        st=en.strip()
        if re.fullmatch(r"[a-z'\-]+",st) and st not in LINK_ALLOW: return None
        if re.fullmatch(r"[A-Z]{1,6}",st): return None
        return TMl.get(en.lower())
    # comma list made entirely of known entries -> token-wise
    if ',' in en and en not in TM:
        toks=en.split(',')
        short=all(len(t.strip())<=30 and len(t.split())<=4 for t in toks)
        if short and any(t.strip() in TM for t in toks):
            return ','.join((t[:len(t)-len(t.lstrip())]+TM.get(t.strip(),t.strip())+t[len(t.rstrip()):]) if t.strip() else t for t in toks)
        if all(t.strip() in TM or not t.strip() for t in toks) and any(t.strip() for t in toks):
            return ','.join((t[:len(t)-len(t.lstrip())]+TM[t.strip()]+t[len(t.rstrip()):]) if t.strip() else t for t in toks)
    v=TM.get(en)
    if v is None:
        m=re.match(r'^(.+?) \((.*)$',en)
        if m and m.group(1).lower() in TMl: v=TMl[m.group(1).lower()]+' ('+m.group(2)
    return v
def build(outdir):
    import json as _j, shutil as _sh
    os.makedirs(outdir+'/media/Text/Hails',exist_ok=True)
    repl={}
    for r in rows:
        if r['src']=='bc' and r['cat'] in ('TEXT','TEXT_LINKED','NAMEGEN','CMPKEY'):
            k=tr(r['en'],r['cat'],'bc')
            if k: repl[int(r['id'])]=k
    if os.path.exists('ai_bc_override.csv'):
        for r in csv.DictReader(open('ai_bc_override.csv',encoding='utf-8-sig')): repl[int(r['id'])]=r['ko']
    patches={int(k):v for k,v in _j.load(open('instr_patches.json')).items()} if os.path.exists('instr_patches.json') else {}
    if os.path.exists('new_strings.json'):
        nid=11885
        for ent in _j.load(open('new_strings.json')):
            repl[nid]=ent['ko']
            for site in ent['sites']: patches[int(site)]=[7,nid]
            nid+=1
    if os.environ.get('RELEASE'):
        DBG=set(range(18655,18790))|set(range(108590,108630))|set(range(109843,109883))|{474664,282506,171592,612348,612381}
        patches={k:v for k,v in patches.items() if k not in DBG}
        print('RELEASE: debug hooks removed')
    bcpatch.build(repl,outdir+'/media/bytecode.byc',patches)
    names_map=_j.load(open('names_map.json')) if os.path.exists('names_map.json') else {}
    words_map=_j.load(open('words_map.json')) if os.path.exists('words_map.json') else {}
    lineins=_j.load(open('txt_line_insert.json')) if os.path.exists('txt_line_insert.json') else {}
    lineov=_j.load(open('txt_line_override.json')) if os.path.exists('txt_line_override.json') else {}
    subov=_j.load(open('txt_sub_override.json')) if os.path.exists('txt_sub_override.json') else {}
    NAMEFILES=set(v for v in _j.load(open('names_src.json')).values()) if os.path.exists('names_src.json') else set()
    byfile=collections.defaultdict(list)
    for r in rows:
        if r['src']=='txt' and r['cat'] in ('TEXT','NAMEGEN'):
            f,l,s=r['id'].rsplit(':',2); k=tr(r['en'],r['cat'],'txt')
            if k: byfile[f].append((int(l),int(s),r['en'],k))
    if os.path.exists('txt_segs2.json'):
        TMt=TMS['txt']
        for sg in _j.load(open('txt_segs2.json')):
            en=sg['en']; k=words_map.get(en) or TMt.get(en) or names_map.get(en)
            if k: byfile[sg['file']].append((sg['line'],sg['s'],en,k))
    for nf in NAMEFILES: byfile.setdefault(nf+'.txt',[])
    for f in lineov: byfile.setdefault(f,[])
    for f in subov: byfile.setdefault(f,[])
    changed=[]
    KEEPF=set(_j.load(open('txt_keep_files.json'))) if os.path.exists('txt_keep_files.json') else set()
    for f,items in byfile.items():
        if f in KEEPF: continue
        L,enc,nl=readlines(ORIG_TEXT+f)
        ov=lineov.get(f,{}); skip=set()
        for i,l in enumerate(L):
            if l.strip() in ov: L[i]=l.replace(l.strip(),ov[l.strip()]); skip.add(i)
        spans=collections.defaultdict(list); keep=[]
        for it in items:
            l,s,en,k=it; e=s+len(en)
            if l in skip or any(not(e<=a or s>=bb) for a,bb in spans[l]): continue
            spans[l].append((s,e)); keep.append(it)
        for l,s,en,k in sorted(keep,key=lambda x:(x[0],-x[1])):
            assert L[l][s:s+len(en)]==en,(f,l,s,en)
            L[l]=L[l][:s]+k+L[l][s+len(en):]
        if f[:-4] in NAMEFILES:
            for i,l in enumerate(L):
                st=l.strip()
                if st and not st.startswith('`') and st in names_map: L[i]=l.replace(st,names_map[st],1)
        for a_,b_ in subov.get(f,[]):
            for i_,l_ in enumerate(L):
                if a_ in l_ and not l_.lstrip().startswith('`'): L[i_]=l_.replace(a_,b_)
        for pos,txt in sorted(lineins.get(f,[]),reverse=True): L.insert(pos,txt)
        open(outdir+'/media/Text/'+f,'wb').write(nl.join(L).encode('utf8'))
        changed.append(f)
    # AddImg.txt display-name field (file / id / name)
    if os.path.exists('addimg_ko.tsv'):
        amap=dict(l.rstrip('\n').split('\t') for l in open('addimg_ko.tsv',encoding='utf-8') if '\t' in l)
        bcl={}
        for r in rows:
            if r['src']=='bc': bcl.setdefault(r['en'].lower(),[]).append(r)
        L,enc,nl=readlines(ORIG_TEXT+'AddImg.txt'); st=0; n=0
        for i,l in enumerate(L):
            s=l.split('`')[0].strip()
            if not s: continue
            if st==0: st=1
            elif st==1:
                if s.isdigit(): st=2
            elif st==2:
                st=0
                if s=='#' or s.startswith('#') or s.startswith('UI_'): continue
                k=amap.get(s) or TMS['txt'].get(s) or words_map.get(s) or TMLS['txt'].get(s.lower())
                if not k: continue
                bad=False
                for r in bcl.get(s.lower(),[]):
                    if r['cat']=='KEEP' or (r['cat'] in ('CMPKEY','TEXT_LINKED') and tr(r['en'],r['cat'],'bc')!=k): bad=True
                if bad: continue
                L[i]=l.replace(s,k,1); n+=1
        open(outdir+'/media/Text/AddImg.txt','wb').write(nl.join(L).encode('utf8')); changed.append('AddImg.txt')
        print('addimg names',n)
    if os.path.isdir('full_ko'):
        for fn in os.listdir('full_ko'):
            _sh.copy(os.path.join('full_ko',fn),outdir+'/media/Text/'+fn); changed.append(fn)
    ex='nm/work_5/story_ko'
    if os.path.exists(ex):
        os.makedirs(outdir+'/media/Images/openingstoryframes',exist_ok=True)
        for fn in os.listdir(ex): _sh.copy(os.path.join(ex,fn),outdir+'/media/Images/openingstoryframes/'+fn)
    if os.path.exists('txt_post.json'):
        for f_,a_,b_ in _j.load(open('txt_post.json',encoding='utf-8')):
            p_=outdir+'/media/Text/'+f_
            if not os.path.exists(p_): _sh.copy(ORIG_TEXT+f_,p_)
            t_=open(p_,'rb').read().decode('utf8')
            assert a_ in t_,(f_,a_)
            open(p_,'wb').write(t_.replace(a_,b_).encode('utf8'))
            if f_ not in changed: changed.append(f_)
    print('bytecode strings replaced',len(repl),'txt files',len(changed),'instr patches',len(patches))
    return repl,changed
if __name__=='__main__': build(sys.argv[1])
