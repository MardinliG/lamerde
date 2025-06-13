import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk

from ui.login_ui import setup_login_ui
from ui.game_selection_ui import setup_game_selection_ui
from mastermind.client import MastermindClient
from morpion.client import MorpionClient
from config import Config

class AppClient:
    """Client principal pour l'application de jeux en réseau."""
    def __init__(self, host="localhost", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur: {e}")
            return
            
        self.pseudo = None
        
        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Jeux en réseau - Connexion")
        self.root.geometry("800x600")
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
        self.setup_login_ui()

    def setup_login_ui(self):
        """Configure l'interface de connexion."""
        setup_login_ui(self)

    def validate_pseudo(self):
        """Valide le pseudo et envoie une requête CONNECT."""
        pseudo = self.pseudo_entry.get().strip()
        if not pseudo:
            messagebox.showerror("Erreur", "Veuillez entrer un pseudo.")
            return
        self.pseudo = pseudo
        message = json.dumps({"action": "CONNECT", "pseudo": pseudo})
        try:
            self.client.send(message.encode())
            response = self.client.recv(1024).decode()
            response_data = json.loads(response)
            if response_data.get("status") == "ERROR":
                messagebox.showerror("Erreur", response_data.get("message", "Pseudo déjà pris."))
                return
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion au serveur échouée: {e}")
            return
        self.setup_game_selection_ui()

    def setup_game_selection_ui(self):
        """Configure l'interface de sélection de jeu."""
        setup_game_selection_ui(self)

    def launch_mastermind(self):
        """Lance le jeu Mastermind."""
        self.root.withdraw()  # Cache la fenêtre principale
        mastermind_client = MastermindClient(self.pseudo, self.client, self.root)
        mastermind_client.run()

    def launch_morpion(self):
        """Lance le jeu Morpion."""
        self.root.withdraw()  # Cache la fenêtre principale
        morpion_client = MorpionClient(self.pseudo, self.client, self.root)
        morpion_client.run()

    def quit_app(self):
        """Quitte l'application."""
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?"):
            try:
                self.client.close()
            except:
                pass
            self.root.quit()

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
        try:
            self.client.close()
        except:
            pass
