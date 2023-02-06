#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
from os import path
import subprocess

# Conditional import :
from platform import system
if system() == "Windows":
    from pexpect.popen_spawn import PopenSpawn as spawn
else :
    from pexpect import spawn
from pexpect import TIMEOUT

WIDTH = 7
HEIGHT = 6
TIMEOUT = 0.1


class Player(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def startGame(self, no, width, height):
        self.no = no
        self.playing = True

    @abstractmethod
    def askMove(self, verbose):
        pass

class User(Player):

    def __init__(self):
        super().__init__()

    def startGame(self, no, width, height):
        return super().startGame(no, width, height)

    def askMove(self, verbose):
        if verbose:
            print(f"Column for {self} : ", end="")
        try:
            return input()
        except KeyboardInterrupt:
            sys.exit(1)

    def __str__(self):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def prepareCommand(progPath, progName):
        if not path.exists(progPath):
            sys.stderr.write(f"File {progPath} not found\n")
            sys.exit(1)
        extension = path.splitext(progPath)[1]
        match extension:
            case ".py":
                return f"python {progPath}"
            case ".js":
                return f"node {progPath}"
            case ".cpp":
                subprocess.run(["g++", progPath, "-o", f"{progName}.out"])
                return f"./{progName}.out"
            case _:
                return f"./{progPath}"

    def __init__(self, progPath):
        super().__init__()
        self.progPath = progPath
        self.progName = path.splitext(path.basename(progPath))[0]
        self.command = AI.prepareCommand(self.progPath, self.progName);

    def startGame(self, no, width, height):
        super().startGame(no, width, height)
        self.prog = spawn(self.command, timeout=TIMEOUT)
        self.prog.delaybeforesend = None
        # self.prog.setecho(False)
        start = 2 - self.no
        self.prog.sendline(f"{width} {height} {start}")

    def askMove(self, verbose):
        if verbose:
            print(f"Column for {self} : ", end="")
        try:
            progInput = self.prog.readline().decode('ascii').strip()
        except TIMEOUT:
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
    width, height = len(board), len(board[0])
    for x in range(width):
        for y in range(height):
            if board[x][y] == no:
                for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                    streak = 1
                    for i in range(1, 4):
                        nx, ny = x + dx * i, y + dy * i
                        if nx >= width or ny >= height:
                            break
                        if board[nx][ny] == no:
                            streak += 1
                        else:
                            break
                    if streak >= 4:
                        return True
    return False

def checkDraw(board):
    for x in range(len(board)):
        if not board[x][-1]:
            return False
    return True

def display(board):
    width, height = len(board), len(board[0])
    print()
    line = "  " + ' '.join(str((x+1)%10) for x in range(width)) + "  "
    print(line)
    line = '┌' + '─' * (width * 2 + 1) + '┐'
    print(line)
    for y in range(height - 1, -1, -1) :
        line = "│ "
        raw_line = ' '.join(str(board[x][y]) for x in range(width))
        line += raw_line.replace('0', '.') + " │"
        print(line)
    line = '└' + '─' * (width * 2 + 1) + '┘'
    print(line)
    line = "  " + ' '.join(str((x+1)%10) for x in range(width)) + "  "
    print(line)

def fallHeight(board, x):
    y = len(board[0])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

def sanithize(board, userInput, verbose=False):
    try:
        x = int(userInput) - 1
    except ValueError:
        if verbose: print("Invalid input")
        return
    if not (0 <= x < len(board)):
        if verbose: print("Out of bounds")
        return
    y = fallHeight(board, x)
    if y == len(board[0]):
        if verbose: print("Column full")
        return
    return (x, y)

def endMessage(winner=None):
    if winner is None:
        print("Draw")
    else:
        print(f"{winner} wins")

def game(players, width, height, verbose=False):
    players = list(players)
    for i, player in enumerate(players):
        player.startGame(i+1, width, height)
    turn = 0
    player = players[turn]
    board = [[0 for _ in range(height)] for _ in range(width)]
    while len(players) > 1:
        player = players[turn % len(players)]
        if verbose:
            display(board)
        userInput = False
        while not userInput:
            userInput = player.askMove(verbose)
            userInput = sanithize(board, userInput, verbose)
            if not userInput and isinstance(player, AI):
                players.remove(player)
                turn -= 1
                break
        if not userInput:
            continue
        x, y = userInput
        y = fallHeight(board, x)
        board[x][y] = player.no
        for otherPlayer in players:
            if otherPlayer != player and isinstance(otherPlayer, AI):
                otherPlayer.tellLastMove(x)
        if checkWin(board, player.no):
            if verbose :
                display(board)
            break
        elif checkDraw(board):
            if verbose:
                endMessage()
            return
        turn += 1
    if verbose:
        endMessage(player)
        return
    elif isinstance(player, AI):
        return player.progName

def main():
    args = list(sys.argv[1:])
    verbose = True
    nbPlayers = 2
    width, height = WIDTH, HEIGHT
    if "-s" in args:
        args.remove("-s")
        if len(args) >= 2:
            verbose = False
    if "-g" in args:
        id = args.index("-g")
        args.pop(id)
        width = int(args.pop(id))
        height = int(args.pop(id))
    if "-p" in args:
        id = args.index("-p")
        args.pop(id)
        nbPlayers = int(args.pop(id))
    players = []
    while(args):
        players.append(AI(args.pop(0)))
    while len(players) < nbPlayers:
        players.append(User())
    winnerFile = game(players, width, height, verbose)
    if not verbose and winnerFile is not None:
        print(winnerFile)


if __name__ == "__main__":
    main()

