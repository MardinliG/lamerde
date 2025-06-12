import sqlite3
from models import Player, Match, Turn

class Database:
    """Gère la base de données SQLite pour le projet."""
    def __init__(self, db_name="matchmaking.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        """Crée les tables nécessaires."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                pseudo TEXT PRIMARY KEY,
                ip TEXT,
                port INTEGER,
                join_date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1 TEXT,
                player2 TEXT,
                board TEXT,
                is_finished INTEGER,
                result TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player TEXT,
                move INTEGER
            )
        ''')
        self.conn.commit()

    def add_player(self, player: Player):
        """Ajoute un joueur à la base."""
        self.cursor.execute('''
            INSERT OR REPLACE INTO players (pseudo, ip, port, join_date)
            VALUES (?, ?, ?, ?)
        ''', (player.pseudo, player.ip, player.port, player.join_date.isoformat()))
        self.conn.commit()

    def add_match(self, match: Match) -> int:
        """Ajoute un match à la base et retourne son ID."""
        self.cursor.execute('''
            INSERT INTO matches (player1, player2, board, is_finished, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (match.player1.pseudo, match.player2.pseudo, str(match.board), int(match.is_finished), match.result))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_match(self, match: Match):
        """Met à jour un match existant."""
        self.cursor.execute('''
            UPDATE matches
            SET board = ?, is_finished = ?, result = ?
            WHERE id = ?
        ''', (str(match.board), int(match.is_finished), match.result, match.id))
        self.conn.commit()

    def add_turn(self, turn: Turn):
        """Ajoute un tour à la base."""
        self.cursor.execute('''
            INSERT INTO turns (match_id, player, move)
            VALUES (?, ?, ?)
        ''', (turn.match_id, turn.player.pseudo, turn.move))
        self.conn.commit()

    def close(self):
        """Ferme la connexion à la base."""
        self.conn.close()