"""
Module d'extension de la base de données pour gérer le système de classement.
Ajoute les tables et fonctions nécessaires pour stocker et manipuler les classements des joueurs.
"""
import sqlite3
from datetime import datetime

def upgrade_database(db_name="matchmaking.db"):
    """
    Met à jour la base de données pour ajouter le support du système de classement.
    
    Args:
        db_name (str, optional): Le nom de la base de données. Defaults to "matchmaking.db".
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Vérifier si la table player_rankings existe déjà
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_rankings'")
    if not cursor.fetchone():
        # Créer la table des classements
        cursor.execute('''
            CREATE TABLE player_rankings (
                pseudo TEXT PRIMARY KEY,
                elo_rating INTEGER DEFAULT 1200,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                last_game_date TEXT,
                FOREIGN KEY (pseudo) REFERENCES players(pseudo)
            )
        ''')
        
        # Créer la table d'historique des matchs pour le classement
        cursor.execute('''
            CREATE TABLE ranking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_pseudo TEXT,
                old_rating INTEGER,
                new_rating INTEGER,
                rating_change INTEGER,
                match_date TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id),
                FOREIGN KEY (player_pseudo) REFERENCES players(pseudo)
            )
        ''')
        
        print("Tables de classement créées avec succès.")
    else:
        print("Les tables de classement existent déjà.")
    
    conn.commit()
    conn.close()

class RankingDatabase:
    """Classe pour gérer les opérations de base de données liées au classement."""
    
    def __init__(self, db_name="matchmaking.db"):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_name (str, optional): Le nom de la base de données. Defaults to "matchmaking.db".
        """
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def get_player_ranking(self, pseudo):
        """
        Récupère les informations de classement d'un joueur.
        
        Args:
            pseudo (str): Le pseudo du joueur
            
        Returns:
            dict: Les informations de classement du joueur ou None si le joueur n'existe pas
        """
        self.cursor.execute('''
            SELECT elo_rating, games_played, wins, losses, draws, last_game_date
            FROM player_rankings
            WHERE pseudo = ?
        ''', (pseudo,))
        
        result = self.cursor.fetchone()
        if result:
            return {
                'pseudo': pseudo,
                'elo_rating': result[0],
                'games_played': result[1],
                'wins': result[2],
                'losses': result[3],
                'draws': result[4],
                'last_game_date': result[5]
            }
        
        # Si le joueur n'a pas encore de classement, l'initialiser
        self.initialize_player_ranking(pseudo)
        return {
            'pseudo': pseudo,
            'elo_rating': 1200,
            'games_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'last_game_date': None
        }
    
    def initialize_player_ranking(self, pseudo):
        """
        Initialise le classement d'un nouveau joueur.
        
        Args:
            pseudo (str): Le pseudo du joueur
        """
        try:
            self.cursor.execute('''
                INSERT INTO player_rankings (pseudo, elo_rating, games_played, wins, losses, draws)
                VALUES (?, 1200, 0, 0, 0, 0)
            ''', (pseudo,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Le joueur existe déjà, ignorer l'erreur
            pass
    
    def update_rankings_after_match(self, match_id, winner_pseudo, loser_pseudo, is_draw=False):
        """
        Met à jour les classements des joueurs après un match.
        
        Args:
            match_id (int): L'ID du match
            winner_pseudo (str): Le pseudo du gagnant
            loser_pseudo (str): Le pseudo du perdant
            is_draw (bool, optional): Indique si le match est un match nul. Defaults to False.
            
        Returns:
            tuple: (nouveau classement du gagnant, nouveau classement du perdant)
        """
        from mastermind.elo import calculate_rating_change
        
        # Récupérer les classements actuels
        winner_data = self.get_player_ranking(winner_pseudo)
        loser_data = self.get_player_ranking(loser_pseudo)
        
        winner_rating = winner_data['elo_rating']
        loser_rating = loser_data['elo_rating']
        winner_games = winner_data['games_played']
        loser_games = loser_data['games_played']
        
        # Calculer les nouveaux classements
        new_winner_rating, new_loser_rating = calculate_rating_change(
            winner_rating, loser_rating, winner_games, loser_games, is_draw
        )
        
        # Mettre à jour les statistiques du gagnant
        self.cursor.execute('''
            UPDATE player_rankings
            SET elo_rating = ?,
                games_played = games_played + 1,
                wins = CASE WHEN ? = 0 THEN wins ELSE wins + 1 END,
                draws = CASE WHEN ? = 1 THEN draws + 1 ELSE draws END,
                last_game_date = ?
            WHERE pseudo = ?
        ''', (new_winner_rating, 0 if is_draw else 1, 1 if is_draw else 0, datetime.now().isoformat(), winner_pseudo))
        
        # Mettre à jour les statistiques du perdant
        self.cursor.execute('''
            UPDATE player_rankings
            SET elo_rating = ?,
                games_played = games_played + 1,
                losses = CASE WHEN ? = 0 THEN losses + 1 ELSE losses END,
                draws = CASE WHEN ? = 1 THEN draws + 1 ELSE draws END,
                last_game_date = ?
            WHERE pseudo = ?
        ''', (new_loser_rating, 0 if is_draw else 1, 1 if is_draw else 0, datetime.now().isoformat(), loser_pseudo))
        
        # Enregistrer l'historique des changements de classement
        self.cursor.execute('''
            INSERT INTO ranking_history (match_id, player_pseudo, old_rating, new_rating, rating_change, match_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match_id, winner_pseudo, winner_rating, new_winner_rating, new_winner_rating - winner_rating, datetime.now().isoformat()))
        
        self.cursor.execute('''
            INSERT INTO ranking_history (match_id, player_pseudo, old_rating, new_rating, rating_change, match_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match_id, loser_pseudo, loser_rating, new_loser_rating, new_loser_rating - loser_rating, datetime.now().isoformat()))
        
        self.conn.commit()
        
        return (new_winner_rating, new_loser_rating)
    
    def get_top_players(self, limit=10):
        """
        Récupère les meilleurs joueurs classés par ELO.
        
        Args:
            limit (int, optional): Le nombre de joueurs à récupérer. Defaults to 10.
            
        Returns:
            list: Liste des meilleurs joueurs avec leurs statistiques
        """
        self.cursor.execute('''
            SELECT pseudo, elo_rating, games_played, wins, losses, draws
            FROM player_rankings
            WHERE games_played > 0
            ORDER BY elo_rating DESC
            LIMIT ?
        ''', (limit,))
        
        results = self.cursor.fetchall()
        top_players = []
        
        for row in results:
            top_players.append({
                'pseudo': row[0],
                'elo_rating': row[1],
                'games_played': row[2],
                'wins': row[3],
                'losses': row[4],
                'draws': row[5],
                'win_rate': round(row[3] / row[2] * 100, 1) if row[2] > 0 else 0
            })
        
        return top_players
    
    def get_player_rank(self, pseudo):
        """
        Récupère le rang d'un joueur parmi tous les joueurs classés.
        
        Args:
            pseudo (str): Le pseudo du joueur
            
        Returns:
            int: Le rang du joueur (1 pour le meilleur) ou None si le joueur n'a pas de classement
        """
        self.cursor.execute('''
            SELECT COUNT(*) + 1
            FROM player_rankings
            WHERE elo_rating > (
                SELECT elo_rating FROM player_rankings WHERE pseudo = ?
            )
            AND games_played > 0
        ''', (pseudo,))
        
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def get_player_history(self, pseudo, limit=10):
        """
        Récupère l'historique des changements de classement d'un joueur.
        
        Args:
            pseudo (str): Le pseudo du joueur
            limit (int, optional): Le nombre d'entrées à récupérer. Defaults to 10.
            
        Returns:
            list: Liste des changements de classement du joueur
        """
        self.cursor.execute('''
            SELECT rh.match_id, rh.old_rating, rh.new_rating, rh.rating_change, rh.match_date,
                   m.player1, m.player2, m.result
            FROM ranking_history rh
            JOIN matches m ON rh.match_id = m.id
            WHERE rh.player_pseudo = ? AND m.game_type = 'mastermind'
            ORDER BY rh.match_date DESC
            LIMIT ?
        ''', (pseudo, limit))
        
        results = self.cursor.fetchall()
        history = []
        
        for row in results:
            opponent = row[5] if row[5] != pseudo else row[6]
            result = "Victoire" if row[7] == pseudo else ("Match nul" if row[7] == "draw" else "Défaite")
            
            history.append({
                'match_id': row[0],
                'old_rating': row[1],
                'new_rating': row[2],
                'rating_change': row[3],
                'match_date': row[4],
                'opponent': opponent,
                'result': result
            })
        
        return history
    
    def close(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()
