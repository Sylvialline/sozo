# fy2008_s_program 本地重建数据与参考答案

本目录依据公开归档中的 [2009 Summer Entrance Examination Programming 试题](https://github.com/diohabara/open_inshi/blob/master/the_university_of_tokyo/graduate_school_of_information_science_and_technology/creative_informatics/fy2008_s_en_program.pdf) 整理。`problem.md`、`data/` 和 `answers/` 均为仓库内的本地重建内容，不是官方原始附件或官方答案。

## 文件说明

- `problem.md`：依据原题整理、并保留 Figure 3 阶梯展开关系的核心题意。
- `data/`：按题目格式确定性生成的 7 个 ASCII/CRLF 本地练习输入文件。
- `answers/standard_answers.md`：针对本地数据与模型生成的 Q1-Q5 参考答案。
- `answers/answers.json`：机器可读的同一套参考答案。
- `generation_manifest.json`：生成的五个状态的确切最短距离及生成路径。
- `scripts/cube_model.py`：24 面片几何模型、旋转与整颗魔方置向模型。
- `scripts/generate_data.py`：确定性数据生成器。
- `scripts/solve.py`：标准答案生成程序。
- `scripts/validate.py`：格式、几何性质、最短距离和答案校验程序。
- `validation.json`：格式、最短路与 Figure 3 固定转动样例的校验报告。

## 重新生成与验证

在本目录运行：

```bash
python scripts/generate_data.py
python scripts/solve.py
python scripts/validate.py
```

脚本只使用 Python 标准库。生成过程是确定性的，重复运行将得到相同的数据和答案。

## 数据设计

- `rotseq.txt` 第一行严格沿用题面指定的 `R1 U3 F2`，其余三行覆盖不同旋转和长度。
- `data1.txt` 至 `data5.txt` 均从初始状态仅使用 U/R/F 旋转生成，因此已经正确置向。
- 五个状态的确切最短复原长度依次为 2、3、4、5、6，覆盖题目允许范围中的多个规模。
- 面片下标严格采用题图的阶梯展开方式 `U R /  F D /    L B`；缩进表示共享边，不可把六个面当作彼此独立的正视图。
- 沿展开图共享边折叠后，U/R/F 旋转共同不动的 D-L-B 角对应 `r3`、`y2`、`b1`。
