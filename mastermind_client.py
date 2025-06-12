import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk
import random

class MastermindClient:
    """Client pour jouer au Mastermind en 1v1."""
    def __init__(self, host="localhost", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur: {e}")
            return
            
        self.pseudo = None
        self.match_id = None
        self.opponent = None
        self.my_code = []  # Code secret créé par le joueur
        self.guesses = []  # Tentatives du joueur
        self.opponent_guesses = []  # Tentatives de l'adversaire
        self.feedback = []  # Feedback pour les tentatives du joueur
        self.opponent_feedback = []  # Feedback pour les tentatives de l'adversaire
        self.max_attempts = 10
        self.colors = ["red", "green", "blue", "yellow", "purple", "orange"]
        self.code_length = 4
        self.game_over = False
        
        # Interface graphique
        self.root = tk.Tk()
        self.root.title("Mastermind - Connexion")
        self.root.geometry("800x600")
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
            text="MASTERMIND 1v1", 
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

    def validate_pseudo(self):
        """Valide le pseudo et envoie une requête CONNECT."""
        pseudo = self.pseudo_entry.get().strip()
        if not pseudo:
            messagebox.showerror("Erreur", "Veuillez entrer un pseudo.")
            return
        self.pseudo = pseudo
        message = json.dumps({"action": "CONNECT", "pseudo": pseudo, "game": "mastermind"})
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
        
        self.root.title(f"Mastermind - Menu Principal - {self.pseudo}")
        
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
        
        # Bouton pour jouer au Mastermind
        play_button = tk.Button(
            menu_frame, 
            text="Jouer au Mastermind", 
            font=("Helvetica", 14, "bold"), 
            bg=self.button_color, 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_code_creation_ui,
            activebackground=self.button_hover
        )
        play_button.pack(pady=10)
        
        # Bouton pour les règles
        rules_button = tk.Button(
            menu_frame, 
            text="Règles du jeu", 
            font=("Helvetica", 14, "bold"), 
            bg=self.button_color, 
            fg="white", 
            width=20, 
            height=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.show_rules,
            activebackground=self.button_hover
        )
        rules_button.pack(pady=10)
        
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
        
        # Lancer l'écoute du serveur
        threading.Thread(target=self.listen_server, daemon=True).start()

    def show_rules(self):
        """Affiche les règles du jeu."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Mastermind - Règles - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Règles du Mastermind 1v1", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(30, 20))
        
        # Frame pour les règles
        rules_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        rules_frame.pack(pady=10, padx=40, fill="both", expand=True)
        
        # Texte des règles
        rules_text = """
        Dans cette version 1v1 du Mastermind:
        
        1. Chaque joueur crée un code secret de 4 couleurs.
        2. Les deux joueurs essaient simultanément de deviner le code de l'adversaire.
        3. Après chaque tentative, vous recevez un feedback:
           • Pion noir: bonne couleur à la bonne position
           • Pion blanc: bonne couleur mais mauvaise position
        4. Le premier joueur qui trouve le code de l'adversaire gagne.
        5. Si les deux joueurs trouvent le code au même tour, c'est un match nul.
        6. Si personne ne trouve le code après 10 tentatives, c'est un match nul.
        
        Bonne chance!
        """
        
        rules_label = tk.Label(
            rules_frame, 
            text=rules_text, 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color,
            justify="left"
        )
        rules_label.pack(pady=10, fill="both")
        
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

    def quit_game(self):
        """Quitte le jeu."""
        if messagebox.askyesno("Quitter", "Êtes-vous sûr de vouloir quitter?"):
            try:
                self.client.close()
            except:
                pass
            self.root.quit()

    def setup_code_creation_ui(self):
        """Interface pour créer son code secret."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Mastermind - Création du Code - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Créez votre code secret", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(30, 20))
        
        # Instructions
        instructions_label = tk.Label(
            self.current_frame, 
            text="Sélectionnez 4 couleurs pour créer votre code secret", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        instructions_label.pack(pady=10)
        
        # Frame pour le code
        code_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        code_frame.pack(pady=20)
        
        # Emplacements pour le code
        self.code_slots = []
        for i in range(self.code_length):
            slot = tk.Canvas(code_frame, width=40, height=40, bg="white", highlightthickness=1, highlightbackground="black")
            slot.grid(row=0, column=i, padx=5)
            self.code_slots.append(slot)
        
        # Frame pour les couleurs disponibles
        colors_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        colors_frame.pack(pady=20)
        
        # Boutons de couleurs
        for i, color in enumerate(self.colors):
            color_button = tk.Button(
                colors_frame, 
                bg=color, 
                width=3, 
                height=1, 
                bd=2, 
                relief=tk.RAISED, 
                command=lambda c=color: self.add_color_to_code(c)
            )
            color_button.grid(row=0, column=i, padx=5)
        
        # Bouton pour effacer
        clear_button = tk.Button(
            self.current_frame, 
            text="Effacer", 
            font=("Helvetica", 12), 
            bg="#f0ad4e", 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.clear_code,
            activebackground="#ec971f"
        )
        clear_button.pack(pady=10)
        
        # Bouton pour valider
        self.validate_code_button = tk.Button(
            self.current_frame, 
            text="Valider et chercher un adversaire", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.validate_code,
            state=tk.DISABLED,
            activebackground=self.button_hover
        )
        self.validate_code_button.pack(pady=10)
        
        # Bouton pour revenir au menu
        back_button = tk.Button(
            self.current_frame, 
            text="Retour au Menu", 
            font=("Helvetica", 12), 
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

    def setup_waiting_ui(self):
        """Affiche l'écran d'attente d'un adversaire."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Mastermind - Recherche d'adversaire - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Recherche d'un adversaire", 
            font=("Helvetica", 22, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(100, 30))
        
        # Message d'attente
        waiting_label = tk.Label(
            self.current_frame, 
            text="Veuillez patienter pendant que nous cherchons un adversaire...", 
            font=("Helvetica", 14), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        waiting_label.pack(pady=20)
        
        # Animation d'attente (simple texte qui change)
        self.waiting_animation_label = tk.Label(
            self.current_frame, 
            text=".", 
            font=("Helvetica", 24, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        self.waiting_animation_label.pack(pady=20)
        self.animate_waiting_dots()
        
        # Bouton pour annuler
        cancel_button = tk.Button(
            self.current_frame, 
            text="Annuler", 
            font=("Helvetica", 12, "bold"), 
            bg="#d9534f", 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.cancel_matchmaking,
            activebackground="#c9302c"
        )
        cancel_button.pack(pady=30)

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
        self.setup_main_menu()

    def setup_game_ui(self):
        """Configure l'interface du jeu Mastermind."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Mastermind vs {self.opponent}")
        
        # Titre du jeu
        game_title = tk.Label(
            self.current_frame, 
            text=f"Mastermind: {self.pseudo} vs {self.opponent}", 
            font=("Helvetica", 16, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        game_title.pack(pady=(10, 5))
        
        # Frame principale divisée en deux
        main_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Côté gauche: Vos tentatives
        left_frame = tk.Frame(main_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        tk.Label(
            left_frame, 
            text=f"Vos tentatives", 
            font=("Helvetica", 14, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        ).pack(pady=5)
        
        # Tableau pour vos tentatives
        self.my_guesses_frame = tk.Frame(left_frame, bg=self.bg_color)
        self.my_guesses_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Côté droit: Tentatives de l'adversaire
        right_frame = tk.Frame(main_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        tk.Label(
            right_frame, 
            text=f"Tentatives de {self.opponent}", 
            font=("Helvetica", 14, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        ).pack(pady=5)
        
        # Tableau pour les tentatives de l'adversaire
        self.opponent_guesses_frame = tk.Frame(right_frame, bg=self.bg_color)
        self.opponent_guesses_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurer les colonnes pour qu'elles aient la même taille
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Frame pour la sélection des couleurs et la soumission
        bottom_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # Frame pour la sélection actuelle
        self.current_guess_frame = tk.Frame(bottom_frame, bg=self.bg_color)
        self.current_guess_frame.pack(pady=5)
        
        # Emplacements pour la tentative actuelle
        self.current_guess_slots = []
        for i in range(self.code_length):
            slot = tk.Canvas(self.current_guess_frame, width=30, height=30, bg="white", highlightthickness=1, highlightbackground="black")
            slot.grid(row=0, column=i, padx=3)
            self.current_guess_slots.append(slot)
        
        # Frame pour les couleurs disponibles
        colors_frame = tk.Frame(bottom_frame, bg=self.bg_color)
        colors_frame.pack(pady=5)
        
        # Boutons de couleurs
        for i, color in enumerate(self.colors):
            color_button = tk.Button(
                colors_frame, 
                bg=color, 
                width=2, 
                height=1, 
                bd=2, 
                relief=tk.RAISED, 
                command=lambda c=color: self.add_color_to_guess(c)
            )
            color_button.grid(row=0, column=i, padx=3)
        
        # Boutons d'action
        actions_frame = tk.Frame(bottom_frame, bg=self.bg_color)
        actions_frame.pack(pady=5)
        
        # Bouton pour effacer
        clear_button = tk.Button(
            actions_frame, 
            text="Effacer", 
            font=("Helvetica", 10), 
            bg="#f0ad4e", 
            fg="white", 
            padx=10, 
            pady=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.clear_guess,
            activebackground="#ec971f"
        )
        clear_button.grid(row=0, column=0, padx=5)
        
        # Bouton pour soumettre
        self.submit_guess_button = tk.Button(
            actions_frame, 
            text="Soumettre", 
            font=("Helvetica", 10, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=10, 
            pady=2, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.submit_guess,
            state=tk.DISABLED,
            activebackground=self.button_hover
        )
        self.submit_guess_button.grid(row=0, column=1, padx=5)
        
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
        # Effacer les frames
        for widget in self.my_guesses_frame.winfo_children():
            widget.destroy()
        for widget in self.opponent_guesses_frame.winfo_children():
            widget.destroy()
        
        # Afficher vos tentatives
        for i, guess in enumerate(self.guesses):
            guess_frame = tk.Frame(self.my_guesses_frame, bg=self.bg_color)
            guess_frame.pack(fill="x", pady=2)
            
            # Numéro de tentative
            num_label = tk.Label(
                guess_frame, 
                text=f"{i+1}.", 
                font=("Helvetica", 10), 
                bg=self.bg_color, 
                fg=self.text_color,
                width=2
            )
            num_label.grid(row=0, column=0, padx=2)
            
            # Couleurs de la tentative
            for j, color in enumerate(guess):
                color_canvas = tk.Canvas(guess_frame, width=20, height=20, bg=color, highlightthickness=1, highlightbackground="black")
                color_canvas.grid(row=0, column=j+1, padx=2)
            
            # Feedback (pions noirs et blancs) si disponible
            if i < len(self.feedback):
                black_pins, white_pins = self.feedback[i]
                feedback_frame = tk.Frame(guess_frame, bg=self.bg_color)
                feedback_frame.grid(row=0, column=len(guess)+1, padx=5)
                
                # Afficher les pions noirs
                for j in range(black_pins):
                    pin = tk.Canvas(feedback_frame, width=10, height=10, bg="black", highlightthickness=0)
                    pin.grid(row=0, column=j, padx=1)
                
                # Afficher les pions blancs
                for j in range(white_pins):
                    pin = tk.Canvas(feedback_frame, width=10, height=10, bg="white", highlightthickness=1, highlightbackground="black")
                    pin.grid(row=0, column=black_pins+j, padx=1)
            else:
                # Si pas encore de feedback, afficher "En attente..."
                waiting_label = tk.Label(
                    guess_frame, 
                    text="En attente...", 
                    font=("Helvetica", 8, "italic"), 
                    bg=self.bg_color, 
                    fg="#999999"
                )
                waiting_label.grid(row=0, column=len(guess)+1, padx=5)
        
        # Afficher les tentatives de l'adversaire
        for i, (guess, feedback) in enumerate(zip(self.opponent_guesses, self.opponent_feedback)):
            guess_frame = tk.Frame(self.opponent_guesses_frame, bg=self.bg_color)
            guess_frame.pack(fill="x", pady=2)
            
            # Numéro de tentative
            num_label = tk.Label(
                guess_frame, 
                text=f"{i+1}.", 
                font=("Helvetica", 10), 
                bg=self.bg_color, 
                fg=self.text_color,
                width=2
            )
            num_label.grid(row=0, column=0, padx=2)
            
            # Couleurs de la tentative
            for j, color in enumerate(guess):
                color_canvas = tk.Canvas(guess_frame, width=20, height=20, bg=color, highlightthickness=1, highlightbackground="black")
                color_canvas.grid(row=0, column=j+1, padx=2)
            
            # Feedback (pions noirs et blancs)
            black_pins, white_pins = feedback
            feedback_frame = tk.Frame(guess_frame, bg=self.bg_color)
            feedback_frame.grid(row=0, column=len(guess)+1, padx=5)
            
            # Afficher les pions noirs
            for j in range(black_pins):
                pin = tk.Canvas(feedback_frame, width=10, height=10, bg="black", highlightthickness=0)
                pin.grid(row=0, column=j, padx=1)
            
            # Afficher les pions blancs
            for j in range(white_pins):
                pin = tk.Canvas(feedback_frame, width=10, height=10, bg="white", highlightthickness=1, highlightbackground="black")
                pin.grid(row=0, column=black_pins+j, padx=1)

    def show_game_result(self, result, player1_code, player2_code):
        """Affiche le résultat de la partie avec une interface améliorée."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)
        
        self.root.title(f"Mastermind - Fin de partie - {self.pseudo}")
        
        # Titre
        title_label = tk.Label(
            self.current_frame, 
            text="Fin de la partie", 
            font=("Helvetica", 24, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        title_label.pack(pady=(20, 15))
        
        # Résultat
        if result == self.pseudo:
            result_text = "Vous avez gagné !"
            result_color = "#5cb85c"  # Vert
        elif result == "draw":
            result_text = "Match nul !"
            result_color = "#f0ad4e"  # Orange
        else:
            result_text = f"{self.opponent} a gagné !"
            result_color = "#d9534f"  # Rouge
            
        result_label = tk.Label(
            self.current_frame, 
            text=result_text, 
            font=("Helvetica", 20, "bold"), 
            bg=self.bg_color, 
            fg=result_color
        )
        result_label.pack(pady=10)
        
        # Statistiques de la partie
        stats_frame = tk.Frame(self.current_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        stats_frame.pack(pady=15, padx=20, fill="x")
        
        # Titre des statistiques
        tk.Label(
            stats_frame, 
            text="Statistiques de la partie", 
            font=("Helvetica", 14, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        ).pack(pady=5)
        
        # Tableau des statistiques
        stats_table = tk.Frame(stats_frame, bg=self.bg_color)
        stats_table.pack(pady=5, padx=10)
        
        # En-têtes du tableau
        tk.Label(
            stats_table, 
            text="Joueur", 
            font=("Helvetica", 12, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color,
            width=15
        ).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Label(
            stats_table, 
            text="Tentatives", 
            font=("Helvetica", 12, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color,
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Données du joueur
        tk.Label(
            stats_table, 
            text=self.pseudo, 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color
        ).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Label(
            stats_table, 
            text=str(len(self.guesses)), 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color
        ).grid(row=1, column=1, padx=5, pady=5)
        
        # Données de l'adversaire
        tk.Label(
            stats_table, 
            text=self.opponent, 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color
        ).grid(row=2, column=0, padx=5, pady=5)
        
        tk.Label(
            stats_table, 
            text=str(len(self.opponent_guesses)), 
            font=("Helvetica", 12), 
            bg=self.bg_color, 
            fg=self.text_color
        ).grid(row=2, column=1, padx=5, pady=5)
        
        # Frame pour les codes secrets
        codes_frame = tk.Frame(self.current_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE)
        codes_frame.pack(pady=15, padx=20, fill="x")
        
        # Titre des codes secrets
        tk.Label(
            codes_frame, 
            text="Codes secrets", 
            font=("Helvetica", 14, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        ).pack(pady=5)
        
        # Tableau des codes secrets
        codes_table = tk.Frame(codes_frame, bg=self.bg_color)
        codes_table.pack(pady=5, padx=10)
        
        # Code secret du joueur
        tk.Label(
            codes_table, 
            text=f"Votre code:" , 
            font=("Helvetica", 12, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color,
            width=15,
            anchor="e"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        my_code_frame = tk.Frame(codes_table, bg=self.bg_color)
        my_code_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # Déterminer quel code est le vôtre
        my_code = self.my_code
        
        for i, color in enumerate(my_code):
            color_canvas = tk.Canvas(my_code_frame, width=30, height=30, bg=color, highlightthickness=1, highlightbackground="black")
            color_canvas.grid(row=0, column=i, padx=3)
        
        # Code secret de l'adversaire
        tk.Label(
            codes_table, 
            text=f"Code de {self.opponent}:", 
            font=("Helvetica", 12, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color,
            width=15,
            anchor="e"
        ).grid(row=1, column=0, padx=5, pady=5)
        
        opponent_code_frame = tk.Frame(codes_table, bg=self.bg_color)
        opponent_code_frame.grid(row=1, column=1, padx=5, pady=5)
        
        # Déterminer quel code est celui de l'adversaire
        opponent_code = player2_code if self.pseudo == player1_code else player1_code
        
        for i, color in enumerate(opponent_code):
            color_canvas = tk.Canvas(opponent_code_frame, width=30, height=30, bg=color, highlightthickness=1, highlightbackground="black")
            color_canvas.grid(row=0, column=i, padx=3)
        
        # Boutons pour les actions après la partie
        buttons_frame = tk.Frame(self.current_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        # Bouton pour rejouer
        replay_button = tk.Button(
            buttons_frame, 
            text="Nouvelle partie", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white", 
            padx=20, 
            pady=5, 
            bd=0, 
            relief=tk.FLAT, 
            command=self.setup_code_creation_ui,
            activebackground=self.button_hover
        )
        replay_button.grid(row=0, column=0, padx=10)
        
        # Bouton pour revenir au menu
        menu_button = tk.Button(
            buttons_frame, 
            text="Menu principal", 
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
        menu_button.grid(row=0, column=1, padx=10)
        
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
            try:
                self.client.close()
            except:
                pass

    def run(self):
        """Démarre l'interface graphique."""
        self.root.mainloop()
        try:
            self.client.close()
        except:
            pass

if __name__ == "__main__":
    client = MastermindClient()
    client.run()
