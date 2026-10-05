import os as _o
import re,json,glob,os
from txtextract import readlines
WORDLIST=['hurricanum','HumanEnders','SmellsAll','SmellsGood','SmellsBad','DiseaseStarters','DiseaseEnders','DiseaseMutators','Plants','names-of-plants2','Greek Letters','ArtCol','EarthCityCountry','treesbynumber','WeaponEnergies','WeaponTypes','EngEne','ScanEne','SheEne','WarpKinds','ScanKinds','SheKind','Menial','MenialQual','Rarity','suits','TempKind','Uses','Wreckage','opinion','Attitudes','MeleeWeaponEnergies','HandWepEnergies','TransMeth','WhereYouKeepIt','ThingsArtifactsDo','Crimes','VillainPowers','franchise','RealShipJobs','PartNames']
NUMPREFIX=['monsterpowerlist','RacComPriUP','RacComPriDN','racialinteractionteasers']
CSVNAME={'names-of-plants':1,'Essence By Plant':1,'Hand_Wep_Mods':1,'Hand_Wep_New':1}
out=[]
for f in WORDLIST+NUMPREFIX+list(CSVNAME):
    p=_o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))),'game','full','Text',f+'.txt')
    if not os.path.exists(p): print('missing',f); continue
    L,enc,nl=readlines(p)
    for i,l in enumerate(L):
        if not l.strip() or l.startswith('`') or not re.search('[A-Za-z]{2}',l): continue
        if f in WORDLIST:
            s=len(l)-len(l.lstrip()); e=len(l.rstrip()); 
            # stop at inline comment
            m=re.search(r'\s`',l); 
            if m and m.start()>s: e=len(l[:m.start()].rstrip())
            out.append({'file':f+'.txt','line':i,'s':s,'e':e,'en':l[s:e]})
        elif f in NUMPREFIX:
            m=re.match(r'^((?:\s*-?\d+\s*;)+)\s*',l)
            if m and re.search('[A-Za-z]{2}',l[m.end():]):
                s=m.end(); e=len(l.rstrip()); out.append({'file':f+'.txt','line':i,'s':s,'e':e,'en':l[s:e]})
        else:
            parts=l.split(','); k=CSVNAME[f]
            if len(parts)>k and re.search('[A-Za-z]{2}',parts[k]) and re.match(r'^\s*\d+\s*$',parts[0]):
                s=len(','.join(parts[:k]))+1; e=s+len(parts[k])
                v=l[s:e]; ls=s+len(v)-len(v.lstrip()); le=ls+len(v.strip())
                out.append({'file':f+'.txt','line':i,'s':ls,'e':le,'en':l[ls:le]})
json.dump(out,open('txt_segs2.json','w'),ensure_ascii=False)
import collections
print(len(out),collections.Counter(o['file'] for o in out).most_common(60))
print(len({o['en'] for o in out}))
