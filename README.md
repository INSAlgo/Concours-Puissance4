# Concours Puissance 4 d'INSAlgo

Bienvenue dans le grand tournoi de Puissance 4 d'INSAlgo ! Sur le mois de février, vous pourrez développer une petite IA capable jouer au jeu, dans le langage de votre choix. À la fin, toutes les IA vont se rencontrer, et les meilleures remporteront des prix !

```plaintext
┌───────────────┐
│ . . . . . . . │
│ . . . . . . . │
│ . 2 . 1 . . . │
│ 2 1 1 1 . . . │
│ 2 1 1 2 2 1 2 │
│ 2 2 1 1 2 1 2 │
└───────────────┘
```

# Programme

## Spécification

La communication avec votre programme est automatisée. Les entrées se présentent sous cette forme :

Sur une première ligne, `W H N S` des entiers séparés par des espaces avec
 - W : (width) largeur de la grille
 - H : (height) hauteur de la grille
 - N : nombre de joueurs. Pour le concours, on aura toujours N=2, mais vous pouvez supporter des parties multijoueurs si ça vous amuse
 - S : (start) le tour de début de votre programme (1 ou 2)

Votre programme doit ensuite supporter une boucle de jeu :
 - Lire le coup de votre adversaire : un entier `M` avec 0 <= M < W, la colonne dans laquelle l'adversaire a joué
 - Afficher son coup : la colonne `K` avec 0 <= K < W

 Si S = 1, votre programme doit commence en premier, donc affiche son coup. Si S = 2, il doit d'abord lire le coup de l'adversaire

Pour permettre le debug, les sorties commençant par `>` seront transmises à l'écran en étant ignorées par le jeu.

Un exemple d'IA (pas très intelligente) en Python est donné : [template.py](https://github.com/INSAlgo/Concours-Puissance4/blob/main/test-ai/template.py). Vous pouvez vous en servire de base pour votre IA.

## Tester un programme en local

Récupérez le script [puissance4.py](https://github.com/INSAlgo/Concours-Puissance4/blob/main/puissance4.py) et installez ses dépendances : `pip install pexpect`. (Pour ce faire, vous pouvez utiliser le fichier [requirements.txt](https://github.com/INSAlgo/Concours-Puissance4/blob/main/requirements.txt) si vous connaissez). Ce script fournit un certain nombre d'outils pour tester et debugger votre programme :

`python puissance4.py [OPTIONS] [prog1, prog2, prog3, ..., progN]`

Exemples :
- partie entre deux joueurs, sans IA : `python puissance4.py`
- partie contre votre IA : `python puissance4.py prog1`
- partie entre 2 IA : `python puissance4.py prog1 prog2`
- partie de l'IA contre elle-même : `python puissance4.py prog1 prog1`

Les options sont :
  - `-s` : mode silencieux
  - `-g W H` (par défaut W = 7, H = 6) : la taille de la grille (W = largeur, H = hauteur)
  - `-p N` (par défaut, N = 2) : nombre de joueurs

Un exemple plus compliqué : partie à 5 joueurs dont 2 IA et 3 humains sur une grille 20x20 :

`python puissance4.py -g 20 20 -p 5 prog1 prog2`

Les programmes acceptés sont :
 - les scripts Python `.py`
 - les scripts JavaScript `.js`
 - les classes java compilées `.class`
 - Les exécutables compilés (C, C++, ...)

# Le concours

## Déroulement du concours

Pour être tenu au courant du déroulement du concours, venez sur le [Discord d'INSAlgo](https://discord.gg/fGTkMQetSC). La phase de développement des IA s'étent jusqu'au 21 février, pendant laquelle les participants peuvent soumettre leur code.

A la fin, votre programme participera à un tournoi qui fera se rencontrer toutes les IA (avec le script [tournoi.py](https://github.com/INSAlgo/Concours-Puissance4/blob/main/tournoi.py)). Chaque IA se battra 2 fois contre chacune des autres IA, une fois en commencant, une fois en laissant l'adversaire commencer. Une victoire rapporte un point, une défaite ou une égalité ne rapporte pas de point. Un temps de réponse trop long ou un coup invalide fait perdre le match au programme.

## Participer au concours

Les soumissions sont faites par message privé au bot Dijkstra-Chan du serveur Discord. Pour ce faire, envoyez la commande `!p4 submit` avec votre fichier attaché dans le même message. Donner comme nom à votre programme votre pseudo.

Votre dernière soumission vous représentera lors du tournoi final.
Pour le tournoi, transmettez votre code source et non un executable.
Les langages acceptés sont :
 - Python `.py`
 - JavaScript `.js`
 - C++ `.cpp` (qui sera compilé avec g++ en O3)
 - C `.c` (qui sera compilé avec gcc en O3)
 - Java `.java`
 - C# `.cs`
 - Rust `.rs`

Si vous souhaitez participer avec un autre langage, contactez un membre de bureau d'INSAlgo sur le serveur Discord.

## Règles du concours

Tous les étudiants de l'INSA Lyon peuvent participer, à l'exception des organisateurs. Il est autorisé de participer à plusieurs, danc ce cas, soumettez un seul programme pour le groupe.

Les soumissions se terminent le 21 février 2023 à 18h.

Les soumissions doivent être ORIGINALES, c'est-à-dire ne pas implémenter une solution toute prête trouvée sur internet. Les organisateurs vérifieront le code avant de valider les gagnants, alors soyez honnêtes ! Pour rendre cette tache plus facile, écrivez autant que possible du code lisible et commenté.

Les prix sont:
 - **64 €** pour le premier
 - **32 €** pour le deuxième
 - **16 €** pour le troisième

Si un groupe gagne, la récompense est par groupe et non par personnes. Si des égalités se présentent, les personnes/groupes à égalité se partageront la somme des prix, par exemple :
  - 1er : Bob -> il gagne 64 €
  - 2e ex-aequo : Alice et Eve -> elles gagnent chacune (32+16)/2 = 24 €
