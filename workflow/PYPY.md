# PyPy 应急加速工作流

PyPy 适合作为考场中的第二运行时：当算法已经确定、纯 Python 循环需要运行数十秒到
数分钟，而现场没有时间重写算法时，可以用同一份脚本尝试 JIT 加速。它不是默认运行
时，也不是算法优化的替代品；先保证答案正确，再用实测决定是否切换。

## 一次性准备（Windows）

1. 打开 [PyPy 官方下载页](https://pypy.org/download.html)，下载稳定版的
   **PyPy3 / Windows 64 bit** 压缩包。选择与题解语法兼容的 Python 版本；本仓库
   当前可以优先选择 PyPy3.11。
2. 在仓库中创建 `workflow/runtimes/`，把压缩包完整解压到里面。保留压缩包自带的
   顶层目录即可，不必改名，也不要只移动其中的 exe。
3. 从仓库根目录检查启动器能否找到它：

   ```powershell
   python .\workflow\run_python.py pypy .\workflow\run_python.py --help
   ```

`workflow/runtimes/` 已被 Git 忽略；解释器是平台相关的大文件，公司电脑和家里电脑
各自执行一次以上准备即可。若系统已经能直接执行 `pypy3`，也可以不放本地副本，
启动器会继续从 PATH 查找。

若 Windows 报告缺少运行库，按官方下载页的提示安装 Microsoft VC Runtime。考前
应在断网状态实际启动一次，不能把下载或安装留到考试现场。

## 最短命令

直接运行使用 `Exam` / `AnswerBook` 的题解：

```powershell
python .\workflow\run_python.py pypy .\2019-s\solve.py
```

运行另一个 `Exam` 题解只需要替换脚本路径：

```powershell
python .\workflow\run_python.py pypy .\2025-8\solve.py
```

同一启动器切回 CPython：

```powershell
python .\workflow\run_python.py python .\2019-s\solve.py
```

`auto` 会优先使用 PyPy，找不到时明确警告并回退到 CPython：

```powershell
python .\workflow\run_python.py auto .\2019-s\solve.py
```

启动器总会使用 `-u`，实时显示任务日志；它还会切到被运行脚本的目录，并在结束时
打印整个进程的墙钟时间。启动器本身由仓库原有的 CPython 启动，再创建真正执行题解
的 PyPy 子进程；因此无需修改 PATH 或 PowerShell 执行策略。若不需要仓库启动器，
等价的基础命令是：

```powershell
pypy3 -u .\2019-s\solve.py
```

## UTF-8 控制台输出

仓库启动器会给 CPython/PyPy 子进程固定设置 `PYTHONUTF8=1` 和
`PYTHONIOENCODING=utf-8`。Windows 有控制台时，运行期间还会把输入、输出代码页临时
切换到 UTF-8（65001），结束后恢复原代码页。因此 task 返回值、JSON、异常和日志中的
中文都使用同一编码，不依赖当前 PowerShell 是 936 还是 65001。

直接运行 `pypy3` 不经过这层处理；如需绕过启动器，应先手动执行：

```powershell
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
```

## 考场怎么选

先用同一个代表性输入分别跑一次 CPython 和 PyPy，以启动器的 `[elapsed]` 为准；不要
根据“PyPy 通常更快”直接假定本题也更快。

优先尝试 PyPy 的情况：

- 热点是长时间反复执行的 Python `for` / `while`、列表、字典、集合和自定义函数；
- 单次运行至少持续数秒，尤其是数十秒到数分钟；
- 代码以标准库或纯 Python 依赖为主。

保留 CPython 的情况：

- 任务很短，JIT 还来不及热身；
- 时间主要花在 NumPy、SciPy 或其他 C 扩展内部；
- PyPy 下内存明显不足，或依赖尚未在 PyPy 环境中安装、验证；
- 两个解释器的输出不一致。此时以已经核验过的 CPython 路径为准。

同一批相似数据尽量交给一次 `exam.execute()` 处理，不要每个文件重新启动一个 PyPy
进程；JIT 的已编译代码不会跨进程保存，反复启动会重复支付热身成本。

## 和 `Exam` / 超时的关系

PyPy 只替换解释器，不改变 `Exam`、`AnswerBook`、`Case` 或 task 接口。Windows
超时子进程会沿用当前解释器，因此从 PyPy 启动时，受控 task 也运行在 PyPy 下。

如果某项本来就准备运行约 300 秒，`Exam(timeout=...)` 或 task / case 上的超时必须
大于预计时间；若这是有意进行的无上限“挣扎运行”，应由题解作者把该项设为
`timeout=None`。否则任务会按仓库原有规则被强制终止，换解释器也绕不过超时。

为争取部分答案，优先通过 `exam.execute(only=task_name, ...)` 只运行目标题组；短任务
先跑完并抄写，再把剩余时间交给长任务。

## 第三方包

CPython 中安装过的包不会自动出现在 PyPy 中。必须针对 PyPy 单独安装：

```powershell
$pypy = Get-ChildItem .\workflow\runtimes -Recurse -Filter 'pypy3*.exe' |
    Select-Object -First 1
& $pypy.FullName -m ensurepip
& $pypy.FullName -m pip install primefac
```

上例直接满足当前 `2019-s` 质因数分解参考实现所用的 `primefac`；安装其他包时替换
最后一个参数即可。装在 CPython 环境里的同名包不能被 PyPy 直接复用。

这些命令只应在考前、有网络时使用。若某题依赖 NumPy/SciPy 等 C 扩展，必须提前用
真实导入与小数据验证；为了现场可靠性，本仓库的通用工具仍保持标准库优先。

## 官方资料

- [下载与安装](https://doc.pypy.org/install.html)
- [适合 JIT 的程序与热身成本](https://pypy.org/features.html)
- [解释器间的包隔离与 C 扩展说明](https://doc.pypy.org/faq.html)
