import sqlite3
from models import Player, Match, Turn

class Database:
    def __init__(self, db_name="matchmaking.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
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
                move INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')
        self.conn.commit()

    def add_player(self, player: Player):
        try:
            self.cursor.execute('''
                INSERT INTO players (pseudo, ip, port, join_date)
                VALUES (?, ?, ?, ?)
            ''', (player.pseudo, player.ip, player.port, player.join_date.isoformat()))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # If pseudo already exists, update the record
            self.update_player(player)

    def update_player(self, player: Player):
        self.cursor.execute('''
            UPDATE players SET ip = ?, port = ?, join_date = ?
            WHERE pseudo = ?
        ''', (player.ip, player.port, player.join_date.isoformat(), player.pseudo))
        self.conn.commit()

    def add_match(self, match: Match) -> int:
        self.cursor.execute('''
            INSERT INTO matches (player1, player2, board, is_finished, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (match.player1.pseudo, match.player2.pseudo, str(match.board), int(match.is_finished), match.result))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_match(self, match: Match):
        self.cursor.execute('''
            UPDATE matches SET board = ?, is_finished = ?, result = ? WHERE id = ?
        ''', (str(match.board), int(match.is_finished), match.result, match.id))
        self.conn.commit()

    def add_turn(self, turn: Turn):
        self.cursor.execute('''
            INSERT INTO turns (match_id, player, move)
            VALUES (?, ?, ?)
        ''', (turn.match_id, turn.player.pseudo, turn.move))
        self.conn.commit()

    def close(self):
        self.conn.close()