#!/usr/bin/env python3

from io import StringIO
import sys
from abc import ABC, abstractmethod
import os
import asyncio
import argparse
import re

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
TIMEOUT_LENGTH = 0.1
EMOJI_NUMBERS = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
EMOJI_COLORS = ('🟠', '🔴', '🟡', '🟢', '🔵', '🟣', '🟤',  '⚪️', '⚫️')

class Player(ABC):

    ofunc = None

    def __init__(self, no, name):
        self.no = no + 1
        self.name = name

    @abstractmethod
    async def start_game(self, width, height, nbPlayers):
        self.alive = True

    @abstractmethod
    async def lose_game(self):
        await Player.print(StringIO(f"{self} is eliminated"))

    @abstractmethod
    async def ask_move(self, board, debug) -> tuple[tuple[int, int] | None, str | None]:
        pass

    @abstractmethod
    async def tell_move(self, move: int):
        pass

    async def tell_other_players(self, players, move):
        for other_player in players:
            if self != other_player and other_player.alive:
                await other_player.tell_move(move)

    @staticmethod
    async def sanithize(board, userInput):
        output = StringIO()
        if userInput == "stop" :
            return None, "user interrupt"
        try:
            x = int(userInput)
        except ValueError:
            print("Invalid input", file=output)
            await Player.print(output)
            return None, "invalid input"
        if not (0 <= x < len(board)):
            print("Out of bounds", file=output)
            await Player.print(output)
            return None, "out of bounds"
        y = fall_height(board, x)
        if y == len(board[0]):
            print("Column full", file=output)
            await Player.print(output)
            return None, "column full"
        return (x, y), None

    @staticmethod
    async def print(output: StringIO, send=True):
        print(output.getvalue(), end="")
        if User.ofunc and send:
            await User.ofunc(output.getvalue())
        output.close()

    def __str__(self):
        return self.name

class User(Player):

    def __init__(self, no, name=None, ifunc=None):
        super().__init__(no, name)
        self.ifunc = ifunc

    async def start_game(self, width, height, nbPlayers):
        await super().start_game(width, height, nbPlayers)

    async def lose_game(self):
        await super().lose_game()
        
    async def ask_move(self, board, debug):
        await super().ask_move(board, debug)
        output = StringIO()
        print(f"Column for {self} : ", end="", file=output)
        await Player.print(output)
        user_input = await self.input()
        return await User.sanithize(board, user_input)

    async def tell_move(self, move: int):
        return super().tell_move(move)
    
    def render(self):
        return self.name if self.name else f"Player {self.no}"

    async def input(self):
        if self.ifunc:
            user_input = await self.ifunc(self.name)
            output = StringIO()
            print(user_input, file=output)
            await Player.print(output, send=False)
            return user_input
        else:
            return input()

class AI(Player):

    @staticmethod
    def prepare_command(progPath):
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

    def __init__(self, no, prog_path, discord):
        self.prog_name = os.path.splitext(os.path.basename(prog_path))[0]
        name = f"<@{self.prog_name}>'s AI" if discord else f"AI {no} ({self.prog_name})"
        super().__init__(no, name)
        self.prog_path = prog_path
        self.command = AI.prepare_command(self.prog_path)

    async def start_game(self, width, height, nbPlayers):
        await super().start_game(width, height, nbPlayers)
        result = await asyncio.gather(asyncio.get_event_loop().run_in_executor(
            None,
            self._spawn
        ))
        self.prog = result[0]
        self.prog.delaybeforesend = 0
        if system() != "Windows": self.prog.setecho(False)
        self.prog.sendline(f"{width} {height} {nbPlayers} {self.no}")

    def _spawn(self):
        return spawn(self.command, timeout=TIMEOUT_LENGTH)

    async def lose_game(self):
        await super().lose_game()
        if system() == "Windows":
            pass
            # self.prog.kill(CTRL_C_EVENT)
        else :
            self.prog.close()

    async def ask_move(self, board, debug) -> tuple[tuple[int, int] | None, str | None]:
        await super().ask_move(board, debug)
        try:
            while True:
                output = StringIO()
                progInput = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.prog.readline
                )
                # progInput = self.prog.readline()
                if not isinstance(progInput, bytes):
                    continue
                progInput = progInput.decode().strip()
                if progInput.startswith("Traceback"):
                    if debug:
                        print(file=output)
                        print(progInput, file=output)
                        progInput = self.prog.read()
                        if isinstance(progInput, bytes):
                            print(progInput.decode(), file=output)
                        await Player.print(output)
                    return None, "error"
                if progInput.startswith(">"):
                    if debug:
                        print(f"{self} {progInput}", file=output)
                        await Player.print(output)
                else:
                    break
            output = StringIO()
            print(f"Column for {self} : {progInput}", file=output)
            await Player.print(output)
        except TIMEOUT:
            output = StringIO()
            print(f"{self} did not respond in time (over {TIMEOUT_LENGTH}s)", file=output)
            await Player.print(output)
            return None, "timeout"
        return await User.sanithize(board, progInput)

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


def check_win(board, no):
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

def check_draw(board):
    for x in range(len(board)):
        if not board[x][-1]:
            return False
    return True

def render_grid(board, emoji):
    output = StringIO()
    print("", file=output)
    width, height = len(board), len(board[0])
    if emoji:
        print(''.join(EMOJI_NUMBERS[x % 10] for x in range(width)), file=output)
        for y in range(height - 1, -1, -1) :
            print(''.join(EMOJI_COLORS[board[x][y] % len(EMOJI_COLORS)] if board[x][y] else "⬛" for x in range(width)), file=output)
        print(''.join(EMOJI_NUMBERS[x % 10] for x in range(width)), file=output)
    else:
        print('  ' + ' '.join(str(x % 10) for x in range(width)) + '  ', file=output)
        print('┌' + '─' * (width * 2 + 1) + '┐', file=output)
        for y in range(height - 1, -1, -1) :
            print('│ ' + ' '.join(str(board[x][y]) if board[x][y] else '.' for x in range(width)) + ' │', file=output)
        print('└' + '─' * (width * 2 + 1) + '┘', file=output)
        print('  ' + ' '.join(str(x % 10) for x in range(width)) + '  ', file=output)
    return output

def fall_height(board, x):
    y = len(board[x])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

def render_end(board, winner, errors, silent, discord):
    if discord:
        output = board
        print("", file=board)
    else:
        output = StringIO()
    if winner:
        print(f"{winner} won", end="", file=output)
    else:
        print("Draw", end="", file=output)
    if silent and errors:
        error_list = (f"{player}: {error}" for player, error in errors.items())
        print(f" ({', '.join(error_list)})", file=output)
    return output

async def game(players: list[User | AI], width, height, emoji, debug):

    nb_players = len(players)
    alive_players = nb_players
    errors = {}
    starters = (player.start_game(width, height, nb_players) for player in players)
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

            await Player.print(render_grid(board, emoji))

            # player input
            user_input, error = None, None
            while not user_input:
                user_input, error = await player.ask_move(board, debug)
                if isinstance(player, AI) or error == "user interrupt":
                    break

            # saving eventual error
            if not user_input:
                await player.lose_game()
                errors[player] = error
                player.alive = False
                alive_players -= 1
                await player.tell_other_players(players, -1)

            else:

                x, y = user_input
                board[x][y] = player.no
                await player.tell_other_players(players, x)
            
                # end check
                if check_win(board, player.no):
                    winner = player
                    break

                elif check_draw(board):
                    break
        
        turn += 1

    if alive_players == 1:
        # nobreak
        winner = [player for player in players if player.alive][0]
    
    enders = (player.stop_game() for player in players if isinstance(player, AI))
    await asyncio.gather(*enders)

    final_board = render_grid(board, emoji)

    return players, winner, errors, final_board


async def main(raw_args=None, ifunc=None, ofunc=None, discord=True):

    parser = argparse.ArgumentParser()
    parser.add_argument("prog", nargs="*", \
            help="AI program to play the game ('user' to play yourself)")
    parser.add_argument("-g", "--grid", type=int, nargs=2, default=[WIDTH, HEIGHT], metavar=("WIDTH", "HEIGHT"), \
            help="size of the grid")
    parser.add_argument("-p", "--players", type=int, default=2, metavar="NB_PLAYERS", \
            help="number of players (if more players than programs are provided, the other ones will be filled as real players)")
    parser.add_argument("-s", "--silent", action="store_true", \
            help="only show the result of the game")
    parser.add_argument("-e", "--emoji", action="store_true", \
            help="display grid with emojis")
    parser.add_argument("-n", "--nodebug", action="store_true", \
            help="do not print the debug output of the programs")

    args = parser.parse_args(raw_args)
    width, height = args.grid

    User.ofunc = ofunc
    players = []
    ai_only = True
    pattern = re.compile(r"^\<\@[0-9]{18}\>$")
    for i, name in enumerate(args.prog):
        if name == "user":
            players.append(User(i))
            ai_only = False
        elif pattern.match(name):
            players.append(User(i, name, ifunc))
            ai_only = False
        else:
            players.append(AI(i, name, discord))
    while len(players) < args.players:
        players.append(User(len(players)))
        ai_only = False

    origin_stdout = sys.stdout
    if args.silent:
        if not ai_only:
            output = StringIO("Game cannot be silent since humans are playing")
            tmp = output.getvalue()
            await User.print(output)
            raise Exception(tmp)
        if discord:
            User.ofunc = None
        else:
            sys.stdout = open(os.devnull, "w")

    output = StringIO()

    players, winner, errors, board = await game(players, width, height, args.emoji, not args.nodebug)

    if args.silent:
        sys.stdout = origin_stdout
        User.ofunc = ofunc
    await Player.print(render_end(board, winner, errors, args.silent, discord))

    return players, winner, errors

if __name__ == "__main__":
    asyncio.run(main())

