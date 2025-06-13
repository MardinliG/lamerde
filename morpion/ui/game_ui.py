import tkinter as tk

def setup_game_ui(client):
    """Configure l'interface du jeu."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Morpion vs {client.opponent}")
    
    # Titre du jeu
    game_title = tk.Label(
        client.current_frame, 
        text=f"Morpion: {client.pseudo} ({client.symbol}) vs {client.opponent}", 
        font=("Helvetica", 16, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    game_title.pack(pady=(20, 10))
    
    # Frame pour le plateau de jeu
    game_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    game_frame.pack(pady=10)
    
    # Plateau de jeu
    client.buttons = []
    for i in range(9):
        btn = tk.Button(
            game_frame, 
            text=" ", 
            font=("Helvetica", 24, "bold"), 
            width=3, 
            height=1, 
            bd=2, 
            relief=tk.RAISED, 
            command=lambda x=i: client.play_move(x),
            bg="white",
            activebackground="#e6e6e6"
        )
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        client.buttons.append(btn)
    
    # Status du jeu
    client.status_label = tk.Label(
        client.current_frame, 
        text="En attente de votre tour...", 
        font=("Helvetica", 14), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    client.status_label.pack(pady=20)
    
    # Bouton pour abandonner
    forfeit_button = tk.Button(
        client.current_frame, 
        text="Abandonner", 
        font=("Helvetica", 12), 
        bg="#d9534f", 
        fg="white", 
        padx=10, 
        pady=3, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.forfeit_game,
        activebackground="#c9302c"
    )
    forfeit_button.pack(pady=10)
