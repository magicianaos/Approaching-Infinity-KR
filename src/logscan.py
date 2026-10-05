# 사용: python3 logscan.py <AI_DB 파일> <popupmem 파일...>
import re,sys
EN=re.compile(r"[A-Za-z][A-Za-z' -]{2,}")
IGN=re.compile(r"^(HP|XP|SPD|EMP|DLC|IBOL|FPS)$")
seen=set()
for f in sys.argv[1:]:
    for l in open(f,encoding='utf8',errors='replace'):
        l=l.rstrip('\n')
        if 'AI_DB' in f and not l[:6] in ('[MSG] ','[FLT] ','[BUB] '): continue
        body=re.sub(r'&\d+','',l[6:] if l[:1]=='[' else l)
        ws=[w.strip() for w in EN.findall(body) if not IGN.match(w.strip())]
        if ws and body not in seen:
            seen.add(body); print(f.split('/')[-1][:12],'|',body[:200],'  <=',ws[:5])
