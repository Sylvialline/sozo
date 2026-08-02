"""用途：C++17/STL 到 Python 标准库的可复制速查。

示例输入：脚本内置 ``[5, 1, 5, 2]``，无需终端输入。
示例输出：打印各容器/算法的代表结果与完整对应表。
复杂度：表中另列；本演示的数据量很小。
常见陷阱：``list.pop(0)`` 是 O(n)；``sort()`` 原地修改并返回 None；
``dict``/``set`` 是哈希结构，Python 标准库没有平衡树 set/map。
"""

from bisect import bisect_left, bisect_right
from collections import Counter, deque
from heapq import heapify, heappop, heappush
from itertools import accumulate


STL_MAP = {
    "vector": "list",
    "array": "list（可变）/ tuple（不可变）",
    "pair": "tuple",
    "unordered_map": "dict",
    "map": "dict + sorted(...)（无平衡树 map）",
    "unordered_set": "set",
    "set": "无直接平衡树对应；需要有序结果时 sorted(set)",
    "multiset": "collections.Counter",
    "stack": "list",
    "queue / deque": "collections.deque",
    "priority_queue": "heapq（默认最小堆）",
    "lower_bound / upper_bound": "bisect_left / bisect_right",
}


def sequence_demo() -> None:
    """list/tuple：创建、增删查、遍历、排序和复制。"""
    vector = [5, 1, 5]                  # vector<int>
    vector.append(2)                    # push_back，均摊 O(1)
    vector.pop()                         # pop_back，O(1)
    vector.remove(1)                     # 按值删除首项，O(n)
    found = 5 in vector                  # 查找 O(n)
    traversed = [x * 2 for x in vector]  # range-for
    ordered = sorted(vector)             # O(n log n)，保留原对象
    copied = vector.copy()               # 浅拷贝 O(n)

    array = [3, 1, 2]                    # 可修改的固定用途数组
    array.sort()                          # 原地排序，返回 None
    immutable_array = (3, 1, 2)          # tuple 不可增删改
    pair = ("alice", 90)
    name, score = pair                    # structured binding
    print("list:", vector, found, traversed, ordered, copied)
    print("array/tuple/pair:", array, immutable_array, name, score)


def mapping_demo() -> None:
    """dict：unordered_map；排序键后可模拟按键有序遍历。"""
    scores = {"bob": 80}                 # 创建
    scores["alice"] = 90                 # 添加/更新，平均 O(1)
    scores.setdefault("carol", 70)
    scores.pop("bob")                    # 删除，平均 O(1)
    found = "alice" in scores            # 查找，平均 O(1)
    items = list(scores.items())          # 遍历
    ordered = sorted(scores.items())      # map 风格，O(n log n)
    copied = scores.copy()                # 浅拷贝
    print("dict:", found, items, ordered, copied)


def set_and_multiset_demo() -> None:
    """set/Counter：集合与可重复元素集合。"""
    values = {3, 1}                      # unordered_set
    values.add(2)                        # 平均 O(1)
    values.discard(9)                     # 不存在也不报错
    values.remove(3)                      # 不存在会 KeyError
    found = 2 in values
    ordered = sorted(values)              # 需要确定顺序时显式排序
    copied_set = values.copy()

    bag = Counter([2, 2, 1])             # multiset
    bag[3] += 1                           # 添加
    bag[2] -= 1                           # 删除一次
    if bag[2] == 0:
        del bag[2]                        # Counter 的零计数不会自动消失
    count = bag[2]                        # 查询重数
    elements = sorted(bag.elements())     # 遍历所有副本
    copied_bag = bag.copy()
    print("set:", found, ordered, copied_set)
    print("Counter:", count, elements, sorted(copied_bag.items()))


def adapters_demo() -> None:
    """stack/queue/deque/priority_queue 的常用完整操作。"""
    stack = [1, 2]                       # 创建
    stack.append(3)                      # push，均摊 O(1)
    top = stack[-1]                      # top，O(1)
    popped = stack.pop()                  # pop，O(1)
    stack_found = 2 in stack              # 查找 O(n)
    stack_copy = stack.copy()

    queue = deque([1, 2])                # queue/deque
    queue.append(3)                      # push_back，O(1)
    queue.appendleft(0)                   # push_front，O(1)
    front = queue[0]
    queue.popleft()                       # pop_front，O(1)
    queue.pop()                           # pop_back，O(1)
    queue_found = 2 in queue              # 查找 O(n)
    queue_copy = queue.copy()

    heap = [5, 1, 3]                     # priority_queue（最小堆）
    heapify(heap)                          # O(n)
    heappush(heap, 2)                     # O(log n)
    minimum = heappop(heap)               # O(log n)
    heap_found = 3 in heap                 # O(n)
    heap_copy = heap.copy()
    heap_ordered = [heappop(heap_copy) for _ in range(len(heap_copy))]

    max_heap = [-x for x in [5, 1, 3]]   # 最大堆：存负数
    heapify(max_heap)
    maximum = -heappop(max_heap)
    print("stack:", top, popped, stack_found, stack_copy)
    print("deque:", front, queue_found, list(queue), list(queue_copy))
    print("heap:", minimum, heap_found, heap_ordered, "max =", maximum)


def algorithm_demo() -> None:
    """常见 STL 算法的一行 Python 对应写法。"""
    data = [5, 1, 5, 2]
    ordered = sorted(data)
    print("lower/upper:", bisect_left(ordered, 5), bisect_right(ordered, 5))
    print("sort/reverse:", ordered, list(reversed(ordered)), ordered[::-1])
    print("sum/accumulate:", sum(data), list(accumulate(data)))
    print("min/max:", min(data), max(data))
    print("count_if:", sum(x % 2 == 1 for x in data))
    print("find_if:", next((x for x in data if x > 3), None))
    print("iota:", list(range(4)))
    print("unique unordered/ordered:", set(data), list(dict.fromkeys(data)))
    print("lambda key:", sorted(data, key=lambda x: (-x, x)))
    print("enumerate/zip:", list(enumerate("ab")), list(zip("ab", [10, 20])))


def print_reference() -> None:
    print("\nSTL -> Python")
    for cpp, python in STL_MAP.items():
        print(f"{cpp:24} -> {python}")
    print(
        "\n复杂度摘要：list 尾部增删均摊 O(1)，中间增删/查找 O(n)；"
        "dict/set 平均 O(1)；deque 两端 O(1)；heap 顶 O(1)、增删 O(log n)。"
    )
    print(
        "复制均为浅拷贝：list.copy()/dict.copy()/set.copy()/deque.copy()；"
        "嵌套可变对象需要 copy.deepcopy。"
    )


def main() -> None:
    sequence_demo()
    mapping_demo()
    set_and_multiset_demo()
    adapters_demo()
    algorithm_demo()
    print_reference()


if __name__ == "__main__":
    main()
