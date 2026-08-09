from pathlib import Path
from collections import Counter

def read_ints(path):
    s=Path(path).read_text(encoding="utf-8").strip()
    return [] if not s else list(map(int,s.split(",")))
def pairs(path):
    a=read_ints(path); return list(zip(a[0::2],a[1::2]))
def triples(path):
    a=read_ints(path); return list(zip(a[0::3],a[1::3],a[2::3]))
def constraints(path):
    d={}
    for n,s,t in triples(path): d[n]=(s,t)
    return d

def solve1(path):
    c=constraints(path); w=max(t-s for s,t in c.values())
    return [(f"x{n}",s,t) for n,(s,t) in sorted(c.items()) if t-s==w]

def solve2(path):
    cnt=Counter(m for m,_ in pairs(path)); mx=max(cnt.values())
    return [f"x{n}" for n in sorted(cnt) if cnt[n]==mx]

def analyze(program,inequality):
    c=constraints(inequality); cur={}; hist={}; appeared=set()
    def init(n):
        if n not in cur:
            cur[n]=c.get(n,(0,100)); hist[n]=cur[n]
        return cur[n]
    def add(n,v):
        if n in hist:
            a,b=hist[n]; hist[n]=(min(a,v[0]),max(b,v[1]))
        else: hist[n]=v
    ps=pairs(program)
    for m,n in ps:
        appeared|={m,n}; v=init(n); cur[m]=v; add(m,v)
    return c,ps,cur,hist,appeared

def solve3(program,inequality):
    _,_,cur,_,app=analyze(program,inequality)
    return {f"x{n}":("Undefined" if n not in app else cur[n]) for n in (31,41,51)}

def solve4(program,inequality):
    _,_,_,hist,app=analyze(program,inequality)
    return {f"x{n}":("Undefined" if n not in app else hist[n]) for n in (31,41,51)}

def solve5(program,inequality):
    c,_,_,hist,app=analyze(program,inequality); out=[]
    for n in sorted(app):
        if n in c:
            a,b=hist[n]; s,t=c[n]
            if a<s or t<b: out.append(f"x{n}")
    return out or "None"

def solve6(program,inequality):
    c=constraints(inequality); out=[]; seen=set()
    for m,n in pairs(program):
        if (m,n) in seen: continue
        seen.add((m,n))
        if m in c and n in c:
            sm,tm=c[m]; sn,tn=c[n]
            if not(sm<=sn<=tn<=tm): out.append(f"x{m}=x{n}")
    return out or "None"

def solve7(program,inequality):
    c=constraints(inequality); ps=pairs(program)
    vs=sorted({x for p in ps for x in p}); reach=[0]*1000
    for v in vs: reach[v]|=1<<v
    for m,n in ps: reach[m]|=1<<n
    for k in vs:
        bit=1<<k; rk=reach[k]
        for i in vs:
            if reach[i]&bit: reach[i]|=rk

    fixed=[v for v in vs if v in c]
    for u in fixed:
        su,tu=c[u]; ru=reach[u]
        for v in fixed:
            if (ru>>v)&1:
                sv,tv=c[v]
                if not(su<=sv<=tv<=tu): return "None"

    out={}
    for x in vs:
        if x in c: continue
        anc=[u for u in fixed if (reach[u]>>x)&1]
        out[x]=(0,999) if not anc else (
            max(c[u][0] for u in anc),
            min(c[u][1] for u in anc)
        )
    allc=dict(c); allc.update(out)
    for m,n in ps:
        sm,tm=allc[m]; sn,tn=allc[n]
        if not(sm<=sn<=tn<=tm): return "None"
    return [(f"x{n}",s,t) for n,(s,t) in sorted(out.items())]
