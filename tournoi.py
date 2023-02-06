#!/usr/bin/env python3

import os
import sys
from itertools import combinations

from puissance4 import game, AI, WIDTH, HEIGHT


def explore(dirname: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, dirs, files in os.walk(dirname):
        for file in files:
            # if file.endswith(extension)):
            path_to_files.append({
                "path": os.path.join(root, file), 
                "filename": os.path.splitext(file)[0]
            })
    return path_to_files


def print_scores(scores: dict[str, int]) -> None:
    # Tri :
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(result):
        print(f"{i+1}. {name} ({score})")


def main():
    width, height = WIDTH, HEIGHT
    args = list(sys.argv[1:])
    if "-g" in args:
        id = args.index("-g")
        args.pop(id)
        try:
            width = int(args.pop(id))
            height = int(args.pop(id))
        except (IndexError, ValueError):
            pass
    files = explore("ai")
    paths = [file["path"] for file in files]
    players = [AI(name) for name in paths]
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    for p1, p2 in combinations(players, 2):
        result = game(p1, p2, width, height)
        scores[result] += 1

        result = game(p1, p2, width, height)
        scores[result] += 1

    print_scores(scores)

if __name__ == '__main__':
    main()

