# 官方离线文档

本目录中的文档与当前考试环境匹配：

| 项目 | 本机版本 | 离线文档 | 入口 |
| --- | --- | --- | --- |
| Python | 3.12.7 | 3.12.7 | [`python-3.12.7/index.html`](python-3.12.7/index.html) |
| NumPy | 1.26.4 | 1.26 系列手册 | [`numpy-1.26/index.html`](numpy-1.26/index.html) |
| SciPy | 1.13.1 | 1.13.1 | [`scipy-1.13.1/index.html`](scipy-1.13.1/index.html) |

考试时直接双击 [`index.html`](index.html)，再选择项目或 API Reference。各文档的
搜索页和搜索索引已经包含在本地，不需要互联网。

如果浏览器限制 `file://` 页面脚本，可在仓库根目录运行：

```powershell
python -m http.server 8000 --directory offline_docs
```

然后打开 `http://localhost:8000/`。这只是本机静态文件服务器，不访问互联网。

## 官方来源

- Python 3.12.7 HTML：<https://www.python.org/ftp/python/doc/3.12.7/python-3.12.7-docs-html.zip>
- NumPy 1.26 HTML：<https://numpy.org/doc/1.26/numpy-html.zip>
- SciPy 1.13.1 HTML：<https://docs.scipy.org/doc/scipy-1.13.1/scipy-html-1.13.1.zip>

下载归档经 ZIP 完整性读取后解压；归档本身随后删除以免重复占用空间。下载时计算的
SHA-256 如下：

```text
Python  d1f641e5530348db9e0657f3f32d07981f03d51f1ac5364c73f014a05e63835e
NumPy   1dc88fc45a7709143b7b917e8e807e4985c41fe3fb7ee5fc55c3aeec5f369fdd
SciPy   d2618f3bd074f138ad4a41ea1a646c76db4d38cb0e988da679814ebb71737116
```

NumPy 官方按 `1.26` 系列提供这份 HTML 手册；它对应本机安装的 NumPy 1.26.4。
