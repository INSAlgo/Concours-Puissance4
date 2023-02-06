import random

W, H, S = map(int, input().split())
if not int(S): input()

while True:
    print(random.randint(1, W))
    input()
