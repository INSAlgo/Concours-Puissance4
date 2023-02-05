WIDTH = 7
HEIGHT = 6

def checkWin(board):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            color = board[x][y]
            if color:
                for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                    streak = 1
                    for i in range(1, 4):
                        nx, ny = x + dx * i, y + dy * i
                        if nx >= WIDTH or ny >= HEIGHT:
                            break
                        if board[nx][ny] == color:
                            streak += 1
                        else:
                            break
                    if streak >= 4:
                        return color
    return 0


def display(board):
    print()
    print("  ", end="")
    for x in range(1, WIDTH + 1):
        print(x, end=" ")
    print()
    print("┌" + "─" * (WIDTH * 2 + 1) + "┐")
    for y in range(HEIGHT - 1, -1, -1):
        print("│", end=" ")
        for x in range(WIDTH):
            if board[x][y]:
                print(board[x][y], end=" ")
            else:
                print(".", end=" ")
        print("│")
    print("└" + "─" * (WIDTH * 2 + 1) + "┘")
    print("  ", end="")
    for x in range(1, WIDTH + 1):
        print(x, end=" ")
    print()

def fallHeight(board, x):
    y = HEIGHT
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

def sanithize(board, userInput, verbose=False):
    try:
        x = int(userInput) - 1
    except ValueError:
        if verbose: print("Invalid input")
        return -1
    if not (0 <= x < WIDTH):
        if verbose: print("Out of bounds")
        return -1
    if fallHeight(board, x) == HEIGHT:
        if verbose: print("Column full")
        return -1
    return x

def askMove(color):
    return input("Column for player " + str(color) + " : ")

def game():
    board = [[0 for _y in range(HEIGHT)] for _x in range(WIDTH)]
    win = 0
    player = 1
    while win == 0:
        display(board)
        while True:
            userInput = askMove(player)
            x = sanithize(board, userInput, verbose=True)
            if x != -1:
                break
        y = fallHeight(board, x)
        board[x][y] = player
        win = checkWin(board)
        player = 3 - player
    display(board)
    print("Player", win, "wins")

if __name__ == "__main__":
    game()

