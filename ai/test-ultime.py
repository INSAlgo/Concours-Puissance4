import random

W, H, N, S = map(int, input().split())

x = random.randint(1, W)
t = 0
while True:
    t = t % N + 1
    if t == S:
        print(x)
    else:
        input()
