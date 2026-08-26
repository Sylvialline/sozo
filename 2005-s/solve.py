from dataclasses import dataclass
from itertools import combinations_with_replacement as cwr

@dataclass
class Spot:
    liberty: int
    neighbors: list[int]
    regions: set[int]

@dataclass
class Region:
    components: set[frozenset[int]]

@dataclass
class Position:
    spots: list[Spot]
    regions: list[Region]


def make_fig_1_3():
    spots = [
        Spot(liberty=0, neighbors=[3, 4, 4], regions={0, 1}),
        Spot(liberty=2, neighbors=[3], regions={0}),
        Spot(liberty=3, neighbors=[], regions={1}),
        Spot(liberty=1, neighbors=[0, 1], regions={0}),
        Spot(liberty=1, neighbors=[0, 0], regions={0, 1}),
    ]
    regions = [
        Region({frozenset([0, 1, 3, 4])}),
        Region({frozenset([0, 4]), frozenset([2])})
    ]
    position = Position(spots, regions)
    return position

def make_fig_1_2():
    spots = [
        Spot(liberty=2, neighbors=[3], regions={0}),
        Spot(liberty=2, neighbors=[3], regions={0}),
        Spot(liberty=3, neighbors=[], regions={0}),
        Spot(liberty=1, neighbors=[0, 1], regions={0}),
    ]
    regions = [
        Region({frozenset([0, 1, 3]), frozenset([2])}),
    ]
    position = Position(spots, regions)
    return position

def make_fig_2():
    spots = [
        Spot(liberty=1, neighbors=[4, 4], regions={0, 1}),
        Spot(liberty=3, neighbors=[], regions={1}),
        Spot(liberty=3, neighbors=[], regions={0}),
        Spot(liberty=3, neighbors=[], regions={0}),
        Spot(liberty=1, neighbors=[0, 0], regions={0, 1}),
    ]
    regions = [
        Region({frozenset([0, 4]), frozenset([2]), frozenset([3])}),
        Region({frozenset([0, 4]), frozenset([1])})
    ]
    position = Position(spots, regions)
    return position


def task3():
    print(make_fig_1_3())


def compute_n_m(p: Position):
    cur_n = len(p.spots)
    tot_lib = sum(s.liberty for s in p.spots)
    n = (cur_n + tot_lib) // 4
    m = cur_n - n
    return n, m

def task4():
    print(compute_n_m(make_fig_1_3())[0])

def connectable_pairs(p: Position):
    res = []
    n = len(p.spots)
    for i, j in cwr(range(n), 2):
        si, sj = p.spots[i], p.spots[j]
        if si.liberty == 0 or sj.liberty == 0:
            continue
        if i == j and si.liberty == 1:
            continue
        rg = si.regions & sj.regions
        if not rg:
            continue
        r = p.regions[next(iter(rg))]
        for c in r.components:
            if i in c and j in c:
                res.append(f"#({i+1},{j+1})")
                break
        else:
            res.append(f"({i+1},{j+1})")
    return ' '.join(res)

def task5():
    # print(connectable_pairs(make_fig_1_3()))
    print(connectable_pairs(make_fig_1_2()))
    print(connectable_pairs(make_fig_2()))


if __name__ == "__main__":
    task3()
    task4()
    task5()

    