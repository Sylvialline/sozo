"""用途：用 configparser 读取 INI 配置并进行字符串、整数和布尔转换。
示例输入：[runner] workers=4, debug=yes；[paths] input=data
示例输出：workers=4 debug=True input=data。
复杂度：读取 O(配置字符数)，查询通常 O(1)。
常见陷阱：默认值是字符串；键名默认不区分大小写；插值中的 % 有特殊含义。
"""

from configparser import ConfigParser


def parse_config(text: str) -> ConfigParser:
    config = ConfigParser()
    config.read_string(text)
    return config


def main() -> None:
    text = """\
[runner]
workers = 4
debug = yes

[paths]
input = data
"""
    config = parse_config(text)
    print("workers:", config.getint("runner", "workers"))
    print("debug:", config.getboolean("runner", "debug"))
    print("input:", config["paths"]["input"])
    print("missing with fallback:", config.get("paths", "output", fallback="results"))


if __name__ == "__main__":
    main()
