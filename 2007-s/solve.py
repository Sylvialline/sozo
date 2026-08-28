from itertools import combinations
import math
from pathlib import Path
import sys

HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"
OUTPUT = HERE/"output"
sys.path.insert(0, str(ROOT))

from utils import AnswerBook, Graph, KeyedDSU, DSU
from utils.itertools_ext import batched


edges = list(batched(map(int, (DATA/"edges.txt").read_text().split()), 2))

def component_sizes(g: Graph[int]):
    dsu = KeyedDSU(g.nodes())
    for u, v in g.edges():
        if u < v:
            dsu.union(u, v)
    roots = {dsu.find(u) for u in g}
    return sorted((dsu.size(root) for root in roots), reverse=True)

def cluster_coefficients(g: Graph[int], nodes: list[int]) -> list[float]:
    edges = set(g.edges())
    res = []
    for u in nodes:
        neighbors = list(g.neighbors(u))
        pairs = math.comb(len(neighbors), 2)
        cnt = sum((v, w) in edges for v, w in combinations(neighbors, 2))
        coeff = cnt / pairs if pairs else 0
        res.append(coeff)
    return res

def average_cluster_coefficient(g: Graph[int]) -> float:
    coeffs = cluster_coefficients(g, list(g))
    return sum(coeffs) / len(coeffs)

def diameter_with_average(g: Graph[int]) -> tuple[int, float]:
    records = {}
    for u in g:
        dis = g.bfs_distances(u)
        for v, d in dis.items():
            if u >= v:
                continue
            records[(u, v)] = d
    vals = list(records.values())
    return max(vals), sum(vals) / len(vals)


def make_g2():
    n = 100
    g = Graph.from_nodes(range(1, n+1))
    for u, v in edges[:181]:
        g.add_undirected_edge(u, v)
    return g

def make_n_g3():
    tot = 100
    dsu = DSU(tot + 1)
    left = tot - 1
    for n, e in enumerate(edges, start=1):
        left -= dsu.union(e[0], e[1])
        if left == 0:
            return n, Graph.from_edges(edges[:n], undirected=True)
    assert False

def make_g4():
    n, g = make_n_g3()
    for u, v in edges[n:n+100]:
        g.add_undirected_edge(u, v)
    return g

def task2():
    answer = {}
    g2 = make_g2()
    n, g3 = make_n_g3()
    g4 = make_g4()
    answer["connected components of g2"] = component_sizes(g2)
    answer["cluster coefficients of 1 to 10"] = cluster_coefficients(g2, list(range(1, 11)))
    answer["average cluster coefficient of g2"] = average_cluster_coefficient(g2)
    answer["2.4"] = {
        "n": n,
        "avg coeff of g3": average_cluster_coefficient(g3)
    }
    answer["avg coeff of g4"] = average_cluster_coefficient(g4)
    return answer

def task3():
    _, g3 = make_n_g3()
    g4 = make_g4()
    u, v = 27, 63
    g3_uv = g3.bfs_distances(u)[v]
    g4_uv = g4.bfs_distances(u)[v]
    g3_avg = diameter_with_average(g3)[1]
    g4_avg = diameter_with_average(g4)[1]
    return dict(g3_uv=g3_uv, g4_uv=g4_uv, g3_avg=g3_avg, g4_avg=g4_avg)

def task4():
    n, g = make_n_g3()
    cur = diameter_with_average(g)[0]
    res = [(n, cur)]
    for i in range(n, len(edges)):
        u, v = edges[i]
        g.add_undirected_edge(u, v)
        nxt = diameter_with_average(g)[0]
        if nxt < cur:
            cur = nxt
            res.append((i+1, cur))
    return res

book = AnswerBook(base_dir=OUTPUT)

book.run('2', task2)
book.run('3', task3)
book.run('4', task4)
 
book.write_json()

    