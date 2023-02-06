#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
from os import path
import subprocess
import pexpect

WIDTH = 7
HEIGHT = 6
TIMEOUT = 0.1


class Player(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def startGame(self, no, width, height):
        self.no = no

    @abstractmethod
    def askMove(self, verbose):
        pass

    @abstractmethod
    def tellLastMove(self, x):
        pass

class User(Player):

    def __init__(self):
        super().__init__()

    def startGame(self, no, width, height):
        return super().startGame(no, width, height)

    def askMove(self, verbose):
        if verbose:
            print(f"Column for player {self.no} : ", end="")
        try:
            return input()
        except KeyboardInterrupt:
            sys.exit(1)

    def tellLastMove(self, x):
        return super().tellLastMove(x)

    def __str__(self):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def prepareCommand(progPath, progName):
        if not path.exists(progPath):
            sys.stderr.write(f"File {progName} not found\n")
            sys.exit(1)
        extension = progName.split(".")[-1]
        match extension:
            case "py":
                return f"python {progPath}"
            case "js":
                return f"node {progPath}"
            case "cpp":
                subprocess.run(["g++", progPath, "-o", f"{progName}.out"])
                return f"./{progName}.out"
            case _:
                return f"./{progName}"

    def __init__(self, progPath):
        super().__init__()
        self.progPath = progPath
        self.progName = path.basename(progPath)
        self.command = AI.prepareCommand(self.progPath, self.progName);

    def startGame(self, no, width, height):
        super().startGame(no, width, height)
        self.prog = pexpect.spawn(self.command, timeout=TIMEOUT)
        self.prog.delaybeforesend = None
        self.prog.setecho(False)
        start = 2 - self.no
        self.prog.sendline(f"{width} {height} {start}")

    def askMove(self, verbose):
        if verbose:
            print(f"Column for {self} : ", end="")
        try:
            progInput = self.prog.readline().decode('ascii').strip()
        except pexpect.TIMEOUT:
            print("Program 1 took too long")
            return False
        if verbose:
            print(progInput)
        return progInput

    def tellLastMove(self, x):
        self.prog.sendline(str(x))

    def __str__(self):
        return f"AI {self.no} ({self.progName})"


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
        return
    if not (0 <= x < WIDTH):
        if verbose: print("Out of bounds")
        return
    y = fallHeight(board, x)
    if y == HEIGHT:
        if verbose: print("Column full")
        return
    return (x, y)

def winMessage(winner):
    print(f"{winner} wins")
    return ""

def game(p1: Player, p2: Player, width=WIDTH, height=HEIGHT, verbose=False):
    p1.startGame(1, width, height)
    p2.startGame(2, width, height)
    players = (p1, p2)
    turn = 0
    board = [[0 for _ in range(height)] for _ in range(width)]
    winner = None
    while winner is None:
        turn += 1
        player = players[(turn + 1)% 2]
        otherPlayer = players[turn % 2]
        if verbose:
            display(board)
        userInput = False
        while not userInput:
            userInput = player.askMove(verbose)
            userInput = sanithize(board, userInput, verbose)
            if not userInput and isinstance(player, AI):
                if verbose:
                    return winMessage(otherPlayer)
                elif isinstance(player, AI):
                    return player.progName
        x, y = userInput
        y = fallHeight(board, x)
        board[x][y] = player.no
        otherPlayer.tellLastMove(x)
        if checkWin(board, player.no):
            if verbose:
                display(board)
                return winMessage(otherPlayer)
            elif isinstance(player, AI):
                return player.progName

def main():
    args = list(sys.argv[1:])
    verbose = True
    if "-s" in args:
        args.remove("-s")
        if len(args) >= 2:
            verbose = False
    if len(args):
        p1 = AI(args.pop())
    else:
        p1 = User()
    if len(args):
        p2 = AI(args.pop())
    else:
        p2 = User()
    winnerFile = game(p1, p2, WIDTH, HEIGHT, verbose)
    if not verbose:
        print(winnerFile)


if __name__ == "__main__":
    main()

