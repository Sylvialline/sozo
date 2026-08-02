# Python 考场速查示例库

这是一套面向 C++17/STL 使用者的 Python 3 离线速查库。目标不是从头讲授算法，而是
让你在考试中通过文件名或全文搜索，迅速找到一段短小、完整、能直接运行和改写的标准
库示例。

除 [`14_optional_numpy/`](14_optional_numpy/) 和
[`numerical_fitting/numpy_solution.py`](13_example_tasks/numerical_fitting/numpy_solution.py)
这一可选对照外，所有示例只使用 Python 标准库。每个 `.py` 文件均可独立运行，并在
开头给出用途、示例输入/输出、复杂度和常见陷阱。

## 三条最常用命令

在仓库根目录运行：

```powershell
python samples/00_quick_reference/cpp_to_python_stl.py
python samples/12_exam_workflows/full_exam_template.py
python samples/run_all_samples.py
```

只检查某一主题：

```powershell
python samples/run_all_samples.py --pattern heap
python samples/run_all_samples.py --pattern 13_example_tasks --show-output
```

## C++/STL 快速迁移

| C++ | Python | 首选示例 |
|---|---|---|
| `vector` | `list` | [`list_vector.py`](05_containers/list_vector.py) |
| `array` | `list` / `tuple` | [`cpp_to_python_stl.py`](00_quick_reference/cpp_to_python_stl.py) |
| `pair` / 结构化绑定 | `tuple` / 元组解包 | [`tuple_pair.py`](05_containers/tuple_pair.py) |
| `unordered_map` | `dict` | [`dict_unordered_map.py`](05_containers/dict_unordered_map.py) |
| `map` | `dict` 后按键 `sorted` | [`cpp_to_python_stl.py`](00_quick_reference/cpp_to_python_stl.py) |
| `unordered_set` | `set` | [`set_unordered_set.py`](05_containers/set_unordered_set.py) |
| `set`（平衡树） | 标准库无直接对应 | [`common_pitfalls.py`](00_quick_reference/common_pitfalls.py) |
| `multiset` | `collections.Counter` | [`counter_multiset.py`](05_containers/counter_multiset.py) |
| `stack` | `list` + `append/pop` | [`list_stack.py`](05_containers/list_stack.py) |
| `queue` | `collections.deque` | [`deque_queue.py`](05_containers/deque_queue.py) |
| `priority_queue` | `heapq`（默认最小堆） | [`heapq_priority_queue.py`](05_containers/heapq_priority_queue.py) |
| `lower_bound` / `upper_bound` | `bisect_left/right` | [`binary_search_bisect.py`](07_algorithms/binary_search_bisect.py) |
| `accumulate` | `sum` / `itertools.accumulate` | [`accumulate_prefix_sum.py`](06_iteration_and_functional_tools/accumulate_prefix_sum.py) |
| 带下标循环 | `enumerate` | [`enumerate_zip.py`](06_iteration_and_functional_tools/enumerate_zip.py) |
| 同时遍历容器 | `zip` | [`enumerate_zip.py`](06_iteration_and_functional_tools/enumerate_zip.py) |

完整对照及创建、增删、查找、排序、复制和复杂度集中在
[`cpp_to_python_stl.py`](00_quick_reference/cpp_to_python_stl.py)。

## 推荐查阅顺序

1. [`00_quick_reference/`](00_quick_reference/)：先建立 STL 对照并浏览高频陷阱。
2. [`01_input_output/`](01_input_output/) 与
   [`02_files_and_directories/`](02_files_and_directories/)：掌握 USB 文件和批量目录处理。
3. [`03_text_parsing/`](03_text_parsing/) 与
   [`04_standard_formats/`](04_standard_formats/)：按题目数据格式选择解析方式。
4. [`05_containers/`](05_containers/) 至 [`09_matrices_and_sparse_data/`](09_matrices_and_sparse_data/)：
   用文件名直接寻找容器或算法。
5. [`12_exam_workflows/`](12_exam_workflows/)：熟悉完整考试执行流程。
6. [`13_example_tasks/`](13_example_tasks/)：查看多个模块如何组合成完整小任务。
7. [`10_object_oriented/`](10_object_oriented/)、
   [`11_debugging_and_testing/`](11_debugging_and_testing/)：按需补充。

## 按场景查找

| 我想…… | 查看 |
|---|---|
| 找 `vector`、`unordered_map`、集合 | [`05_containers/`](05_containers/) |
| 使用最小堆、最大堆、惰性删除 | [`heapq_priority_queue.py`](05_containers/heapq_priority_queue.py)、[`max_heap.py`](05_containers/max_heap.py)、[`heap_with_lazy_deletion.py`](05_containers/heap_with_lazy_deletion.py) |
| 使用 `lower_bound` | [`binary_search_bisect.py`](07_algorithms/binary_search_bisect.py) |
| 读取整个文件 | [`read_whole_file.py`](01_input_output/read_whole_file.py) |
| 逐行读取文件 | [`read_file_by_lines.py`](01_input_output/read_file_by_lines.py) |
| 批量读取目录文件 | [`batch_read_files.py`](02_files_and_directories/batch_read_files.py) |
| 递归遍历和镜像输出目录 | [`list_directory_recursive.py`](02_files_and_directories/list_directory_recursive.py)、[`mirror_output_directory.py`](02_files_and_directories/mirror_output_directory.py) |
| 用正则匹配文件名 | [`regex_filename_filter.py`](02_files_and_directories/regex_filename_filter.py) |
| 用普通字符串筛选文件名 | [`substring_filename_filter.py`](02_files_and_directories/substring_filename_filter.py) |
| 在终端输入和文件输入间切换 | [`switch_file_and_terminal.py`](01_input_output/switch_file_and_terminal.py) |
| 临时替换并恢复 `sys.stdin` | [`redirect_stdin_temporarily.py`](01_input_output/redirect_stdin_temporarily.py) |
| 区分脚本目录和当前工作目录 | [`resolve_script_relative_path.py`](01_input_output/resolve_script_relative_path.py) |
| 用 `yield` 逐行产生答案 | [`generator_solver.py`](12_exam_workflows/generator_solver.py) |
| 输出到终端、单独文件或总文件 | [`full_exam_template.py`](12_exam_workflows/full_exam_template.py) |
| 失败后继续批处理 | [`continue_after_file_error.py`](12_exam_workflows/continue_after_file_error.py) |
| 处理 CSV、JSON、JSON Lines | [`04_standard_formats/`](04_standard_formats/) |
| 用正则或 tokenizer 解析混合文本 | [`03_text_parsing/`](03_text_parsing/) |
| 写矩阵、COO、CSR 或稀疏数据 | [`09_matrices_and_sparse_data/`](09_matrices_and_sparse_data/) |
| 写 BFS、DFS、Dijkstra | [`bfs.py`](07_algorithms/bfs.py)、[`dfs_iterative.py`](07_algorithms/dfs_iterative.py)、[`dijkstra.py`](07_algorithms/dijkstra.py) |
| 写并查集 | [`union_find.py`](07_algorithms/union_find.py) 或 [`../utils/dsu.py`](../utils/dsu.py) |
| 写抽象类、继承和覆写 | [`abstract_base_class.py`](10_object_oriented/abstract_base_class.py)、[`inheritance_and_override.py`](10_object_oriented/inheritance_and_override.py) |
| 排查覆写参数名/数量问题 | [`override_signature_pitfalls.py`](10_object_oriented/override_signature_pitfalls.py) |
| 做简单线性拟合 | [`least_squares_without_numpy.py`](08_math_and_statistics/least_squares_without_numpy.py) |
| 批量运行测试文件 | [`batch_test_runner.py`](11_debugging_and_testing/batch_test_runner.py) |

## 重要入口文件

| 文件 | 用途 |
|---|---|
| [`cpp_to_python_stl.py`](00_quick_reference/cpp_to_python_stl.py) | 集中速查 C++17/STL 到 Python 的容器、算法和复杂度对应 |
| [`full_exam_template.py`](12_exam_workflows/full_exam_template.py) | 演示筛选输入、批量执行、容错、计时和多种输出方式 |
| [`io_runner.py`](15_utils/io_runner.py) | 完整考试模板使用的可复用批处理基础设施 |
| [`run_all_samples.py`](run_all_samples.py) | 在独立进程中批量验证示例，可用 `--pattern` 缩小范围 |

## 目录总索引

| 目录 | 内容 |
|---|---|
| [`00_quick_reference`](00_quick_reference/) | STL 全面对照、基础语法、常用一行写法、复杂度与陷阱 |
| [`01_input_output`](01_input_output/) | stdin、文件输入切换、编码、换行和脚本相对路径 |
| [`02_files_and_directories`](02_files_and_directories/) | pathlib、glob、正则筛选、自然排序、目录镜像与容错批处理 |
| [`03_text_parsing`](03_text_parsing/) | 数字、键值、分段、定宽、括号、tokenizer 和简单语言 |
| [`04_standard_formats`](04_standard_formats/) | CSV、JSON、JSON Lines、configparser 和二进制 I/O |
| [`05_containers`](05_containers/) | list、tuple、dict、set、Counter、deque、heap、bisect 和复制 |
| [`06_iteration_and_functional_tools`](06_iteration_and_functional_tools/) | enumerate、zip、推导式、生成器和 itertools |
| [`07_algorithms`](07_algorithms/) | 二分、前缀和、窗口、图搜索、最短路、DP 和回溯 |
| [`08_math_and_statistics`](08_math_and_statistics/) | math、组合数、浮点、统计、几何、矩阵和随机数据 |
| [`09_matrices_and_sparse_data`](09_matrices_and_sparse_data/) | 稠密矩阵、COO、CSR、转换、乘法和网格读取 |
| [`10_object_oriented`](10_object_oriented/) | 类、dataclass、继承、ABC、覆写、排序、多态和组合 |
| [`11_debugging_and_testing`](11_debugging_and_testing/) | assert、stderr、计时、unittest、doctest 和临时文件 |
| [`12_exam_workflows`](12_exam_workflows/) | 单文件、批量、输出目录、容错、计时和完整考试模板 |
| [`13_example_tasks`](13_example_tasks/) | 九个带真实输入和期望输出的完整综合任务 |
| [`14_optional_numpy`](14_optional_numpy/) | 可选 NumPy 数组、读取、矩阵、统计和最小二乘 |
| [`15_utils`](15_utils/) | 可复用 runner、筛选、解析、自然排序和计时工具 |

## 九个完整任务

- [`word_frequency`](13_example_tasks/word_frequency/)：批量词频与 `Counter`
- [`log_analysis`](13_example_tasks/log_analysis/)：正则日志解析与汇总
- [`graph_from_files`](13_example_tasks/graph_from_files/)：图文件与连通分量
- [`sparse_matrix`](13_example_tasks/sparse_matrix/)：COO、CSR、查询和乘向量
- [`simple_interpreter`](13_example_tasks/simple_interpreter/)：tokenizer 与递归下降解释器
- [`infection_data`](13_example_tasks/infection_data/)：时间序列、移动平均和拟合
- [`image_like_grid`](13_example_tasks/image_like_grid/)：字符网格、连通区域和变换
- [`directory_tree`](13_example_tasks/directory_tree/)：递归目录树和文件统计
- [`numerical_fitting`](13_example_tasks/numerical_fitting/)：标准库/NumPy 最小二乘对照

每个任务都包含 `README.md`、`solution.py`、真实 `input/` 和
`output_expected/`。

## Windows PowerShell 与 CMD

PowerShell：

```powershell
python .\samples\12_exam_workflows\full_exam_template.py
Get-ChildItem .\samples -Recurse -Filter *.py |
    Select-String -Pattern 'bisect_left'
```

CMD：

```bat
python samples\12_exam_workflows\full_exam_template.py
findstr /s /n /i "bisect_left" samples\*.py
```

路径处理示例统一优先使用 `pathlib.Path`。请特别记住：

- `Path("input.txt")` 相对于当前工作目录 `Path.cwd()`；
- `Path(__file__).resolve().parent` 才是脚本所在目录；
- `list.pop(0)` 为 O(n)，队列应使用 `deque.popleft()`；
- `[[0] * m] * n` 会共享内部列表；
- `list.sort()` 原地排序并返回 `None`；
- `//` 对负数向下取整；
- Python 标准库没有平衡树 `set/map`；
- 递归深度有限，深图优先使用迭代 DFS。
