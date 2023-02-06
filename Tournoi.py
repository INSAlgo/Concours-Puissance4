import os
from itertools import combinations

from puissance4 import game, AI


def explore(dirname: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, dirs, files in os.walk(dirname):
        for file in files:
            # if file.endswith(extension)):
            path_to_files.append({"path": os.path.join(root, file), "filename": file})
    return path_to_files


def print_scores(scores: dict[str, int]) -> None:
    print("Résultat des scores :")
    # Tri :
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(result):
        print(f"{i+1}. {os.path.splitext(name)[0]}, score : {score}")


def main():
    files = explore("ai")
    paths = [file["path"] for file in files]
    players = [AI(i, name) for i, name in enumerate(paths)]
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    for p1, p2 in combinations(players, 2):
        result = game(p1, p2, False)
        scores[result] += 1

        result = game(p2, p1, False)
        scores[result] += 1

    print_scores(scores)

    


if __name__ == '__main__':
    main()

