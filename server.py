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
        # Nombre de joueurs connectés
        self.connected_label = tk.Label(self.root, text="Joueurs connectés: 0")
        self.connected_label.pack(pady=5)

        # Nombre de joueurs en file d'attente
        self.queue_label = tk.Label(self.root, text="Joueurs en file: 0")
        self.queue_label.pack(pady=5)

        # Matchs en cours
        tk.Label(self.root, text="Matchs en cours:").pack(pady=5)
        self.matches_frame = tk.Frame(self.root)
        self.matches_frame.pack(fill="both", expand=True)
        self.matches_labels = {}  # Stocke les labels des matchs pour mise à jour

        # Historique des matchs terminés
        tk.Label(self.root, text="Historique des matchs terminés:").pack(pady=5)
        self.history_tree = ttk.Treeview(self.root, columns=("ID", "Player1", "Player2", "Result"), show="headings")
        self.history_tree.heading("ID", text="ID Match")
        self.history_tree.heading("Player1", text="Joueur 1")
        self.history_tree.heading("Player2", text="Joueur 2")
        self.history_tree.heading("Result", text="Résultat")
        self.history_tree.pack(fill="both", expand=True)

        # Bouton pour actualiser l'historique
        tk.Button(self.root, text="Rafraîchir l'historique", command=self.update_history).pack(pady=5)

        # Lancer la mise à jour périodique
        self.update_monitoring_ui()

    def update_monitoring_ui(self):
        """Met à jour l'interface de monitoring."""
        # Mise à jour des joueurs connectés
        with self.lock:
            self.connected_label.config(text=f"Joueurs connectés: {len(self.clients)}")
            self.queue_label.config(text=f"Joueurs en file: {self.queue.qsize()}")

            # Mise à jour des matchs en cours
            for widget in self.matches_frame.winfo_children():
                widget.destroy()
            self.matches_labels.clear()
            for match_id, (match, game) in self.matches.items():
                board_str = "\n".join([f"{game.board[0:3]}", f"{game.board[3:6]}", f"{game.board[6:9]}"])
                label_text = f"Match {match_id}: {match.player1.pseudo} vs {match.player2.pseudo}\nPlateau:\n{board_str}\nStatut: {'Terminé' if match.is_finished else 'En cours'}"
                label = tk.Label(self.matches_frame, text=label_text, justify="left", font=("Courier", 10))
                label.pack(anchor="w", pady=2)
                self.matches_labels[match_id] = label

        # Planifier la prochaine mise à jour
        self.root.after(1000, self.update_monitoring_ui)

    def update_history(self):
        """Met à jour l'historique des matchs terminés."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.db.cursor.execute("SELECT id, player1, player2, result FROM matches WHERE is_finished = 1")
        for row in self.db.cursor.fetchall():
            self.history_tree.insert("", "end", values=row)

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
            # Supprimer le client de la liste s'il se déconnecte
            for pseudo, socket in list(self.clients.items()):
                if socket == client_socket:
                    with self.lock:
                        del self.clients[pseudo]
                    break
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
        """Démarre le serveur et l'interface graphique."""
        # Lancer le thread du serveur
        threading.Thread(target=self.run_server, daemon=True).start()
        # Lancer l'interface graphique
        self.root.mainloop()
        # Fermer proprement à la fermeture de l'interface
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