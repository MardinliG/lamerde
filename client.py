import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import sys

class GameClient:
    """Client amélioré pour jouer au Morpion via le serveur de matchmaking."""
    def __init__(self, host="localhost", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur: {e}")
            sys.exit(1)
            
        self.pseudo = None
        self.symbol = None
        self.match_id = None
        self.opponent = None
        self.current_turn = "X"  # X commence toujours
        self.is_my_turn = False
        self.in_queue = False  # Indique si le joueur est dans la file
        
        # Statistiques du joueur
        self.stats = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }

        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Morpion - Connexion")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Définir les couleurs et styles
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a6ea9"
        self.text_color = "#333333"
        self.button_color = "#5a81c2"
        self.button_hover = "#7094d1"
        
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
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        # Logo ou titre
        title_label = tk.Label(
            self.current_frame, 
            text="MORPION EN LIGNE", 
            font=("Helvetica", 24, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(50, 30))
        
        # Sous-titre
        subtitle_label = tk.Label(
            self.current_frame, 
            text="Entrez votre pseudo pour commencer", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Frame pour le formulaire
        form_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        form_frame.pack(pady=20)
        
        # Label pour le pseudo
        pseudo_label = tk.Label(
            form_frame, 
            text="Pseudo:", 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        pseudo_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        # Entrée pour le pseudo
        self.pseudo_entry = tk.Entry(
            form_frame, 
            font=("Helvetica", 12), 
            width=20, 
            bd=2, 
            relief=tk.GROOVE
        )
        self.pseudo_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.pseudo_entry.focus_set()
        
        # Bouton de validation
        validate_button = tk.Button(
            self.current_frame, 
            text="Se Connecter", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.validate_pseudo,
            activebackground=self.button_hover
        )
        validate_button.pack(pady=20)
        
        # Lier la touche Entrée à la validation
        self.pseudo_entry.bind("<Return>", lambda event: self.validate_pseudo())
        
        # Pied de page
        footer_label = tk.Label(
            self.current_frame, 
            text="© 2024 Morpion en ligne", 
            font=("Helvetica", 8), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)

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
        self.setup_main_menu()

    def setup_main_menu(self):
        """Configure le menu principal."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Morpion - Menu Principal - {self.pseudo}")
        
        # Titre du menu
        title_label = tk.Label(
            self.current_frame, 
            text=f"Bienvenue, {self.pseudo}!", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(50, 30))
        
        # Frame pour les boutons du menu
        menu_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        menu_frame.pack(pady=20)
        
        # Bouton pour jouer au Morpion
        play_button = tk.Button(
            menu_frame, 
            text="Jouer au Morpion", 
            font=("Helvetica", 14, "bold"), 
            bg=self.button_color, 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_waiting_ui,
            activebackground=self.button_hover
        )
        play_button.pack(pady=10)
        
        # Bouton pour voir les statistiques
        stats_button = tk.Button(
            menu_frame, 
            text="Mes Statistiques", 
            font=("Helvetica", 14, "bold"), 
            bg=self.button_color, 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.show_statistics,
            activebackground=self.button_hover
        )
        stats_button.pack(pady=10)
        
        # Bouton pour les options
        options_button = tk.Button(
            menu_frame, 
            text="Options", 
            font=("Helvetica", 14, "bold"), 
            bg=self.button_color, 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.show_options,
            activebackground=self.button_hover
        )
        options_button.pack(pady=10)
        
        # Bouton pour quitter
        quit_button = tk.Button(
            menu_frame, 
            text="Quitter", 
            font=("Helvetica", 14, "bold"), 
            bg="#d9534f", 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.quit_game,
            activebackground="#c9302c"
        )
        quit_button.pack(pady=10)
        
        # Pied de page
        footer_label = tk.Label(
            self.current_frame, 
            text="© 2024 Morpion en ligne", 
            font=("Helvetica", 8), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)
        
        # Lancer l'écoute du serveur
        threading.Thread(target=self.listen_server, daemon=True).start()

    def show_statistics(self):
        """Affiche les statistiques du joueur."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Morpion - Statistiques - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Mes Statistiques", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(50, 30))
        
        # Frame pour les statistiques
        stats_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        stats_frame.pack(pady=20)
        
        # Afficher les statistiques
        stats_labels = [
            (f"Parties jouées: {self.stats['games_played']}", 0),
            (f"Victoires: {self.stats['wins']}", 1),
            (f"Défaites: {self.stats['losses']}", 2),
            (f"Matchs nuls: {self.stats['draws']}", 3)
        ]
        
        for text, row in stats_labels:
            label = tk.Label(
                stats_frame, 
                text=text, 
                font=("Helvetica", 14), 
                bg=self.bg_color, 
                fg=self.text_color
            )
            label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        # Bouton pour revenir au menu
        back_button = tk.Button(
            self.current_frame, 
            text="Retour au Menu", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_main_menu,
            activebackground=self.button_hover
        )
        back_button.pack(pady=20)

    def show_options(self):
        """Affiche les options du jeu."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Morpion - Options - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Options", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(50, 30))
        
        # Frame pour les options
        options_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        options_frame.pack(pady=20)
        
        # Option pour changer le thème
        theme_label = tk.Label(
            options_frame, 
            text="Thème:", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        theme_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        theme_var = tk.StringVar(value="Clair")
        theme_menu = ttk.Combobox(
            options_frame, 
            textvariable=theme_var, 
            values=["Clair", "Sombre", "Bleu"], 
            state="readonly", 
            width=15
        )
        theme_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Option pour le son
        sound_label = tk.Label(
            options_frame, 
            text="Son:", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        sound_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        sound_var = tk.BooleanVar(value=True)
        sound_check = ttk.Checkbutton(options_frame, variable=sound_var)
        sound_check.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Bouton pour sauvegarder les options
        save_button = tk.Button(
            self.current_frame, 
            text="Sauvegarder", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=lambda: self.save_options(theme_var.get(), sound_var.get()),
            activebackground=self.button_hover
        )
        save_button.pack(pady=10)
        
        # Bouton pour revenir au menu
        back_button = tk.Button(
            self.current_frame, 
            text="Retour au Menu", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_main_menu,
            activebackground=self.button_hover
        )
        back_button.pack(pady=10)

    def save_options(self, theme, sound):
        """Sauvegarde les options."""
        # Ici vous pourriez sauvegarder les options dans un fichier de configuration
        messagebox.showinfo("Options", "Options sauvegardées avec succès!")

    def quit_game(self):
        """Quitte le jeu."""
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?"):
            try:
                self.client.close()
            except:
                pass
            self.root.quit()

    def setup_waiting_ui(self):
        """Configure l'écran pour rejoindre ou quitter la file."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Morpion - File d'attente - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="File d'attente", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(50, 30))
        
        # Status
        self.status_label = tk.Label(
            self.current_frame, 
            text="Vous n'êtes pas dans la file d'attente.", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        self.status_label.pack(pady=20)
        
        # Frame pour les boutons
        buttons_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        # Bouton pour rejoindre la file
        self.join_button = tk.Button(
            buttons_frame, 
            text="Rejoindre la file d'attente", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.join_queue,
            activebackground=self.button_hover
        )
        self.join_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Bouton pour quitter la file
        self.leave_button = tk.Button(
            buttons_frame, 
            text="Quitter la file d'attente", 
            font=("Helvetica", 12, "bold"), 
            bg="#d9534f", 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.leave_queue,
            state=tk.DISABLED,
            activebackground="#c9302c"
        )
        self.leave_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Animation d'attente (peut être ajoutée plus tard)
        
        # Bouton pour revenir au menu
        back_button = tk.Button(
            self.current_frame, 
            text="Retour au Menu", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_main_menu,
            activebackground=self.button_hover
        )
        back_button.pack(pady=20)

    def setup_game_ui(self):
        """Configure l'interface du jeu."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Morpion vs {self.opponent}")
        
        # Titre du jeu
        game_title = tk.Label(
            self.current_frame, 
            text=f"Morpion: {self.pseudo} ({self.symbol}) vs {self.opponent}", 
            font=("Helvetica", 16, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        game_title.pack(pady=(20, 10))
        
        # Frame pour le plateau de jeu
        game_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        game_frame.pack(pady=10)
        
        # Plateau de jeu
        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                game_frame, 
                text=" ", 
                font=("Helvetica", 24, "bold"), 
                width=3, 
                height=1, 
                bd=2, 
                relief=tk.RAISED, 
                command=lambda x=i: self.play_move(x),
                bg="white",
                activebackground="#e6e6e6"
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)
        
        # Status du jeu
        self.status_label = tk.Label(
            self.current_frame, 
            text="En attente de votre tour...", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        self.status_label.pack(pady=20)
        
        # Bouton pour abandonner
        forfeit_button = tk.Button(
            self.current_frame, 
            text="Abandonner", 
            font=("Helvetica", 12), 
            bg="#d9534f", 
            fg="white", 
            padx=10, 
            pady=3, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.forfeit_game,
            activebackground="#c9302c"
        )
        forfeit_button.pack(pady=10)
        
        self.update_status()

    def forfeit_game(self):
        """Abandonne la partie en cours."""
        if messagebox.askyesno("Abandonner", "Êtes-vous sûr de vouloir abandonner cette partie?"):
            # Ici vous pourriez envoyer un message au serveur pour signaler l'abandon
            self.setup_main_menu()

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
            self.client.close()

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
        else:
            print("status_label n'est pas encore défini, mise à jour différée.")

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
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        # Titre du résultat
        result_label = tk.Label(
            self.current_frame, 
            text="Fin de la partie", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        result_label.pack(pady=(50, 20))
        
        # Message du résultat
        message_label = tk.Label(
            self.current_frame, 
            text=message, 
            font=("Helvetica", 18, "bold"), 
            bg=self.bg_color, 
            fg=color
        )
        message_label.pack(pady=20)
        
        # Boutons pour les actions après la partie
        buttons_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        buttons_frame.pack(pady=30)
        
        # Bouton pour rejouer
        replay_button = tk.Button(
            buttons_frame, 
            text="Rejouer", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_waiting_ui,
            activebackground=self.button_hover
        )
        replay_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Bouton pour revenir au menu
        menu_button = tk.Button(
            buttons_frame, 
            text="Menu Principal", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_main_menu,
            activebackground=self.button_hover
        )
        menu_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Réinitialiser les variables de jeu
        self.opponent = None
        self.match_id = None
        self.symbol = None
        self.is_my_turn = False

    def handle_match_interrupted(self, message):
        """Gère l'interruption du match due à une déconnexion."""
        messagebox.showinfo("Match annulé", message)
        self.opponent = None
        self.match_id = None
        self.symbol = None
        self.is_my_turn = False
        self.setup_main_menu()

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
        self.client.close()

if __name__ == "__main__":
    client = GameClient()
    client.run()
