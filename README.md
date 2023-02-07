# Introduction

Bienvenue dans le grand tournoi de Puissance 4 d'INSAlgo !

# Spécifications du programme

Il va faloir créer un programme capable de jouer au puissance 4 !
La communication avec ce programme sera automatisée. Les entrées se présentent sous cette forme :

Sur une première ligne, les entiers W, H, N, S séparés par des espaces avec
 - W : (width) largeur de la grille
 - H : (height) hauteur de la grille
 - N : nombre de joueurs. Pour le concours, on aura toujours N=2, mais vous pouvez supporter des parties multijoueurs si ça vous amuse
 - S : (start) le tour de début de votre programme

Si S = 1, votre programme commence, il ne doit pas lire plus d'input 
et doit afficher son coup : la colonne K avec 1<=K<=M.
Si S = 2, il attend d'abord que le premier joueur joue

Votre programme doit ensuite supporter une boucle de jeu :
 - Lire le coup de votre adversaire : un entier M avec 1<=M<=W : la colonne dans laquelle l'adversaire a joué.
 - Votre programme doit ensuite afficher son coup : la colonne K avec 1<=K<=M.

Pour permettre un debug plus précis, les sorties commençant par `>` seront transmises à l'écran en étant ignorées par le programme.

# Tester un programme en local

Pour installer les dépendances du programme : `pip install -r requirements.txt`

Le programme nécéssite java pour exécuter les `.class` et node pour executer les `.js`.

Le programme puissance4.py vous fournit un certain nombre d'outils pour tester et debugger votre programme.

`python puissance4.py [OPTIONS] [prog1, prog2, prog3, ..., progN]`

Les options sont :
  - `-s` : mode silencieux
  - `-g W H` (par défaut W = 7, H = 6) : la taille de la grille (W = largeur, H = hauteur)
  - `-p N` (par défaut, N = 2) : nombre de joueurs

Les programmes acceptés sont :
 - les scripts Python `.py`
 - les scripts JavaScript `.js`
 - les classes java compilées : `.class`
 - Les exécutables compilés

Jouer au jeu de base, sans IAs :
`python puissance4.py`

Jouer contre votre IA :
`python puissance4.py prog1`

Partie entre 2 IAs :
`python puissance4.py prog1 prog2`

Partie de l'IA contre elle-même :
`python puissance4.py prog1 prog1`

Partie à 5 joueurs dont 2 IAs et 3 humains sur une grille 20x20 :
`python puissance4.py -g 20 20 -p 5 prog1 prog2`

# Le concours

## Déroulement du concours

Pour être tenu au courant du déroulement du concours, vous pouvez rejoindre le [Discord d'INSAlgo](https://discord.gg/fGTkMQetSC)

Le concours se compose de la phase de développement des IA qui s'étent jusqu'au 21 février 2023 à 18h

Avant cette date, les participants pourront soumettre leur code.

A la fin, le code participera à un tournoi qui fera se rencontrer toutes les IA.

Chaque IA se battra 2 fois contre chacune des autres IA, une fois en commencant, une fois en laissant l'adversaire commencer.
Une victoire rapporte un point, une défaire rapporte 0 points. Une égalité ne fait pas gagner de point.

Une temps de réponse trop long ou un coup invalide fait perdre le match au programme.

# Participer au concours

Pour participer au concours, vous devez être étudiant de l'INSA Lyon à date de fin du concours le 21 février, et pas membre du bureau d'INSAlgo.

Les soumissions sont faites par message privé au bot 1048680176118136942.
Pour soumettre un code, envoyez la commande `!p4 submit` avec votre fichier attaché dans le même message.
Donner à votre programme le nom de votre pseudo.

Votre dernière soumission vous représentera lors du tournoi.

Pour le tournoi, transmettez votre code source et non un executable.
Les langages acceptés sont :
 - Python (.py)
 - JavaScript (.js)
 - C++ (.cpp), sera compilé avec g++ en O3
 - C (.c), sera compilé avec gcc en O3
 - Java (.java)

Si vous souhaitez participer avec un autre langage, contactez un membre de bureau d'INSAlgo sur le serveur Discord.

# Regles du concours

Les soumissions se terminent le 21 février à 18h.

Les soumissions doivent être ORIGINALES, c'est-à-dire ne pas implémenter une solution toute prête trouvée sur internet.

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



