"""
Module client pour le jeu Morpion.
Contient la classe principale MorpionClient qui gère la connexion au serveur
et l'interface utilisateur.
"""
import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk

from morpion.ui.main_menu_ui import setup_main_menu_ui
from morpion.ui.waiting_ui import setup_waiting_ui
from morpion.ui.game_ui import setup_game_ui
from morpion.ui.result_ui import setup_result_ui
from morpion.ui.stats_ui import setup_stats_ui
from morpion.config import Config

class MorpionClient:
    """Client pour jouer au Morpion en 1v1."""
    def __init__(self, pseudo, client_socket=None, parent_root=None, host="localhost", port=12345):
        # Si un socket client est fourni, l'utiliser, sinon en créer un nouveau
        if client_socket:
            self.client = client_socket
        else:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((host, port))
            except Exception as e:
                print(f"Erreur de connexion: {e}")
                messagebox.showerror("Erreur", f"Impossible de se connecter au serveur: {e}")
                return
            
        self.pseudo = pseudo
        self.parent_root = parent_root
        self.match_id = None
        self.opponent = None
        self.symbol = None
        self.is_my_turn = False
        self.in_queue = False
        
        # Statistiques du joueur
        self.stats = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }
        
        # Interface graphique
        if parent_root:
            self.root = tk.Toplevel(parent_root)
            self.root.protocol("WM_DELETE_WINDOW", self.return_to_main)
        else:
            self.root = tk.Tk()
            
        self.root.title("Morpion - Menu Principal")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Définir les couleurs et styles
        self.bg_color = Config.BG_COLOR
        self.accent_color = Config.ACCENT_COLOR
        self.text_color = Config.TEXT_COLOR
        self.button_color = Config.BUTTON_COLOR
        self.button_hover = Config.BUTTON_HOVER
        
        self.root.configure(bg=self.bg_color)
        
        # Créer un style pour les widgets
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), background=self.button_color)
        self.style.configure("TLabel", font=("Helvetica", 12), background=self.bg_color, foreground=self.text_color)
        self.style.configure("TFrame", background=self.bg_color)
        
        self.current_frame = None
        self.setup_main_menu()

    def setup_main_menu(self):
        """Configure le menu principal."""
        setup_main_menu_ui(self)
        # Lancer l'écoute du serveur
        threading.Thread(target=self.listen_server, daemon=True).start()

    def show_statistics(self):
        """Affiche les statistiques du joueur."""
        setup_stats_ui(self)

    def quit_game(self):
        """Quitte le jeu."""
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?"):
            self.return_to_main()

    def return_to_main(self):
        """Retourne au menu principal de l'application."""
        if self.parent_root:
            self.root.destroy()
            self.parent_root.deiconify()  # Réaffiche la fenêtre principale
        else:
            try:
                self.client.close()
            except:
                pass
            self.root.quit()

    def setup_waiting_ui(self):
        """Configure l'écran pour rejoindre ou quitter la file."""
        setup_waiting_ui(self)

    def join_queue(self):
        """Envoie une requête pour rejoindre la file d'attente."""
        if self.in_queue:
            return
        message = json.dumps({"action": "JOIN", "pseudo": self.pseudo})
        self.client.send(message.encode())
        self.in_queue = True
        self.status_label.config(text="Vous êtes dans la file d'attente...")
        self.join_button.config(state=tk.DISABLED)
        self.leave_button.config(state=tk.NORMAL)

    def leave_queue(self):
        """Envoie une requête pour quitter la file d'attente."""
        if not self.in_queue:
            return
        message = json.dumps({"action": "LEAVE", "pseudo": self.pseudo})
        self.client.send(message.encode())
        self.in_queue = False
        self.status_label.config(text="Vous avez quitté la file d'attente.")
        self.join_button.config(state=tk.NORMAL)
        self.leave_button.config(state=tk.DISABLED)

    def setup_game_ui(self):
        """Configure l'interface du jeu."""
        setup_game_ui(self)
        self.update_status()

    def play_move(self, position):
        """Joue un coup si c'est au tour du joueur."""
        if not self.is_my_turn or self.buttons[position]["text"] != " ":
            return
        self.buttons[position]["text"] = self.symbol
        self.buttons[position]["fg"] = "#4a6ea9" if self.symbol == "X" else "#d9534f"
        self.is_my_turn = False
        self.update_status()
        message = json.dumps({
            "action": "MOVE",
            "pseudo": self.pseudo,
            "match_id": self.match_id,
            "position": position
        })
        self.client.send(message.encode())

    def update_board(self, position, symbol):
        """Met à jour le plateau avec le coup de l'adversaire."""
        self.buttons[position]["text"] = symbol
        self.buttons[position]["fg"] = "#4a6ea9" if symbol == "X" else "#d9534f"

    def update_status(self):
        """Met à jour le message de statut."""
        if hasattr(self, 'status_label'):
            if self.is_my_turn:
                self.status_label.config(text="À votre tour !", fg="#5cb85c")
            elif self.in_queue:
                self.status_label.config(text="Vous êtes dans la file d'attente...", fg=self.text_color)
            else:
                if self.opponent:
                    self.status_label.config(text=f"Tour de {self.opponent}...", fg="#d9534f")
                else:
                    self.status_label.config(text="Vous n'êtes pas dans la file d'attente.", fg=self.text_color)

    def end_game(self, result):
        """Affiche le résultat du match."""
        # Mettre à jour les statistiques
        self.stats["games_played"] += 1
        if result == self.pseudo:
            self.stats["wins"] += 1
            message = "Vous avez gagné !"
            color = "#5cb85c"  # Vert
        elif result == "draw":
            self.stats["draws"] += 1
            message = "Match nul !"
            color = "#f0ad4e"  # Orange
        else:
            self.stats["losses"] += 1
            message = f"{self.opponent} a gagné !"
            color = "#d9534f"  # Rouge
            
        # Afficher le résultat
        setup_result_ui(self, message, color)
        
        # Réinitialiser les variables de jeu
        self.opponent = None
        self.match_id = None
        self.symbol = None
        self.is_my_turn = False

    def forfeit_game(self):
        """Abandonne la partie en cours."""
        if messagebox.askyesno("Abandonner", "Êtes-vous sûr de vouloir abandonner cette partie?"):
            # Ici vous pourriez envoyer un message au serveur pour signaler l'abandon
            self.setup_main_menu()

    def handle_match_interrupted(self, message):
        """Gère l'interruption du match due à une déconnexion."""
        messagebox.showinfo("Match annulé", message)
        self.opponent = None
        self.match_id = None
        self.symbol = None
        self.is_my_turn = False
        self.setup_main_menu()

    def listen_server(self):
        """Écoute les messages du serveur."""
        try:
            while True:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message["action"]

                if action == "CONNECT":
                    # Réponse déjà gérée dans validate_pseudo
                    pass
                elif action == "START":
                    self.opponent = message["opponent"]
                    self.match_id = message["match_id"]
                    self.symbol = message["symbol"]
                    self.is_my_turn = self.symbol == "X"
                    self.in_queue = False
                    self.root.after(0, self.setup_game_ui)
                    self.root.after(100, self.update_status)
                elif action == "MOVE":
                    position = message["position"]
                    symbol = message["symbol"]
                    self.root.after(0, self.update_board, position, symbol)
                    self.is_my_turn = True
                    self.root.after(0, self.update_status)
                elif action == "END":
                    result = message["result"]
                    self.root.after(0, self.end_game, result)
                elif action == "LEFT_QUEUE":
                    self.in_queue = False
                    self.root.after(0, lambda: self.status_label.config(text="Vous avez quitté la file d'attente."))
                    self.root.after(0, lambda: self.join_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.leave_button.config(state=tk.DISABLED))
                elif action == "MATCH_INTERRUPTED":
                    self.root.after(0, self.handle_match_interrupted, message["message"])

        except Exception as e:
            print(f"Erreur de connexion: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Connexion perdue."))
            self.return_to_main()

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
