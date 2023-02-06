import random

W, H, S = map(int, input().split())
if not int(S): input()

x = random.randint(1, W)
while True:
    print(x)
    input()
