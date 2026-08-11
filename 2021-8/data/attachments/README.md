# 2021-8 Programming 1 / Programming 2 合成数据

本目录是一套依据 `2021-8-programming.pdf` 题面确定性生成的练习数据，**不是原考试 USB 中的数据**。PDF 包含 Programming 1 和 Programming 2 两张独立试卷，共 8 个小题；两张试卷都引用名为 `data` 的文件夹。由于本仓库只交付一个 `2021-8/data/`，本数据包采用下面这个明确、可复现的约定：

- `data/` 根目录的 8 个 `.txt` 都参与 Programming 1(2) 的求和；
- 同样的 8 个 `.txt` 都参与 Programming 2(2) 的两两相似度比较；
- `attachments/` 中的文本、答案和代码都不是输入数据。

## 输入与约束

每个输入文件都只有一行，以冒号分隔非负十进制整数，并以一个换行结束。题面没有给出长度、数值或文件数量上界；本数据包只声称满足题面语义及让所有问题有定义所必需的条件：

- 每个文件至少有 10 个不同值；
- `infections.txt` 至少有 7 天数据；
- `infections2.txt` 至少有 31 天数据；
- `data/` 至少包含两个输入文件。

输入文件如下：

- `infections.txt`：Programming 1(1)(3)(4) 和 Programming 2(1) 的指定输入；
- `infections2.txt`：Programming 2(3)(4) 的指定输入；
- `baseline.txt`、`plateau.txt`、`sawtooth.txt`：不同长度、重复分布和变化模式；
- `echo_short.txt`、`echo_long_a.txt`、`echo_long_b.txt`：短序列嵌入长序列中，用于覆盖非零对齐位置和并列最优文件对。

数据还覆盖正/负/零增量、去重排名、大整数平方误差、多个最短最大和区间，以及两个数学上精确并列的 31 天最快指数增长窗口。详细规模见 `dataset_summary.json`。

## 文件说明

```text
data/
├─ baseline.txt
├─ echo_long_a.txt
├─ echo_long_b.txt
├─ echo_short.txt
├─ infections.txt
├─ infections2.txt
├─ plateau.txt
├─ sawtooth.txt
└─ attachments/
   ├─ README.md
   ├─ answers.json
   ├─ answers.txt
   ├─ dataset_summary.json
   ├─ diff.txt
   ├─ generate_data.py
   ├─ manifest.sha256.tsv
   ├─ reference_solver.py
   └─ test_reference_solver.py
```

- `reference_solver.py`：8 个小题的标准库参考实现，也是参考答案生成代码。
- `answers.json`：机器可读参考答案；`answers.txt`：便于抄录的答案。
- `diff.txt`：Programming 1(3) 要求生成的参考输出文件；它位于附件中，因此不会被误当作输入。
- `generate_data.py`：固定公式、无随机状态的可复现生成器。
- `test_reference_solver.py`：绕过标准解主函数，独立朴素复算正式数据的全部 8 个答案；另含最大区间的随机二次暴力对拍和公式单元测试。
- `manifest.sha256.tsv`：所有正式输入、答案、文档和代码（清单自身除外）的字节数与 SHA-256。

重新生成全部输入与参考答案：

```powershell
python 2021-8/data/attachments/generate_data.py
```

单独运行标准解或测试：

```powershell
python 2021-8/data/attachments/reference_solver.py
python 2021-8/data/attachments/test_reference_solver.py -v
```

所有脚本只依赖 Python 标准库。生成器只写本数据包列出的输入/答案产物，不读取、创建或修改 `solve.py`。
