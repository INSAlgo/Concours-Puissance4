import random

W, H, N, S = map(int, input().split())

t = 0
while True:
    t = t % N + 1
    if t == S:
        print(random.randrange(0, W))
    else:
        input()