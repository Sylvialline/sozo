# 交付内容与复现方法

目录严格分为：

```text
problem.md
data/
answers/
attachments/
```

其中 `data/q1.txt` 至 `data/q6.txt` 是多测输入；`answers/q1.txt` 至 `answers/q6.txt` 是逐行标准答案；`answers/standard_answers.md` 给出公式、算法和校验值。

`attachments/` 中保留了全部工作脚本和核验材料：

- `generate_data.py`：确定性生成六个输入文件。
- `exact_geometry.py`：精确十进制、$\mathbb Q(\sqrt3)$、圆盘计数、科赫边界和扫描线算法。
- `solve.py`：生成六个答案文件。
- `validate.py`：独立慢算法、性质测试、格式和哈希检查。
- `source_crosscheck.md`：英日两版逐项核验结果。
- `manifest.json`：种子、范围、用例数和输入哈希。
- `validation.json`：最终验证结果及输入/答案哈希。

在交付目录内执行：

```bash
python attachments/generate_data.py
python attachments/solve.py
python attachments/validate.py
```

标准答案生成器只用 `Decimal`、`Fraction` 和整数运算读取或判断十进制输入；没有把 `d` 转换为二进制浮点数。面积统一使用高精度 `Decimal.sqrt()`，再按规定舍入到 20 位小数。

六个输入文件合计 53,363 组独立询问。问（4）的 75 组覆盖固定 20 位小数格式下全部 62 种可区分答案，并保留若干超大 $n$ 检测低效实现。完整标准解在当前 Python 环境约 2 分钟内完成；验证器约 10 秒完成格式、范围、哈希、公式、独立圆盘枚举和 47 组独立科赫绕数检查。
