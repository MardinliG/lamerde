import socket
import threading
import json
from queue import Queue
from models import Player, Match, Turn, TicTacToe, MastermindMatch, Mastermind
from database import Database
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class MatchmakingServer:
    """Serveur de matchmaking pour les jeux Morpion et Mastermind avec interface de monitoring."""
    def __init__(self, host="localhost", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.morpion_queue = Queue()  # File d'attente des joueurs pour Morpion
        self.mastermind_queue = Queue()  # File d'attente des joueurs pour Mastermind
        self.matches = {}     # Dictionnaire match_id -> (Match, Game)
        self.clients = {}     # Dictionnaire pseudo -> socket
        self.mastermind_codes = {}  # Dictionnaire pseudo -> code secret pour Mastermind
        self.db = Database()
        self.lock = threading.Lock()
        print(f"Serveur démarré sur {host}:{port}")

        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Monitoring du Serveur de Jeux")
        self.setup_monitoring_ui()

    def setup_monitoring_ui(self):
        """Configure l'interface de monitoring."""
        # Créer un notebook (onglets)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)
        
        # Onglet général
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="Général")
        
        self.connected_label = tk.Label(general_tab, text="Joueurs connectés: 0")
        self.connected_label.pack(pady=5)

        self.morpion_queue_label = tk.Label(general_tab, text="Joueurs en file Morpion: 0")
        self.morpion_queue_label.pack(pady=5)
        
        self.mastermind_queue_label = tk.Label(general_tab, text="Joueurs en file Mastermind: 0")
        self.mastermind_queue_label.pack(pady=5)

        # Onglet Morpion
        morpion_tab = ttk.Frame(notebook)
        notebook.add(morpion_tab, text="Morpion")
        
        tk.Label(morpion_tab, text="Matchs de Morpion en cours:").pack(pady=5)
        self.morpion_matches_frame = tk.Frame(morpion_tab)
        self.morpion_matches_frame.pack(fill="both", expand=True)
        
        # Onglet Mastermind
        mastermind_tab = ttk.Frame(notebook)
        notebook.add(mastermind_tab, text="Mastermind")
        
        tk.Label(mastermind_tab, text="Matchs de Mastermind en cours:").pack(pady=5)
        self.mastermind_matches_frame = tk.Frame(mastermind_tab)
        self.mastermind_matches_frame.pack(fill="both", expand=True)

        # Onglet Historique
        history_tab = ttk.Frame(notebook)
        notebook.add(history_tab, text="Historique")
        
        tk.Label(history_tab, text="Historique des matchs terminés:").pack(pady=5)
        self.history_tree = ttk.Treeview(history_tab, columns=("ID", "Game", "Player1", "Player2", "Result"), show="headings")
        self.history_tree.heading("ID", text="ID Match")
        self.history_tree.heading("Game", text="Jeu")
        self.history_tree.heading("Player1", text="Joueur 1")
        self.history_tree.heading("Player2", text="Joueur 2")
        self.history_tree.heading("Result", text="Résultat")
        self.history_tree.pack(fill="both", expand=True)

        # Onglet Connexions
        connections_tab = ttk.Frame(notebook)
        notebook.add(connections_tab, text="Connexions")
        
        tk.Label(connections_tab, text="Historique des connexions:").pack(pady=5)
        self.connection_tree = ttk.Treeview(connections_tab, columns=("Pseudo", "IP", "Port", "JoinDate"), show="headings")
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
            self.morpion_queue_label.config(text=f"Joueurs en file Morpion: {self.morpion_queue.qsize()}")
            self.mastermind_queue_label.config(text=f"Joueurs en file Mastermind: {self.mastermind_queue.qsize()}")

            # Mise à jour des matchs de Morpion
            for widget in self.morpion_matches_frame.winfo_children():
                widget.destroy()
                
            # Mise à jour des matchs de Mastermind
            for widget in self.mastermind_matches_frame.winfo_children():
                widget.destroy()
                
            for match_id, (match, game) in self.matches.items():
                if match.game_type == "morpion":
                    board_str = "\n".join([f"{game.board[0:3]}", f"{game.board[3:6]}", f"{game.board[6:9]}"])
                    label_text = f"Match {match_id}: {match.player1.pseudo} vs {match.player2.pseudo}\nPlateau:\n{board_str}\nStatut: {'Terminé' if match.is_finished else 'En cours'}"
                    label = tk.Label(self.morpion_matches_frame, text=label_text, justify="left", font=("Courier", 10))
                    label.pack(anchor="w", pady=2)
                elif match.game_type == "mastermind":
                    p1_guesses = len(match.player1_guesses)
                    p2_guesses = len(match.player2_guesses)
                    label_text = f"Match {match_id}: {match.player1.pseudo} vs {match.player2.pseudo}\n"
                    label_text += f"Tentatives: {match.player1.pseudo}: {p1_guesses}, {match.player2.pseudo}: {p2_guesses}\n"
                    label_text += f"Statut: {'Terminé' if match.is_finished else 'En cours'}"
                    label = tk.Label(self.mastermind_matches_frame, text=label_text, justify="left", font=("Courier", 10))
                    label.pack(anchor="w", pady=2)

        self.root.after(1000, self.update_monitoring_ui)

    def update_history(self):
        """Met à jour l'historique des matchs et connexions terminés."""
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Vérifier si la colonne game_type existe
            self.db.cursor.execute("PRAGMA table_info(matches)")
            columns = [column[1] for column in self.db.cursor.fetchall()]
            
            if 'game_type' in columns:
                # Nouvelle version avec game_type
                self.db.cursor.execute("SELECT id, game_type, player1, player2, result FROM matches WHERE is_finished = 1")
            else:
                # Ancienne version sans game_type
                self.db.cursor.execute("SELECT id, 'morpion' as game_type, player1, player2, result FROM matches WHERE is_finished = 1")
            
            for row in self.db.cursor.fetchall():
                self.history_tree.insert("", "end", values=row)

            for item in self.connection_tree.get_children():
                self.connection_tree.delete(item)
            self.db.cursor.execute("SELECT pseudo, ip, port, join_date FROM players")
            for row in self.db.cursor.fetchall():
                self.connection_tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'historique: {e}")

    def handle_client(self, client_socket, address):
        """Gère la communication avec un client."""
        pseudo = None
        game_type = "morpion"  # Par défaut
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message.get("action")

                if action == "CONNECT":
                    pseudo = message["pseudo"]
                    game_type = message.get("game", "morpion")  # Type de jeu (morpion ou mastermind)
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
                        self.morpion_queue.put((player, client_socket))
                    self.check_morpion_queue()
                elif action == "JOIN_MASTERMIND":
                    if not pseudo:
                        continue
                    player = Player(pseudo, address[0], address[1], datetime.now())
                    code = message.get("code", [])
                    with self.lock:
                        self.db.update_player(player)
                        self.mastermind_codes[pseudo] = code
                        self.mastermind_queue.put((player, client_socket))
                    self.check_mastermind_queue()
                elif action == "LEAVE":
                    if not pseudo:
                        continue
                    with self.lock:
                        temp_queue = Queue()
                        removed = False
                        while not self.morpion_queue.empty():
                            player, socket = self.morpion_queue.get()
                            if player.pseudo != pseudo:
                                temp_queue.put((player, socket))
                            else:
                                removed = True
                                socket.send(json.dumps({"action": "LEFT_QUEUE"}).encode())
                        self.morpion_queue = temp_queue
                    self.check_morpion_queue()
                elif action == "LEAVE_MASTERMIND":
                    if not pseudo:
                        continue
                    with self.lock:
                        temp_queue = Queue()
                        removed = False
                        while not self.mastermind_queue.empty():
                            player, socket = self.mastermind_queue.get()
                            if player.pseudo != pseudo:
                                temp_queue.put((player, socket))
                            else:
                                removed = True
                                socket.send(json.dumps({"action": "LEFT_QUEUE"}).encode())
                        self.mastermind_queue = temp_queue
                        if pseudo in self.mastermind_codes:
                            del self.mastermind_codes[pseudo]
                elif action == "MOVE":
                    if not pseudo:
                        continue
                    self.handle_morpion_move(pseudo, message["match_id"], message["position"])
                elif action == "MASTERMIND_GUESS":
                    if not pseudo:
                        continue
                    self.handle_mastermind_guess(pseudo, message["match_id"], message["guess"])

        except Exception as e:
            print(f"Erreur avec client {address}: {e}")
        finally:
            self.handle_disconnect(pseudo, client_socket)

    def handle_disconnect(self, pseudo, client_socket):
        """Gère la déconnexion d'un client."""
        with self.lock:
            if pseudo and pseudo in self.clients:
                del self.clients[pseudo]
                if pseudo in self.mastermind_codes:
                    del self.mastermind_codes[pseudo]

            # Nettoyer la file d'attente Morpion
            temp_queue = Queue()
            while not self.morpion_queue.empty():
                player, socket = self.morpion_queue.get()
                if socket != client_socket:
                    temp_queue.put((player, socket))
            self.morpion_queue = temp_queue
            
            # Nettoyer la file d'attente Mastermind
            temp_queue = Queue()
            while not self.mastermind_queue.empty():
                player, socket = self.mastermind_queue.get()
                if socket != client_socket:
                    temp_queue.put((player, socket))
            self.mastermind_queue = temp_queue

            # Gérer les matchs en cours
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

    def check_morpion_queue(self):
        """Vérifie la file d'attente pour créer des matchs de Morpion."""
        with self.lock:
            if self.morpion_queue.qsize() >= 2:
                player1, socket1 = self.morpion_queue.get()
                player2, socket2 = self.morpion_queue.get()
                game = TicTacToe()
                match = Match(id=0, player1=player1, player2=player2, board=game.board, is_finished=False, result=None, game_type="morpion")
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

    def check_mastermind_queue(self):
        """Vérifie la file d'attente pour créer des matchs de Mastermind."""
        with self.lock:
            if self.mastermind_queue.qsize() >= 2:
                player1, socket1 = self.mastermind_queue.get()
                player2, socket2 = self.mastermind_queue.get()
                
                # Récupérer les codes secrets
                player1_code = self.mastermind_codes.get(player1.pseudo, [])
                player2_code = self.mastermind_codes.get(player2.pseudo, [])
                
                # Créer le match de Mastermind
                game = Mastermind()
                match = MastermindMatch(
                    id=0, 
                    player1=player1, 
                    player2=player2, 
                    board=[], 
                    is_finished=False, 
                    result=None,
                    player1_code=player1_code,
                    player2_code=player2_code
                )
                match.id = self.db.add_match(match)
                self.matches[match.id] = (match, game)

                # Envoyer les messages de début de partie
                start_message1 = json.dumps({
                    "action": "MASTERMIND_START",
                    "opponent": player2.pseudo,
                    "match_id": match.id
                })
                socket1.send(start_message1.encode())
                
                start_message2 = json.dumps({
                    "action": "MASTERMIND_START",
                    "opponent": player1.pseudo,
                    "match_id": match.id
                })
                socket2.send(start_message2.encode())
                
                # Nettoyer les codes stockés
                if player1.pseudo in self.mastermind_codes:
                    del self.mastermind_codes[player1.pseudo]
                if player2.pseudo in self.mastermind_codes:
                    del self.mastermind_codes[player2.pseudo]

    def handle_morpion_move(self, pseudo: str, match_id: int, position: int):
        """Gère un coup joué par un joueur au Morpion."""
        with self.lock:
            if match_id not in self.matches:
                print(f"Match {match_id} not found for {pseudo}")
                return
            match, game = self.matches[match_id]
            if match.game_type != "morpion":
                print(f"Match {match_id} is not a Morpion game")
                return
                
            player = match.player1 if pseudo == match.player1.pseudo else match.player2
            opponent = match.player2 if pseudo == match.player1.pseudo else match.player1
            symbol = "X" if pseudo == match.player1.pseudo else "O"

            print(f"Processing move: {pseudo} plays {symbol} at position {position}")
            if game.play_move(position, symbol):
                turn = Turn(match_id, player, position)
                self.db.add_turn(turn)
                match.board = game.board
                self.db.update_match(match)

                move_message = json.dumps({
                    "action": "MOVE",
                    "position": position,
                    "symbol": symbol
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

    def handle_mastermind_guess(self, pseudo: str, match_id: int, guess: list):
        """Gère une tentative de devinette au Mastermind."""
        with self.lock:
            if match_id not in self.matches:
                print(f"Match {match_id} not found for {pseudo}")
                return
            match, game = self.matches[match_id]
            if match.game_type != "mastermind" or not isinstance(match, MastermindMatch):
                print(f"Match {match_id} is not a Mastermind game")
                return
                
            # Déterminer si c'est le joueur 1 ou 2
            is_player1 = (pseudo == match.player1.pseudo)
            player = match.player1 if is_player1 else match.player2
            opponent = match.player2 if is_player1 else match.player1
            
            # Récupérer le code à deviner (code de l'adversaire)
            code_to_guess = match.player2_code if is_player1 else match.player1_code
            
            # Vérifier la tentative
            black_pins, white_pins = game.check_guess(code_to_guess, guess)
            feedback = (black_pins, white_pins)
            
            # Enregistrer la tentative et le feedback
            if is_player1:
                match.player1_guesses.append(guess)
                match.player1_feedback.append(feedback)
            else:
                match.player2_guesses.append(guess)
                match.player2_feedback.append(feedback)
                
            # Enregistrer le tour dans la base de données
            turn = Turn(match_id, player, guess, feedback)
            self.db.add_turn(turn)
            self.db.update_mastermind_match(match)
            
            # Envoyer le feedback au joueur
            guess_feedback_message = json.dumps({
                "action": "MASTERMIND_FEEDBACK",
                "black_pins": black_pins,
                "white_pins": white_pins,
                "guess_number": len(match.player1_guesses) if is_player1 else len(match.player2_guesses)
            })
            self.clients[pseudo].send(guess_feedback_message.encode())
            
            # Informer l'adversaire de la tentative
            opponent_message = json.dumps({
                "action": "MASTERMIND_OPPONENT_GUESS",
                "guess": guess,
                "black_pins": black_pins,
                "white_pins": white_pins,
                "guess_number": len(match.player1_guesses) if is_player1 else len(match.player2_guesses)
            })
            self.clients[opponent.pseudo].send(opponent_message.encode())
            
            # Vérifier si le joueur a trouvé le code
            has_won = (black_pins == len(code_to_guess))
            
            # Vérifier si le match est terminé
            match_ended = False
            result = None
            
            if has_won:
                # Le joueur a trouvé le code
                match_ended = True
                result = pseudo
            elif (is_player1 and len(match.player1_guesses) >= match.max_attempts) or \
                 (not is_player1 and len(match.player2_guesses) >= match.max_attempts):
                # Le joueur a atteint le nombre maximum de tentatives
                if is_player1 and len(match.player2_guesses) >= match.max_attempts:
                    # Les deux joueurs ont atteint le max de tentatives
                    match_ended = True
                    result = "draw"
                elif not is_player1 and len(match.player1_guesses) >= match.max_attempts:
                    # Les deux joueurs ont atteint le max de tentatives
                    match_ended = True
                    result = "draw"
            
            if match_ended:
                match.is_finished = True
                match.result = result
                self.db.update_match(match)
                
                end_message = json.dumps({
                    "action": "MASTERMIND_END",
                    "result": result,
                    "player1_code": match.player1_code,
                    "player2_code": match.player2_code
                })
                
                try:
                    self.clients[match.player1.pseudo].send(end_message.encode())
                    self.clients[match.player2.pseudo].send(end_message.encode())
                    print(f"Sent end message to {match.player1.pseudo} and {match.player2.pseudo}")
                except Exception as e:
                    print(f"Failed to send end message: {e}")
                
                del self.matches[match_id]

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

print("Server corrigé avec succès!")
