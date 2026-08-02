"""用途：在字符串或文件风格对象中读取、修改并写回 JSON。
示例输入：{"name":"A","scores":[3,1,4],"active":true}
示例输出：格式化后的 JSON，scores 增加 5，且保留中文。
复杂度：解析与序列化均为 O(JSON 字符数)，内存 O(数据大小)。
常见陷阱：JSON 的 null/true/false 对应 Python 的 None/True/False；键通常是字符串。
"""

import json


def update_json(text: str) -> str:
    data = json.loads(text)
    data["scores"].append(5)
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def main() -> None:
    source = '{"name":"东京","scores":[3,1,4],"active":true}'
    rendered = update_json(source)
    print(rendered)
    restored = json.loads(rendered)
    print("best:", max(restored["scores"]))


if __name__ == "__main__":
    main()
