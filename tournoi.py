#!/usr/bin/env python3

import itertools
import os
import sys
import subprocess
import argparse
import asyncio
import puissance4
    
SRCDIR = "ai"
MAX_PARALLEL_PROCESSES = 200
ALLOWED_EXTENSIONS = ['.py', '.js', '', '.out', '.class']

def split(arr, size = MAX_PARALLEL_PROCESSES):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs

def explore(dirname: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, _, files in os.walk(dirname):
        for file in files:
            if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                path_to_files.append({
                    "path": os.path.join(root, file), 
                    "filename": os.path.splitext(file)[0]
                })
    return path_to_files

def print_game_results(game_nb, nb_games, players, winner, errors):
    print(f"({game_nb}/{nb_games})",
          f"{' vs '.join(players)} ->",
          f"{winner if winner else 'Draw'}",
          sep = " ", end = "")
    if errors:
        print(f" ({' '.join(f'{player}: {error}' for player, error in errors.items())})")
    else:
        print()

def print_scores(scoreboard, nbGames) -> None:
    print()
    print(f"Results for {nbGames} games")
    for i, (name, score) in enumerate(scoreboard):
        print(f"{i+1}. {name} ({score})")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rematches", type=int, default=1, metavar="NB_REMATCHES")
    parser.add_argument("-p", "--players", type=int, default=2, metavar="NB_PLAYERS")
    parser.add_argument("-d", "--directory", default=SRCDIR, metavar="SRC_DIRECTORY")
    parser.add_argument("-l", "--log", action="store_true")

    args, remaining_args = parser.parse_known_args()
    rematches = args.rematches
    nb_players = args.players
    src_dir = args.directory
    if args.log:
        log_file = open("log", "w")
        sys.stdout = log_file
        sys.stderr = log_file

    asyncio.run(tournament(rematches, nb_players, src_dir, remaining_args))

async def tournament(rematches, nb_players, src_dir, args):
    print(f"Tournament for {SRCDIR} folder")

    # Compile programs
    subprocess.run(('make', f"SRCDIR={src_dir}"), capture_output=True)

    # Get all programs
    files = explore("out")
    paths = [file["path"] for file in files if not file["path"].startswith(".")]

    # Initialize score
    scores = {file["filename"] : 0 for file in files}
    game_nb = 0

    # Create list of coroutines to run
    games = list()

    for combinations in itertools.combinations(paths, nb_players):
        for players in itertools.permutations(combinations):
            for _ in range(rematches):
                games.append(puissance4.main(list(players) + args))

    nb_games = len(games)

    # Make sublists of size MAX_PARALLEL_PROCESSES
    games = split(games)

    # Awaiting and printing results
    origin_stdout = sys.stdout
    devnull = open(os.devnull, "w")

    for subGames in games :

        sys.stdout = devnull
        results = await asyncio.gather(*subGames)
        sys.stdout = origin_stdout

        for players, winner, errors in results:
            game_nb += 1
            if winner:
                scores[str(winner)] += 1
            print_game_results(game_nb, nb_games, players, winner, errors)

    scoreboard = sorted(scores.items(), key=lambda score: score[1], reverse=True)
    print_scores(scoreboard, nb_games)
    subprocess.run(('make', 'clean'), capture_output=True)

    return scoreboard

if __name__ == '__main__':
    main()

