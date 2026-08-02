"""类、构造函数、实例属性和实例方法的最小完整示例。

示例输入：创建余额 100 的账户，存入 50，再取出 30。
示例输出：余额 120，并显示交易次数 2。
复杂度：本例每次存取均为 O(1)。
常见陷阱：实例方法第一个参数通常命名为 ``self``；属性属于各实例而非局部变量。
"""


class BankAccount:
    def __init__(self, owner: str, balance: int = 0) -> None:
        if balance < 0:
            raise ValueError("initial balance cannot be negative")
        self.owner = owner
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self.transaction_count += 1

    def withdraw(self, amount: int) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            return False
        self.balance -= amount
        self.transaction_count += 1
        return True


def main() -> None:
    account = BankAccount("Alice", 100)
    account.deposit(50)
    print("withdraw succeeded:", account.withdraw(30))
    print("owner/balance/transactions:", account.owner, account.balance, account.transaction_count)


if __name__ == "__main__":
    main()
