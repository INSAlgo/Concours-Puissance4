#!/usr/bin/env python3

from typing import Callable
import sys
from abc import ABC, abstractmethod
from os import path
import subprocess
from asyncio import run

# Conditional import for pexpect for cross-OS :
from platform import system
if system() == "Windows":
    from pexpect.popen_spawn import PopenSpawn as spawn
    from signal import CTRL_C_EVENT
else :
    from pexpect import spawn
from pexpect import TIMEOUT

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
    async def askMove(self, board, verbose):
        pass

    @abstractmethod
    async def tellMove(self, move: int):
        pass

    @abstractmethod
    def pprint():
        pass

    @staticmethod
    def sanithize(board, userInput, verbose=False):
        if userInput == "stop" :
            return (None, "user interrupt")
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

    def __init__(self,
            ask_func: Callable[[list[list[int]], int], str] = None,
            tell_func: Callable[[int, int], None] = None,
            game_id: int = None
        ):
        super().__init__()
        self.ask_func = ask_func
        self.tell_func = tell_func
        self.game_id = game_id

    def startGame(self, no, width, height, nbPlayers):
        return super().startGame(no, width, height, nbPlayers)

    async def askMove(self, board, verbose):
        if self.ask_func is not None :
            return User.sanithize(board, await self.ask_func(board, self.game_id), verbose)
        
        if verbose:
            print(f"Column for {self.pprint()} : ", end="")
        try:
            return User.sanithize(board, input(), verbose)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
    
    async def tellMove(self, move):
        if self.tell_func is not None :
            await self.tell_func(move, self.game_id)

    def pprint(self):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def prepareCommand(progPath, progName):
        if not path.exists(progPath):
            raise Exception(f"File {progPath} not found\n")
        
        extension = path.splitext(progPath)[1]
        match extension:
            case ".py":
                return f"python3 {progPath}"
            case ".js":
                return f"node {progPath}"
            case ".class":
                return f"java -cp {path.dirname(progPath)} {path.splitext(path.basename(progPath))[0]}"
            case ".cpp" | ".c":
                subprocess.run(["g++", progPath, "-o", f"{progName}.out"])
                return f"./{progName}.out"
            case _:
                return f"./{progPath}"

    def __init__(self, progPath):
        super().__init__()
        self.progPath = progPath
        self.progName = path.splitext(path.basename(progPath))[0]
        self.command = AI.prepareCommand(self.progPath, self.progName)

    def startGame(self, no, width, height, nbPlayers):
        super().startGame(no, width, height, nbPlayers)
        self.prog = spawn(self.command, timeout=TIMEOUT_LENGTH)
        self.prog.delaybeforesend = None
        if system() != "Windows": self.prog.setecho(False)
        self.prog.sendline(f"{width} {height} {nbPlayers} {no}")

    def loseGame(self, verbose):
        if verbose: print(f"{self.pprint()} is eliminated")
        if system() == "Windows":
            self.prog.kill(CTRL_C_EVENT)
        else :
            self.prog.close()

    async def askMove(self, board, verbose):
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

    async def tellMove(self, x):
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

def display(board, verbose=True) -> list[str]:
    width, height = len(board), len(board[0])

    lines = [""]
    if verbose : print()

    line = "  " + ' '.join(str(x%10) for x in range(width)) + "  "
    lines.append(line)
    if verbose : print(line)

    line = '┌' + '─' * (width * 2 + 1) + '┐'
    lines.append(line)
    if verbose : print(line)

    for y in range(height - 1, -1, -1) :
        line = "│ "
        raw_line = ' '.join(str(board[x][y]) for x in range(width))
        line += raw_line.replace('0', '.') + " │"
        lines.append(line)
        if verbose : print(line)
    
    line = '└' + '─' * (width * 2 + 1) + '┘'
    lines.append(line)
    if verbose : print(line)

    line = "  " + ' '.join(str(x%10) for x in range(width)) + "  "
    lines.append(line)
    if verbose : print(line)

    return lines

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

async def game(players: list[User | AI], width, height, verbose=False, discord=False):
    if discord :
        log = []
    else :
        log = None

    # init
    L = len(players)
    players = list(players)
    alive = [True for _ in range(L)]
    errors = {}
    for i, player in enumerate(players):
        player.startGame(i+1, width, height, L)
    turn = 0
    board = [[0 for _ in range(height)] for _ in range(width)]

    winner = None

    # game loop
    while sum(alive) > 1:
        i = turn % L
        player = players[i]

        # eliminated player :
        if not alive[i] :
            userInput = None

        else :

            # displaying board :
            if verbose or discord :
                board_disp = display(board, verbose)
                if discord : log += board_disp
            
            # getting player output :
            userInput, error = None, None
            while not userInput:
                userInput, error = await player.askMove(board, verbose)
                if isinstance(player, AI) or error == "user interrupt" :
                    break
            
            # logging move :
            if discord and userInput is not None :
                line = f"Player {player.no} played on column {userInput[0]}"
                log.append(line)
        
            # saving eventual error
            if error:
                if isinstance(player, AI):
                    errors[player.no] = error
                    line = f"{player.pprint()} is eliminated, cause : {error}"
                    player.loseGame(verbose)
                    if discord : log.append(line)
                    if verbose : print(line)
                alive[i] = False

        # register move :
        if userInput is None :
            x = -1
        else :
            x, y = userInput
            board[x][y] = player.no
        
        # giving last move info to other players :
        for j in range(L):
            if j != i and alive[j]:
                await players[j].tellMove(x)
        
        # end check :
        if x >= 0 :
            if checkWin(board, player.no):
                if verbose or discord :
                    board_disp = display(board, verbose)
                    if discord : log += board_disp
                winner = player
                break

            elif checkDraw(board):
                if verbose or discord :
                    board_disp = display(board, verbose)
                    if discord : log += board_disp
                break
        
        turn += 1
    
    if sum(alive) == 1 :
        winner = players[alive.index(True)]
    return (winner, errors, log)

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
        if name == "user":
            players.append(User())
        else:
            players.append(AI(name))
    while len(players) < nbPlayers:
        players.append(User())
    winner, errors, _ = run(game(players, width, height, verbose))
    renderEnd(winner, errors, verbose)


if __name__ == "__main__":
    main()

