import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox

class GameClient:
    """Client pour jouer au Morpion via le serveur de matchmaking."""
    def __init__(self, host="localhost", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.pseudo = None
        self.symbol = None
        self.match_id = None
        self.opponent = None
        self.current_turn = "X"  # X commence toujours
        self.is_my_turn = False
        self.in_queue = False  # Indique si le joueur est dans la file

        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Morpion - Connexion")
        self.current_frame = None
        self.setup_login_ui()

    def setup_login_ui(self):
        """Configure l'interface de connexion."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        tk.Label(self.current_frame, text="Pseudo:").pack()
        self.pseudo_entry = tk.Entry(self.current_frame)
        self.pseudo_entry.pack()
        tk.Button(self.current_frame, text="Valider", command=self.validate_pseudo).pack()

    def validate_pseudo(self):
        """Valide le pseudo et passe à l'écran d'attente."""
        pseudo = self.pseudo_entry.get().strip()
        if not pseudo:
            messagebox.showerror("Erreur", "Veuillez entrer un pseudo.")
            return
        self.pseudo = pseudo
        self.setup_waiting_ui()

    def setup_waiting_ui(self):
        """Configure l'écran pour rejoindre ou quitter la file."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()
        self.root.title(f"Morpion - {self.pseudo}")

        self.status_label = tk.Label(self.current_frame, text="Vous n'êtes pas dans la file d'attente.")
        self.status_label.pack(pady=5)
        self.join_button = tk.Button(self.current_frame, text="Rejoindre la file d'attente", command=self.join_queue)
        self.join_button.pack(pady=5)
        self.leave_button = tk.Button(self.current_frame, text="Quitter la file d'attente", command=self.leave_queue, state="disabled")
        self.leave_button.pack(pady=5)

        # Lancer l'écoute du serveur
        threading.Thread(target=self.listen_server, daemon=True).start()

    def setup_game_ui(self):
        """Configure l'interface du jeu."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        self.root.title(f"Morpion vs {self.opponent}")
        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.current_frame, text=" ", width=10, height=5, command=lambda x=i: self.play_move(x))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)
        self.status_label = tk.Label(self.current_frame, text="En attente de votre tour...")
        self.status_label.grid(row=3, column=0, columnspan=3)

    def join_queue(self):
        """Envoie une requête pour rejoindre la file d'attente."""
        if self.in_queue:
            return
        message = json.dumps({"action": "JOIN", "pseudo": self.pseudo})
        self.client.send(message.encode())
        self.in_queue = True
        self.status_label.config(text="Vous êtes dans la file d'attente...")
        self.join_button.config(state="disabled")
        self.leave_button.config(state="normal")

    def leave_queue(self):
        """Envoie une requête pour quitter la file d'attente."""
        if not self.in_queue:
            return
        message = json.dumps({"action": "LEAVE", "pseudo": self.pseudo})
        self.client.send(message.encode())
        self.in_queue = False
        self.status_label.config(text="Vous avez quitté la file d'attente.")
        self.join_button.config(state="normal")
        self.leave_button.config(state="disabled")

    def listen_server(self):
        """Écoute les messages du serveur."""
        try:
            while True:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message["action"]

                if action == "START":
                    self.opponent = message["opponent"]
                    self.match_id = message["match_id"]
                    self.symbol = message["symbol"]
                    self.is_my_turn = self.symbol == "X"
                    self.in_queue = False  # Sortir de la file
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
                    self.root.after(0, lambda: self.join_button.config(state="normal"))
                    self.root.after(0, lambda: self.leave_button.config(state="disabled"))

        except Exception as e:
            print(f"Erreur de connexion: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Connexion perdue."))
            self.client.close()

    def play_move(self, position):
        """Joue un coup si c'est au tour du joueur."""
        if not self.is_my_turn or self.buttons[position]["text"] != " ":
            return
        self.buttons[position]["text"] = self.symbol
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

    def update_status(self):
        """Met à jour le message de statut."""
        if hasattr(self, 'status_label'):
            if self.is_my_turn:
                self.status_label.config(text="À votre tour !")
            elif self.in_queue:
                self.status_label.config(text="Vous êtes dans la file d'attente...")
            else:
                self.status_label.config(text=f"Tour de {self.opponent}...")
        else:
            print("status_label n'est pas encore défini, mise à jour différée.")

    def end_game(self, result):
        """Affiche le résultat du match."""
        if result == self.pseudo:
            message = "Vous avez gagné !"
        elif result == "draw":
            message = "Match nul !"
        else:
            message = f"{self.opponent} a gagné !"
        messagebox.showinfo("Fin du match", message)
        self.root.quit()

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
        self.client.close()

if __name__ == "__main__":
    client = GameClient()
    client.run()