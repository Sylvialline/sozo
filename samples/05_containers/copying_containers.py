"""用途：对比赋值、浅拷贝和 deepcopy 对嵌套容器的影响。
示例输入：original = [[1], [2]]，分别修改 alias/shallow/deep。
示例输出：赋值共享外层；浅拷贝仍共享内层；深拷贝完全独立。
复杂度：浅拷贝 O(外层长度)；深拷贝通常 O(全部可达数据大小)。
常见陷阱：a = b 不会复制；list.copy()/切片仅复制一层；深拷贝可能昂贵或不适用。
"""

from copy import deepcopy


def main() -> None:
    original = [[1], [2]]
    alias = original
    shallow = original.copy()
    deep = deepcopy(original)

    alias.append([3])           # original 的外层也改变
    shallow[0].append(9)        # original 的第 0 个内层也改变
    deep[1].append(8)           # 仅 deep 改变

    print("original:", original)
    print("alias is original:", alias is original)
    print("shallow:", shallow)
    print("deep:", deep)


if __name__ == "__main__":
    main()
