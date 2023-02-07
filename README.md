# Introduction

Bienvenue dans le grand toutnoi de puissance4 d'INSAlgo !

# Spécification du programme

Il va faloir créer un programme capable de jouer au puissance 4 !
La communication avec ce programme sera automatisée. Les entrées se présentent sous cette forme :

Sur une première ligne, les entiers W, H, N, S séparés par des espaces avec
 - W : largeur de la grille
 - H : largeur de la grille
 - N : nombre de joueurs, danc ce concours, N=2, vous n'est pas obligés de supporter le support de parties avec plus de joueurs
 - S : La position de départ. Pour N = 2, on 

Si S = 1, votre programme démarre, il ne doit pas lire plus d'input 
et doit afficher son coup : la colonne K avec 1<=K<=M.

Votre programme doit ensuite supporter une boucle de jeu :
 - Lire le coup de votre adversaire : un entier M avec 1<=M<=W : la colonne dans laquelle l'adversaire a joué.
 - Votre programme doit ensuite afficher son coup : la colonne K avec 1<=K<=M.

Pour permettre un degub plus précis, les sorties commencant par `>` seront transmises a l'écran en étant ignorées par le programme.

# Tester un programme en local

Pour installer les dépendances du programme : `pip install -r requirements.txt`

Le programme nécéssite java pour executer les `.class` et node jour executer les `.js`.

Le programme puissance4.py vous fournit un certain nombre d'outils pour tester et debugger votre programme.

`python puissance4.py [OPTIONS] [prog1, prog2, prog3, ..., progN]`

Les options sont :
  - `-s` : mode silencieux
  - `-g W H` (par défaut W = 7, H = 6): regle la taille de la grille : largeur = W, hauteur = H
  - `-p N` (par défaut, N = 2) : nombre de joueurs

Les programmes acceptés sont :
 - les scripts Python `.py`
 - les scripts JavaScript `.js`
 - les classes java compilées : `.class`
 - Les exécutables compilés

Le programme vous permet notamment de jouer contre votre IA :
`python puissance4.py prog1`

De se faire battre 2 IA :
`python puissance4.py prog1 prog2`

Ou encore de se faire battre l'IA contre elle meme :
`python puissance4.py prog1 prog1`

De jouer a 3 joueurs humains sans IA sur une grille 20x20:
`python puissance4.py -p 3 -g 20 20`

# Le concours

## Déroulement du concours

Pour être tenu au courant du déroulement du concours, vous pouvez rejoindre le Discord d'INSAlgo

Le concours se compose de la phase de développement des IA qui s'étent jusqu'à DATE à HEURE

Avant cette date, les participants pourront soumettre leur code.

A la fin, le code participera à un tournoi qui fera se battre toutes les IA.

Chaque IA se battra 2 fois contre chacune des autres IA, une fois en commencant, une fois en laissant l'adversaire commencer.
Une victoire rapporte un point, une défaire rapporte 0 points. Une égalité ne fait pas gagner de point.

Une temps de réponse trop long ou un coupo invalide fait pertre le match au programme.

# Participer au concours

Pour participer au concours, vous devez être étudiant de l'INSA Lyon à date de fin du concours le DATE PAS FIXEE.

Les soumissions sont faites par message privé à au bot 1048680176118136942.
Pour sometrre un code, envoyez la commande `!p4 submit` avec votre fichier attaché dans le meme message.

Votre dernière soumission vous représentera lors du tournoi.

Pour le tournoi, transmettez votre code source et non un executable.
Les langages sont acceptés sont :
 - Python (.py)
 - JavaScript (.js)
 - C++ (.cpp), sera compilé avec g++ en O3
 - C (.c), sera compilé avec gcc en O3
 - Java (.java)

Si vous souhaitez participer avec un autre langage, contactez un membre de bureau d'INSAlgo sur le serveur Discord.

# Regles du concours

Les soumissions se terminent le DATE à HEURE.

Les soumissions doivent être ORIGINALES, c'est à dire ne pas implémenter une solution toute prête trouvée sur internet.

Les organisateurs vérifieront le code avant de valider les gagnants, alors soyez honnêtes !

Il est autorisé de participer à plusieurs, danc ce cas, soumettez un seul programme pour le groupe.

Les gains sont:
 - 64€ pour le premier
 - 32€ pour le deuxième
 - 16€ pour le troisième

Si un groupe gagne, la récompense est par GROUPE et non par PERSONNES.

Si des égalités se présentent, les personnes/groupes à égalité se partageront la somme des gains.
Ex :
  - 1er : bob -> il gagne 64€
  - 2e ex-aequo : alice et eve -> elles gagnent chacune (32+16)/2 = 24 €



