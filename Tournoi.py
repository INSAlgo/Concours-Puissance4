import subprocess
import os
from itertools import combinations
from collections import defaultdict, prio


def explore(dirname: str, extension: str) -> list[dict[str, str]]:
    path_to_files = list()
    for root, dirs, files in os.walk(dirname):
        for file in files:
            # if file.endswith(extension)):
            path_to_files.append({"path": os.path.join(root, file), "filename": file})
    return path_to_files


def print_scores(scores: dict[str, int]) -> None:
    print("Résultat des scores :")
    # Tri :
    result = sorted(scores.items(), key=lambda x: x[1])
    for i, name, score in enumerate(result):
        print(f"{i}. {os.path.splitext()[0]}, score : {score}")


def main():
    files = explore("ai")
    paths = [file["path"] for file in files]
    scores = dict()
    for file in files:
        scores[file["filename"]] = 0

    for p1, p2 in combinations(paths, 2):
        result = subprocess.call(["./puissance4.py", p1, p2, "-s"], capture_output=True)
        scores[result.stdout] += 1

        result = subprocess.call(["./puissance4.py", p2, p1, "-s"], capture_output=True)
        scores[result.stdout] += 1

    print_scores(scores)

    


if __name__ == '__main__':
    main()

