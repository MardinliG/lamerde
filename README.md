# Projet Serveur de Matchmaking - Morpion

Ce projet implémente un serveur de matchmaking pour un jeu de Morpion (Tic-Tac-Toe) avec un client graphique.

## Prérequis
- Python 3.8+
- Bibliothèques : `tkinter` (inclus avec Python), `sqlite3` (inclus avec Python)

## Structure
- `models.py` : Classes POO pour le modèle de données et la logique du jeu.
- `database.py` : Gestion de la base de données SQLite.
- `server.py` : Serveur de matchmaking avec sockets.
- `client.py` : Client avec interface graphique Tkinter.

## Installation
1. Clonez le dépôt ou copiez les fichiers dans un dossier.
2. Assurez-vous que Python est installé.

## Exécution
1. **Démarrez le serveur** :
   ```bash
   python server.py