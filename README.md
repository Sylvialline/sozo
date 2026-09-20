# 东京大学创造情报学专攻编程考试备考仓库

这个仓库服务于东京大学大学院情报理工学系研究科创造情报学专攻的编程考试。
考试不在线提交程序：考生在个人电脑上读取 USB 中的数据、运行代码，再把答案抄到
答题纸上。因此，本仓库优化的不是在线评测通过率，而是完整的考试工作流：

> 读题 → 编码 → 运行必要计算 → 快速辨认答案 → 低风险抄写

## 核心边界

每个题目目录中的 `solve.py` 都代表考试现场需要从零编写的代码。

- `solve.py` 的所有代码必须由仓库所有者亲手编写。
- 自动化工具可以读取、运行、计时、测试和评审 `solve.py`，但不得创建、编辑、
  格式化、移动、重命名或删除它。
- 修改建议写在对话或独立的 `notes.md` 中，再由仓库所有者亲自实施。
- `utils/`、`workflow/`、编辑器任务、文档和测试工具属于考前准备的基础设施，可以
  持续维护和扩充。

这条边界也记录在根目录的 `AGENTS.md` 中，供后续自动化会话读取。

## 维护原则

优先级从高到低如下：

1. **正确且可核验**：宁可明确报错，也不要静默给出可能错误的答案。
2. **降低现场认知负担**：辅助工具处理文件发现、批量运行、计时和答案展示；
   `solve.py` 只处理题目逻辑。
3. **只做必要计算**：面对未知数据规模，避免为当前小问执行无关算法。
4. **标准库优先**：默认只使用 Python 标准库，确保断网环境可运行。
5. **可读性优先于炫技**：允许为了输入速度采用简写，但不采用难以现场检查的隐藏
   魔法。
6. **复用必须有收益**：只有通用、接口简单、经过测试且比重写更省事的逻辑才进入
   `utils/`。

衡量性能时，不只看算法运行时间，也看找到命令、辨认输出和抄写答案所需的总时间。

## 快速使用

在项目根目录执行：

```powershell
# 运行题解中注册的全部 Exam task
python -u .\2025-8\solve.py
```

只运行特定任务时，在题解末尾使用 `exam.execute(only=task3)`；写入同级
`answer.json` 时使用 `exam.execute(output=True, only=task3)`。`Exam` 负责题组选择、
数据读取、可选计时、日志和答案输出。

VS Code 工作区提供两个现场入口：

- 在新建的 Python 文件中输入 `exam-default` 并确认代码补全，可插入 `Path`、`DATA`、
  `Batch`、`Case`、`Rows` 和 `Exam` 的默认文件头；光标会停在文件头末尾继续编写。
- Python 扩展内置的 **Run Python File** 继续用当前选择的 CPython；需要用 PyPy 运行
  当前编辑器文件时，按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>。默认 Build Task
  会调用仓库启动器并明确显示实际使用的 PyPy 路径与总耗时。也可从命令面板选择
  `Tasks: Run Task` → `Python: Run Current File with PyPy`。

命令行中需要尝试 PyPy 时，使用同一个仓库启动器：

```powershell
# 直接运行使用 Exam / AnswerBook 的题解
python .\workflow\run_python.py pypy .\2019-s\solve.py

# 同一题解切换到 PyPy
python .\workflow\run_python.py pypy .\2025-8\solve.py
```

安装、CPython/PyPy 对比、适用边界和超时注意事项见
[`workflow/PYPY.md`](workflow/PYPY.md)。默认工作流仍使用 CPython；PyPy 是经过本题
实测后再启用的应急运行时。仓库启动器会统一子进程和 Windows 控制台为 UTF-8，避免
当前代码页为 936 时 PyPy 的中文输出乱码。

遇到慢 task 时，先做函数级扫描，再下钻到具体代码行：

```powershell
python .\workflow\profile_python.py functions .\2022-8\solve.py
python .\workflow\profile_python.py lines .\2022-8\solve.py
```

安装、读表方式、`Exam` 超时/多进程注意事项和最终实测顺序见
[`workflow/PROFILING.md`](workflow/PROFILING.md)。

## Python 考场速查库

现场文档分成五个入口：

- [`utils/QUICK_REFERENCE.md`](utils/QUICK_REFERENCE.md)：从 `AnswerBook`、`Exam`、
  `Case`、`Batch`、`Series` 到 `@exam.task` 的答案执行与编排速查；
- [`REFERENCE_PATTERNS.md`](REFERENCE_PATTERNS.md)：按题型场景定位历年 `solve.py`
  中值得复用但不适合抽成通用 API 的参考写法；
- [`samples/README.md`](samples/README.md)：面向 C++17/STL 使用者的 Python 3 离线
  示例索引，覆盖语法、标准库、解析、容器、算法、矩阵、调试和完整小任务；
- [`offline_docs/index.html`](offline_docs/index.html)：与本机版本匹配的 Python、NumPy、
  SciPy 官方 HTML 文档总入口，可完全离线浏览和搜索；
- [`workflow/PROFILING.md`](workflow/PROFILING.md)：慢任务的函数级、逐行诊断与
  CPython/PyPy 最终实测流程。

写题时优先查 `utils` 速查手册来选择运行范式；遇到似曾相识的题型时查历年代码参考
索引；需要回忆 Python 写法或算法模板时再查 `samples/`。

```powershell
python samples/00_quick_reference/cpp_to_python_stl.py
python samples/run_all_samples.py
```

当前目录 `2025-8` 保持原位，因为自动移动目录会连带移动受保护的 `solve.py`。
新题目建议使用零补齐的 `YYYY-MM` 命名；是否统一旧目录由仓库所有者决定并亲自操作。

## 目录职责

```text
.
├── AGENTS.md          # solve.py 的保护规则
├── README.md          # 仓库理念和现场用法
├── REFERENCE_PATTERNS.md # 历年题解中的参考型代码索引
├── .vscode/           # Python 默认片段与当前文件的 PyPy 运行任务
├── workflow/          # 运行时、性能诊断手册与跨电脑 skill 资产
├── samples/           # Python 考场速查、完整示例与批量自检
├── utils/             # 已验证的通用模块及 QUICK_REFERENCE.md
└── YYYY-MM/
    ├── solve.py       # 仅仓库所有者编辑
    ├── notes.md       # 复盘、复杂度、陷阱和改进建议
    ├── problem.pdf
    └── data/          # 数据、标准答案和独立验证程序
```

## `Exam` 编排任务，`AnswerBook` 管理答案

完整接口、选型表和常见场景可直接查阅
[`utils/QUICK_REFERENCE.md`](utils/QUICK_REFERENCE.md)；本节保留整体用法概览。

现场代码优先使用 `Exam` 一次声明题组。规则相同的 `a/b/c` 小题用 `Series`，
特殊文件组合用 `Case`：

```python
from utils import Case, Exam, Series, read_data


def parse(data: str) -> list[int]:
    return list(map(int, data.split(",")))

exam = Exam(reader=read_data, parser=parse, timeout=2)


@exam.task(
    Series(
        "1",
        {"a": (6, 4), "b": (100, 150)},
        label_separator=".",
    )
)
def task1(n, m, data):
    ...


@exam.task(Case("4.a", 2, 4, 4, 3, files=("4a", "4b")))
def task4(a_n, a_m, b_n, b_m, a_data, b_data):
    ...


if __name__ == "__main__":
    exam.execute()
```

`reader` 现在可以省略。`Exam()` 默认按完整文件名精确读取创建位置同级的
`data/`，例如 `Case("1", files=("q1.txt",))` 会读取 `data/q1.txt`；文件缺失会直接
抛出 `FileNotFoundError`。需要旧的文件名包含匹配时，仍可显式使用
`Exam(reader=read_data)`。

`Series("1")` 默认生成 `1a/1b/1c`，并分别读取 `1a/1b/1c`；如果每个
case 需要两份数据，写成 `Series("3", input_count=2)`，它会读取
`3a1/3a2`、`3b1/3b2`、`3c1/3c2`。映射中的 tuple 是放在数据前面的
task 参数，因此推荐把 task 接口统一写成“普通参数在前，输入数据在后”。

所有位置参数都对应输入文件时，可以直接省略 group：

```python
@exam.task
def solve(data):
    return parse_and_solve(data)
```

这与 `exam.add(solve)` 相同，内部根据位置参数数量生成 `Series("solve", input_count=1)`。
完整函数名直接作为 label 前缀，不要求形如 `task1`；默认生成 `solvea/solveb/solvec`，
分别读取同名文件。装饰器返回原函数，因此 task 仍可脱离 `Exam` 单独调用。需要普通参数、
特殊标签或其他题组结构时，显式传入 `Case`、`Batch` 或 `Series`。

像 `2014-s` 这样，task 不接收参数且只需执行一次时，使用 `add_once`：

```python
exam.add_once(task1)
```

它只调用一次 `task1()`，并直接使用函数名 `"task1"` 作为 label；不会生成 `a/b/c`。

只调试某个装饰器 task 时不需要注释其他注册：

```python
exam.execute(only=solve, output=None)
```

这会运行 `solve` 注册的全部 case；也可以传 `only=(task1, solve)` 选择多个 task。
省略 `only` 时仍执行全部任务。

`Case(..., files=("4a", "4b"))` 会按顺序读取指定文件，并把结果追加到
普通参数后。单项可传 `timeout=5` 覆盖 `Exam` 的类级超时，显式传
`timeout=None` 可关闭该项限制。`execute()` 默认把答案打印到终端；
`execute(output=True)` 写入调用代码同级的 `answer.json`，
`execute(output="result.json")` 可指定文件名，`execute(output=None)` 则只返回
内部的 `AnswerBook`。读取、解析和 task 调用共同处于错误日志及超时边界内；启用
`show_time=True` 时也会一起计时。

一个文件含有多组测试时，使用独立的 `Batch`。它只接受一个输入源，第三个参数
`calls` 把一次读取的内容转换为多组完整的 task 位置参数：

```python
from utils import Batch, Rows

exam = Exam()
exam.add(task6, Batch("6", "q6.txt", Rows(str, int)))
```

这里 `q6.txt` 只读取一次，`task6(d, n)` 按行执行，答案是保持原顺序的 list。`calls`
返回的每个 tuple 会展开为一次调用；标量表示一次单参数调用，空 tuple 表示一次无参数
调用。`Rows` 把每个非空白行按空白切列，并用给出的转换器逐列处理；`Rows()` 则让每个
非空白行触发一次无参数调用。这一形式可直接覆盖 `2013-s/data` 的逐行多测格式。
`Case` 始终只调用 task 一次。`Batch` 没有普通参数和 `files`，因此不会出现“固定参数是
否追加到每次调用”或“多个文件按 zip 还是笛卡尔积展开”的隐含规则；`calls` 必须产出
每次调用的全部参数。

`Exam(parser=parse)` 设置全局解析器；reader 返回字典时，会保持键和结构并递归解析叶子
文本。`Case`、`Batch` 或 `Series` 都可以覆盖全局 parser，显式传 `parser=None` 则关闭
该项的解析。

`reader` 也可在 `Case`、`Batch`、`Series` 或单个 `Input` 上覆盖，`parser` 与 `reader`
分别独立继承，优先级为 `Input > Case/Batch/Series > Exam`。省略配置表示继承；
`parser=None` 明确关闭解析。需要根目录精确路径或 glob 时使用 `read_files`：

```python
from utils import Case, Exam, Input, read_files

exam = Exam(read_files, parser=parse)
exam.add(task_one, Case("one", files=("infections.txt",)))
exam.add(task_all, Case("all", files=("data/data*.txt",)))
exam.add(
    task_mixed,
    Case("mixed", Input("infections.txt"), Input("raw.txt", parser=None)),
)
```

精确路径始终读取成字符串；glob 始终读取成按相对路径排序的字典，即使只匹配一个文件。
找不到输入时会直接抛出 `FileNotFoundError`。旧 `read_data` 的匹配和返回规则保持不变。

`Exam(reader=read_data)` 可以直接使用：`Exam` 会把创建位置所在的题目目录绑定给
`read_data`，经过内部调用层或 Windows 超时子进程时也不会误读 `utils/data/`。
`Case(..., files=("",))` 会把 `data/` 下全部普通文件作为一个读取结果传给 task。

`AnswerBook` 负责执行 task、记录答案，并可将结果打印到终端或写入文件：

```python
from utils import AnswerBook, read_data as rd

book = AnswerBook(timeout=2, show_time=True)
book.run("1.a", task1, 6, 4, rd("1a"))
book.run("1.b", task1, 100, 150, rd("1b"), timeout=5)
book.run("1.c", task1, 10, 10, rd("1c"), timeout=None)

book.print_json()  # 打印到终端
book.write_json()  # 写入调用代码同级的 answer.json
```

成功任务默认保存为 `{"result": task返回值}`；传入 `show_time=True` 后增加
`"time": 秒数`。即使 task 返回字典，也完整放在 `result` 下。未启用计时且没有超时
限制时直接在当前进程调用 task，也不会读取计时器。`run()` 未指定
`timeout` 时使用类级限制，传入数值可覆盖它，显式传入 `None` 可关闭该项任务的
限制。有超时限制的 task 会在独立子进程中执行，超限后子进程将被强制终止，并记录
`timeout` 和 `timeout_limit`；启用 `show_time` 时还会记录 `time`。task 及其参数和
返回值必须支持 `pickle` 序列化。
每项任务默认在 stderr 输出开始、完成、超时或失败日志，传入 `show_log=False`
可以关闭。`write_json("result.json")` 可以指定其他文件名或路径。

通过 `Exam` 启用超时时，`reader` 和 `parser` 也在同一个受控子进程中执行，因此应把
自定义函数写在模块顶层，以便 `pickle`；普通的现场写法自然满足这一点。

JSON 默认保持对象结构的换行缩进，但 `[1, 2, 3]` 这类仅含简单值的一维数组
会留在单行，矩阵和对象数组仍按层级展开。需要完全采用标准缩进时，可传
`book.dumps(inline_simple_lists=False)`；`print_json()` 和 `write_json()`
也接受同名参数。输出前会递归转换常见的非 JSON 类型，包括 `set`、`frozenset`、
dataclass、Enum、Path、日期时间、Decimal、迭代器，以及 NumPy 标量和数组；集合会按
稳定顺序输出，普通容器不会在 `book.answers` 中被替换。一次性迭代器会在输出时被
消费并转成数组。自定义对象可实现 `__json__()`，返回任意可继续转换的对象。仍无法
转换的对象会明确抛出 `TypeError`，不会被静默写成含糊的字符串。

这套能力也作为独立接口暴露，无须创建 `AnswerBook`：

```python
from utils import pretty_json, to_jsonable

safe_data = to_jsonable(data)  # 返回可交给 json.dumps 的副本
text = pretty_json(data)       # 鲁棒转换并使用上述 pretty print 规则
```

## `read_data()` 快速读取数据

在题目代码中调用 `read_data("3a")`，会读取该代码文件同级 `data/` 目录中所有
文件名包含 `3a` 的普通文件：

```python
from utils import read_data

data = read_data("3a")
all_data = read_data("")  # 读取 data/ 下全部普通文件
```

- 没有匹配时返回 `None`；
- 恰好一个匹配时直接返回文件内容 `str`；
- 多个匹配时返回 `{文件名: 文件内容}` 字典。

空字符串按包含语义匹配所有文件。匹配是区分大小写的字面包含而不是正则；文件按文件名
排序，并使用 UTF-8 解码。复杂正则筛选可在 `read_data("")` 返回的字典上自行完成，
无需让日常文件名承担正则特殊字符风险。

## 正因子与因子对

`divisors(n)` 返回升序正因子，`factor_pairs(n)` 默认只返回第一项不大于第二项的
因子对。需要同时枚举 `(a, b)` 和 `(b, a)` 时传入 `include_swapped=True`：

```python
from utils import divisors, factor_pairs

divisors(12)  # [1, 2, 3, 4, 6, 12]
factor_pairs(12)  # [(1, 12), (2, 6), (3, 4)]
factor_pairs(12, include_swapped=True)
```

两个函数都要求 `n` 为正整数，并正确去除完全平方数平方根位置的重复项。

## `DSU` / `KeyedDSU`：整数与任意键并查集

节点是连续整数 `0 .. n-1` 时使用数组实现的 `DSU(n)`；节点是字符串、元组等任意
可哈希对象时使用 `KeyedDSU(keys)`：

```python
from utils import DSU, KeyedDSU

numbered = DSU(10)
named = KeyedDSU(["alice", "bob", "carol"])
named.union("alice", "bob")

named.add("dave")               # 动态加入；新增返回 True
assert named.same("alice", "bob")
assert named.size("alice") == 2
assert named.components == 3
assert named.component_count == 3  # components 的只读语义化别名

named.roots()                    # {"alice", "carol", "dave"}
named.members("bob")            # ["alice", "bob"]
named.groups()                   # {"alice": ["alice", "bob"], ...}
```

两者的 `union(a, b)` 都只在实际发生合并时返回 `True`。`KeyedDSU` 不会在查询时
静默创建未知键；请先通过构造参数或 `add()` 注册，否则抛出 `KeyError`。`roots()`、
`members()` 和 `groups()` 都会压缩涉及节点的路径并返回容器快照；修改返回值不会影响
并查集。整数版的成员按编号排列，任意键版保持键的加入顺序。

## `PriorityQueue`：稳定的最小堆与最大堆

`PriorityQueue` 默认弹出最小元素，支持初始化数据、`key=`、最大堆和单独指定优先级；
优先级相同时保持入队顺序，因此元素本身不需要能够相互比较：

```python
from utils import PriorityQueue

pq = PriorityQueue([5, 1, 3])
pq.push(2)
pq.peek()  # 1，不移除
pq.pop()   # 1

jobs = PriorityQueue(key=lambda job: job.cost)
jobs.push(job)

max_pq = PriorityQueue(reverse=True)
max_pq.push("answer", priority=42)
priority, item = max_pq.pop_with_priority()
```

空队列要写成 `PriorityQueue()`，不能写成只引用类本身的 `PriorityQueue`。不标泛型也能
直接 `push()`；如果希望类型检查器准确识别 `pop()` 的返回类型，或者 Huffman 队列会
同时存放多个 `Node` 子类，显式写出共同基类：

```python
nodes = PriorityQueue[Node](key=lambda node: node.weight)
nodes.push(Leaf(weight, char))
nodes.push(Internal(weight, left, right))
```

队列还提供 `peek_with_priority()`、`clear()`、`len(pq)` 和 `bool(pq)`。它不维护
decrease-key 映射；Dijkstra 等算法仍可重复压入新状态，并由调用方跳过过期状态。

## `nth` / `nth_element`：无需完整排序地选择第 n 个元素

`nth(iterable, n)` 是无副作用的选择函数：它返回与 `sorted(iterable)[n]` 相同的
元素，但不修改输入或做完整排序，并且可以接受生成器、元组等任意 iterable。

`nth_element(values, n)` 则保留 C++ 同名函数的语义，只接受列表并原地重排：返回后
`values[n]` 就是结果，左侧元素
不大于它，右侧元素不小于它。支持 Python 负索引，并沿用 `sorted` 熟悉的 `key=`、
`reverse=` 和稳定平局规则；`reverse=True` 时左右关系也随之反转：

```python
from utils import nth, nth_element

median = nth(values, len(values) // 2)  # values 不变
third_largest = nth_element(values, 2, reverse=True)
oldest = nth(records, 0, key=lambda record: record.age)
```

两个函数都采用 quickselect，平均时间 O(n)，内部空间 O(n)；索引越界抛出
`IndexError`，行为与普通序列索引一致。

## `Graph`：显式节点集、BFS、缩点与拓扑排序

`Graph` 的核心不变量是：`g.adj` 的 key 集合就是完整节点集。无论节点是否有
出边，都必须作为 key 存在；`g[u]` 和 `g.neighbors(u)` 只查询，缺失节点会抛出
`KeyError`，绝不会因查询而创建节点。`add_edge(u, v)` 会显式补齐两个端点。
`Graph` 以节点类型为泛型参数；函数边界写成 `Graph[int]`、`Graph[str]` 后，迭代
节点、邻居、距离字典、SCC 等结果都会保留该类型。权重类型保持动态。

```python
from utils import Graph

def solve_integer_graph(g: Graph[int]) -> None:
    for node in g:             # node 推断为 int
        ...

g = Graph.from_edges(
    [("a", "b"), ("b", "a"), ("b", "c")],
)

parts = g.condensation()
print(parts.members)          # 每个 SCC 的原节点
print(parts.component_of["a"])

# 结果也可直接解包；类型检查器可识别 cg 是 Graph。
cg, members, component_of = g.condense()

# 默认保证每条 u -> v 都有 u 在 v 前；reverse=True 时则 v 在 u 前。
for component in parts.graph.topological_sort(reverse=True):
    for node in parts.members[component]:
        ...

# BFS：起点距离为 0，不可达节点不在字典中；带权图也忽略权值。
dist = g.bfs_distances("a")
# 若题目统计路径访问的节点数，而不是经过的边数，使用 dist[target] + 1。

wg = Graph.from_edges([("a", "b", 3), ("a", "c", 1)], weighted=True)
weighted_dist = wg.dijkstra_distances("a")  # 按非负权值计算
```

`condensation()` 返回的 DAG 节点为 `0..k-1`，`members[i]` 和
`component_of[u]` 提供两种方向的映射。跨 SCC 的平行边会保留；加权图也保留这些边的
权重。原图有环时，直接对它调用 `topological_sort()` 会明确抛出 `ValueError`。
`bfs_distances(start)` 返回最少边数，因此起点为 `0`；对带权图调用时会忽略权值。
题目若把起点和终点都计入“访问的节点数”，由调用方对目标距离加 `1`。
`dijkstra_distances(start)` 用于带权图，按非负权值返回最短距离；两个方法都省略不可达
节点，起点不存在时抛出 `KeyError`。

## 函数对拍

`stress(fast, slow, generate, trials=1000, seed=0)` 用随机小数据比较候选解法与暴力解法，
首次差异或异常就报告可复现输入。生成器接收独立 `rng`，返回一组参数 tuple；
也可以直接传手工用例或穷举用例。两个解法各取独立深拷贝，支持原地修改输入。
反例自动保存在脚本旁的 `.stress/`，修改代码后重跑会优先重测；`stress(fast, slow)`
则只重测已保存的反例，无需手工复制数据。
完整示例、反例复现和自定义比较见 [`utils/STRESS.md`](utils/STRESS.md)。

## `utils/` 收录标准

一个模块进入 `utils/` 前，应同时满足：

1. 在不同题型中有较高的再次使用概率；
2. 语义不依赖某一道题的特殊定义；
3. 接口比现场重写更短、更容易记忆；
4. 有覆盖核心行为和边界情况的测试；
5. 不依赖网络、隐式全局状态或第三方包。

例如并查集适合进入 `utils/`；“线段与开放网格内部相交”这样的特殊几何定义应留在
对应题目中。四方向常量等几行即可重写的内容，也不必为了抽象而抽象。

## 每次真题训练后的整理流程

1. 保存题面、最终代码和数据来源说明。
2. 用独立答案或人工结果核对每个小问。
3. 记录正确性风险、复杂度、性能热点和容易抄错的输出。
4. 为发现的问题补充最小合成数据，而不是只记录文字结论。
5. 评估是否存在真正通用的模块；满足上述标准后再放入 `utils/`。
6. 确认 `solve.py` 的任何修改均由仓库所有者亲自完成。

## 考前离线检查

建议定期在断网状态完成以下检查：

```powershell
python --version
python -m unittest discover -s tests -v
python -u .\2025-8\solve.py
python .\workflow\run_python.py pypy .\workflow\run_python.py --help
```

同时确认：

- `python` 命令和 Python 扩展内置的 **Run Python File** 可以用 CPython 直接运行；
- 在空 Python 文件中输入 `exam-default` 能展开默认文件头；
- 打开一个 Python 文件后，<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> 能通过默认
  Build Task 找到已解压的 PyPy，并显示所选解释器；
- 仓库、解释器和所需资料均位于本机；
- `utils` 没有未安装的第三方依赖；
- 常用命令不依赖 shell 历史或网络搜索；
- 输出中的文件名、答案和用时容易区分。
