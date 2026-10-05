# 라틴풍 가상 단어 → 한글 음차
import re
CHO='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
JUNG='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
JONG=['']+list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')
def comp(c,v,f=''):
    return chr(0xAC00+(CHO.index(c)*21+JUNG.index(v))*28+JONG.index(f))
VOW='aeiouy'
# consonant token -> (initial jamo, coda jamo or None, standalone syllable)
CONS={'b':('ㅂ','ㅂ','브'),'c':('ㅋ','ㄱ','크'),'k':('ㅋ','ㄱ','크'),'ck':('ㅋ','ㄱ','크'),'ch':('ㅋ','ㄱ','크'),
 'd':('ㄷ',None,'드'),'f':('ㅍ',None,'프'),'ph':('ㅍ',None,'프'),'g':('ㄱ','ㄱ','그'),'h':('ㅎ',None,''),
 'j':('ㅈ',None,'지'),'l':('ㄹ','ㄹ','ㄹ'),'m':('ㅁ','ㅁ','ㅁ'),'n':('ㄴ','ㄴ','ㄴ'),'ng':('ㅇ','ㅇ','ㅇ'),
 'p':('ㅍ','ㅂ','프'),'r':('ㄹ',None,''),'s':('ㅅ',None,'스'),'sh':('ㅅ',None,'시'),'t':('ㅌ','ㅅ','트'),'th':('ㅌ',None,'스'),
 'v':('ㅂ',None,'브'),'w':('ㅇ',None,'우'),'x':('ㅋ',None,'크스'),'z':('ㅈ',None,'즈'),'q':('ㅋ',None,'크'),'y':('ㅇ',None,'이')}
VMAP={'a':'ㅏ','e':'ㅔ','i':'ㅣ','o':'ㅗ','u':'ㅜ','y':'ㅣ','ae':'ㅐ','oe':'ㅚ','ee':'ㅣ','oo':'ㅜ','ai':'ㅏ이','ei':'ㅔ이','au':'ㅏ우','ou':'ㅜ','eu':'ㅔ우'}
YV={'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅐ':'ㅒ','ㅣ':'ㅣ'}
WV={'ㅏ':'ㅘ','ㅔ':'ㅞ','ㅣ':'ㅟ','ㅗ':'ㅝ','ㅐ':'ㅙ','ㅜ':'ㅜ'}
def tokens(w):
    w=w.lower(); w=re.sub(r"[^a-z]","",w)
    out=[];i=0
    while i<len(w):
        c=w[i]
        if c in 'aeiou' or (c=='y' and (i+1>=len(w) or w[i+1] not in 'aeiou') and i>0):
            two=w[i:i+2]
            if two in ('ae','oe','ee','oo','ai','ei','au','ou','eu'): out.append(('V',two)); i+=2; continue
            out.append(('V',c)); i+=1; continue
        two=w[i:i+2]
        if two in ('ch','ph','sh','th','ck','ng') and not (two=='ng' and i+2<len(w)):
            out.append(('C',two)); i+=2; continue
        if two=='qu': out.append(('C','q')); out.append(('W','')); i+=2; continue
        if i+1<len(w) and w[i+1]==c and c!='l': i+=1; continue  # double consonant collapse
        out.append(('C',c)); i+=1
    return out
def translit(word):
    t=tokens(word)
    syl=[]  # list of [cho, jung, jong] or str
    i=0
    def addv(ch,v,glide=None):
        vs=VMAP[v]
        first=vs[0]; rest=vs[1:]
        if glide=='y': first=YV.get(first,first)
        if glide=='w': first=WV.get(first,first)
        syl.append([ch,first,''])
        if rest=='이': syl.append(['ㅇ','ㅣ',''])
        if rest=='우': syl.append(['ㅇ','ㅜ',''])
    while i<len(t):
        k,v=t[i]
        if k=='V':
            addv('ㅇ',v); i+=1; continue
        if k=='W':  # after q
            i+=1; continue
        # consonant
        nxt=t[i+1] if i+1<len(t) else None
        glide=None
        if v=='q' and nxt and nxt[0]=='W':
            if i+2<len(t) and t[i+2][0]=='V':
                addv('ㅋ',t[i+2][1],'w'); i+=3; continue
            syl.append(['ㅋ','ㅜ','']); i+=2; continue
        if nxt and nxt[0]=='V':
            vv=nxt[1]
            ini=CONS[v][0]
            if v=='c' and vv[0] in 'eiy': ini='ㅅ'
            if v=='g' and vv[0] in 'eiy': ini='ㅈ'
            if v=='y': addv('ㅇ',vv,'y'); i+=2; continue
            if v=='w': addv('ㅇ',vv,'w'); i+=2; continue
            if v=='sh': addv('ㅅ',vv,'y' if vv[0] in 'aou' else None); i+=2; continue
            if v=='x':
                if syl and isinstance(syl[-1],list) and syl[-1][2]=='': syl[-1][2]='ㄱ'
                else: syl.append(['ㅋ','ㅡ',''])
                addv('ㅅ',vv); i+=2; continue
            if v=='l' and syl and isinstance(syl[-1],list) and syl[-1][2]=='' and (t[i-1][0]=='V' or syl[-1][1]=='ㅡ'):
                syl[-1][2]='ㄹ'
            addv(ini,vv); i+=2; continue
        # consonant not before vowel
        coda=CONS[v][1]
        prev_open= bool(syl) and isinstance(syl[-1],list) and syl[-1][2]=='' and i>0 and t[i-1][0]=='V'
        prev_open_any= bool(syl) and isinstance(syl[-1],list) and syl[-1][2]==''
        if v=='r':
            syl.append(['ㄹ','ㅡ','']); i+=1; continue
        if v=='h': i+=1; continue
        before_liq = nxt is not None and nxt[0]=='C' and nxt[1] in ('l','r')
        if v=='t' or before_liq: coda=None if v not in ('l','m','n','ng') else coda
        if coda and prev_open and not (v=='t' and nxt is None):
            syl[-1][2]=coda; i+=1; continue
        if v in ('l','m','n','ng') and prev_open_any:
            syl[-1][2]=CONS[v][1]; i+=1; continue
        s=CONS[v][2]
        if v=='l': s='ㄹ'
        STD={'브':['ㅂ','ㅡ',''],'크':['ㅋ','ㅡ',''],'드':['ㄷ','ㅡ',''],'프':['ㅍ','ㅡ',''],'그':['ㄱ','ㅡ',''],'지':['ㅈ','ㅣ',''],
             '스':['ㅅ','ㅡ',''],'시':['ㅅ','ㅣ',''],'트':['ㅌ','ㅡ',''],'즈':['ㅈ','ㅡ',''],'이':['ㅇ','ㅣ',''],'우':['ㅇ','ㅜ','']}
        if s in STD and v!='x':
            syl.append(list(STD[s])); i+=1; continue
        if s in ('ㄹ','ㅁ','ㄴ','ㅇ'):
            if syl and isinstance(syl[-1],list) and syl[-1][2]=='': syl[-1][2]=s
            else: syl.append(['ㅇ','ㅡ',s])
        elif s: 
            if v=='x' and prev_open: syl[-1][2]='ㄱ'; syl.append('스')
            else: syl.append(s)
        i+=1
    out=''
    for s in syl:
        if isinstance(s,str):
            out+=s
        else: out+=comp(*s)
    return out
if __name__=='__main__':
    import sys
    for w in sys.argv[1:]: print(w,translit(w))
