from __future__ import annotations
from fractions import Fraction
from pathlib import Path
from collections import deque
import heapq, json

WHITE=-1; BLACK=0; GRAY=1
ROOT=Path(__file__).resolve().parent

def parse(path):
    a=list(map(int,path.read_text().strip().split(','))); out=[]; i=0
    while i<len(a):
        n=5 if a[i]==1 else 6
        out.append(tuple(a[i:i+n])); i+=n
    return out

def line_cells(x1,y1,x2,y2):
    dx=x2-x1; dy=y2-y1
    for y in range(min(y1,y2),max(y1,y2)):
      for x in range(min(x1,x2),max(x1,x2)):
        lo=[Fraction(0)]; hi=[Fraction(1)]
        if dx>0: lo.append(Fraction(x-x1,dx)); hi.append(Fraction(x+1-x1,dx))
        else: lo.append(Fraction(x+1-x1,dx)); hi.append(Fraction(x-x1,dx))
        if dy>0: lo.append(Fraction(y-y1,dy)); hi.append(Fraction(y+1-y1,dy))
        else: lo.append(Fraction(y+1-y1,dy)); hi.append(Fraction(y-y1,dy))
        if max(lo)<min(hi): yield x,y

def draw(shapes):
    g={}
    for s in shapes:
      t,c=s[:2]
      if t==0:
        _,_,x1,y1,x2,y2=s
        for y in range(y1,y2+1):
          for x in range(x1,x2+1): g[x,y]=c
      elif t==1:
        _,_,cx,cy,r=s
        for y in range(cy-r,cy+r):
          for x in range(cx-r,cx+r):
            dx=0 if x<=cx<=x+1 else min(abs(cx-x),abs(cx-(x+1)))
            dy=0 if y<=cy<=y+1 else min(abs(cy-y),abs(cy-(y+1)))
            if dx*dx+dy*dy<r*r: g[x,y]=c
      else:
        for p in line_cells(*s[2:]): g[p]=c
    return g

def box(g):
    xs=[x for x,y in g]; ys=[y for x,y in g]
    return min(xs),min(ys),max(xs),max(ys)

def comps(g):
    seen=set(); best=[0,0]
    for p,c in g.items():
      if p in seen: continue
      q=deque([p]); seen.add(p); n=0
      while q:
        x,y=q.popleft(); n+=1
        for z in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
          if z not in seen and g.get(z,WHITE)==c: seen.add(z); q.append(z)
      best[c]=max(best[c],n)
    return best

def path(g):
    x0,y0,x1,y1=box(g); a=(x0,y0); b=(x1,y1); c=g.get(a,WHITE)
    lim=(x0-1,y0-1,x1+1,y1+1); d={a:(0,1)}; pq=[(0,1,*a)]
    while pq:
      cost,n,x,y=heapq.heappop(pq)
      if d.get((x,y))!=(cost,n): continue
      if (x,y)==b: return cost,n,a,b,c
      for z in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
        xx,yy=z
        if not(lim[0]<=xx<=lim[2] and lim[1]<=yy<=lim[3]): continue
        nd=(cost+(g.get(z,WHITE)!=c),n+1)
        if nd<d.get(z,(10**18,10**18)): d[z]=nd; heapq.heappush(pq,(nd[0],nd[1],xx,yy))

expected=json.loads((ROOT/'answers.json').read_text())
actual={}
for p in sorted(ROOT.glob('data*.txt')):
    s=parse(p); name=p.name
    if name.startswith('data1'):
      actual[name]={'rectangles':sum(x[0]==0 for x in s),'circles':sum(x[0]==1 for x in s),'line_segments':sum(x[0]==2 for x in s)}
    else:
      g=draw(s)
      if name.startswith('data2'):
        actual[name]={'lower_right_cell':list(box(g)[2:])}
      elif name.startswith('data3'):
        actual[name]={'black_cells':sum(v==0 for v in g.values()),'gray_cells':sum(v==1 for v in g.values())}
      elif name.startswith('data4'):
        b0,b1=comps(g); actual[name]={'largest_black_component':b0,'largest_gray_component':b1}
      else:
        cost,n,a,b,c=path(g); actual[name]={'minimum_different_color_cells':cost,'shortest_length':n,'a':list(a),'b':list(b),'color_of_a':('white' if c==-1 else 'black' if c==0 else 'gray')}

assert actual==expected, (actual,expected)
print('All 16 files match answers.json')
