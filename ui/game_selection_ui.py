import tkinter as tk

def setup_game_selection_ui(client):
    """Configure l'interface de sélection de jeu."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Sélection de jeu - {client.pseudo}")
    
    # Titre du menu
    title_label = tk.Label(
        client.current_frame, 
        text=f"Bienvenue, {client.pseudo}!", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(50, 30))
    
    # Sous-titre
    subtitle_label = tk.Label(
        client.current_frame, 
        text="Choisissez un jeu", 
        font=("Helvetica", 16), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    subtitle_label.pack(pady=(0, 20))
    
    # Frame pour les boutons de jeu
    games_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    games_frame.pack(pady=20)
    
    # Bouton pour Mastermind (jeu principal)
    mastermind_frame = tk.Frame(games_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE, padx=20, pady=20)
    mastermind_frame.grid(row=0, column=0, padx=20, pady=10)
    
    mastermind_title = tk.Label(
        mastermind_frame, 
        text="MASTERMIND", 
        font=("Helvetica", 18, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    mastermind_title.pack(pady=10)
    
    mastermind_desc = tk.Label(
        mastermind_frame, 
        text="Jeu de réflexion où vous devez\ndeviner un code secret", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color,
        justify="center"
    )
    mastermind_desc.pack(pady=10)
    
    mastermind_button = tk.Button(
        mastermind_frame, 
        text="Jouer au Mastermind", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.launch_mastermind,
        activebackground=client.button_hover
    )
    mastermind_button.pack(pady=10)
    
    # Bouton pour Morpion
    morpion_frame = tk.Frame(games_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE, padx=20, pady=20)
    morpion_frame.grid(row=0, column=1, padx=20, pady=10)
    
    morpion_title = tk.Label(
        morpion_frame, 
        text="MORPION", 
        font=("Helvetica", 18, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    morpion_title.pack(pady=10)
    
    morpion_desc = tk.Label(
        morpion_frame, 
        text="Jeu classique de Tic-Tac-Toe\nen mode 1v1", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color,
        justify="center"
    )
    morpion_desc.pack(pady=10)
    
    morpion_button = tk.Button(
        morpion_frame, 
        text="Jouer au Morpion", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.launch_morpion,
        activebackground=client.button_hover
    )
    morpion_button.pack(pady=10)
    
    # Bouton pour quitter
    quit_button = tk.Button(
        client.current_frame, 
        text="Quitter", 
        font=("Helvetica", 12), 
        bg="#d9534f", 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.quit_app,
        activebackground="#c9302c"
    )
    quit_button.pack(pady=30)
