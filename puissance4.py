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

    async def tell_other_players(self, players, move):
        for other_player in players:
            if self != other_player and other_player.alive:
                await other_player.tell_move(move)

    @abstractmethod
    def pprint():
        pass

    @staticmethod
    def sanithize(board, userInput):
        if userInput == "stop" :
            return None, "user interrupt"
        try:
            x = int(userInput)
        except ValueError:
            print("Invalid input")
            return None, "invalid input"
        if not (0 <= x < len(board)):
            print("Out of bounds")
            return None, "out of bounds"
        y = fallHeight(board, x)
        if y == len(board[0]):
            print("Column full")
            return None, "column full"
        return (x, y), None


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
    def prepareCommand(progPath):
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
            case _:
                return f"./{progPath}"

    def __init__(self, progPath):
        super().__init__()
        self.progPath = progPath
        self.progName = os.path.splitext(os.path.basename(progPath))[0]
        self.command = AI.prepareCommand(self.progPath)

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
            await player.tell_other_players(players, -1)

        else :

            display(board)

            # player input
            user_input, error = None, None
            while not user_input:
                user_input, error = await player.ask_move(board)
                if isinstance(player, AI) or error == "user interrupt":
                    break

            # saving eventual error
            if not user_input:
                player.lose_game()
                errors[player] = error
                player.alive = False
                alive_players -= 1
                await player.tell_other_players(players, -1)

            else:

                x, y = user_input
                board[x][y] = player.no
                await player.tell_other_players(players, x)
            
                # end check
                if checkWin(board, player.no):
                    display(board)
                    winner = player
                    break

                elif checkDraw(board):
                    display(board)
                    break
        
        turn += 1

    if alive_players == 1:
        # nobreak
        winner = [player for player in players if player.alive][0]
    
    renderEnd(winner)

    enders = (player.stop_game() for player in players if isinstance(player, AI))
    await asyncio.gather(*enders)

    return players, winner, errors


async def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("prog", nargs="*", \
            help="AI program to play the game ('user' to play yourself)")
    parser.add_argument("-l", "--log", action="store_true", \
            help="redirect the game output to the file named 'log'")
    parser.add_argument("-g", "--grid", type=int, nargs=2, default=[WIDTH, HEIGHT], metavar=("WIDTH", "HEIGHT"), \
            help="size of the grid")
    parser.add_argument("-p", "--players", type=int, default=2, metavar="NB_PLAYERS", \
            help="number of players (if more players than programs are provided, the other ones will be filled as real players)")
    parser.add_argument("-r", "--rematches", type=int, default=0, metavar="NB_REMATCHES", \
            help="number of rematches")
    parser.add_argument("-s", "--silent", action="store_true", \
            help="only show the result")

    args = parser.parse_args(args)
    width, height = args.grid

    players = []
    ai_only = True
    for name in args.prog:
        if name == "user":
            players.append(User())
            ai_only = False
        else:
            players.append(AI(name))
    while len(players) < args.players:
        players.append(User())
        ai_only = False

    origin_stdout = sys.stdout
    if args.log or args.silent:
        if not ai_only:
            raise Exception("Game cannot be silent since humans are playing")
        log_file = open("log" if args.log else os.devnull, "w")
        sys.stdout = log_file
        sys.stderr = log_file

    players, winner, errors = await game(players, width, height)
    if args.silent:
        sys.stdout = origin_stdout
        print(f"{winner.pprint() if winner else 'Draw'}", end="")
        if errors:
            print(f" [{', '.join(f'{player.pprint()}: {error}' for player, error in errors.items())}]")
        else:
            print()
    return players, winner, errors

if __name__ == "__main__":
    asyncio.run(main())

