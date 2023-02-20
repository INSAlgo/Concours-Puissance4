import random
import time

W, H, N, S = map(int, input().split())

t = 0
while True:
    t = t % N + 1
    time.sleep(0.08)
    if t == S:
        print(random.randrange(0, W))
    else:
        input()
