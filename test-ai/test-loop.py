import time

W, H, N, S = map(int, input().split())

p = 0
x = 0
while True:
    time.sleep(0.08)
    p = p % N + 1
    x = (x + 1) % W
    if p == S:
        print(x)
    else:
        input()
