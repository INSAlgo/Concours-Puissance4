W, H, N, S = map(int, input().split())

t = 0
x = 0
while True:
    t = t % N + 1
    x = x % W + 1
    if t == S:
        print(x)
    else:
        input()
