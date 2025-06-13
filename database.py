import sqlite3
import json
from models import Player, Match, Turn, MastermindMatch
from datetime import datetime

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
                result TEXT,
                game_type TEXT DEFAULT 'morpion'
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player TEXT,
                move TEXT,
                feedback TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mastermind_matches (
                match_id INTEGER PRIMARY KEY,
                player1_code TEXT,
                player2_code TEXT,
                player1_guesses TEXT,
                player2_guesses TEXT,
                player1_feedback TEXT,
                player2_feedback TEXT,
                max_attempts INTEGER DEFAULT 10,
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
            self.update_player(player)

    def update_player(self, player: Player):
        self.cursor.execute('''
            UPDATE players SET ip = ?, port = ?, join_date = ?
            WHERE pseudo = ?
        ''', (player.ip, player.port, player.join_date.isoformat(), player.pseudo))
        self.conn.commit()

    def add_match(self, match: Match) -> int:
        self.cursor.execute('''
            INSERT INTO matches (player1, player2, board, is_finished, result, game_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match.player1.pseudo, match.player2.pseudo, str(match.board), int(match.is_finished), match.result, match.game_type))
        self.conn.commit()
        match_id = self.cursor.lastrowid
        
        # Si c'est un match de Mastermind, ajouter les données spécifiques
        if match.game_type == "mastermind" and isinstance(match, MastermindMatch):
            self.add_mastermind_match(match, match_id)
            
        return match_id

    def add_mastermind_match(self, match: MastermindMatch, match_id: int):
        self.cursor.execute('''
            INSERT INTO mastermind_matches (
                match_id, player1_code, player2_code, 
                player1_guesses, player2_guesses, 
                player1_feedback, player2_feedback, max_attempts
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            json.dumps(match.player1_code),
            json.dumps(match.player2_code),
            json.dumps(match.player1_guesses),
            json.dumps(match.player2_guesses),
            json.dumps(match.player1_feedback),
            json.dumps(match.player2_feedback),
            match.max_attempts
        ))
        self.conn.commit()

    def update_match(self, match: Match):
        self.cursor.execute('''
            UPDATE matches SET board = ?, is_finished = ?, result = ? WHERE id = ?
        ''', (str(match.board), int(match.is_finished), match.result, match.id))
        self.conn.commit()
        
        # Si c'est un match de Mastermind, mettre à jour les données spécifiques
        if match.game_type == "mastermind" and isinstance(match, MastermindMatch):
            self.update_mastermind_match(match)

    def update_mastermind_match(self, match: MastermindMatch):
        self.cursor.execute('''
            UPDATE mastermind_matches SET 
                player1_guesses = ?, player2_guesses = ?,
                player1_feedback = ?, player2_feedback = ?
            WHERE match_id = ?
        ''', (
            json.dumps(match.player1_guesses),
            json.dumps(match.player2_guesses),
            json.dumps(match.player1_feedback),
            json.dumps(match.player2_feedback),
            match.id
        ))
        self.conn.commit()

    def add_turn(self, turn: Turn):
        move_data = json.dumps(turn.move) if isinstance(turn.move, list) else str(turn.move)
        feedback_data = json.dumps(turn.feedback) if turn.feedback else None
        
        self.cursor.execute('''
            INSERT INTO turns (match_id, player, move, feedback)
            VALUES (?, ?, ?, ?)
        ''', (turn.match_id, turn.player.pseudo, move_data, feedback_data))
        self.conn.commit()

    def get_match(self, match_id: int) -> Match:
        """Récupère un match par son ID."""
        self.cursor.execute('''
            SELECT id, player1, player2, board, is_finished, result, game_type
            FROM matches WHERE id = ?
        ''', (match_id,))
        match_data = self.cursor.fetchone()
        
        if not match_data:
            return None
            
        player1 = self.get_player(match_data[1])
        player2 = self.get_player(match_data[2])
        
        if match_data[6] == "mastermind":
            self.cursor.execute('''
                SELECT player1_code, player2_code, player1_guesses, player2_guesses,
                       player1_feedback, player2_feedback, max_attempts
                FROM mastermind_matches WHERE match_id = ?
            ''', (match_id,))
            mm_data = self.cursor.fetchone()
            
            if mm_data:
                return MastermindMatch(
                    id=match_data[0],
                    player1=player1,
                    player2=player2,
                    board=[],
                    is_finished=bool(match_data[4]),
                    result=match_data[5],
                    game_type="mastermind",
                    player1_code=json.loads(mm_data[0]),
                    player2_code=json.loads(mm_data[1]),
                    player1_guesses=json.loads(mm_data[2]),
                    player2_guesses=json.loads(mm_data[3]),
                    player1_feedback=json.loads(mm_data[4]),
                    player2_feedback=json.loads(mm_data[5]),
                    max_attempts=mm_data[6]
                )
        
        return Match(
            id=match_data[0],
            player1=player1,
            player2=player2,
            board=eval(match_data[3]),
            is_finished=bool(match_data[4]),
            result=match_data[5],
            game_type=match_data[6]
        )

    def get_player(self, pseudo: str) -> Player:
        """Récupère un joueur par son pseudo."""
        self.cursor.execute('''
            SELECT pseudo, ip, port, join_date FROM players WHERE pseudo = ?
        ''', (pseudo,))
        player_data = self.cursor.fetchone()
        
        if not player_data:
            return None
            
        return Player(
            pseudo=player_data[0],
            ip=player_data[1],
            port=player_data[2],
            join_date=datetime.fromisoformat(player_data[3])
        )

    def close(self):
        self.conn.close()

print("Database mis à jour avec succès!")
