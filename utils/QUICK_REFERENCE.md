# `AnswerBook` / `Exam` 现场速查手册

这份手册只覆盖答案执行与编排相关的高频接口。选择原则是：先用能清楚表达题目结构的
最高层接口；遇到不规则任务时再向下退一层。

| 层级 | 适用场景 | 自由度 |
| --- | --- | --- |
| `AnswerBook` | 参数、输入和执行顺序完全不规则 | 最高 |
| `Exam.add` + `Case` | case 不规则，但仍希望统一读取、计时和输出 | 高 |
| `Exam.add` + `Batch` | 一个输入文件包含多组独立调用 | 高 |
| `Exam.add` + `Series` | `a/b/c` 等规则题组 | 中 |
| `Exam.add_once(task)` | 无参数 task 只执行一次，label 使用函数名 | 低 |
| `@exam.task(...)` | 用装饰器声明显式 `Case` / `Batch` / `Series` | 低 |
| `@exam.task` / `Exam.add(task)` | 按函数参数推导规则题组，函数名作为 label 前缀 | 最低、最短 |

## 1. `AnswerBook`：逐项手动执行

### 最小用法

```python
from utils import AnswerBook

book = AnswerBook()
book.run("1.a", task1, 6, 4, data)
book.run("1.b", task1, 100, 150, other_data)
book.print_json()
```

`run(label, task, *args, **kwargs)` 原样调用 `task(*args, **kwargs)`，并把答案保存到
`book.answers[label]`。默认结构是：

```python
{
    "result": task_return_value,
}
```

需要耗时时显式使用 `AnswerBook(show_time=True)`，答案中会增加
`"time": elapsed_seconds`。task 返回字典时也会完整放在 `result` 下。

### 超时和日志

```python
book = AnswerBook(timeout=2)                 # 所有任务默认 2 秒
book.run("1.a", task1, data)                # 使用 2 秒
book.run("1.b", task1, data, timeout=5)     # 单项覆盖为 5 秒
book.run("1.c", task1, data, timeout=None)  # 单项关闭超时
```

超时项不会消失，而会保存为：

```python
{
    "timeout": True,
    "timeout_limit": configured_seconds,
}
```

`show_time=True` 时，超时答案也会增加 `time`。没有启用超时且 `show_time=False` 时，
task 直接在当前进程运行，并且不会读取计时器；只有 `timeout` 会要求使用子进程。

默认向 stderr 输出 `START`、`DONE`、`TIMEOUT`、`FAILED` 日志；不需要时使用
`AnswerBook(show_log=False)`。普通异常会记录失败日志并重新抛出，不会伪装成答案。

启用超时后 task 在 `spawn` 子进程中运行。task、reader、parser、参数和返回值必须可被
`pickle`，现场最稳妥的做法是把这些函数写在模块顶层，并把执行入口放在：

```python
if __name__ == "__main__":
    ...
```

### 取得和输出结果

```python
answers = book.answers       # 原始答案字典
copied = book.as_dict()      # 顶层浅拷贝
text = book.dumps()          # JSON 字符串
book.print_json()            # 打印 JSON
path = book.write_json()     # 同级 answer.json
book.write_json("result.json")
```

默认 pretty print 会缩进对象结构，并让 `[1, 2, 3]` 这类简单一维数组保持单行：

```python
book.dumps(indent=4)
book.print_json(inline_simple_lists=False)
book.write_json(indent=None)  # 紧凑 JSON
```

task 可直接返回 `set`、`frozenset`、dataclass、Enum、Path、日期时间、Decimal、
迭代器、NumPy 标量或数组，输出时会递归转成 JSON 可处理的数据。集合会稳定排序；
一次性迭代器会被消费。自定义类型可实现 `__json__()` 返回可转换对象。未知类型仍会
抛出 `TypeError`，便于及时发现遗漏。

相同的转换和排版也可以脱离 `AnswerBook` 使用：

```python
from utils import pretty_json, to_jsonable

data = {"seen": {3, 1, 2}, "matrix": [[1, 2], [3, 4]]}
safe_data = to_jsonable(data)  # 可直接交给 json.dumps
text = pretty_json(data)       # 自动转换，并使用 AnswerBook 的排版规则
```

`pretty_json()` 也接受 `indent` 和 `inline_simple_lists`，含义与
`book.dumps()` 的同名参数一致。

## 2. `Exam`：统一读取、执行和输出

`Exam` 把输入读取也纳入 `AnswerBook` 的异常和超时边界；传入 `show_time=True` 时读取、
解析和 task 调用会作为一个整体计时。

最短用法不需要 reader。默认 reader 按完整文件名读取同级 `data/`：

```python
from utils import Case, Exam

exam = Exam()
exam.add(task1, Case("1", files=("q1.txt",)))  # data/q1.txt
```

它只接受 `data/` 内的相对路径，精确读取一个 UTF-8 文件；缺失时抛出
`FileNotFoundError`。需要文件名包含匹配或一次读取多个文件时，再显式使用旧的
`read_data`：

```python
from utils import Exam, read_data

def parse(data: str) -> list[int]:
    return list(map(int, data.split(",")))


exam = Exam(reader=read_data, parser=parse, timeout=2)
```

`reader` 接收文件名匹配串并读取原始数据；可选的 `parser` 接收一份文本并返回 task
真正需要的数据。直接传官方 `read_data` 时，`Exam` 会绑定创建位置所在的题目目录；
即使进入 Windows 超时子进程，也仍会读取正确的同级 `data/`。

reader 返回字符串时，parser 执行一次；reader 返回字典时，parser 会递归应用到每个叶子
值，文件名键和字典结构保持不变：

```python
read_data("all")
# {"a.txt": "1,2", "b.txt": "3,4"}

# 传入 task 前变成：
# {"a.txt": [1, 2], "b.txt": [3, 4]}
```

同一份试题通常只需要一个全局 parser。特殊格式可在 `Case`、`Batch` 或 `Series` 上
覆盖；显式传 `parser=None` 会为该组关闭全局解析：

```python
def parse_colon(data: str) -> list[int]:
    return list(map(int, data.split(":")))


Case("old", files=("old",), parser=parse_colon)  # 覆盖全局 parser
Case("text", files=("text",), parser=None)       # 保留 reader 原始结果
Series("7", parser=parse_colon)                  # 整组覆盖
```

reader 和 parser 都能逐层设置，且二者分别独立继承：

```text
Input > Case/Batch/Series > Exam
```

省略某项表示继承；`parser=None` 表示明确关闭解析。覆盖 reader 不会自动关闭 parser。
`Series` 是 `Case` 工厂，它的设置会传给生成的每个 Case：

```python
from utils import Input

Case("case", Input("x", reader=other_reader))
Case("raw", files=("x",), reader=other_reader, parser=None)
Series("7", reader=other_reader, parser=parse_colon)
```

执行方式：

```python
book = exam.execute()                       # 默认打印答案
book = exam.execute(output=True)            # 写同级 answer.json
book = exam.execute(output="result.json")   # 写指定文件
book = exam.execute(output=None)             # 只返回 AnswerBook
book = exam.execute(output=False)            # 同上
```

`indent` 和 `inline_simple_lists` 会转交给 JSON 输出方法。一个 `Exam` 只能执行一次，执行
后也不能继续注册 case；重复答案标签会在读取任何输入、运行任何任务之前报错。

## 3. `Case`：精确描述一次调用

```python
from utils import Case

Case("4.a", 2, 4, files=("4a", "4b"))
```

它最终调用：

```python
task(2, 4, reader("4a"), reader("4b"))
```

规则是“普通参数在前，`files` 读取结果按顺序追加在后”。`files` 必须写成 tuple；单个
文件也要写成 `files=("4a",)`，末尾逗号不能省略。

其中每项可以是字符串，也可以是带局部配置的 `Input`；字符串等价于完全继承的
`Input("4a")`：

```python
Case(
    "mixed",
    files=("left", Input("right", reader=other_reader, parser=None)),
)
```

单项超时可以覆盖 `Exam`：

```python
Case("slow", files=("5a",), timeout=10)
Case("unlimited", files=("5b",), timeout=None)
```

parser 也有同样的继承思路：不写表示继承 `Exam.parser`，传 callable 表示覆盖，传
`None` 表示关闭。覆盖只影响这个 `Case`。

### 一次取得 `data/` 下全部文件

空字符串是合法匹配串，表示匹配全部普通文件：

```python
Case("all", files=("",))

def task_all(all_data):
    # 多文件时 all_data 是按文件名排序的 {filename: text}
    ...
```

这仍然只给 task 追加一个参数；该参数是 `read_data("")` 的整体返回值。

如果 task 更适合接收 `list[str]`，把转换留给 reader：

```python
def rd_many(name):
    matched = read_data(name)
    if matched is None:
        raise FileNotFoundError(f"没有文件匹配 {name!r}")
    if isinstance(matched, str):
        return [matched]
    return list(matched.values())

exam = Exam(reader=rd_many)

@exam.task(Case("all", files=("",)))
def task_all(datasets):
    # datasets: list[str]，顺序与文件名排序一致
    ...
```

### `Input`：在嵌套参数中放置输入

`files=` 适合尾部参数；需要把数据嵌入 list、tuple 或 dict 时使用 `Input`：

```python
from utils import Case, Input

Case(
    "nested",
    {"left": Input("4a"), "right": [Input("4b"), Input("4c")]},
)
```

执行前，所有嵌套的 `Input` 都会递归替换成对应的 reader 返回值。使用 `read_data` 时，
`Input("")` 同样表示读取 `data/` 下的全部文件。

`Input.name` 是交给 reader 的不透明 selector，不内建路径或 glob 语义。单个 Input 可只
覆盖 reader、只覆盖 parser，或同时覆盖二者；未设置的字段继续继承
Case/Batch/Series/Exam。

### 根目录相对路径与 glob：`read_files`

官方数据同时位于题目根目录和 `data/` 子目录时，使用 `read_files`：

```python
from utils import Case, Exam, read_files

exam = Exam(read_files, parser=parse_colon)
exam.add(task_root, Case("root", files=("infections.txt",)))
exam.add(task_nested, Case("nested", files=("data/data*.txt",)))
```

- 精确路径始终返回 `str`；
- 含 glob 的 selector 始终返回有序 `{相对路径: 文本}`，即使只有一个匹配；
- 不存在或零匹配会抛出 `FileNotFoundError`；
- 不接受绝对路径、空 selector 或离开题目目录的 `..`。

`Exam` 会把创建位置绑定为 reader 根目录，改变 CWD 或进入 Windows 超时子进程都不会
改变读取位置。也可通过 `Exam(..., base_dir=path)` 显式指定根目录。`read_data` 的旧行为
保持不变，仍专门读取同级 `data/` 并使用文件名子串匹配。

## 4. `Batch`：一个输入执行多次 task

`Batch` 与 `Case` 分开：`Case` 永远只调用一次 task；`Batch` 只接受一个输入源，第三个
参数 `calls` 将读取、解析后的值转换成多组完整的 task 位置参数。每次返回值按顺序
组成 list：

```python
from utils import Batch, Rows

Batch("6", "q6.txt", Rows(str, int))
# 依次执行 task6(d, n)，最终 result 是所有返回值组成的 list
```

`calls` 产出的 tuple 会展开成位置参数；标量作为一个位置参数；空 tuple 调用无参数
task。`Rows` 跳过空白行，把每个非空白行按空白切列，并用给出的转换器逐列处理。
`Rows(float)` 适合单列小数，`Rows(str, int)` 适合 `d n`，`Rows()` 则让每个非空白行
触发一次无参数调用。若 Batch 配置了 `parser`，`calls` 收到的是 parser 处理后的值。
自定义 `calls` 在启用超时时要定义在模块顶层以支持 `pickle`；`Rows` 本身可直接用于
超时模式。

`Batch` 没有普通参数和 `files`，`calls` 必须产出每次 task 调用的全部参数。需要组合
多个物理文件时，使用一个明确的自定义 reader，让 `Batch.source` 仍表示一个批输入；
框架不会猜测多个文件应当 zip、广播还是做笛卡尔积。

## 5. `Series`：批量生成规则 case

### 默认 `a/b/c`，每项一份输入

```python
from utils import Series

Series("1")
```

会生成：

| 答案标签 | reader 匹配串 |
| --- | --- |
| `1a` | `1a` |
| `1b` | `1b` |
| `1c` | `1c` |

### 标签加分隔符

```python
Series("1", label_separator=".")
```

答案标签变为 `1.a/1.b/1.c`，文件匹配串仍是 `1a/1b/1c`。

### 每项多份输入

```python
Series("3", input_count=2)
```

生成 `3a1/3a2`、`3b1/3b2`、`3c1/3c2`，所以 task 接收两个数据参数。
`input_count=0` 表示这一组不读取文件。

### 每个 variant 带不同普通参数

```python
Series(
    "2",
    {
        "a": (10, 20),
        "b": (100, 200),
    },
    input_count=1,
    label_separator=".",
)
```

对应调用：

```python
task(10, 20, reader("2a"))
task(100, 200, reader("2b"))
```

映射值必须是 tuple。也可以用 `Series("7", "abcd")` 自定义 variant 集合。整组可用
`timeout=` 设置同一个单项超时策略，用 `parser=` 覆盖或关闭全局 parser。

## 6. `Exam.add`：显式注册

`add` 最适合动态组织或不想使用装饰器的场景：

```python
exam.add_once(summary)  # 调用 summary() 一次，label 为 "summary"
exam.add(solve)  # 等价于裸 @exam.task，自动生成 Series("solve", ...)
exam.add(task1, Series("1"))
exam.add(
    task4,
    Case("4.a", files=("4a", "4b")),
    Case("4.b", files=("4c",)),
)
```

`add_once(task)` 专门表示一次无参数调用，label 直接采用函数名。省略 group 的普通
`add(task)` 则与裸 `@exam.task` 使用同一套自动推导：完整函数名作为
`Series.prefix`，位置参数数量作为 `input_count`。函数名没有 `task...` 格式要求。
同一个 task 后也可以同时放多个显式 `Case` / `Batch` / `Series`。`add` 返回 `exam`
自身，可以链式书写，但现场通常分行更容易检查。

## 7. `@exam.task(...)`：装饰器式显式注册

把注册规则放在函数旁边：

```python
@exam.task(Series("1", {"a": (6, 4), "b": (100, 150)}))
def task1(n, m, data):
    ...


@exam.task(
    Case("4.a", files=("4a", "4b")),
    Case("4.b", files=("4c", "4d")),
)
def task4(left, right):
    ...
```

装饰器返回原函数，因此仍可直接调用 `task1(...)` 做小样例调试。

## 8. `@exam.task`：自动推导规则题组

所有位置参数都对应输入文件时使用最短写法：

```python
@exam.task
def solve(data):
    return parse_and_solve(data)
```

推导规则：

- 完整函数名直接成为 `Series.prefix`，不要求形如 `task1`；
- 默认生成 `a/b/c` 三项；
- 位置参数数量就是 `input_count`；
- `solve(data)` 因此读取 `solvea/solveb/solvec`；
- `solve(left, right)` 读取 `solvea1/solvea2`、`solveb1/solveb2`、`solvec1/solvec2`；
- `*args` 和必需的仅关键字参数无法自动推导，应改用显式 `Case` / `Batch` / `Series`。

只要有普通参数、特殊标签、不同 variant、非标准文件名或自定义超时，就使用
`@exam.task(...)`。

## 9. 只调试指定 task

装饰器可以全部保留，通过 `execute(only=...)` 选择本次要运行的 task：

```python
exam.execute(only=task3, output=None)
```

这个调用会执行 `task3` 注册的全部 `Case` / `Batch` / `Series`，其他 task 不读取数据也
不运行。
需要同时检查多个 task 时传入可迭代对象：

```python
exam.execute(only=(task1, task3), output=None)
```

`only=None` 是默认值，表示执行全部已注册 task。应直接传装饰器返回的函数对象；传入
未注册函数会立即报错，避免因为名字写错而静默得到空答案。

## 10. 可直接套用的完整骨架

```python
from utils import Case, Exam, Series, read_data


def parse(data: str) -> list[int]:
    return list(map(int, data.split(",")))


exam = Exam(reader=read_data, parser=parse, timeout=2)


@exam.task
def solve(data):
    return parse_and_solve(data)


@exam.task(Series("2", {"a": (10,), "b": (100,)}, label_separator="."))
def task2(n, data):
    ...


@exam.task(
    Case(
        "special",
        files=("left", "right"),
        timeout=None,
        parser=None,
    )
)
def task_special(left, right):
    ...


if __name__ == "__main__":
    exam.execute(output=True)
```

调试某一题时只需把最后一行临时改成
`exam.execute(only=task2, output=None)`，不必注释其他 `@exam.task`。

## 11. `read_data` 匹配规则

```python
read_data("3a")  # 文件名包含字面字符串 3a
read_data("")    # data/ 下全部普通文件
```

- 区分大小写；
- 只扫描 `data/` 这一层，不递归进入子目录；
- 按文件名排序；
- 使用 UTF-8 解码；
- 无匹配返回 `None`；唯一匹配返回 `str`；多个匹配返回 `{filename: str}`。

这里刻意采用字面包含而不是正则。这样文件名中的 `.`、`[`、`+` 都没有隐藏语义，现场
也更容易确认匹配范围。极少数需要正则的情况，先用 `read_data("")` 取得字典，再在自定义
reader 中用 `re.fullmatch` 或 `re.search` 过滤即可。

## 12. 常见错误速查

| 现象 | 检查 |
| --- | --- |
| task 少参数或多参数 | `Case` 普通参数在前，`files` 结果追加在后 |
| 单文件变成了 tuple 书写错误 | 使用 `files=("1a",)`，保留逗号 |
| 预期字符串却得到 dict | 匹配串命中了多个文件；缩小匹配或让 reader 主动处理 |
| `read_data` 返回 `None` | 检查同级 `data/`、大小写和匹配串 |
| 空串没有全选 | 确保写的是 `files=("",)` 而不是空 tuple `files=()` |
| parser 没有生效 | 只有 `Input` / `files` 的 reader 结果会解析；检查 Case 是否传了 `parser=None` |
| parser 收到字典 | 不会；映射会递归处理，parser 只接收叶子值 |
| 多测文件只执行了一次 | 改用 `Batch(..., calls=...)`，让它产出每次调用的位置参数 tuple |
| 默认 reader 找不到文件 | 传完整文件名（包括扩展名），并确认文件位于同级 `data/` |
| 超时模式启动失败 | task、reader、parser、参数、返回值保持可 pickle，入口加 `__main__` guard |
| bare `@exam.task` 推导错误 | 位置参数必须全部对应输入文件；其他结构改用显式 `Case`、`Batch` 或 `Series` |
| 只想调试一个 task | 保留所有装饰器，调用 `exam.execute(only=task1, output=None)` |
| `only` 报未注册 task | 直接传被当前 `exam` 装饰或 `add` 过的函数对象 |
| 没有生成文件 | `execute()` 默认打印；写文件要用 `output=True` |
