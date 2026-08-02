# Optional NumPy samples

本目录是唯一允许依赖第三方库的示例区。核心仓库和考试工作流不依赖 NumPy。

先确认考试电脑已经安装：

```powershell
python -c "import numpy; print(numpy.__version__)"
```

未安装 NumPy 时，本目录脚本会打印提示并正常退出。不要在考试前未经验证就依赖它。

- [`numpy_array_basics.py`](numpy_array_basics.py)：数组、切片、布尔索引
- [`loadtxt_genfromtxt.py`](loadtxt_genfromtxt.py)：规则/缺失数据读取
- [`matrix_operations.py`](matrix_operations.py)：矩阵乘法、转置、求解线性方程
- [`statistics.py`](statistics.py)：均值、方差、分位数
- [`least_squares.py`](least_squares.py)：线性最小二乘
