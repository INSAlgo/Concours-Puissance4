import sys

import pexpect

prog1 = "p1.py"
prog2 = "p2.py"

p1 = pexpect.spawn("./"+prog1, timeout = 1)
p1.setecho(False)
p2 = pexpect.spawn("./"+prog2, timeout = 1)
p2.setecho(False)

try :
    p1.sendline('start')
    output = p1.readline().decode('ascii').strip()
    print("a", output)
except pexpect.TIMEOUT as e:
    print("Program 1 took too long")
    sys.exit(0)

for _ in range(26):
    try :
        p2.sendline(output)
        output = p2.readline().decode('ascii').strip()
        print("b", output)
    except pexpect.TIMEOUT as e:
        print("Program 2 took too long")
        sys.exit(0)

    try :
        p1.sendline(output)
        output = p1.readline().decode('ascii').strip()
        print("a", output)
    except pexpect.TIMEOUT as e:
        print("Program 1 took too long")
        sys.exit(0)


p1.close()
p2.close()
