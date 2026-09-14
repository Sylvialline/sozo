# fy2012_s_program 交付说明

本数据包基于英文版和日文版原题逐项交叉核验后制作，包含完整中文题面、5 个主数据文件、6 问标准答案、12 个补充回归用例，以及全部生成、求解和验证脚本。

## 文件结构

```text
problem_zh.md                 中文题面
source_crosscheck.md          英日版本逐项核验记录
data/prog1.txt ... prog5.txt  原题要求的 5 个测试文件
outputs/q1.out ... q6.out     六问的逐字标准输出
answers/standard_answers.md   标准答案与解释
answers/answers.json          机器可读答案
tests/programs/*.txt          12 个补充回归程序
tests/expected/*.out          回归程序逐字标准输出
scripts/interpreter.py        标准 L 语言解释器
scripts/generate_data.py      确定性数据生成器
scripts/solve.py              标准答案生成器
scripts/validate.py           独立 VM、结构检查与性质测试
scripts/mutation_check.py     代表性错误实现检出测试
generation_manifest.json      文件规模、哈希及回归用例元数据
validation.json               最终验证报告
mutation_report.json          代表性错误实现检出报告
```

## 重新生成与验证

在本目录执行：

```bash
python scripts/generate_data.py
python scripts/solve.py
python scripts/validate.py
python scripts/mutation_check.py
```

所有生成过程均为确定性的。`validate.py` 除使用标准解释器外，还包含一套独立实现，并执行固定答案检查、12 个定向回归用例和 394 个性质测试。`mutation_check.py` 还会运行 14 类有意写错的解释器语义，确认本数据能使它们全部暴露错误。

## 主数据针对的常见错误

| 数据 | 重点覆盖 |
|---|---|
| `prog1.txt` | 变量、正负整数、0、大绝对值整数、所有 5 个操作码、未使用操作数 |
| `prog2.txt` | 负数、变量到变量赋值、源目的相同的加法、仅使用本问允许的 3 条指令 |
| `prog3.txt` | 多字符变量名、`CMP` 真/假两种分支、被跳过的错误答案、前后跳转、变量偏移、相对当前行 |
| `prog4.txt` | 递归式嵌套子程序、LIFO 返回栈、变量偏移 `SUB`、全局变量共享、未使用操作数 |
| `prog5.txt` | 递归函数、两次递归调用、局部变量遮蔽、调用者状态恢复、`in/out`、返回值传播 |

补充回归集把这些特性拆成较小的单一目的用例，便于定位候选程序具体在哪条语义上出错。

## 数据合规性

- 所有 L 代码均为 ASCII 文本，且每行恰好一条三字段指令。
- 所有程序均少于 100 行，同时满足英文版和日文版的行数表述。
- `prog2.txt` 不含 `CMP/JMP`。
- `prog1.txt` 中作为变量名出现的只有 `x` 和 `y`。
- 所有实际执行路径均终止于 `PRN`，且不会读取未赋值的普通变量。
