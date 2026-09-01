# Python 性能瓶颈诊断速查

`line_profiler` 很适合在已知某个 task 较慢时继续定位到具体代码行，但不应单独承担
第一次排查。考场默认使用两层诊断：先用标准库 `cProfile` 找慢函数，再用
`line_profiler` 检查慢函数中的各行；修改后必须退出 profiler，以普通运行时间判断是否
真的变快。

## 一次性准备

在有网络时，从仓库根目录执行：

```powershell
python -m pip install --user -r .\workflow\requirements-profiling.txt
python -c "import line_profiler; print(line_profiler.__version__)"
```

本仓库通过 `python -m kernprof` 调用工具，不依赖用户 Scripts 目录是否位于 PATH。
考前应断网执行一次下面的逐行命令。当前固定版本面向 CPython；不要尝试在 PyPy 中
安装或运行逐行 profiler。

## 考场最短流程

### 0. 只留下需要诊断的任务

先选一个能稳定复现慢问题的代表性输入，并让 `Exam` 只执行目标题目：

```python
exam.execute(only=task4)
```

分析期间应让该任务的有效超时为 `None`。非空超时会让 `AnswerBook` 在子进程中运行
任务，而逐行 profiler 对多进程的统计可能缺失；profiler 自身还会显著拖慢程序。

### 1. 不改代码，先找慢函数

```powershell
python .\workflow\profile_python.py functions .\2022-8\solve.py
```

默认分别显示累计时间和函数自身时间前 15 项：

- `cumtime` 高：整个调用树耗时高，先沿它向下找；
- `tottime` 高：时间主要消耗在函数自己的 Python 代码中；
- `ncalls` 异常高：通常应先检查重复计算、状态数量或复杂度。

需要查看更多函数时，把 `--top` 放在脚本路径之前：

```powershell
python .\workflow\profile_python.py functions --top 30 .\2022-8\solve.py
```

### 2. 不加装饰器，定位具体代码行

```powershell
python .\workflow\profile_python.py lines .\2022-8\solve.py
```

入口会自动分析该 `solve.py` 中实际执行过的顶层函数，并生成
`solve.py.lprof`。重点阅读：

- `Hits`：该行执行次数；先判断状态规模或循环次数是否超出预期；
- `Time`：该行累计耗时；优先处理总耗时最大的行；
- `Per Hit`：单次成本；用于区分“便宜但次数多”和“单次本身昂贵”；
- `% Time`：该行占当前函数的比例，不是占整个程序的比例。

调用其他函数的那一行会包含被调用过程的等待时间；如果被调用函数也出现在报告中，
应继续查看它自己的逐行表，避免把同一调用链误认为两个独立瓶颈。

### 3. 按这个顺序决定是否改

1. 先看复杂度：状态数、嵌套循环、重复 BFS/排序/解析是否本可避免；
2. 再消除重复工作：缓存、把不变量移出循环、合并重复遍历；
3. 最后才做局部常数优化；
4. 用原输入重新运行普通 CPython，确认墙钟时间确实下降；
5. 若热点是长时间纯 Python 循环，再按 [`PYPY.md`](PYPY.md) 实测 PyPy。

不要拿 profiler 中的总时间比较 CPython 和 PyPy。逐行插桩会改变运行特征，PyPy 的
JIT 路径也不同；最终判断只能使用不带 profiler 的真实运行。

## 自动分析遗漏函数时

嵌套函数、动态创建的函数或特殊包装可能没有出现在自动报告中。此时只给目标函数临时
添加 `@profile`，并使用 kernprof 运行：

```python
@exam.task
@profile
def task4(data):
    ...
```

```powershell
python -m kernprof -lv .\2022-8\solve.py
```

这里 `@profile` 必须紧贴函数、位于 `@exam.task` 下方，使 Exam 注册到已插桩函数。
`profile` 由 kernprof 临时注入，无须 import；普通 `python solve.py` 不认识它，所以诊断
结束后应立即删除该装饰器。通常优先使用前面的自动分析命令，避免改动考场代码。

## 限制与清理

- 逐行分析有明显开销，只适合代表性数据，不适合最终计时；
- 多线程、多进程和异步代码可能缺少或扭曲统计；
- NumPy 等 C 扩展只能显示“调用它的这一行很慢”，不能继续展开 C 内部；
- `solve.py.prof` 和 `solve.py.lprof` 是临时报告，已由 Git 忽略，可以随时删除。

官方资料：

- [line_profiler 安装与基本用法](https://kernprof.readthedocs.io/en/stable/)
- [Python `cProfile` / `pstats`](https://docs.python.org/3/library/profile.html)
- [line_profiler PyPI 页面](https://pypi.org/project/line-profiler/)
