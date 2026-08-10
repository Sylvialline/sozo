from __future__ import annotations
from collections import Counter, defaultdict
from itertools import batched
from typing import Iterable
from pathlib import Path
import sys

PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PATH))

from utils import Exam, read_data

sys.setrecursionlimit(5000)

def rd(name: str) -> Iterable[int]:
    return map(int, read_data(name).split(','))


exam = Exam(reader=rd)


def union(tx, ty):
    return (
        min(tx[0], ty[0]),
        max(tx[1], ty[1])
    )

def intersection(tx, ty):
    return (
        max(tx[0], ty[0]),
        min(tx[1], ty[1])
    )

def is_in(tl, tr):
    if tl is None or tr is None:
        return True
    return tr[0]<=tl[0] and tl[1]<=tr[1]

def var_str(var):
    return f"x{var}"

def asn_str(item):
    return f"x{item[0]} = x{item[1]}"


class Ranges:
    def __init__(self, data: Iterable[int]):
        self.data = {
            n: (sn, tn)
            for n, sn, tn in batched(data, 3)
        }

    @staticmethod
    def item_str(item):
        return f"x{item[0]} in [{item[1][0]}, {item[1][1]}]"
        
    def max_range(self):
        range = max(r-l for l, r in self.data.values())
        res = []
        for item in self.data.items():
            if item[1][1] - item[1][0] == range:
                res.append(self.item_str(item))
        return res

class Assignments:
    def __init__(self, data: Iterable[int]):
        self.data = [
            (m, n)
            for m, n in batched(data, 2)
        ]

    def most_frequent_left_operand(self):
        c = Counter(l for l,r in self.data)
        times = max(c.values())
        return times, [var_str(k) for k,v in c.items() if v == times]

class Program:
    def __init__(self, inq: Ranges, asn: Assignments):
        self.inq = inq
        self.asn = asn
        self.now = {}
        self.during = {}
        self.run()

    def run(self):
        for l, r in self.asn.data:
            if r not in self.during:
                self.during[r] = self.now[r] = self.inq.data.get(r, (0, 100))

            self.now[l] = self.now[r]
            if l not in self.during:
                self.during[l] = self.now[l]
            else:
                self.during[l] = union(self.during[l], self.now[l])

    def get_end(self, vars):
        return {var_str(k):(self.now.get(k, 'Undefined')) for k in vars}

    def get_during(self, vars):
        return {var_str(k):(self.during.get(k, 'Undefined')) for k in vars}

    def vars_inconsistent(self):
        return [var_str(k) for k,v in self.during.items() if not is_in(v, self.inq.data.get(k))]

    def asns_inconsistent(self):
        res = {a for a in self.asn.data if not is_in(self.inq.data.get(a[1]), self.inq.data.get(a[0]))}
        return list(map(asn_str, res))

class Graph:
    def __init__(self, data: dict[int, list]):
        # 不要使用defaultdict存储图
        self.data = data

    def compress(self):
        "返回 (缩点后的图, {new: [old]}, {old: new})"
        dfn, low = {}, {}
        ti = 0
        s, ins = [], set()
        scc = 0
        new_g: dict[int, list] = {}
        own = defaultdict(list)
        belong = {}
        def dfs(u):
            nonlocal ti, scc
            ti += 1
            dfn[u] = low[u] = ti
            s.append(u)
            ins.add(u)

            #fixed: 不能在外层遍历dict时改变大小；defaultdict索引写法容易被隐式修改
            #当前写法已摒弃defaultdict，改成初始化时确定好所有keys，相当于指定了图中有哪些节点
            for v in self.data[u]:
                if v not in dfn:
                    dfs(v)
                    low[u] = min(low[u], low[v])
                elif v in ins:
                    low[u] = min(low[u], dfn[v])

            print(f"dfn[{u}]={dfn[u]}, low[{u}]={low[u]}")

            if dfn[u] == low[u]:
                scc += 1
                new_g[scc] = [] # 相当于创建节点
                while True:
                    v = s.pop()
                    print(f"stack {u, v}")
                    ins.remove(v)
                    belong[v] = scc
                    own[scc].append(v)
                    if v == u:
                        break

        for u in self.data.keys():
            if u not in dfn:
                dfs(u)

        for u, vs in self.data.items():
            for v in vs:
                bu, bv = belong[u], belong[v]
                if bu != bv:
                    new_g[bu].append(bv)

        return Graph(new_g), own, belong

    def top_sort(self):
        in_d = Counter()
        for u, vs in self.data.items():
            in_d.update(vs)

        # print(in_d)
        s = [u for u in self.data if in_d[u] == 0]
        # print(s)
        res = []

        while s:
            u = s.pop()
            res.append(u)
            for v in self.data[u]:
                in_d[v] -= 1
                if in_d[v] == 0:
                    s.append(v)

        return reversed(res)

def define(inq: Ranges, asn: Assignments):
    keys = {n for pair in asn.data for n in pair}
    g = {k:[] for k in keys}

    defs = {}
    for l, r in asn.data:
        g[r].append(l)

    g = Graph(g)
    cg, own, belong = g.compress()
    rg = {}
    
    for w, us in own.items():
        r = None
        for u in us:
            if u in inq.data:
                if not r:
                    r = inq.data[u]
                elif r != inq.data[u]:
                    return None

        if r:
            rg[w] = r
            for u in us:
                if u not in inq.data:
                    defs[u] = r

    # print(g.data)
    # print(own, belong)
    # print(cg.data)
    # print(list(cg.top_sort()))
        
    for w in cg.top_sort():
        if w not in rg:
            tmp = (0, 999)
            for m in cg.data[w]:
                tmp = intersection(tmp, rg[m])
                if tmp[1] < tmp[0]:
                    return None
            rg[w] = tmp
            for u in own[w]:
                assert u not in inq.data
                defs[u] = tmp
        else:
            for m in cg.data[w]:
                if not is_in(rg[w], rg[m]):
                    return None

    for u in g.data:
        b1 = u in inq.data
        b2 = u in defs
        assert b1 ^ b2

    return {var_str(k):v for k,v in defs.items()}

def define_using_graph_utils(inq: Ranges, asn: Assignments):
    from utils import Graph
    g = Graph.from_edges(((r,l) for l,r in asn.data))
    c = g.condense()
    result = {}
    dp = {}
    for w in c.graph.topological_sort(reverse=True):
        inter = None
        for u in c.members[w]:
            if u in inq.data:
                if inter is None:
                    inter = inq.data[u]
                elif inter != inq.data[u]:
                    return None

        if inter is None:
            inter = (0, 999)
            for m in c.graph.neighbors(w):
                inter = intersection(inter, dp[m])
                if inter[0] > inter[1]:
                    return None
            dp[w] = inter
            for u in c.members[w]:
                result[u] = inter
        else:
            for m in c.graph.neighbors(w):
                if not is_in(inter, dp[m]):
                    return None
            dp[w] = inter
            for u in c.members[w]:
                if u not in inq.data:
                    result[u] = inter

    return {var_str(k):v for k,v in sorted(result.items())}

        

@exam.task
def task1(data):
    inqs = Ranges(data)
    res = inqs.max_range()
    return res

@exam.task
def task2(data):
    asns = Assignments(data)
    times, res = asns.most_frequent_left_operand()
    return {
        'times': times,
        'variables': res
    }

@exam.task
def task3(data1, data2):
    prog = Program(asn=Assignments(data1), inq=Ranges(data2))
    return prog.get_end([31, 41, 51])

@exam.task
def task4(data1, data2):
    prog = Program(asn=Assignments(data1), inq=Ranges(data2))
    return prog.get_during([31, 41, 51])

@exam.task
def task5(data1, data2):
    prog = Program(asn=Assignments(data1), inq=Ranges(data2))
    return prog.vars_inconsistent()

@exam.task
def task6(data1, data2):
    prog = Program(asn=Assignments(data1), inq=Ranges(data2))
    return prog.asns_inconsistent()

@exam.task
def task7(data1, data2):
    # res = define(asn=Assignments(data1), inq=Ranges(data2))
    res = define_using_graph_utils(asn=Assignments(data1), inq=Ranges(data2))
    return {
        'definitions': res
    }

if __name__ == "__main__":
    exam.execute(output=True)
 