# from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from itertools import count
import json
from pathlib import Path
import sys
from typing import Optional
HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"
sys.path.insert(0, str(ROOT))

from utils import PriorityQueue

@dataclass
class Node:
    weight: int

@dataclass
class Leaf(Node):
    char: str

@dataclass
class Internal(Node):
    left: Node
    right: Node

def dfs(u: Node, table: dict[str, str], cur = ''):
    match u:
        case Leaf(_, char):
            table[char] = cur
        case Internal(_, left, right):
            dfs(left , table, cur + '0')
            dfs(right, table, cur + '1')
            

text = Path(DATA/"q21.txt").read_text()
counter = Counter(text)
counter['NL'] = counter.pop('\n')
counter['SP'] = counter.pop(' ')
q = PriorityQueue[Node]()

order = count()
for char, cnt in sorted(counter.items()):
    q.push(Leaf(cnt, char), priority=(cnt, next(order)))

order = count(-1, -1)
while len(q) >= 2:
    (pu, u), (pv, v) = q.pop_with_priority(), q.pop_with_priority()
    if pu < pv:
        u, v = v, u
    node = Internal(u.weight + v.weight, u, v)
    q.push(node, priority=(node.weight, next(order)))

root = q.pop()
table = {}
dfs(root, table)
print(json.dumps(table, indent=2))

average_bits = sum(len(table[char]) * cnt for char, cnt in counter.items()) / counter.total()
print(f"{average_bits = :.3f}")