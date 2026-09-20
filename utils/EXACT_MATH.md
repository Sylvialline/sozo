# 精确数值、取整与位标志速查

从 `2013-s` 提炼的考场写法。`Fraction`、`isqrt`、`IntFlag` 直接使用标准库；
区间计数和二次根式数提供可 import 的实现。具体几何递归留在原题作为参考。

## Fraction：从输入开始保留精确值

```python
from fractions import Fraction
from math import floor, ceil

x = Fraction("0.1")        # 精确的 1/10
y = Fraction(2, 3)         # 2/3
z = Fraction("-7/3")
n, d = z.numerator, z.denominator  # -7, 3；分母恒正
floor(z), ceil(z)          # -3, -2
```

`Fraction(0.1)` 和 `Fraction.from_float(0.1)` 保留二进制 float 的实际值，不能恢复
原始十进制输入。精确读取用 `Fraction(token)`；整数之商用 `Fraction(a, b)`，
避免 `Fraction(a / b)` 先发生浮点除法。数据文件可直接用 `Rows(Fraction, int)`。
不要用 `int(x)` 替代 `floor(x)`：负数的 `int` 向零截断。

## 整数除法和平方根取整

```python
# a 为整数，b 为正整数；a 为负数也成立。
floor_div = a // b
ceil_div = -((-a) // b)

from math import isqrt

# n 为非负整数。
r = isqrt(n)
floor_sqrt = r
ceil_sqrt = r + (r * r != n)
```

`isqrt` 直接给出整数平方根下取整。对大整数，不要先 `sqrt(n)` 再转整数。
如果 `u` 是整数，`u² <= n` 等价于 `-isqrt(n) <= u <= isqrt(n)`，
可以将带平方根的格点判定化成整数上下界。

原题 [`lp_circle_r`](../2013-s/solve.py#L23) 消去圆方程的分母，再用 `isqrt`
计算每列整数纵坐标的范围。坐标变换留在题解中，取整方法可以直接借用。

## count_integers：统一开闭区间计数

```python
from utils import count_integers

count_integers(-2, 2)                                    # 5，[-2, 2]
count_integers(-2, 2, left_closed=False)                 # 4，(-2, 2]
count_integers(-2, 2, right_closed=False)                # 4，[-2, 2)
count_integers(-2, 2, left_closed=False, right_closed=False)  # 3
count_integers(1, 1, left_closed=False)                  # 0
count_integers(3, 1)                                    # 0，空区间
```

支持有限的 `int`、`float`、`Fraction`、`Qn` 端点及实现 `__floor__` / `__ceil__`
的其他类型。不加 epsilon；float 以已经存储的数值为准。短写法是：

```python
left = ceil(lo) if left_closed else floor(lo) + 1
right = floor(hi) if right_closed else ceil(hi) - 1
count = max(0, right - left + 1)
```

`max(0, ...)` 覆盖反向区间和退化开区间。原题
[`lp_1d`](../2013-s/solve.py#L69) 是题内版本；跨题复用优先使用通用工具。

## Qn：固定根号参数的精确数值构造器

```python
from functools import partial
from fractions import Fraction
from math import floor, ceil
from utils import Qn, count_integers

Q3 = partial(Qn, 3)
Q2 = partial(Qn, 2)
SQRT3 = Q3(0, 1)

x = Q3(1, 2)               # 1 + 2√3
y = Q3(Fraction(1, 2), -1) # 1/2 - √3
z = Q3("0.1", "2/3")      # 1/10 + (2/3)√3

assert SQRT3 * SQRT3 == 3
assert 1 / (2 + SQRT3) == 2 - SQRT3
assert floor(x) == 4
assert ceil(-x) == -4
assert 1 < SQRT3 < 2
assert count_integers(-SQRT3, SQRT3) == 3
```

`Qn(n, a=0, b=0)` 表示 `a + b√n`。`Q3 = partial(Qn, 3)` 提供固定模板参数的
调用体验，不动态生成新类。`Q3` 是构造器而非类型；类型标注和 `isinstance` 使用 `Qn`。

- `n` 为正的非完全平方整数，例如 2、3、5、8。完全平方根直接使用 `Fraction`。
- 系数接受整数、`Fraction` 或分数/十进制字符串，不隐式接受 float。
- 支持 `+ - * /`（包括与 `int`、`Fraction` 的反向运算）、负号、比较、`abs`、`bool`、
  `hash`、`floor`、`ceil`、`sign()`、`is_integer()`。未实现幂、`//`、取模等运算。
- 运算结果仍为 `Qn`，`a`、`b` 恒为 `Fraction`；根式系数消去后也可与整数或分数比较。
- 不同 `n` 的两个非有理数混算或比较（包括 `==`）抛出 `TypeError`；不自动化简
  `√8 = 2√2`，同一道题应统一根号参数。`b=0` 的有理数可以跨 `n` 混算和比较。
- 对象不可变，支持 `deepcopy`、`pickle`；固定参数的 `partial` 也能 pickle。

比较通过符号及平方大小完成；取整通分成 `(A + B√n) / D`，用 `isqrt(n*B*B)` 求整数
根式下界，最后用 `// D`。负根式系数需要处理下取整方向。全程不经过 float，
适合边界格点判定；大量 `Fraction` 运算仍有开销，优先在确需根式精确性的地方使用。

专用实现 [`2013-s/Q3.py`](../2013-s/Q3.py#L10) 保留为题目参考。新题直接 import
`Qn` 即可；若手动迁移原题，可把 `Q3` 构造器绑定和 `SQRT3` 常量改成上面的写法。

## IntFlag：表示可组合的有限状态集合

```python
from enum import IntFlag, auto

class Side(IntFlag):
    D = auto()
    R = auto()
    L = auto()
    ALL = D | R | L

active = Side.D | Side.L
assert Side.D in active             # 是否包含 D
assert not (Side.R in active)
assert (Side.D | Side.L) in active  # 是否同时包含全部指定标志
assert active & (Side.D | Side.R)   # 是否包含至少一个指定标志

added = active | Side.R
common = active & Side.R
remaining = active & ~Side.D       # 移除 D
opposite = Side.ALL & ~active      # 显式全集 ALL 内求补集
empty = Side(0)
assert not empty
```

`|` 是并集，`&` 是交集，`^` 是切换/对称差；添加已有标志不会重复。
独立的单比特成员表示元素，组合成员表示常用集合。全集的补集显式写作
`ALL & ~flags`，读代码时即可看到范围；普通整数的 `~` 则会得到负整数。

原题的 [`Side`](../2013-s/solve.py#L83) 和
[`lp_flake_n`](../2013-s/solve.py#L109) 传递仍有效的边：
`including & ~Side.D` 保留除底边之外的当前有效边，而不是替换为固定两条边。
这种“有限集合随递归传播”的写法值得查阅；坐标变换与代理三角形分解留在原题。
