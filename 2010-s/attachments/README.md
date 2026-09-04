# fy2010_s_program 数据、答案与脚本

本目录对应 `fy2010_s_en_program.pdf` 与 `fy2010_s_ja_program.pdf`，即 2011 年度夏季入学考试（2010 年实施）的编程题。

## 文件结构

- `problem.md`：去除考试流程、空白页和重复说明后的核心题意。
- `data/s1.txt`、`data/s2.txt`、`data/s3.txt`：源字符串测试数据。
- `data/c1.txt`、`data/c2.txt`：合法压缩字符串测试数据。
- `outputs/q1.out` 至 `outputs/q6.out`：各问参考输出。
- `answers/standard_answers.md`：便于阅读的标准答案。
- `answers/answers.json`：机器可读答案及问6分块校验信息。
- `scripts/codec.py`：辞典构建、压缩、解压和分块处理。
- `scripts/generate_data.py`：确定性强数据生成器。
- `scripts/solve.py`：标准答案生成器。
- `scripts/validate.py`：独立实现、格式约束和答案校验器。
- `generation_manifest.json`：数据长度、随机种子和查错点说明。
- `validation.json`：最终校验报告。

## 强数据覆盖点

- 重叠引用和逐字符自复制；
- 多次出现时选择最小位置；
- `000`、`009`、`099`、`100`、`993` 等边界替换指示串；
- 空格、逗号、句点及有效的文件首尾空格；
- 长度恰为 1000 的单块数据；
- 1000 字符分块处重置辞典；
- 问6最后一个块长度小于 6。

## 重新生成与验证

在本目录运行：

```bash
python scripts/generate_data.py
python scripts/solve.py
python scripts/validate.py
```

全部脚本仅使用 Python 标准库。生成过程确定，重复运行会得到完全相同的数据和答案。
