import os
from itertools import combinations

import subprocess

from puissance4 import game, AI


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
    print("Résultat des scores :")
    # Tri :
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(result):
        print(f"{i+1}. {name}, score : {score}")


def main():
    subprocess.run(['make'], capture_output=True)
    files = explore("out")
    paths = [file["path"] for file in files]
    players = [AI(name) for name in paths]
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    for p1, p2 in combinations(players, 2):
        result = game(p1, p2)
        scores[result] += 1

        result = game(p2, p1)
        scores[result] += 1

    print_scores(scores)
    subprocess.run(['make', 'clean'], capture_output=True)

    


if __name__ == '__main__':
    main()

