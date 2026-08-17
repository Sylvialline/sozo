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
- `run.py`、`utils/`、编辑器任务、文档和测试工具属于考前准备的基础设施，可以
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
# 运行题目目录中的全部 data*.txt
python run.py 2025-8 --time

# 只运行文件名包含 3a 或 5c 的数据
python run.py 2025-8 --only '3a|5c'

# 只运行 data3*，并且只取得 solve() 生成的第 3 个答案
python run.py 2025-8 --only '^data3' --answer 3 --time

# 把答案写入题目目录下的 output/
python run.py 2025-8 --out output

# 使用其他文件名规则；正则采用完整匹配
python run.py 2025-8 --pattern 'case\d+\.in'
```

在 VS Code 中打开某个题目的 `solve.py` 后，也可以按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> 运行当前题目的全部数据。

## Python 考场速查库

现场文档分成四个入口：

- [`utils/QUICK_REFERENCE.md`](utils/QUICK_REFERENCE.md)：从 `AnswerBook`、`Exam`、
  `Case`、`Series` 到 `@exam.task` 的答案执行与编排速查；
- [`REFERENCE_PATTERNS.md`](REFERENCE_PATTERNS.md)：按题型场景定位历年 `solve.py`
  中值得复用但不适合抽成通用 API 的参考写法；
- [`samples/README.md`](samples/README.md)：面向 C++17/STL 使用者的 Python 3 离线
  示例索引，覆盖语法、标准库、解析、容器、算法、矩阵、调试和完整小任务；
- [`offline_docs/index.html`](offline_docs/index.html)：与本机版本匹配的 Python、NumPy、
  SciPy 官方 HTML 文档总入口，可完全离线浏览和搜索。

写题时优先查 `utils` 速查手册来选择运行范式；遇到似曾相识的题型时查历年代码参考
索引；需要回忆 Python 写法或算法模板时再查 `samples/`。

```powershell
python samples/00_quick_reference/cpp_to_python_stl.py
python samples/12_exam_workflows/full_exam_template.py
python samples/run_all_samples.py
```

当前目录 `2025-8` 保持原位，因为自动移动目录会连带移动受保护的 `solve.py`。
新题目建议使用零补齐的 `YYYY-MM` 命名；是否统一旧目录由仓库所有者决定并亲自操作。

## `solve()` 接口

基础形式保持为单参数，不向问题代码引入文件名路由：

```python
def solve(data: str):
    ...
    return answer
```

多问问题可以使用生成器，让答案按照题号依次产生：

```python
def solve(data: str):
    ...
    yield answer_1
    ...
    yield answer_2
```

`--answer N` 使用从 1 开始的编号，只适用于返回迭代器或生成器的 `solve()`。runner
会执行到第 `N` 个 `yield`，取得并输出该答案，然后关闭生成器；第 `N` 个 `yield`
之后的代码不会执行。不指定该参数时，runner 会像以前一样消费并输出全部结果。

`--answer` 不会分析文件名，也不会改变 `solve(data)` 的接口。文件筛选和答案筛选是
两个独立操作：

- `--only` 决定运行哪些数据文件；
- `--answer` 决定消费第几个生成结果。

## 目录职责

```text
.
├── AGENTS.md          # solve.py 的保护规则
├── README.md          # 仓库理念和现场用法
├── REFERENCE_PATTERNS.md # 历年题解中的参考型代码索引
├── run.py             # 稳定的批量运行入口
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

`Series("1")` 默认生成 `1a/1b/1c`，并分别读取 `1a/1b/1c`；如果每个
case 需要两份数据，写成 `Series("3", input_count=2)`，它会读取
`3a1/3a2`、`3b1/3b2`、`3c1/3c2`。映射中的 tuple 是放在数据前面的
task 参数，因此推荐把 task 接口统一写成“普通参数在前，输入数据在后”。

如果函数名是 `task1` 这类形式，而且所有位置参数都是数据输入，还可以直接写：

```python
@exam.task
def task1(data):
    ...


@exam.task
def task3(data1, data2):
    ...
```

此时题号由函数名推导，位置参数数量决定每个 case 读取几份文件。装饰器返回原函数，
因此 task 仍可脱离 `Exam` 单独调用。

只调试某个装饰器 task 时不需要注释其他注册：

```python
exam.execute(only=task3, output=None)
```

这会运行 `task3` 注册的全部 case；也可以传 `only=(task1, task3)` 选择多个 task。
省略 `only` 时仍执行全部任务。

`Case(..., files=("4a", "4b"))` 会按顺序读取指定文件，并把结果追加到
普通参数后。单项可传 `timeout=5` 覆盖 `Exam` 的类级超时，显式传
`timeout=None` 可关闭该项限制。`execute()` 默认把答案打印到终端；
`execute(output=True)` 写入调用代码同级的 `answer.json`，
`execute(output="result.json")` 可指定文件名，`execute(output=None)` 则只返回
内部的 `AnswerBook`。读取、解析和 task 调用共同处于计时、错误日志及超时边界内。

`Exam(parser=parse)` 设置全局解析器；reader 返回字典时，会保持键和结构并递归解析叶子
文本。`Case(..., parser=other_parse)` 或 `Series(..., parser=other_parse)` 可以覆盖全局
解析器，显式传 `parser=None` 则关闭该 case 或题组的解析。

`reader` 也可在 `Case`、`Series` 或单个 `Input` 上覆盖，`parser` 与 `reader` 分别独立
继承，优先级为 `Input > Case/Series > Exam`。省略配置表示继承；`parser=None` 明确关闭
解析。需要根目录精确路径或 glob 时使用 `read_files`：

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

`AnswerBook` 负责执行 task、记录答案和耗时，并可将结果打印到终端或写入文件：

```python
from utils import AnswerBook, read_data as rd

book = AnswerBook(timeout=2)
book.run("1.a", task1, 6, 4, rd("1a"))
book.run("1.b", task1, 100, 150, rd("1b"), timeout=5)
book.run("1.c", task1, 10, 10, rd("1c"), timeout=None)

book.print_json()  # 打印到终端
book.write_json()  # 写入调用代码同级的 answer.json
```

成功任务的答案固定使用 `{"result": task返回值, "time": 秒数}` 结构；即使 task
返回字典，也完整放在 `result` 下，不会与 `time` 混在同一层。`run()` 未指定
`timeout` 时使用类级限制，传入数值可覆盖它，显式传入 `None` 可关闭该项任务的
限制。有超时限制的 task 会在独立子进程中执行，超限后子进程将被强制终止，并记录
包含 `timeout`、`time` 和 `timeout_limit` 的答案；task 及其参数和返回值必须
支持 `pickle` 序列化。
每项任务默认在 stderr 输出开始、完成、超时或失败日志，传入 `show_log=False`
可以关闭。`write_json("result.json")` 可以指定其他文件名或路径。

通过 `Exam` 启用超时时，`reader` 和 `parser` 也在同一个受控子进程中执行，因此应把
自定义函数写在模块顶层，以便 `pickle`；普通的现场写法自然满足这一点。

JSON 默认保持对象结构的换行缩进，但 `[1, 2, 3]` 这类仅含简单值的一维数组
会留在单行，矩阵和对象数组仍按层级展开。需要完全采用标准缩进时，可传
`book.dumps(inline_simple_lists=False)`；`print_json()` 和 `write_json()`
也接受同名参数。

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

## `Graph`：显式节点集、BFS、缩点与拓扑排序

`Graph` 的核心不变量是：`g.adj` 的 key 集合就是完整节点集。无论节点是否有
出边，都必须作为 key 存在；`g[u]` 和 `g.neighbors(u)` 只查询，缺失节点会抛出
`KeyError`，绝不会因查询而创建节点。`add_edge(u, v)` 会显式补齐两个端点。

```python
from utils import Graph

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
python run.py 2025-8 --only '^data1' --answer 1 --time
```

同时确认：

- `python` 命令和 VS Code 默认任务可以直接运行；
- 仓库、解释器和所需资料均位于本机；
- `utils` 没有未安装的第三方依赖；
- 常用命令不依赖 shell 历史或网络搜索；
- 输出中的文件名、答案和用时容易区分。
