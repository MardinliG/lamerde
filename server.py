import socket
import threading
import json
from queue import Queue
from models import Player, Match, Turn, TicTacToe
from database import Database
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class MatchmakingServer:
    """Serveur de matchmaking pour le jeu Morpion avec interface de monitoring."""
    def __init__(self, host="localhost", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.queue = Queue()  # File d'attente des joueurs
        self.matches = {}     # Dictionnaire match_id -> (Match, TicTacToe)
        self.clients = {}     # Dictionnaire pseudo -> socket
        self.db = Database()
        self.lock = threading.Lock()
        print(f"Serveur démarré sur {host}:{port}")

        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Monitoring du Serveur Morpion")
        self.setup_monitoring_ui()

    def setup_monitoring_ui(self):
        """Configure l'interface de monitoring."""
        self.connected_label = tk.Label(self.root, text="Joueurs connectés: 0")
        self.connected_label.pack(pady=5)

        self.queue_label = tk.Label(self.root, text="Joueurs en file: 0")
        self.queue_label.pack(pady=5)

        tk.Label(self.root, text="Matchs en cours:").pack(pady=5)
        self.matches_frame = tk.Frame(self.root)
        self.matches_frame.pack(fill="both", expand=True)
        self.matches_labels = {}

        tk.Label(self.root, text="Historique des matchs terminés:").pack(pady=5)
        self.history_tree = ttk.Treeview(self.root, columns=("ID", "Player1", "Player2", "Result"), show="headings")
        self.history_tree.heading("ID", text="ID Match")
        self.history_tree.heading("Player1", text="Joueur 1")
        self.history_tree.heading("Player2", text="Joueur 2")
        self.history_tree.heading("Result", text="Résultat")
        self.history_tree.pack(fill="both", expand=True)

        tk.Label(self.root, text="Historique des connexions:").pack(pady=5)
        self.connection_tree = ttk.Treeview(self.root, columns=("Pseudo", "IP", "Port", "JoinDate"), show="headings")
        self.connection_tree.heading("Pseudo", text="Pseudo")
        self.connection_tree.heading("IP", text="IP")
        self.connection_tree.heading("Port", text="Port")
        self.connection_tree.heading("JoinDate", text="Date de connexion")
        self.connection_tree.pack(fill="both", expand=True)

        tk.Button(self.root, text="Rafraîchir l'historique", command=self.update_history).pack(pady=5)
        self.update_monitoring_ui()

    def update_monitoring_ui(self):
        """Met à jour l'interface de monitoring."""
        with self.lock:
            self.connected_label.config(text=f"Joueurs connectés: {len(self.clients)}")
            self.queue_label.config(text=f"Joueurs en file: {self.queue.qsize()}")

            for widget in self.matches_frame.winfo_children():
                widget.destroy()
            self.matches_labels.clear()
            for match_id, (match, game) in self.matches.items():
                board_str = "\n".join([f"{game.board[0:3]}", f"{game.board[3:6]}", f"{game.board[6:9]}"])
                label_text = f"Match {match_id}: {match.player1.pseudo} vs {match.player2.pseudo}\nPlateau:\n{board_str}\nStatut: {'Terminé' if match.is_finished else 'En cours'}"
                label = tk.Label(self.matches_frame, text=label_text, justify="left", font=("Courier", 10))
                label.pack(anchor="w", pady=2)
                self.matches_labels[match_id] = label

        self.root.after(1000, self.update_monitoring_ui)

    def update_history(self):
        """Met à jour l'historique des matchs et connexions terminés."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.db.cursor.execute("SELECT id, player1, player2, result FROM matches WHERE is_finished = 1")
        for row in self.db.cursor.fetchall():
            self.history_tree.insert("", "end", values=row)

        for item in self.connection_tree.get_children():
            self.connection_tree.delete(item)
        self.db.cursor.execute("SELECT pseudo, ip, port, join_date FROM players")
        for row in self.db.cursor.fetchall():
            self.connection_tree.insert("", "end", values=row)

    def handle_client(self, client_socket, address):
        """Gère la communication avec un client."""
        pseudo = None
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message.get("action")

                if action == "CONNECT":
                    pseudo = message["pseudo"]
                    with self.lock:
                        if pseudo in self.clients:
                            client_socket.send(json.dumps({
                                "action": "CONNECT",
                                "status": "ERROR",
                                "message": "Pseudo déjà pris."
                            }).encode())
                            continue
                        player = Player(pseudo, address[0], address[1], datetime.now())
                        self.clients[pseudo] = client_socket
                        self.db.add_player(player)
                        client_socket.send(json.dumps({
                            "action": "CONNECT",
                            "status": "OK"
                        }).encode())
                elif action == "JOIN":
                    if not pseudo:
                        continue
                    player = Player(pseudo, address[0], address[1], datetime.now())
                    with self.lock:
                        self.db.update_player(player)
                        self.queue.put((player, client_socket))
                    self.check_queue()
                elif action == "LEAVE":
                    if not pseudo:
                        continue
                    with self.lock:
                        temp_queue = Queue()
                        removed = False
                        while not self.queue.empty():
                            player, socket = self.queue.get()
                            if player.pseudo != pseudo:
                                temp_queue.put((player, socket))
                            else:
                                removed = True
                                socket.send(json.dumps({"action": "LEFT_QUEUE"}).encode())
                        self.queue = temp_queue
                    self.check_queue()
                elif action == "MOVE":
                    if not pseudo:
                        continue
                    self.handle_move(pseudo, message["match_id"], message["position"])

        except Exception as e:
            print(f"Erreur avec client {address}: {e}")
        finally:
            self.handle_disconnect(pseudo, client_socket)

    def handle_disconnect(self, pseudo, client_socket):
        """Gère la déconnexion d'un client."""
        with self.lock:
            if pseudo and pseudo in self.clients:
                del self.clients[pseudo]

            temp_queue = Queue()
            while not self.queue.empty():
                player, socket = self.queue.get()
                if socket != client_socket:
                    temp_queue.put((player, socket))
            self.queue = temp_queue

            for match_id, (match, game) in list(self.matches.items()):
                opponent_pseudo = None
                if match.player1.pseudo == pseudo:
                    opponent_pseudo = match.player2.pseudo
                elif match.player2.pseudo == pseudo:
                    opponent_pseudo = match.player1.pseudo

                if opponent_pseudo and opponent_pseudo in self.clients:
                    match.is_finished = True
                    match.result = "interrupted"
                    self.db.update_match(match)
                    try:
                        self.clients[opponent_pseudo].send(json.dumps({
                            "action": "MATCH_INTERRUPTED",
                            "message": f"Votre adversaire ({pseudo}) s'est déconnecté. Le match est annulé."
                        }).encode())
                    except:
                        pass
                    del self.matches[match_id]

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
                print(f"Match {match_id} not found for {pseudo}")
                return
            match, game = self.matches[match_id]
            player = match.player1 if pseudo == match.player1.pseudo else match.player2
            opponent = match.player2 if pseudo == match.player1.pseudo else match.player1
            symbol = "X" if pseudo == match.player1.pseudo else "O"

            print(f"Processing move: {pseudo} plays {symbol} at position {position}")
            if game.play_move(position, symbol):  # Fixed: Use symbol instead of pseudo
                turn = Turn(match_id, player, position)
                self.db.add_turn(turn)
                match.board = game.board
                self.db.update_match(match)

                move_message = json.dumps({
                    "action": "MOVE",
                    "position": position,
                    "symbol": symbol  # Fixed: Use defined symbol
                })
                try:
                    self.clients[opponent.pseudo].send(move_message.encode())
                    print(f"Sent move to {opponent.pseudo}: {move_message}")
                except Exception as e:
                    print(f"Failed to send move to {opponent.pseudo}: {e}")

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

                    end_message = json.dumps({
                        "action": "END",
                        "result": match.result
                    })
                    try:
                        self.clients[match.player1.pseudo].send(end_message.encode())
                        self.clients[match.player2.pseudo].send(end_message.encode())
                        print(f"Sent end message to {match.player1.pseudo} and {match.player2.pseudo}")
                    except Exception as e:
                        print(f"Failed to send end message: {e}")
                    del self.matches[match_id]
            else:
                print(f"Invalid move by {pseudo} at position {position}")

    def run(self):
        """Démarre le serveur et l'interface graphique."""
        threading.Thread(target=self.run_server, daemon=True).start()
        self.root.mainloop()
        self.db.close()
        self.server.close()

    def run_server(self):
        """Boucle principale du serveur."""
        try:
            while True:
                client, address = self.server.accept()
                print(f"Nouveau client connecté: {address}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        except Exception as e:
            print(f"Erreur serveur: {e}")

if __name__ == "__main__":
    server = MatchmakingServer()
    server.run()