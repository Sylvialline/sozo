# 考场对拍

适合手头已有候选解法和可信的暴力解法，想快速寻找小反例时使用。工具只依赖标准库，
直接比较函数返回值。优先生成暴力解法能很快跑完的小数据，并让暴力解法使用独立思路。

## 最短用法

```python
from utils import stress

def fast(a):
    return sorted(a)

def slow(a):
    # 示例用简单选择排序充当独立参考解法。
    result = []
    while a:
        value = min(a)
        result.append(value)
        a.remove(value)
    return result

def generate(rng):
    n = rng.randint(0, 8)
    a = [rng.randint(-3, 3) for _ in range(n)]
    return (a,)

stress(fast, slow, generate, trials=1000, seed=0)
```

全部新数据通过时向 stderr 打印 `Stress passed: 1000 cases, seed=0`，返回通过总组数
（包括可能存在的 1 组反例重测）。
首次失败会抛出 `StressFailure` 并停止，输出组号、seed、原始参数及两份答案。
反例自动保存，下次运行同一条 `stress(...)` 会先重测它。
如果函数报错，保留原始 traceback，并标明 `generate`、`copy`、`candidate`、
`reference` 或 `compare` 阶段；答案不同的阶段是 `mismatch`。

## 输入约定

每组数据必须是位置参数 **tuple**，始终展开成 `task(*args)`，没有自动猜测规则：

| task 接口 | 一组数据 |
| --- | --- |
| `task(a)`，a 是列表 | `(a,)` |
| `task(n, edges)` | `(n, edges)` |
| `task(pair)`，pair 本身是 tuple | `(pair,)` |
| `task()` | `()` |

两个解法分别获得独立深拷贝；允许排序、`pop`、修改嵌套列表。原始输入会保留，
同一组参数内的别名关系也会保留。两份返回值会立即快照，避免共享可变结果造成误判。
输入和返回值都必须支持 `deepcopy`；生成器等惰性答案请在包装函数中转为 `list`。
只比较返回值；原地算法可包装为“调用算法后返回修改后的列表”。

`cases` 也可以直接传可迭代对象，用于边界测试、穷举或已保存的反例：

```python
stress(fast, slow, [([],), ([0],), ([2, 2, -1],)])

from itertools import product
cases = ((list(a),) for n in range(6) for a in product((-1, 0, 1), repeat=n))
stress(fast, slow, cases, trials=10000)
```

随机生成和枚举都最多执行 `trials` 组，默认 1000；有限序列提前耗尽则按实际组数报告，
空序列报错。穷举时请把上限设得足够大，避免把部分通过误认为完成全枚举。

## 修改代码后直接重测

```python
# 第一次对拍：自动保存首个反例。
stress(fast, slow, generate, trials=1000, seed=42)

# 修改解法后，重新运行上面那行即可：先测旧反例，再测新数据。

# 如果只想快速验证刚才那个错误，省略第三个参数：
stress(fast, slow)
```

无需复制反例或分别给两个函数输入数据，也无需重跑到原来的随机组号。重启 Python 进程
后仍然有效；工具会用当前版本的两个解法和 `equal` 重新计算，不复用旧答案。

- 反例仍失败：立即报 `Stress replay failed`，不调用生成器、不消费新用例。
- 反例通过：显示 `Stress replay passed`；提供了 `cases` 时继续新数据，否则结束。
- 通过的反例保留作回归检查；新对拍发现另一个反例时，替换之前保存的那一组。
- 重测不计入 `trials`，也不消耗随机序列；返回值包含重测通过的组数。
- 没有已保存的反例却调用 `stress(fast, slow)`，明确报错，不显示虚假的通过。

默认位置是**调用脚本旁的 `.stress/`**，按两个函数的模块名和限定名称生成稳定文件名；
修改函数体不会改变位置。目录已加入 `.gitignore`，错误报告会显示具体文件路径。
同一目录下不同函数对分别保存。重命名函数、同名闭包的不同配置或希望分组时，可显式
指定文件，之后的重测也使用该路径：

```python
stress(fast, slow, generate, failure_file=".stress/q6.pickle")
stress(fast, slow, failure_file=".stress/q6.pickle")

# 仅本次运行，关闭自动保存和重测。
stress(fast, slow, generate, failure_file=None)
```

相对路径以调用脚本目录为基准，不随工作目录变化。删除对应文件即可清除旧反例。
文件只保存原始输入及 seed、组号，使用标准库 `pickle`，支持列表、tuple、集合、分数等；
**仅加载自己生成且可信的反例文件**。输入还须支持 pickle；自定义类在新进程中须能导入。
保存失败会在原始失败报告中附加明确说明，不掩盖原始错误。没有得到可重测输入的生成、
复制阶段错误不会写入文件；解法运行异常同样会保存反例。

仍可捕获 `StressFailure` 手工调试。组号 `case_index` 从 1 开始，`seed`、`inputs`、
`actual`、`expected`、`phase` 都能直接读取；`replayed` 表示是否正在重测，
`failure_file` 表示保存或加载反例的路径。重测时 seed、组号保留初次失败时的值。
生成或复制输入阶段失败时，`inputs` 可能为 `None`；该阶段之后尚未产生的答案也是 `None`。

## 自定义答案比较

默认用 `==` 比较。需要浮点容差或答案顺序无关时，传 `equal(actual, expected)`：

```python
from math import isclose
stress(fast, slow, generate, equal=lambda a, b: isclose(a, b, rel_tol=1e-9, abs_tol=1e-9))
stress(fast, slow, generate, equal=lambda a, b: sorted(a) == sorted(b))
```

用 `sorted` 可以保留重复项；仅当题目确实采用集合语义时才用 `set`。
如果存在多个合法答案且不能直接比较，可让两个包装函数返回可比较的目标值，
同时在包装函数内用 `assert` 检查构造是否合法。

## 考场使用范围

这是同进程的函数对拍，支持反例文件保存，但不负责题目文件 I/O、可执行程序、超时、
自动缩小反例或性能基准。
它不会隔离全局变量、随机状态或外部资源：两个解法应只依赖输入；有全局缓存等状态时，
由包装函数负责重置。默认 seed 为 0，每次运行固定序列；想探索新数据可以换 seed。
生成器应主动覆盖空输入、最小规模、重复值、负数以及题目边界。全部通过只说明这些数据
上没有发现差异，参考解法本身仍需可信。

可把对拍代码写进独立的 `check.py`。若导入某个模块会执行其顶层 `exam.execute()`，
导入也会触发这些任务，应由所有者先为题解入口加上 `if __name__ == "__main__":`。
