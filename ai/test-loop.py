W, H, S = map(int, input().split())
if not int(S): input()

x = 0
while True:
    x = (x % W) + 1
    print(x)
    input()
