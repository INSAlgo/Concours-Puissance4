#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
import os
import subprocess
import asyncio
import argparse

# Conditional import for pexpect for cross-OS :
from platform import system
# if system() == "Windows":
#     from pexpect.popen_spawn import PopenSpawn as spawn
#     from signal import CTRL_C_EVENT
# else :
#     from pexpect import spawn
from pexpect import spawn
from pexpect import TIMEOUT

WIDTH = 7
HEIGHT = 6
TIMEOUT_LENGTH = 1


class Player(ABC):

    def __init__(self):
        pass

    @abstractmethod
    async def start_game(self, no, width, height, nbPlayers):
        self.no = no
        self.alive = True

    @abstractmethod
    def lose_game(self):
        print(f"{self.pprint()} is eliminated")

    @abstractmethod
    async def ask_move(self, board) -> tuple[tuple[int, int] | None, str | None]:
        pass

    @abstractmethod
    async def tell_move(self, move: int):
        pass

    @abstractmethod
    def pprint():
        pass

    @staticmethod
    def sanithize(board, userInput):
        if userInput == "stop" :
            return (None, "user interrupt")
        try:
            x = int(userInput)
        except ValueError:
            print("Invalid input")
            return (None, "invalid input")
        if not (0 <= x < len(board)):
            print("Out of bounds")
            return (None, "out of bounds")
        y = fallHeight(board, x)
        if y == len(board[0]):
            print("Column full")
            return (None, "column full")
        return ((x, y), None)

class User(Player):

    def __init__(self):
        super().__init__()

    async def start_game(self, no, width, height, nbPlayers):
        await super().start_game(no, width, height, nbPlayers)

    def lose_game(self):
        super().lose_game()
        
    async def ask_move(self, board):
        print(f"Column for {self.pprint()} : ", end="")
        return User.sanithize(board, input())

    async def tell_move(self, move: int):
        return super().tell_move(move)
    
    def pprint(self):
        return f"Player {self.no}"

class AI(Player):

    @staticmethod
    def prepareCommand(progPath, progName):
        if not os.path.exists(progPath):
            raise Exception(f"File {progPath} not found\n")
        
        extension = os.path.splitext(progPath)[1]
        match extension:
            case ".py":
                return f"python3 {progPath}"
            case ".js":
                return f"node {progPath}"
            case ".class":
                return f"java -cp {os.path.dirname(progPath)} {os.path.splitext(os.path.basename(progPath))[0]}"
            case ".cpp" | ".c":
                subprocess.run(["g++", progPath, "-o", f"{progName}.out"])
                return f"./{progName}.out"
            case _:
                return f"./{progPath}"

    def __init__(self, progPath):
        super().__init__()
        self.progPath = progPath
        self.progName = os.path.splitext(os.path.basename(progPath))[0]
        self.command = AI.prepareCommand(self.progPath, self.progName)

    async def start_game(self, no, width, height, nbPlayers):
        await super().start_game(no, width, height, nbPlayers)
        result = await asyncio.gather(asyncio.get_event_loop().run_in_executor(
            None,
            self._spawn
        ))
        self.prog = result[0]
        self.prog.delaybeforesend = 0
        if system() != "Windows": self.prog.setecho(False)
        self.prog.sendline(f"{width} {height} {nbPlayers} {no}")

    def _spawn(self):
        return spawn(self.command, timeout=TIMEOUT_LENGTH)

    def lose_game(self):
        super().lose_game()
        if system() == "Windows":
            pass
            # self.prog.kill(CTRL_C_EVENT)
        else :
            self.prog.close()

    async def ask_move(self, board) -> tuple[tuple[int, int] | None, str | None]:
        try:
            while True:
                # progInput = await asyncio.get_event_loop().run_in_executor(
                #     None,
                #     self.prog.readline
                # )
                # progInput = progInput.decode("ascii").strip()
                progInput = self.prog.readline()
                if not isinstance(progInput, bytes):
                    continue
                progInput = progInput.decode().strip()
                if progInput.startswith("Traceback"):
                    print()
                    print(progInput)
                    progInput = self.prog.read()
                    if isinstance(progInput, bytes):
                        print(progInput.decode())
                    return None, "error"
                if progInput.startswith(">"):
                    line = f"{self.pprint()} {progInput}"
                    print(line)
                else:
                    break
            line = f"Column for {self.pprint()} : {progInput}"
            print(line)
        except TIMEOUT:
            line = f"{self.pprint()} did not respond in time (over {TIMEOUT_LENGTH}s)"
            print(line)
            return None, "timeout"
        return User.sanithize(board, progInput)

    async def tell_move(self, move: int):
        self.prog.sendline(str(move))

    async def stop_game(self):
        
        # if system() == "Windows":
        #     func = self.prog.kill
        #     args = [CTRL_C_EVENT]
        func = self.prog.close
        args = []
        
        await asyncio.gather(asyncio.get_event_loop().run_in_executor(
            None, 
            func,
            args
        ))

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
    print('  ' + ' '.join(str(x % 10) for x in range(width)) + '  ')
    print('┌' + '─' * (width * 2 + 1) + '┐')

    for y in range(height - 1, -1, -1) :
        print('│ ' + ' '.join(str(board[x][y]) if board[x][y] else '.' for x in range(width)) + ' │')
    
    print('└' + '─' * (width * 2 + 1) + '┘')
    print('  ' + ' '.join(str(x % 10) for x in range(width)) + '  ')

def fallHeight(board, x):
    y = len(board[x])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

def renderEnd(winner):
    if winner:
        print(f"{winner.pprint()} won")
    else:
        print("Draw")

async def game(players: list[User | AI], width, height):

    nb_players = len(players)
    alive_players = nb_players
    errors = {}
    starters = (player.start_game(i+1, width, height, nb_players) for i, player in enumerate(players))
    await asyncio.gather(*starters)
    turn = 0
    board = [[0 for _ in range(height)] for _ in range(width)]
    winner = None

    # game loop
    while alive_players >= 2:
        i = turn % nb_players
        player = players[i]

        if not player.alive:
            user_input = None

        else :

            display(board)

            # getting player output :
            user_input, error = None, None
            while not user_input:
                user_input, error = await player.ask_move(board)
                if isinstance(player, AI) or error == "user interrupt":
                    break

            # saving eventual error
            if error:
                player.lose_game()
                errors[player.no] = error
                player.alive = False
                alive_players -= 1

        # register move :
        if user_input is None :
            x = -1
        else :
            x, y = user_input
            board[x][y] = player.no
        
        # giving last move info to other players :
        for j in range(nb_players):
            if j != i and players[j].alive:
                await players[j].tell_move(x)
        
        # end check :
        if x >= 0 :
            if checkWin(board, player.no):
                display(board)
                winner = player
                break

            elif checkDraw(board):
                display(board)
                break
        
        turn += 1
    
    enders = (player.stop_game() for player in players if isinstance(player, AI))
    await asyncio.gather(*enders)
    
    if alive_players:
        winner = [player for player in players if player.alive][0]
    renderEnd(winner)

    return winner, errors


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("prog", nargs="*", \
            help="AI program to play the game ('user' to play yourself)")
    parser.add_argument("-l", "--log", action="store_true", \
            help="redirect the game output to the file named 'log'")
    parser.add_argument("-g", "--grid", type=int, nargs=2, default=[WIDTH, HEIGHT], metavar=("WIDTH", "HEIGHT"), \
            help="size of the grid")
    parser.add_argument("-p", "--players", type=int, default=2, metavar="NB_PLAYERS", \
            help="number of players (if more players than programs are provided, the other ones will be filled as real players)")

    args = parser.parse_args(args)
    if args.log:
        log_file = open("log", "w")
        sys.stdout = log_file
        sys.stderr = log_file
    nbPlayers = args.players
    width, height = args.grid

    players = []
    for name in args.prog:
        if name == "user":
            players.append(User())
        else:
            players.append(AI(name))
    while len(players) < nbPlayers:
        players.append(User())

    asyncio.run(game(players, width, height))

if __name__ == "__main__":
    main()


