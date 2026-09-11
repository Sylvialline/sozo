# 历年代码参考索引

这里收录不适合抽成通用 `utils`、但遇到相似题型时值得回看真实实现的代码模式。表格只
负责定位，不复制实现；打开对应 `solve.py` 后结合原题语境使用。

| 遇到的情况 | 参考实现 | 重点查看 | 可以借鉴 |
| --- | --- | --- | --- |
| 题目用“单元格 + 墙坐标”描述方格迷宫 | [`2022-8/solve.py:24`](2022-8/solve.py#L24) | `MOVES`、`cell2wall`、`all_walls`、`Maze` | 墙坐标编码、由墙集合构造无向图、边界墙生成 |
| 状态同时包含位置和朝向，需要模拟左手贴墙行走 | [`2022-8/solve.py:310`](2022-8/solve.py#L310) | `Status`、`navigate` | 用不可变状态表示位置与朝向、转向和单步状态转移 |
| 有向图需要 SCC 缩点后按 DAG 顺序计算 | [`2023-8/solve.py:114`](2023-8/solve.py#L114) | `Graph.compress`、`Graph.top_sort`；通用接口见 [`utils/graph.py:338`](utils/graph.py#L338) | 原节点与分量映射、凝缩图上的动态规划顺序 |
| 需要分解较大的整数，环境中可以使用第三方包 | [`2019-s/solve.py:248`](2019-s/solve.py#L248) | `recover_d_by_factorization`、`primefac` | 用 `primefac(n)` 获取质因数，再根据题目关系恢复所需参数 |
| 输入或输出包含二进制文件，需要由 task 手动控制文件 I/O | [`2019-s/solve.py:99`](2019-s/solve.py#L99)、[`2019-s/solve.py:113`](2019-s/solve.py#L113) | `task2`、`task3`、`DATA`、`OUTPUT` | 用 `Case` 传递输入/输出文件名，在 task 内调用 `read_bytes`、`write_bytes` 并返回答案元数据 |
| 用 `curses` 编写需要即时按键和定时刷新的命令行游戏 | [`2011-s/game.py:25`](2011-s/game.py#L25)、[`2011-s/game.py:114`](2011-s/game.py#L114) | `State.draw`、`main_async`、`curses.wrapper` | 用 `erase` 清空窗口，配合 `addstr`、`addch`、`refresh` 重绘；用 `timeout` 轮询按键，并以 `monotonic` 截止时间解耦输入和游戏更新 |

新增条目时优先记录“什么情况下应该来查”，并把函数名或类名写入“重点查看”；只有跨题
稳定、调用比重写更省事的模式才进一步提炼进 `utils`。
