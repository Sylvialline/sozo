# fy2009_s_program 数据、答案与脚本

本目录对应 `fy2009_s_ja_program.pdf` 与 `fy2009_s_en_program.pdf`，即 2010 年度夏季入学考试（2009 年实施）的编程题。

根据本次任务要求，问1至问5全部整理为程序输出题；原题中要求描述算法的问5增加了 `q5.txt`。

## 文件结构

- `problem.md`：去除考试流程和空白页后的核心题意，以及统一后的输入输出格式。
- `data/7.txt`：符合原题示例统计量的 7 矩形数据。
- `data/10.txt`：问1输入。
- `data/1000.txt`：问2、问3、问4共用输入。
- `data/q5.txt`：问5新增的大坐标输入，共 5000 个矩形。
- `outputs/q1.out` 至 `outputs/q5.out`：标准输出文件。
- `answers/standard_answers.md`：便于阅读的标准答案。
- `answers/answers.json`：机器可读答案，其中额外记录问4达到的最大簇面积。
- `scripts/rectangle_model.py`：矩形连接、簇、面积、放置枚举和扫描线算法。
- `scripts/generate_data.py`：确定性数据生成器。
- `scripts/solve.py`：标准答案生成器。
- `scripts/validate.py`：格式、约束、答案和独立性质校验器。
- `generation_manifest.json`：数据规模、随机种子和设计说明。
- `validation.json`：最终校验报告。

## 重新生成

在本目录运行：

```bash
python scripts/generate_data.py
python scripts/solve.py
python scripts/validate.py
```

全部脚本只使用 Python 标准库。数据生成过程确定，重复运行会得到相同文件。
