import tkinter as tk

def setup_game_ui(client):
    """Configure l'interface du jeu Mastermind."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind vs {client.opponent}")
    
    # Titre du jeu
    game_title = tk.Label(
        client.current_frame, 
        text=f"Mastermind: {client.pseudo} vs {client.opponent}", 
        font=("Helvetica", 16, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    game_title.pack(pady=(10, 5))
    
    # Frame principale divisée en deux
    main_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Côté gauche: Vos tentatives
    left_frame = tk.Frame(main_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    
    tk.Label(
        left_frame, 
        text=f"Vos tentatives", 
        font=("Helvetica", 14, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=5)
    
    # Tableau pour vos tentatives
    client.my_guesses_frame = tk.Frame(left_frame, bg=client.bg_color)
    client.my_guesses_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Côté droit: Tentatives de l'adversaire
    right_frame = tk.Frame(main_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    tk.Label(
        right_frame, 
        text=f"Tentatives de {client.opponent}", 
        font=("Helvetica", 14, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=5)
    
    # Tableau pour les tentatives de l'adversaire
    client.opponent_guesses_frame = tk.Frame(right_frame, bg=client.bg_color)
    client.opponent_guesses_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Configurer les colonnes pour qu'elles aient la même taille
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    
    # Frame pour la sélection des couleurs et la soumission
    bottom_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    bottom_frame.pack(fill="x", padx=10, pady=10)
    
    # Frame pour la sélection actuelle
    client.current_guess_frame = tk.Frame(bottom_frame, bg=client.bg_color)
    client.current_guess_frame.pack(pady=5)
    
    # Emplacements pour la tentative actuelle
    client.current_guess_slots = []
    for i in range(client.code_length):
        slot = tk.Canvas(client.current_guess_frame, width=30, height=30, bg="white", highlightthickness=1, highlightbackground="black")
        slot.grid(row=0, column=i, padx=3)
        client.current_guess_slots.append(slot)
    
    # Frame pour les couleurs disponibles
    colors_frame = tk.Frame(bottom_frame, bg=client.bg_color)
    colors_frame.pack(pady=5)
    
    # Boutons de couleurs
    for i, color in enumerate(client.colors):
        color_button = tk.Button(
            colors_frame, 
            bg=color, 
            width=2, 
            height=1, 
            bd=2, 
            relief=tk.RAISED, 
            command=lambda c=color: client.add_color_to_guess(c)
        )
        color_button.grid(row=0, column=i, padx=3)
    
    # Boutons d'action
    actions_frame = tk.Frame(bottom_frame, bg=client.bg_color)
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
        command=client.clear_guess,
        activebackground="#ec971f"
    )
    clear_button.grid(row=0, column=0, padx=5)
    
    # Bouton pour soumettre
    client.submit_guess_button = tk.Button(
        actions_frame, 
        text="Soumettre", 
        font=("Helvetica", 10, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=10, 
        pady=2, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.submit_guess,
        state=tk.DISABLED,
        activebackground=client.button_hover
    )
    client.submit_guess_button.grid(row=0, column=1, padx=5)

def update_game_ui(client):
    """Met à jour l'interface du jeu."""
    # Effacer les frames
    for widget in client.my_guesses_frame.winfo_children():
        widget.destroy()
    for widget in client.opponent_guesses_frame.winfo_children():
        widget.destroy()
    
    # Afficher vos tentatives
    for i, guess in enumerate(client.guesses):
        guess_frame = tk.Frame(client.my_guesses_frame, bg=client.bg_color)
        guess_frame.pack(fill="x", pady=2)
        
        # Numéro de tentative
        num_label = tk.Label(
            guess_frame, 
            text=f"{i+1}.", 
            font=("Helvetica", 10), 
            bg=client.bg_color, 
            fg=client.text_color,
            width=2
        )
        num_label.grid(row=0, column=0, padx=2)
        
        # Couleurs de la tentative
        for j, color in enumerate(guess):
            color_canvas = tk.Canvas(guess_frame, width=20, height=20, bg=color, highlightthickness=1, highlightbackground="black")
            color_canvas.grid(row=0, column=j+1, padx=2)
        
        # Feedback (pions noirs et blancs) si disponible
        if i < len(client.feedback):
            black_pins, white_pins = client.feedback[i]
            feedback_frame = tk.Frame(guess_frame, bg=client.bg_color)
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
                bg=client.bg_color, 
                fg="#999999"
            )
            waiting_label.grid(row=0, column=len(guess)+1, padx=5)
    
    # Afficher les tentatives de l'adversaire
    for i, (guess, feedback) in enumerate(zip(client.opponent_guesses, client.opponent_feedback)):
        guess_frame = tk.Frame(client.opponent_guesses_frame, bg=client.bg_color)
        guess_frame.pack(fill="x", pady=2)
        
        # Numéro de tentative
        num_label = tk.Label(
            guess_frame, 
            text=f"{i+1}.", 
            font=("Helvetica", 10), 
            bg=client.bg_color, 
            fg=client.text_color,
            width=2
        )
        num_label.grid(row=0, column=0, padx=2)
        
        # Couleurs de la tentative
        for j, color in enumerate(guess):
            color_canvas = tk.Canvas(guess_frame, width=20, height=20, bg=color, highlightthickness=1, highlightbackground="black")
            color_canvas.grid(row=0, column=j+1, padx=2)
        
        # Feedback (pions noirs et blancs)
        black_pins, white_pins = feedback
        feedback_frame = tk.Frame(guess_frame, bg=client.bg_color)
        feedback_frame.grid(row=0, column=len(guess)+1, padx=5)
        
        # Afficher les pions noirs
        for j in range(black_pins):
            pin = tk.Canvas(feedback_frame, width=10, height=10, bg="black", highlightthickness=0)
            pin.grid(row=0, column=j, padx=1)
        
        # Afficher les pions blancs
        for j in range(white_pins):
            pin = tk.Canvas(feedback_frame, width=10, height=10, bg="white", highlightthickness=1, highlightbackground="black")
            pin.grid(row=0, column=black_pins+j, padx=1)
