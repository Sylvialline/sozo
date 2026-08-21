"""稳定、易用的优先队列。"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from heapq import heapify, heappop, heappush
from typing import Any, Generic, TypeVar


T = TypeVar("T")
_MISSING = object()


class _Entry(Generic[T]):
    __slots__ = ("priority", "order", "item", "reverse")

    def __init__(
        self,
        priority: Any,
        order: int,
        item: T,
        reverse: bool,
    ) -> None:
        self.priority = priority
        self.order = order
        self.item = item
        self.reverse = reverse

    def __lt__(self, other: _Entry[T]) -> bool:
        if self.priority == other.priority:
            return self.order < other.order
        if self.reverse:
            return other.priority < self.priority
        return self.priority < other.priority


class PriorityQueue(Generic[T]):
    """稳定优先队列，支持 ``key``、最大堆和显式优先级。

    空队列用 ``PriorityQueue()`` 创建；若需精确的静态类型，或队列会混放
    ``Leaf``、``Internal`` 等同一基类的子类，写成 ``PriorityQueue[Node]()``。
    """

    def __init__(
        self,
        items: Iterable[T] | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
        reverse: bool = False,
    ) -> None:
        if key is not None and not callable(key):
            raise TypeError("key 必须是可调用对象或 None")
        if not isinstance(reverse, bool):
            raise TypeError("reverse 必须是 bool")

        self._key = key
        self._reverse = reverse
        self._heap = [
            self._entry(item, order)
            for order, item in enumerate(() if items is None else items)
        ]
        heapify(self._heap)
        self._next_order = len(self._heap)

    def _entry(
        self,
        item: T,
        order: int,
        priority: Any = _MISSING,
    ) -> _Entry[T]:
        if priority is _MISSING:
            priority = item if self._key is None else self._key(item)
        return _Entry(priority, order, item, self._reverse)

    def push(self, item: T, *, priority: Any = _MISSING) -> None:
        """按计算所得或显式指定的优先级加入元素。"""
        heappush(
            self._heap,
            self._entry(item, self._next_order, priority),
        )
        self._next_order += 1

    def pop(self) -> T:
        """移除并返回最高优先级的元素。"""
        if not self._heap:
            raise IndexError("pop from an empty priority queue")
        return heappop(self._heap).item

    def pop_with_priority(self) -> tuple[Any, T]:
        """移除并返回优先级与元素组成的二元组。"""
        if not self._heap:
            raise IndexError("pop from an empty priority queue")
        entry = heappop(self._heap)
        return entry.priority, entry.item

    def peek(self) -> T:
        """返回最高优先级的元素但不移除。"""
        if not self._heap:
            raise IndexError("peek from an empty priority queue")
        return self._heap[0].item

    def peek_with_priority(self) -> tuple[Any, T]:
        """返回最高优先级及其元素但不移除。"""
        if not self._heap:
            raise IndexError("peek from an empty priority queue")
        entry = self._heap[0]
        return entry.priority, entry.item

    def clear(self) -> None:
        """清空队列。"""
        self._heap.clear()
        self._next_order = 0

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)
