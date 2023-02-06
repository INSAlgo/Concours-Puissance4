#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
from os import path
import pexpect

WIDTH = 7
HEIGHT = 6
TIMEOUT = 0.1


class Player(ABC):

    def __init__(self):
        self.no = 0
        self.verbose = True

    @abstractmethod
    def askMove(self):
        pass

    @abstractmethod
    def tellLastMove(self, x):
        pass

    @abstractmethod
    def getName(self, verbose):
        pass

class User(Player):

    def __init__(self):
        super().__init__()

    def askMove(self):
        try:
            return input(f"Column for player {self.no} : ")
        except KeyboardInterrupt:
            sys.exit(1)

    def tellLastMove(self, x):
        super().tellLastMove(x)

    def getName(self, verbose):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def cmd(progName):
        if not path.exists(progName):
            sys.stderr.write(f"File {progName} not found\n")
            sys.exit(1)
        extension = progName.split(".")[-1]
        match extension:
            case "py":
                return f"python {progName}"
            case "js":
                return f"node {progName}"
            case _:
                return f"./{progName}"

    def __init__(self, progName, width=WIDTH, height=HEIGHT, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.progName = path.basename(progName)
        self.prog = pexpect.spawn(AI.cmd(progName), timeout=TIMEOUT)
        self.prog.delaybeforesend = None
        self.prog.setecho(False)
        S = 2 - self.no
        self.prog.sendline(f"{width} {height} {S}")

    def askMove(self):
        if self.verbose:
            print(f"Column for {self.getName()} : ", end="")
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

    def getName(self, verbose=True):
        if verbose:
            return f"AI {self.no} ({self.progName})"
        else:
            return self.progName


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
        return (-1, -1)
    if not (0 <= x < WIDTH):
        if verbose: print("Out of bounds")
        return (-1, -1)
    y = fallHeight(board, x)
    if y == HEIGHT:
        if verbose: print("Column full")
        return (-1, -1)
    return (x, y)

def game(p1: Player, p2: Player, verbose=False):
    p1.no = 1
    p2.no = 2
    players = (p1, p2)
    turn = 0
    board = [[0 for _y in range(HEIGHT)] for _x in range(WIDTH)]
    winner = None
    while winner is None:
        turn += 1
        player = players[(turn + 1)% 2]
        otherPlayer = players[turn % 2]
        display(board, player, player.verbose)
        while True:
            userInput = player.askMove()
            x, y = sanithize(board, userInput, verbose=player.verbose)
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
        print(f"{winner.getName(verbose)} wins")
    else:
        return winner.getName(verbose)

def main():
    args = list(sys.argv[1:])
    verboseAI = True
    verbose = True
    if "-s" in args:
        verboseAI = False
        args.remove("-s")
    if len(args):
        p1 = AI(args.pop(), WIDTH, HEIGHT, verboseAI)
    else:
        p1 = User()
    if len(args):
        p2 = AI(args.pop(), WIDTH, HEIGHT, verboseAI)
        verbose = verboseAI
    else:
        p2 = User()
    winnerFile = game(p1, p2, verbose)
    if not verbose:
        print(winnerFile)


if __name__ == "__main__":
    main()

