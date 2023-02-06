#!/usr/bin/env python3

import os
import sys
from itertools import combinations, permutations
import subprocess

from puissance4 import game, AI, WIDTH, HEIGHT


def explore(dirname: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, _, files in os.walk(dirname):
        for file in files:
            path_to_files.append({
                "path": os.path.join(root, file), 
                "filename": os.path.splitext(file)[0]
            })
    return path_to_files

def printScores(scores: dict[str, int], nbGames, nbPlayers, verbose) -> None:
    if verbose: print()
    print(f"Results for {nbGames} games of {nbPlayers} players")
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(result):
        print(f"{i+1}. {name} ({score})")

def main():
    subprocess.run(['make'], capture_output=True)
    files = explore("out")
    width, height = WIDTH, HEIGHT
    verbose = False
    nbPlayers = 2
    args = list(sys.argv[1:])
    if "-v" in args:
        verbose = True
    if "-p" in args:
        id = args.index("-p")
        args.pop(id)
        nbPlayers = int(args.pop(id))
    if "-g" in args:
        id = args.index("-g")
        args.pop(id)
        try:
            width = int(args.pop(id))
            height = int(args.pop(id))
        except (IndexError, ValueError):
            pass
    paths = [file["path"] for file in files]
    players = [AI(name) for name in paths]
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    nbGames = 0
    for playersCombinations in combinations(players, nbPlayers):
        for playersPermutations in permutations(playersCombinations):
            matchPlayers = list(playersPermutations)
            result = game(matchPlayers, width, height)
            if verbose:
                print(" vs ".join((player.progName for player in matchPlayers)), end=" -> ")
            if result:
                scores[result] += 1
                if verbose: print(result)
            else:
                if verbose: print("draw")
            nbGames += 1

    printScores(scores, nbGames, nbPlayers, verbose)
    subprocess.run(['make', 'clean'], capture_output=True)

if __name__ == '__main__':
    main()

