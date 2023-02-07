import random

W, H, N, S = map(int, input().split())

t = 0
while True:
    t = t % N + 1
    print("> TEST")
    if t == S:
        print(random.randint(1, W))
    else:
        input()
