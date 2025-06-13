"""
Module de calcul ELO pour le système de classement du Mastermind.
Implémente les fonctions nécessaires pour calculer et mettre à jour les scores ELO des joueurs.
"""

def calculate_expected_score(player_rating, opponent_rating):
    """
    Calcule le score attendu d'un joueur contre un adversaire selon leurs classements ELO.
    
    Args:
        player_rating (int): Le classement ELO du joueur
        opponent_rating (int): Le classement ELO de l'adversaire
        
    Returns:
        float: Le score attendu (entre 0 et 1)
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

def calculate_new_rating(player_rating, expected_score, actual_score, k_factor=32):
    """
    Calcule le nouveau classement ELO d'un joueur après un match.
    
    Args:
        player_rating (int): Le classement ELO actuel du joueur
        expected_score (float): Le score attendu du joueur pour ce match
        actual_score (float): Le score réel du joueur (1 pour une victoire, 0.5 pour un match nul, 0 pour une défaite)
        k_factor (int, optional): Le facteur K qui détermine l'ampleur des changements de classement. Defaults to 32.
        
    Returns:
        int: Le nouveau classement ELO du joueur
    """
    return round(player_rating + k_factor * (actual_score - expected_score))

def get_k_factor(player_rating, games_played):
    """
    Détermine le facteur K approprié en fonction du classement et de l'expérience du joueur.
    
    Args:
        player_rating (int): Le classement ELO actuel du joueur
        games_played (int): Le nombre de parties jouées par le joueur
        
    Returns:
        int: Le facteur K à utiliser pour ce joueur
    """
    # Joueurs débutants (moins de 10 parties) - changements plus importants
    if games_played < 10:
        return 40
    # Joueurs établis mais non élites
    elif player_rating < 2000:
        return 32
    # Joueurs d'élite - changements plus conservateurs
    else:
        return 24

def calculate_rating_change(winner_rating, loser_rating, winner_games, loser_games, is_draw=False):
    """
    Calcule les changements de classement ELO pour les deux joueurs après un match.
    
    Args:
        winner_rating (int): Le classement ELO du gagnant
        loser_rating (int): Le classement ELO du perdant
        winner_games (int): Le nombre de parties jouées par le gagnant
        loser_games (int): Le nombre de parties jouées par le perdant
        is_draw (bool, optional): Indique si le match est un match nul. Defaults to False.
        
    Returns:
        tuple: (nouveau classement du gagnant, nouveau classement du perdant)
    """
    # Calculer les scores attendus
    winner_expected = calculate_expected_score(winner_rating, loser_rating)
    loser_expected = calculate_expected_score(loser_rating, winner_rating)
    
    # Déterminer les facteurs K
    winner_k = get_k_factor(winner_rating, winner_games)
    loser_k = get_k_factor(loser_rating, loser_games)
    
    # Calculer les scores réels
    if is_draw:
        winner_actual = 0.5
        loser_actual = 0.5
    else:
        winner_actual = 1.0
        loser_actual = 0.0
    
    # Calculer les nouveaux classements
    new_winner_rating = calculate_new_rating(winner_rating, winner_expected, winner_actual, winner_k)
    new_loser_rating = calculate_new_rating(loser_rating, loser_expected, loser_actual, loser_k)
    
    return (new_winner_rating, new_loser_rating)
