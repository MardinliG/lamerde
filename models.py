from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

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
    id: int 
    player1: Player
    player2: Player
    board: list  
    is_finished: bool
    result: str 
    game_type: str = "morpion"  

@dataclass
class Turn:
    """Représente un tour joué dans un match."""
    match_id: int
    player: Player
    move: int  
    feedback: list = None  

@dataclass
class MastermindMatch(Match):
    """Représente un match de Mastermind entre deux joueurs."""
    player1_code: list = None  
    player2_code: list = None  
    player1_guesses: list = None  
    player2_guesses: list = None  
    player1_feedback: list = None  
    player2_feedback: list = None  
    max_attempts: int = 10  

    def __post_init__(self):
        if self.player1_guesses is None:
            self.player1_guesses = []
        if self.player2_guesses is None:
            self.player2_guesses = []
        if self.player1_feedback is None:
            self.player1_feedback = []
        if self.player2_feedback is None:
            self.player2_feedback = []
        self.game_type = "mastermind"

class TicTacToe:
    """Logique du jeu Morpion."""
    def __init__(self):
        self.board = [" " for _ in range(9)] 

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

class Mastermind:
    """Logique du jeu Mastermind."""
    def __init__(self, code_length=4, colors=None, max_attempts=10):
        self.code_length = code_length
        self.colors = colors or ["red", "green", "blue", "yellow", "purple", "orange"]
        self.max_attempts = max_attempts

    def check_guess(self, code: List[str], guess: List[str]) -> Tuple[int, int]:
        """
        Vérifie une tentative et retourne le feedback.
        
        Args:
            code: Le code secret à deviner
            guess: La tentative du joueur
            
        Returns:
            Tuple[int, int]: (nombre de pions noirs, nombre de pions blancs)
            - Pions noirs: bonne couleur à la bonne position
            - Pions blancs: bonne couleur mais mauvaise position
        """
        if len(code) != len(guess):
            raise ValueError("Le code et la tentative doivent avoir la même longueur")
            
        # Copie des listes pour ne pas modifier les originales
        code_copy = code.copy()
        guess_copy = guess.copy()
        
        # Compter les pions noirs (bonne couleur, bonne position)
        black_pins = 0
        for i in range(len(code)):
            if i < len(guess) and code[i] == guess[i]:
                black_pins += 1
                code_copy[i] = None  # Marquer comme traité
                guess_copy[i] = None  # Marquer comme traité
        
        # Compter les pions blancs (bonne couleur, mauvaise position)
        white_pins = 0
        for i in range(len(guess_copy)):
            if guess_copy[i] is not None:
                for j in range(len(code_copy)):
                    if code_copy[j] is not None and guess_copy[i] == code_copy[j]:
                        white_pins += 1
                        code_copy[j] = None  
                        break
        
        return (black_pins, white_pins)

    def is_correct(self, code: List[str], guess: List[str]) -> bool:
        """Vérifie si la tentative est correcte (tous les pions sont noirs)."""
        black_pins, _ = self.check_guess(code, guess)
        return black_pins == len(code)

print("Models mis à jour avec succès!")
