import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk

from mastermind.ui.main_menu_ui import setup_main_menu_ui
from mastermind.ui.rules_ui import setup_rules_ui
from mastermind.ui.code_creation_ui import setup_code_creation_ui
from mastermind.ui.waiting_ui import setup_waiting_ui
from mastermind.ui.game_ui import setup_game_ui, update_game_ui
from mastermind.ui.result_ui import setup_game_result_ui
from mastermind.config import Config

class MastermindClient:
    """Client pour jouer au Mastermind en 1v1."""
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
        self.my_code = []  # Code secret créé par le joueur
        self.guesses = []  # Tentatives du joueur
        self.opponent_guesses = []  # Tentatives de l'adversaire
        self.feedback = []  # Feedback pour les tentatives du joueur
        self.opponent_feedback = []  # Feedback pour les tentatives de l'adversaire
        self.max_attempts = Config.MAX_ATTEMPTS
        self.colors = Config.COLORS
        self.code_length = Config.CODE_LENGTH
        self.game_over = False
        self.in_queue = False
        
        # Interface graphique
        if parent_root:
            self.root = tk.Toplevel(parent_root)
            self.root.protocol("WM_DELETE_WINDOW", self.return_to_main)
        else:
            self.root = tk.Tk()
            
        self.root.title("Mastermind - Menu Principal")
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
        self.setup_main_menu()

    def setup_main_menu(self):
        """Configure le menu principal."""
        setup_main_menu_ui(self)
        # Lancer l'écoute du serveur
        threading.Thread(target=self.listen_server, daemon=True).start()

    def show_rules(self):
        """Affiche les règles du jeu."""
        setup_rules_ui(self)

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

    def setup_code_creation_ui(self):
        """Interface pour créer son code secret."""
        setup_code_creation_ui(self)
        # Réinitialiser le code
        self.my_code = []

    def add_color_to_code(self, color):
        """Ajoute une couleur au code."""
        if len(self.my_code) < self.code_length:
            self.my_code.append(color)
            slot_index = len(self.my_code) - 1
            self.code_slots[slot_index].config(bg=color)
            
            # Activer le bouton de validation si le code est complet
            if len(self.my_code) == self.code_length:
                self.validate_code_button.config(state=tk.NORMAL)

    def clear_code(self):
        """Efface le code actuel."""
        self.my_code = []
        for slot in self.code_slots:
            slot.config(bg="white")
        self.validate_code_button.config(state=tk.DISABLED)

    def validate_code(self):
        """Valide le code et cherche un adversaire."""
        if len(self.my_code) != self.code_length:
            messagebox.showerror("Erreur", "Veuillez sélectionner 4 couleurs.")
            return
            
        # Afficher l'écran d'attente
        self.setup_waiting_ui()
        
        # Envoyer le code au serveur et rejoindre la file d'attente
        message = json.dumps({
            "action": "JOIN_MASTERMIND", 
            "pseudo": self.pseudo, 
            "code": self.my_code
        })
        self.client.send(message.encode())
        self.in_queue = True

    def setup_waiting_ui(self):
        """Affiche l'écran d'attente d'un adversaire."""
        setup_waiting_ui(self)

    def animate_waiting_dots(self):
        """Anime les points d'attente."""
        if not hasattr(self, 'waiting_animation_label') or not self.waiting_animation_label.winfo_exists():
            return
            
        current_text = self.waiting_animation_label.cget("text")
        if current_text == ".":
            new_text = ".."
        elif current_text == "..":
            new_text = "..."
        else:
            new_text = "."
            
        self.waiting_animation_label.config(text=new_text)
        self.root.after(500, self.animate_waiting_dots)

    def cancel_matchmaking(self):
        """Annule la recherche d'adversaire."""
        message = json.dumps({
            "action": "LEAVE_MASTERMIND", 
            "pseudo": self.pseudo
        })
        self.client.send(message.encode())
        self.in_queue = False
        self.setup_main_menu()

    def setup_game_ui(self):
        """Configure l'interface du jeu Mastermind."""
        setup_game_ui(self)
        
        # Initialiser les variables de jeu
        self.current_guess = []
        self.guesses = []
        self.opponent_guesses = []
        self.feedback = []
        self.opponent_feedback = []
        self.game_over = False
        
        # Mettre à jour l'interface
        self.update_game_ui()

    def add_color_to_guess(self, color):
        """Ajoute une couleur à la tentative actuelle."""
        if len(self.current_guess) < self.code_length and not self.game_over:
            self.current_guess.append(color)
            slot_index = len(self.current_guess) - 1
            self.current_guess_slots[slot_index].config(bg=color)
            
            # Activer le bouton de soumission si la tentative est complète
            if len(self.current_guess) == self.code_length:
                self.submit_guess_button.config(state=tk.NORMAL)

    def clear_guess(self):
        """Efface la tentative actuelle."""
        self.current_guess = []
        for slot in self.current_guess_slots:
            slot.config(bg="white")
        self.submit_guess_button.config(state=tk.DISABLED)

    def submit_guess(self):
        """Soumet la tentative actuelle."""
        if len(self.current_guess) != self.code_length or self.game_over:
            return
            
        # Ajouter la tentative à la liste locale avant d'envoyer au serveur
        # Cela permet d'afficher immédiatement la tentative dans l'interface
        self.guesses.append(self.current_guess.copy())
        
        # Envoyer la tentative au serveur
        message = json.dumps({
            "action": "MASTERMIND_GUESS", 
            "pseudo": self.pseudo,
            "match_id": self.match_id,
            "guess": self.current_guess
        })
        self.client.send(message.encode())
        
        # Réinitialiser la tentative actuelle
        self.clear_guess()
        
        # Mettre à jour l'interface pour afficher la nouvelle tentative
        # (le feedback sera ajouté quand le serveur répondra)
        self.update_game_ui()

    def update_game_ui(self):
        """Met à jour l'interface du jeu."""
        update_game_ui(self)

    def show_game_result(self, result, player1_code, player2_code):
        """Affiche le résultat de la partie avec une interface améliorée."""
        setup_game_result_ui(self, result, player1_code, player2_code)
        
        # Réinitialiser les variables de jeu
        self.game_over = True
        self.opponent = None
        self.match_id = None
        self.guesses = []
        self.opponent_guesses = []
        self.feedback = []
        self.opponent_feedback = []

    def listen_server(self):
        """Écoute les messages du serveur."""
        try:
            while True:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                action = message.get("action")
                
                if action == "MASTERMIND_START":
                    self.opponent = message["opponent"]
                    self.match_id = message["match_id"]
                    self.in_queue = False
                    self.root.after(0, self.setup_game_ui)
                
                elif action == "MASTERMIND_FEEDBACK":
                    black_pins = message["black_pins"]
                    white_pins = message["white_pins"]
                    guess_number = message["guess_number"]
                    
                    # Ajouter le feedback à la liste
                    if guess_number > len(self.feedback):
                        self.feedback.append((black_pins, white_pins))
                        self.root.after(0, self.update_game_ui)
                
                elif action == "MASTERMIND_OPPONENT_GUESS":
                    guess = message["guess"]
                    black_pins = message["black_pins"]
                    white_pins = message["white_pins"]
                    
                    # Ajouter la tentative et le feedback de l'adversaire
                    self.opponent_guesses.append(guess)
                    self.opponent_feedback.append((black_pins, white_pins))
                    self.root.after(0, self.update_game_ui)
                
                elif action == "MASTERMIND_END":
                    result = message["result"]
                    player1_code = message["player1_code"]
                    player2_code = message["player2_code"]
                    self.root.after(0, lambda: self.show_game_result(result, player1_code, player2_code))
                
                elif action == "LEFT_QUEUE":
                    self.in_queue = False
                    self.root.after(0, self.setup_main_menu)
                
                elif action == "MATCH_INTERRUPTED":
                    messagebox.showinfo("Match annulé", message["message"])
                    self.root.after(0, self.setup_main_menu)
                    
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Connexion perdue: {e}"))
            self.return_to_main()

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
