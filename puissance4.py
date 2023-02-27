#!/usr/bin/env python3

from io import StringIO
import sys
from abc import ABC, abstractmethod
import os
import asyncio
import argparse
import re
import pathlib

# Conditional import for pexpect for cross-OS :
# from platform import system

WIDTH = 7
HEIGHT = 6
TIMEOUT_LENGTH = 0.1
DISCORD_TIMEOUT = 60
EMOJI_NUMBERS = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
EMOJI_COLORS = ('🟠', '🔴', '🟡', '🟢', '🔵', '🟣', '🟤',  '⚪️', '⚫️')

class Player(ABC):

    ofunc = None

    def __init__(self, no, emoji, name=None):
        self.no = no + 1
        self.icon = EMOJI_COLORS[self.no] if emoji else self.no
        self.name = name
        self.rendered_name = None

    @abstractmethod
    async def start_game(self, width, height, nbPlayers):
        self.alive = True

    @abstractmethod
    async def lose_game(self):
        await Player.print(f"{self} is eliminated")

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
        if userInput == "stop" :
            return None, "user interrupt"
        try:
            x = int(userInput)
        except ValueError:
            await Player.print("Invalid input")
            return None, "invalid input"
        if not (0 <= x < len(board)):
            await Player.print("Out of bounds")
            return None, "out of bounds"
        y = fall_height(board, x)
        if y == len(board[0]):
            await Player.print("Column full")
            return None, "column full"
        return (x, y), None

    @staticmethod
    async def print(output: StringIO | str, send_discord=True, end="\n"):
        if isinstance(output, StringIO):
            text = output.getvalue()
            output.close()
        else:
            text = output + end
        print(text, end="")
        if Player.ofunc and send_discord:
            await Player.ofunc(text)

    def __str__(self):
        return self.rendered_name

class Human(Player):

    def __init__(self, no, emoji, name=None, ifunc=None):
        super().__init__(no, emoji, name)
        self.rendered_name = f"{self.name} {self.icon}" if name else f"Player {self.icon}"
        self.ifunc = ifunc

    async def start_game(self, width, height, nbPlayers):
        await super().start_game(width, height, nbPlayers)

    async def lose_game(self):
        await super().lose_game()
        
    async def ask_move(self, board, debug):
        await super().ask_move(board, debug)
        await Player.print(f"Column for {self} : ", end="")
        try:
            user_input = await self.input()
        except asyncio.TimeoutError:
            await Player.print(f"User did not respond in time (over {DISCORD_TIMEOUT}s)")
            return None, "timeout"
        return await Human.sanithize(board, user_input)

    async def tell_move(self, move: int):
        return super().tell_move(move)

    async def input(self):
        if self.ifunc:
            user_input = await asyncio.wait_for(self.ifunc(self.name), timeout=DISCORD_TIMEOUT)
            await Player.print(user_input, send_discord=False)
            return user_input
        else:
            return input()

class AI(Player):

    @staticmethod
    def prepare_command(progPath):
        path = pathlib.Path(progPath)
        if not path.is_file():
            raise Exception(f"File {progPath} not found\n")

        match path.suffix:
            case ".py":
                return f"python3 {progPath}"
            case ".js":
                return f"node {progPath}"
            case ".class":
                return f"java -cp {os.path.dirname(progPath)} {os.path.splitext(os.path.basename(progPath))[0]}"
            case _:
                return f"./{progPath}"

    def __init__(self, no, emoji, prog_path, discord):
        super().__init__(no, emoji, pathlib.Path(prog_path).stem)
        if discord:
            self.rendered_name = f"<@{self.name}>'s AI {self.icon}"
        else:
            self.rendered_name = f"AI {self.icon} ({self.name})"
        self.prog_path = prog_path
        self.command = AI.prepare_command(self.prog_path)

    async def start_game(self, width, height, nbPlayers):
        await super().start_game(width, height, nbPlayers)
        self.prog = await asyncio.create_subprocess_shell(AI.prepare_command(self.prog_path),
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        if self.prog.stdin:
            self.prog.stdin.write(f"{width} {height} {nbPlayers} {self.no}\n".encode())
            await self.prog.stdin.drain()

    async def lose_game(self):
        await super().lose_game()

    async def ask_move(self, board, debug) -> tuple[tuple[int, int] | None, str | None]:
        await super().ask_move(board, debug)
        try:
            while True:
                if not self.prog.stdout:
                    return None, "communication failed"
                progInput = await asyncio.wait_for(self.prog.stdout.readuntil(), 0.1)
                if not isinstance(progInput, bytes):
                    continue
                progInput = progInput.decode().strip()
                if progInput.startswith("Traceback"):
                    output = StringIO()
                    if debug:
                        print(file=output)
                        print(progInput, file=output)
                        progInput = self.prog.stdout.read()
                        if isinstance(progInput, bytes):
                            print(progInput.decode(), file=output)
                        await Player.print(output)
                    return None, "error"
                if progInput.startswith(">"):
                    if debug:
                        await Player.print(f"{self} {progInput}")
                else:
                    break
            await Player.print(f"Column for {self} : {progInput}")
        except (asyncio.TimeoutError, asyncio.exceptions.IncompleteReadError):
            await Player.print(f"AI did not respond in time (over {TIMEOUT_LENGTH}s)")
            return None, "timeout"
        return await Human.sanithize(board, progInput)

    async def tell_move(self, move: int):
        if self.prog.stdin:
            self.prog.stdin.write(f"{move}\n".encode())
            await self.prog.stdin.drain()

    async def stop_game(self):
        try:
            self.prog.terminate()
            await self.prog.wait()
        except ProcessLookupError:
            pass


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

def render_end(winner, errors, silent):
    output = StringIO()
    if winner:
        print(f"{winner} won", end="", file=output)
    else:
        print("Draw", end="", file=output)
    if silent and errors:
        error_list = (f"{player} : {error}" for player, error in errors.items())
        print(f"  [{', '.join(error_list)}]", file=output)
    else:
        print("", file=output)
    return output

async def game(players: list[Human | AI], width, height, emoji, debug):

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
                if isinstance(player, AI) or error in ("user interrupt", "timeout"):
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


async def main(raw_args=None, ifunc=None, ofunc=None, discord=False):

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

    Player.ofunc = ofunc
    players = []
    ai_only = True
    pattern = re.compile(r"^\<\@[0-9]{18}\>$")
    for i, name in enumerate(args.prog):
        if name == "user":
            players.append(Human(i, args.emoji))
            ai_only = False
        elif pattern.match(name):
            players.append(Human(i, args.emoji, name, ifunc))
            ai_only = False
        else:
            players.append(AI(i, args.emoji, name, discord))
    while len(players) < args.players:
        players.append(Human(len(players), args.emoji))
        ai_only = False

    origin_stdout = sys.stdout
    if args.silent:
        if not ai_only:
            output = StringIO("Game cannot be silent since humans are playing")
            tmp = output.getvalue()
            await Player.print(output)
            raise Exception(tmp)
        if discord:
            Player.ofunc = None
        else:
            sys.stdout = open(os.devnull, "w")

    players, winner, errors, board = await game(players, width, height, args.emoji, not args.nodebug)

    if args.silent:
        sys.stdout = origin_stdout
        Player.ofunc = ofunc
    else:
        await Player.print(board)
    await Player.print(render_end(winner, errors, args.silent))

    return players, winner, errors

if __name__ == "__main__":
    asyncio.run(main())

