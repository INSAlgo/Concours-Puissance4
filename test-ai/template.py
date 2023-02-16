W, H, N, S = map(int, input().split())

# Fonction pour savoir à quelle hauteur va tomber pion
def fallHeight(board, x):
    y = len(board[x])
    while board[x][y - 1] == 0 and y > 0:
        y -= 1
    return y

# Calcul du meilleur coup à jouer étant donné l'état de la grille
def strategy(board):
    # Recherche de la première colonne non pleine
    x = 0
    while board[x][H - 1] != 0:
        x += 1
    return x

def main():

    board = [[0 for _ in range(H)] for _ in range(W)]
    player = 0

    while True:
        player = player % N + 1

        # Tour de notre IA
        if player == S:
            x = strategy(board)
            print(f"> {x} {fallHeight(board, x)}")  # Debug
            print(x)
        # Tour adversaire
        else:
            x = int(input())

        # Mise à jour de la grille en interne
        if x >= 0 :
            y = fallHeight(board, x)
            board[x][y] = player

if __name__ == "__main__":
    main()
