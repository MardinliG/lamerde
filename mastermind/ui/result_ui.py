import tkinter as tk
from config import Config

def setup_game_result_ui(client, result, player1_code, player2_code):
    """Affiche le résultat de la partie avec une interface améliorée."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Fin de partie - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="Fin de la partie", 
        font=("Helvetica", 24, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(20, 15))
    
    # Résultat
    if result == client.pseudo:
        result_text = "Vous avez gagné !"
        result_color = Config.SUCCESS_COLOR
    elif result == "draw":
        result_text = "Match nul !"
        result_color = Config.WARNING_COLOR
    else:
        result_text = f"{client.opponent} a gagné !"
        result_color = Config.DANGER_COLOR
        
    result_label = tk.Label(
        client.current_frame, 
        text=result_text, 
        font=("Helvetica", 20, "bold"), 
        bg=client.bg_color, 
        fg=result_color
    )
    result_label.pack(pady=10)
    
    # Statistiques de la partie
    stats_frame = tk.Frame(client.current_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    stats_frame.pack(pady=15, padx=20, fill="x")
    
    # Titre des statistiques
    tk.Label(
        stats_frame, 
        text="Statistiques de la partie", 
        font=("Helvetica", 14, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=5)
    
    # Tableau des statistiques
    stats_table = tk.Frame(stats_frame, bg=client.bg_color)
    stats_table.pack(pady=5, padx=10)
    
    # En-têtes du tableau
    tk.Label(
        stats_table, 
        text="Joueur", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        width=15
    ).grid(row=0, column=0, padx=5, pady=5)
    
    tk.Label(
        stats_table, 
        text="Tentatives", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        width=10
    ).grid(row=0, column=1, padx=5, pady=5)
    
    # Données du joueur
    tk.Label(
        stats_table, 
        text=client.pseudo, 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=1, column=0, padx=5, pady=5)
    
    tk.Label(
        stats_table, 
        text=str(len(client.guesses)), 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=1, column=1, padx=5, pady=5)
    
    # Données de l'adversaire
    tk.Label(
        stats_table, 
        text=client.opponent, 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=2, column=0, padx=5, pady=5)
    
    tk.Label(
        stats_table, 
        text=str(len(client.opponent_guesses)), 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=2, column=1, padx=5, pady=5)
    
    # Frame pour les codes secrets
    codes_frame = tk.Frame(client.current_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    codes_frame.pack(pady=15, padx=20, fill="x")
    
    # Titre des codes secrets
    tk.Label(
        codes_frame, 
        text="Codes secrets", 
        font=("Helvetica", 14, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=5)
    
    # Tableau des codes secrets
    codes_table = tk.Frame(codes_frame, bg=client.bg_color)
    codes_table.pack(pady=5, padx=10)
    
    # Code secret du joueur
    tk.Label(
        codes_table, 
        text=f"Votre code:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        width=15,
        anchor="e"
    ).grid(row=0, column=0, padx=5, pady=5)
    
    my_code_frame = tk.Frame(codes_table, bg=client.bg_color)
    my_code_frame.grid(row=0, column=1, padx=5, pady=5)
    
    # Afficher le code du joueur (celui qu'il a créé)
    for i, color in enumerate(client.my_code):
        color_canvas = tk.Canvas(my_code_frame, width=30, height=30, bg=color, highlightthickness=1, highlightbackground="black")
        color_canvas.grid(row=0, column=i, padx=3)
    
    # Code secret de l'adversaire
    tk.Label(
        codes_table, 
        text=f"Code de {client.opponent}:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        width=15,
        anchor="e"
    ).grid(row=1, column=0, padx=5, pady=5)
    
    opponent_code_frame = tk.Frame(codes_table, bg=client.bg_color)
    opponent_code_frame.grid(row=1, column=1, padx=5, pady=5)
    
    # Déterminer quel code est celui de l'adversaire
    # Si je suis player1, alors le code de l'adversaire est player2_code
    # Si je suis player2, alors le code de l'adversaire est player1_code
    opponent_code = player2_code if client.pseudo == player1_code else player1_code
    
    for i, color in enumerate(opponent_code):
        color_canvas = tk.Canvas(opponent_code_frame, width=30, height=30, bg=color, highlightthickness=1, highlightbackground="black")
        color_canvas.grid(row=0, column=i, padx=3)
    
    # Boutons pour les actions après la partie
    buttons_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    buttons_frame.pack(pady=20)
    
    # Bouton pour rejouer
    replay_button = tk.Button(
        buttons_frame, 
        text="Nouvelle partie", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_code_creation_ui,
        activebackground=client.button_hover
    )
    replay_button.grid(row=0, column=0, padx=10)
    
    # Bouton pour revenir au menu
    menu_button = tk.Button(
        buttons_frame, 
        text="Menu principal", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_main_menu,
        activebackground=client.button_hover
    )
    menu_button.grid(row=0, column=1, padx=10)
