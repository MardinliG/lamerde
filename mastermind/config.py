"""
Module de configuration pour le client Mastermind.
Contient les constantes et paramètres de configuration.
"""

class Config:
    """Classe de configuration pour le client Mastermind."""
    # Paramètres du jeu
    MAX_ATTEMPTS = 10
    CODE_LENGTH = 4
    COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]
    
    # Couleurs et styles
    BG_COLOR = "#f0f0f0"
    ACCENT_COLOR = "#4a6ea9"
    TEXT_COLOR = "#333333"
    BUTTON_COLOR = "#5a81c2"
    BUTTON_HOVER = "#7094d1"
    SUCCESS_COLOR = "#5cb85c"
    WARNING_COLOR = "#f0ad4e"
    DANGER_COLOR = "#d9534f"
