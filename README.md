*This project has been created as part of the 42 curriculum by thsykas rdedack*

## DESCRIPTION
**A-Maze-ing** est un projet de programmation en Python dont l’objectif est de concevoir un générateur de labyrinthes capable de créer des structures complexes, aléatoires et :

- soit **parfaites** (un unique chemin entre l’entrée et la sortie),
- soit **imparfaites** (plusieurs chemins possibles).
Le projet ne se limite pas à la génération : il inclut également l’implémentation d’algorithmes de **pathfinding** afin de résoudre le labyrinthe en trouvant le chemin le plus court entre le point de départ et la sortie.

Les algorithmes implémentés sont :

- **DFS (Depth-First Search)** pour la génération et la résolution,
- **A\*** (A-Star) pour la recherche optimisée du plus court chemin.

L’objectif pédagogique est de comprendre :
- l’optimisation de recherche
- la manipulation de grilles et structures de données

## INSTRUCTION
Le projet contient un **Makefile** avec plusieurs règles :
- `make` → lance le programme
- `make lint` → vérifie la conformité avec `flake8` et `mypy`
- `make lint-strict` → exécute `flake8` et `mypy` en mode strict (`--strict`)

## RESSOURCES
pour la partie algoritmie

**DFS (Pathfinding_algo) DepthFirstSearch**  
```bash
https://www.geeksforgeeks.org/dsa/geek-in-a-maze/
```
**A\* (A-Star)**  
```bash
https://www.geeksforgeeks.org/dsa/a-search-algorithm/
```

L’IA a été utilisée principalement pour :

- comprendre et corriger certaines erreurs liées au mode strict de `mypy`,
- clarifier des comportements inattendus lors de la vérification statique des types,
- obtenir des explications techniques sur certaines optimisations ou erreurs spécifiques.
Les algorithmes de génération et de pathfinding ont été conçus et implémentés par l’équipe. L’IA a servi d’outil d’assistance et de débogage, notamment pour améliorer la robustesse du code et respecter les contraintes du mode strict.

## Installation via Wheel (.whl)

Le projet peut être installé facilement en utilisant un fichier `.whl` généré depuis le dépôt.

## Installation via Wheel (.whl)

Le projet peut être installé facilement en utilisant un fichier `.whl` généré depuis le dépôt.

### Étapes :
1. **Génération du fichier `.whl`**  
   Depuis la racine du projet:
   ```bash
      python -m build
    ```

## Instalation via pip
pip install mazegen-0.1.0-py3-none-any.whl
un fois installer lancement du programme : amazeing

## Gestion des dépendances avec `pyproject.toml`
Le projet utilise un fichier `pyproject.toml` pour centraliser la configuration et les dépendances nécessaires au projet.
