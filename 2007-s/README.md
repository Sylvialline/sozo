# fy2007_s_program 数据与标准答案

本目录对应附件 `fy2007_s_program.pdf`（题面标题为“平成 20 年度 / 2008 Summer Entrance Examination”）。

## 文件说明

- `problem.md`：去除考试流程等无关内容后的核心题意。
- `data/edges.txt`：本次生成的完整测试数据，含全部 4,950 个无向顶点对，使用纯 ASCII 与 CRLF 换行。
- `answers/standard_answers.md`：逐题标准答案。
- `answers/answers.json`：同一答案的机器可读版本。
- `answers/q1_answer.svg`：Q1 的一种无交叉画法。
- `scripts/generate_data.py`：确定性数据生成器，仅使用 Python 标准库。
- `scripts/solve.py`：标准解答程序；生成 Markdown 和 JSON 答案。
- `scripts/generate_q1_svg.py`：Q1 图形答案生成器。
- `scripts/validate.py`：独立校验数据格式、题面约束和全部数值答案。
- `validation.json`：校验结果。

## 重新生成

在本目录中依次运行：

```bash
python scripts/generate_data.py
python scripts/solve.py
python scripts/generate_q1_svg.py
python scripts/validate.py
```

生成器固定使用确定性顺序，因此重复运行会得到完全相同的 `edges.txt` 和答案。

## 数据结构概览

- 前 181 条边构成 $G_2$，它有 4 个大小均为 25 的连通分量。
- 第 184 条边加入后首次连通，因而 $G_3$ 的边数为 184。
- 接下来的 100 条边以跨分量匹配为主，提供大量捷径而很少闭合三角形，保证 $G_4$ 的平均聚类系数低于 $G_3$。
- 此后补齐所有尚未出现的顶点对，最终得到 $K_{100}$。
