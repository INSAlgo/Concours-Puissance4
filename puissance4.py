#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
import pexpect

WIDTH = 7
HEIGHT = 6


class Player(ABC):

    def __init__(self, no):
        self.no = no

    @abstractmethod
    def askMove(self):
        pass

    @abstractmethod
    def tellLastMove(self, x):
        pass

class User(Player):

    def __init__(self, no):
        super().__init__(no)

    def askMove(self):
        try:
            return input(f"Column for player {self.no} : ")
        except KeyboardInterrupt:
            sys.exit(1)

    def tellLastMove(self, x):
        pass

class AI(Player):

    def __init__(self, no, progName, W, H, verbose):
        super().__init__(no)
        self.verbose = verbose
        self.progName = progName
        if progName.endswith(".py"):
            cmd = f"python {progName}"
        else:
            cmd = f"./{progName}"
        self.prog = pexpect.spawn(cmd, timeout=1)
        self.prog.setecho(False)
        S = 2 - self.no
        self.prog.sendline(f"{W} {H} {S}")

    def askMove(self):
        if self.verbose:
            print(f"Column for AI {self.no} : ", end="")
        try:
            progInput = self.prog.readline().decode('ascii').strip()
        except pexpect.TIMEOUT:
            print("Program 1 took too long")
            return False
        if self.verbose:
            print(progInput)
        return progInput

    def tellLastMove(self, x):
        self.prog.sendline(str(x))

def checkWin(board, no):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if board[x][y] == no:
                for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                    streak = 1
                    for i in range(1, 4):
                        nx, ny = x + dx * i, y + dy * i
                        if nx >= WIDTH or ny >= HEIGHT:
                            break
                        if board[nx][ny] == no:
                            streak += 1
                        else:
                            break
                    if streak >= 4:
                        return True
    return False


def display(board, player, verbose):
    if isinstance(player, AI) and not verbose:
        return
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

def game(p1: Player, p2: Player, verbose: bool):
    players = (p1, p2)
    turn = 0
    board = [[0 for _y in range(HEIGHT)] for _x in range(WIDTH)]
    winner = None
    while winner is None:
        turn += 1
        player = players[(turn + 1)% 2]
        otherPlayer = players[turn % 2]
        display(board, player, verbose)
        while True:
            userInput = player.askMove()
            x = sanithize(board, userInput, verbose=verbose)
            if x != -1:
                break
            elif isinstance(player, AI):
                winner = otherPlayer
                break
        y = fallHeight(board, x)
        board[x][y] = player.no
        otherPlayer.tellLastMove(x)
        if checkWin(board, player.no):
            winner = player
            display(board, player, verbose)

    if verbose:
        print(f"Player {winner.no} wins")
    else:
        print(winner.no)

def main():
    args = list(sys.argv[1:])
    verboseAI = True
    verbose = True
    if "-s" in args:
        verboseAI = False
        args.remove("-s")
    if len(args):
        p1 = AI(1, args.pop(), WIDTH, HEIGHT, verboseAI)
    else:
        p1 = User(1)
    if len(args):
        p2 = AI(2, args.pop(), WIDTH, HEIGHT, verboseAI)
        verbose = False
    else:
        p2 = User(2)
    game(p1, p2, verbose)


if __name__ == "__main__":
    main()

