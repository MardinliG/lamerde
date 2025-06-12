import socket
import threading
import json
from queue import Queue
from models import Player, Match, Turn, TicTacToe
from database import Database
from datetime import datetime

class MatchmakingServer:
    """Serveur de matchmaking pour le jeu Morpion."""
    def __init__(self, host="localhost", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.queue = Queue()  # File d'attente des joueurs
        self.matches = {}     # Dictionnaire match_id -> Match
        self.clients = {}     # Dictionnaire pseudo -> socket
        self.db = Database()
        self.lock = threading.Lock()
        print(f"Serveur démarré sur {host}:{port}")

    def handle_client(self, client_socket, address):
        """Gère la communication avec un client."""
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message.get("action")

                if action == "JOIN":
                    pseudo = message["pseudo"]
                    player = Player(pseudo, address[0], address[1], datetime.now())
                    with self.lock:
                        self.db.add_player(player)
                        self.queue.put((player, client_socket))
                        self.clients[pseudo] = client_socket
                    self.check_queue()
                elif action == "MOVE":
                    self.handle_move(message["pseudo"], message["match_id"], message["position"])

        except Exception as e:
            print(f"Erreur avec client {address}: {e}")
        finally:
            client_socket.close()

    def check_queue(self):
        """Vérifie la file d'attente pour créer des matchs."""
        with self.lock:
            if self.queue.qsize() >= 2:
                player1, socket1 = self.queue.get()
                player2, socket2 = self.queue.get()
                game = TicTacToe()
                match = Match(id=0, player1=player1, player2=player2, board=game.board, is_finished=False, result=None)
                match.id = self.db.add_match(match)
                self.matches[match.id] = (match, game)

                # Notifier les joueurs du début du match
                start_message = json.dumps({
                    "action": "START",
                    "opponent": player2.pseudo,
                    "match_id": match.id,
                    "symbol": "X"
                })
                socket1.send(start_message.encode())
                start_message = json.dumps({
                    "action": "START",
                    "opponent": player1.pseudo,
                    "match_id": match.id,
                    "symbol": "O"
                })
                socket2.send(start_message.encode())

    def handle_move(self, pseudo: str, match_id: int, position: int):
        """Gère un coup joué par un joueur."""
        with self.lock:
            if match_id not in self.matches:
                return
            match, game = self.matches[match_id]
            player = match.player1 if pseudo == match.player1.pseudo else match.player2
            opponent = match.player2 if pseudo == match.player1.pseudo else match.player1
            symbol = "X" if pseudo == match.player1.pseudo else "O"

            if game.play_move(position, symbol):
                turn = Turn(match_id, player, position)
                self.db.add_turn(turn)
                match.board = game.board
                self.db.update_match(match)

                # Envoyer le coup à l'adversaire
                move_message = json.dumps({
                    "action": "MOVE",
                    "position": position,
                    "symbol": symbol
                })
                self.clients[opponent.pseudo].send(move_message.encode())

                # Vérifier si le match est terminé
                result = game.check_winner()
                if result:
                    match.is_finished = True
                    if result == "X":
                        match.result = match.player1.pseudo
                    elif result == "O":
                        match.result = match.player2.pseudo
                    else:
                        match.result = "draw"
                    self.db.update_match(match)

                    # Notifier les joueurs de la fin
                    end_message = json.dumps({
                        "action": "END",
                        "result": match.result
                    })
                    self.clients[match.player1.pseudo].send(end_message.encode())
                    self.clients[match.player2.pseudo].send(end_message.encode())
                    del self.matches[match_id]

    def run(self):
        """Démarre le serveur."""
        try:
            while True:
                client, address = self.server.accept()
                print(f"Nouveau client connecté: {address}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        finally:
            self.db.close()
            self.server.close()

if __name__ == "__main__":
    server = MatchmakingServer()
    server.run()