import random

W, H, N, S = map(int, input().split())

# Fonction pour savoir a quelle hauteur va tomber pion
def fallHeight(board, x):
    y = len(board[x])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

# Calcul du meilleur coup à jouer étant donné l'état de la grille
def strategy(board):
    # Liste des colonnes, dans un ordre aléatoire
    columns = list(range(0, W))
    random.shuffle(columns)
    for x in columns:
        # On cherche une colonne non pleine
        if board[x][H - 1] == 0:
            return x
    return -1

def main():
    # Initialisation
    board = [[0 for _ in range(H)] for _ in range(W)]

    player = 0
    while True:
        player = player % N + 1

        # Tour de notre IA
        if player == S:
            x = strategy(board)
            print(f"> {x} {fallHeight(board, x)}")
            print(x)
        # Tour adversaire
        else:
            x = int(input())

        # Mise à jour de la grille en interne
        y = fallHeight(board, x)
        board[x][y] = player

if __name__ == "__main__":
    main()
