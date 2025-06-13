# Application de Jeux en Réseau
 
## Description
Cette application propose deux jeux en réseau: Mastermind et Morpion (Tic-Tac-Toe). Les joueurs peuvent se connecter, choisir un jeu et affronter d'autres joueurs en ligne.
 
## Fonctionnalités
- Interface graphique conviviale avec Tkinter
- Système de connexion avec pseudo
- Menu de sélection de jeu
- Deux jeux disponibles: Mastermind et Morpion
- Système de matchmaking automatique
- Statistiques de jeu
 
## Prérequis
- Python 3.6 ou supérieur
- Tkinter (généralement inclus avec Python)
- Connexion réseau pour le mode multijoueur
 
## Installation
 
1. Clonez ce dépôt:
\`\`\`bash
git clone https://github.com/votre-utilisateur/jeux-reseau.git
cd jeux-reseau
\`\`\`
 
2. Assurez-vous que le serveur de matchmaking est en cours d'exécution.
 
## Utilisation
 
1. Lancez l'application:
\`\`\`bash
python main.py
\`\`\`
 
2. Entrez votre pseudo et connectez-vous.
3. Choisissez le jeu auquel vous souhaitez jouer (Mastermind ou Morpion).
4. Suivez les instructions spécifiques à chaque jeu.
 
## Structure du projet
 
\`\`\`
scripts/
├── main.py                # Point d'entrée de l'application
├── app_client.py          # Classe principale de l'application
├── config.py              # Configuration globale
├── ui/                    # Interfaces utilisateur communes
│   ├── __init__.py
│   ├── login_ui.py
│   └── game_selection_ui.py
├── mastermind/            # Module du jeu Mastermind
│   ├── main.py
│   ├── client.py
│   ├── config.py
│   ├── README.md
│   └── ui/
│       ├── __init__.py
│       ├── main_menu_ui.py
│       ├── rules_ui.py
│       ├── code_creation_ui.py
│       ├── waiting_ui.py
│       ├── game_ui.py
│       └── result_ui.py
├── morpion/               # Module du jeu Morpion
│   ├── main.py
│   ├── client.py
│   ├── config.py
│   ├── README.md
│   └── ui/
│       ├── __init__.py
│       ├── main_menu_ui.py
│       ├── waiting_ui.py
│       ├── game_ui.py
│       ├── result_ui.py
│       └── stats_ui.py
└── README.md              # Ce fichier
\`\`\`
 
## Architecture
 
L'application suit une architecture modulaire avec séparation des préoccupations:
 
- **main.py**: Point d'entrée de l'application
- **app_client.py**: Gère la connexion au serveur et le menu de sélection de jeu
- **config.py**: Contient les constantes et paramètres de configuration globaux
- **ui/**: Dossier contenant les modules d'interface utilisateur communs
- **mastermind/**: Module complet pour le jeu Mastermind
- **morpion/**: Module complet pour le jeu Morpion
 
Chaque jeu est implémenté comme un module indépendant avec sa propre logique et ses propres interfaces utilisateur, ce qui facilite la maintenance et l'extension de l'application.
 
## Personnalisation
 
Vous pouvez personnaliser les couleurs, styles et paramètres de l'application en modifiant les fichiers `config.py`