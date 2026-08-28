from collections import deque
from pathlib import Path
import sys

HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"
OUTPUT = HERE/"output"
sys.path.insert(0, str(ROOT))

from utils import read_data

State = tuple[int | str, ...]

I: State = (
     0, 1, 2, 3,
     4, 5, 6, 7,
           8, 9,10,11,
          12,13,14,15,
                16,17,18,19,
                20,21,22,23,
)

R: State = (
     0, 8, 6, 2,
     4, 9, 7, 3,
          10,11,19,23,
          12,13,14,15,
                16,17,18, 1,
                20,21,22, 5,
)

U: State = (
     4, 0,22, 3,
     5, 1,23, 7,
           2, 9,10,11,
           6,13,14,15,
                16,17,18,19,
                 8,12,20,21,
)

F: State = (
     0, 1, 2, 3,
    16,20, 4, 5,
          12, 8, 6,11,
          13, 9, 7,15,
                10,17,18,19,
                14,21,22,23,
)

mp = dict(R=R, U=U, F=F)

init_state = (
    'p','p','w','w',
    'p','p','w','w',
            'g','g','r','r',
            'g','g','r','r',
                    'y','y','b','b',
                    'y','y','b','b',
)

def state_to_str(state):
    s = []
    for i in range(len(state)):
        s.append(state[i])
        if (i+1) % 4 == 0:
            s.append('\n')
    return ''.join(s)


def mul(p1, p2):
    return tuple(p1[p2[i]] for i in range(24))

def inv(p):
    return tuple(p.index(i) for i in range(24))

# def pow(p, n):
#     assert n >= 1
#     res = p
#     n -= 1
#     while n:
#         if n & 1:
#             res = mul(res, p)
#         p = mul(p, p)
#         n >>= 1
#     return res

moves = {
    'R1': R,
    'R2': mul(R, R),
    'R3': inv(R),
    'U1': U,
    'U2': mul(U, U),
    'U3': inv(U),
    'F1': F,
    'F2': mul(F, F),
    'F3': inv(F),
}

def task42():
    state_r = mul(init_state, R)
    state_u = mul(init_state, U)
    state_f = mul(init_state, F)
    print('U:')
    print(state_to_str(state_u))
    print('R:')
    print(state_to_str(state_r))
    print('F:')
    print(state_to_str(state_f))

def task43():
    with (DATA/"rotseq.txt").open() as f:
        for line in f.readlines():
            state = init_state
            for op in line.split():
                state = mul(state, moves[op])
            print(f"state after {line.strip()}:")
            print(state_to_str(state))

def parse_state(data: str):
    return tuple(data.split())


def all_states_in_n_steps(n: int):
    path_book: dict[State, list[str]] = {init_state:[]}
    q = deque([init_state])
    while q:
        u = q.popleft()
        pathu = path_book[u]
        if len(pathu) == n:
            continue
        for name, move in moves.items():
            v = mul(u, move)
            if v not in path_book:
                path_book[v] = pathu + [name]
                q.append(v)

    return path_book

def task5():
    data_dict = read_data("data")
    print(data_dict)
    path_book = all_states_in_n_steps(6)
    for filename, data in data_dict.items():
        state = parse_state(data)
        print(filename)
        print(path_book[state])

print(all_states_in_n_steps(3))

# task42()
# task43()
task5()
