"""用途：速查 dict（哈希映射，近似 unordered_map）及排序遍历。
示例输入：{"red": 2, "blue": 1}，更新 red，新增 green，删除 blue。
示例输出：按键排序后的 [('green', 1), ('red', 5)]。
复杂度：查找/增删平均 O(1)、最坏 O(n)；排序键 O(n log n)。
常见陷阱：dict 保持插入顺序但不按键排序；d[k] 缺失会 KeyError；遍历时勿改大小。
"""


def main() -> None:
    counts = {"red": 2, "blue": 1}     # 创建
    counts["red"] += 3                 # 修改
    counts["green"] = 1                # 添加
    counts.setdefault("yellow", 0)     # 仅缺失时添加
    del counts["blue"]                  # 不存在会 KeyError
    counts.pop("yellow", None)          # 安全删除

    print("red:", counts.get("red", 0))
    print("has blue:", "blue" in counts)
    print("sorted items:", sorted(counts.items()))

    copied = counts.copy()              # 浅拷贝
    merged = counts | {"red": 99, "black": 1}  # 右侧覆盖（Python 3.9+）
    print("copy:", copied)
    print("merged:", merged)


if __name__ == "__main__":
    main()
