"""无需完整排序的顺序统计工具。"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from operator import index
from typing import Any, Generic, TypeVar


T = TypeVar("T")


class _Ranked(Generic[T]):
    __slots__ = ("key", "order", "item")

    def __init__(self, key: Any, order: int, item: T) -> None:
        self.key = key
        self.order = order
        self.item = item


def _before(left: _Ranked[T], right: _Ranked[T], reverse: bool) -> bool:
    if reverse:
        if right.key < left.key:
            return True
        if left.key < right.key:
            return False
    else:
        if left.key < right.key:
            return True
        if right.key < left.key:
            return False
    return left.order < right.order


def _partition(
    values: list[_Ranked[T]],
    left: int,
    right: int,
    pivot_index: int,
    reverse: bool,
) -> int:
    pivot = values[pivot_index]
    values[pivot_index], values[right] = values[right], pivot
    store = left

    for current in range(left, right):
        if _before(values[current], pivot, reverse):
            values[store], values[current] = values[current], values[store]
            store += 1

    values[store], values[right] = values[right], values[store]
    return store


def _select(
    iterable: Iterable[T],
    n: int,
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> tuple[list[_Ranked[T]], int]:
    if key is not None and not callable(key):
        raise TypeError("key must be callable or None")
    if not isinstance(reverse, bool):
        raise TypeError("reverse must be bool")

    try:
        target = index(n)
    except TypeError:
        raise TypeError("n must be an integer") from None

    key_function = (lambda item: item) if key is None else key
    values = [
        _Ranked(key_function(item), order, item)
        for order, item in enumerate(iterable)
    ]

    if target < 0:
        target += len(values)
    if not 0 <= target < len(values):
        raise IndexError("selection index out of range")

    left = 0
    right = len(values) - 1
    while left < right:
        pivot = _partition(
            values,
            left,
            right,
            (left + right) // 2,
            reverse,
        )
        if pivot == target:
            break
        if target < pivot:
            right = pivot - 1
        else:
            left = pivot + 1

    return values, target


def nth(
    iterable: Iterable[T],
    n: int,
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> T:
    """返回排序后索引为 n 的元素，不修改输入或完整排序。

    接受任意 iterable 并支持负索引；``key``、``reverse`` 及相同 key 的
    稳定顺序与 ``sorted`` 一致。平均时间 O(N)，内部空间 O(N)。
    """
    values, target = _select(iterable, n, key=key, reverse=reverse)
    return values[target].item


def nth_element(
    values: list[T],
    n: int,
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> T:
    """将第 n 小元素原地就位并返回，无需完整排序。

    n 之前的元素不大于结果，之后的不小于结果；``reverse=True`` 时方向
    相反。支持负索引，``key`` 及相同 key 的稳定顺序与 ``sorted`` 一致。
    平均时间 O(N)，内部空间 O(N)。
    """
    if not isinstance(values, list):
        raise TypeError("nth_element requires a list; use nth() to avoid mutation")

    ranked, target = _select(values, n, key=key, reverse=reverse)
    values[:] = [value.item for value in ranked]

    return ranked[target].item
