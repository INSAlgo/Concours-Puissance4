#!/usr/bin/env python3

import os
import sys
from itertools import combinations, permutations
import subprocess
from math import factorial
from asyncio import run

from puissance4 import game, AI, WIDTH, HEIGHT, renderEnd
SRCDIR = "test-ai"

def explore(dirname: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, _, files in os.walk(dirname):
        for file in files:
            path_to_files.append({
                "path": os.path.join(root, file), 
                "filename": os.path.splitext(file)[0]
            })
    return path_to_files

def printScores(scores: dict[str, int], nbGames, verbose) -> None:
    if verbose: print()
    print(f"Results for {nbGames} games")
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(result):
        print(f"{i+1}. {name} ({score})")

async def main():
    width, height = WIDTH, HEIGHT
    verbose = True
    rematches = 1
    nbPlayers = 2
    srcDir = SRCDIR
    args = list(sys.argv[1:])
    if "-s" in args:
        verbose = False
    if "-p" in args:
        id = args.index("-p")
        args.pop(id)
        nbPlayers = int(args.pop(id))
    if "-r" in args:
        id = args.index("-r")
        args.pop(id)
        rematches = int(args.pop(id))
    if "-g" in args:
        id = args.index("-g")
        args.pop(id)
        try:
            width = int(args.pop(id))
            height = int(args.pop(id))
        except (IndexError, ValueError):
            pass
    if "-d" in args:
        id = args.index("-d")
        args.pop(id)
        srcDir = args.pop(id)
    subprocess.run(['make', f"SRCDIR={srcDir}"], capture_output=True)
    files = explore("out")
    paths = [file["path"] for file in files]
    players = [AI(name) for name in paths if not name.startswith(".")]
    nbAIs = len(players)
    print(nbAIs)
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    nbGames = factorial(nbAIs) // factorial(nbAIs - nbPlayers) * rematches
    iGame = 0
    if verbose:
        print(f"Tournament between {len(scores)} AIs")
    for playersCombinations in combinations(players, nbPlayers):
        for playersPermutations in permutations(playersCombinations):
            for _ in range(rematches):
                iGame += 1
                matchPlayers = list(playersPermutations)
                res = await game(matchPlayers, width, height)
                winner, errors, _  = res
                if winner:
                    scores[str(winner)] += 1
                if verbose:
                    print(f"({iGame}/{nbGames}) {' vs '.join((player.progName for player in matchPlayers))} -> " , end="")
                    renderEnd(winner, errors)

    printScores(scores, nbGames, verbose)
    subprocess.run(('make', 'clean'), capture_output=True)

if __name__ == '__main__':
    run(main())

