#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
from os import path

# Conditional import :
from platform import system
if system() == "Windows":
    from pexpect.popen_spawn import PopenSpawn as spawn
else :
    from pexpect import spawn
from pexpect import TIMEOUT
import subprocess

WIDTH = 7
HEIGHT = 6
TIMEOUT_LENGTH = 0.1


class Player(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def startGame(self, no, width, height, nbPlayers):
        self.no = no

    @abstractmethod
    def askMove(self, board, verbose):
        pass

    @abstractmethod
    def pprint():
        pass

    @staticmethod
    def sanithize(board, userInput, verbose=False):
        try:
            x = int(userInput)
        except ValueError:
            if verbose: print("Invalid input")
            return (None, "invalid input")
        if not (0 <= x < len(board)):
            if verbose: print("Out of bounds")
            return (None, "out of bounds")
        y = fallHeight(board, x)
        if y == len(board[0]):
            if verbose: print("Column full")
            return (None, "column full")
        return ((x, y), None)

class User(Player):

    def __init__(self):
        super().__init__()

    def startGame(self, no, width, height, nbPlayers):
        return super().startGame(no, width, height, nbPlayers)

    def askMove(self, board, verbose):
        if verbose:
            print(f"Column for {self.pprint()} : ", end="")
        try:
            return User.sanithize(board, input(), verbose)
        except KeyboardInterrupt:
            sys.exit(1)

    def pprint(self):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def prepareCommand(progPath, progName):
        if not path.exists(progPath):
            print(f"File {progPath} not found\n")
            sys.exit(1)
        extension = path.splitext(progPath)[1]
        match extension:
            case ".py":
                return f"python3 {progPath}"
            case ".js":
                return f"node {progPath}"
            case ".class":
                return f"java -cp {path.dirname(progPath)} {path.splitext(path.basename(progPath))[0]}"
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

    def startGame(self, no, width, height, nbPlayers):
        super().startGame(no, width, height, nbPlayers)
        self.prog = spawn(self.command, timeout=TIMEOUT_LENGTH)
        self.prog.delaybeforesend = None
        if system() != "Windows": self.prog.setecho(False)
        self.prog.sendline(f"{width} {height} {nbPlayers} {no}")

    def loseGame(self, verbose):
        if verbose: print(f"{self.pprint()} is eliminated")
        if system() != "Windows": self.prog.close()

    def askMove(self, board, verbose):
        try:
            while True:
                progInput = self.prog.readline().decode("ascii").strip()
                if progInput.startswith("Traceback"):
                    if verbose:
                        print()
                        print(progInput)
                        print(self.prog.read().decode("ascii"))
                    return (None, "error")
                if progInput.startswith(">"):
                    if verbose:
                        print(f"{self.pprint()} {progInput}")
                else:
                    break
            if verbose:
                print(f"Column for {self.pprint()} : {progInput}")
        except TIMEOUT:
            if verbose:
                print(f"{self.pprint()} did not respond in time (over {TIMEOUT_LENGTH}s)")
            return (None, "timeout")
        return User.sanithize(board, progInput, verbose)

    def tellLastMove(self, x):
        self.prog.sendline(str(x))

    def __str__(self):
        return self.progName

    def pprint(self):
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
                        if not (0 <= nx < width and 0 <= ny < height):
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
    line = "  " + ' '.join(str(x%10) for x in range(width)) + "  "
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
    line = "  " + ' '.join(str(x%10) for x in range(width)) + "  "
    print(line)

def fallHeight(board, x):
    y = len(board[x])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

def renderEnd(winner, errors, verbose=False):
    if verbose:
        if winner:
            print(f"{winner.pprint()} won")
        else:
            print("Draw")
    else:
        if winner:
            print(winner, end="")
        else:
            print("draw", end="")
        if errors:
            print(f" ({', '.join((f'{player}: {error}' for player, error in errors.items()))})")
        else:
            print()

def game(players, width, height, verbose=False):
    players = list(players)
    errors = {}
    for i, player in enumerate(players):
        player.startGame(i+1, width, height, len(players))
    turn = 0
    player = players[turn]
    board = [[0 for _ in range(height)] for _ in range(width)]
    while len(players) > 1:
        player = players[turn % len(players)]
        if verbose:
            display(board)
        userInput, error = None, None
        while not userInput:
            userInput, error = player.askMove(board, verbose)
            if isinstance(player, AI):
                break
        if error:
            if isinstance(player, AI):
                player.loseGame(verbose)
                errors[player] = error
            players.remove(player)
            continue
        x, y = userInput
        board[x][y] = player.no
        for otherPlayer in players:
            if otherPlayer != player and isinstance(otherPlayer, AI):
                otherPlayer.tellLastMove(x)
        if checkWin(board, player.no):
            if verbose :
                display(board)
            break
        elif checkDraw(board):
            if verbose :
                display(board)
            return (None, errors)
        turn += 1
    winner = players[turn % len(players)]
    return (winner, errors)

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
        name = args.pop(0)
        print(name)
        if name == "user":
            players.append(User())
        else:
            players.append(AI(name))
    while len(players) < nbPlayers:
        players.append(User())
    winner, errors = game(players, width, height, verbose)
    renderEnd(winner, errors, verbose)


if __name__ == "__main__":
    main()

