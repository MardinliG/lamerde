from dataclasses import dataclass
from datetime import datetime

@dataclass
class Player:
    """Représente un joueur dans la file d'attente ou un match."""
    pseudo: str
    ip: str
    port: int
    join_date: datetime

@dataclass
class Match:
    """Représente un match entre deux joueurs."""
    id: int  # Identifiant unique du match
    player1: Player
    player2: Player
    board: list  # Plateau de jeu (9 cases pour morpion)
    is_finished: bool
    result: str  # "player1", "player2", "draw", ou None

@dataclass
class Turn:
    """Représente un tour joué dans un match."""
    match_id: int
    player: Player
    move: int  # Position du coup (0-8)

class TicTacToe:
    """Logique du jeu Morpion."""
    def __init__(self):
        self.board = [" " for _ in range(9)]  # Plateau 3x3

    def play_move(self, position: int, player: str) -> bool:
        """Joue un coup à la position donnée si valide."""
        if 0 <= position < 9 and self.board[position] == " ":
            self.board[position] = player
            return True
        return False

    def check_winner(self) -> str:
        """Vérifie s'il y a un gagnant ou une égalité."""
        # Combinaisons gagnantes : lignes, colonnes, diagonales
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Lignes
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Colonnes
            (0, 4, 8), (2, 4, 6)              # Diagonales
        ]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return self.board[a]  # Retourne "X" ou "O"
        if " " not in self.board:
            return "draw"
        return None