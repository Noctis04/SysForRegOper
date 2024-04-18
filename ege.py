def f(x, k):
    if x == 20 and k == 6:
        return 1
    elif x > 20:
        return 0
    return f(x + 1, k + 1) + f(x + 2, k + 1) + f(x * 2, k + 1)


print(f(1, 0))