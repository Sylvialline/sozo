import math
E = 551263368336670859257571
N = 3858843578360632069557337

for d in range(1, N // E + 1):
    a = N - E * d + 2
    b = N

    delta = a**2 - 4 * b
    root = math.isqrt(delta)
    if root**2 != delta:
        continue
    p = (a - root) // 2
    q = a - p
    print(f"{d=}, {p=}, {q=}")
    # d = 7
