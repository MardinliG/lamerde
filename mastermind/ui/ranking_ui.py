"""
Module pour l'interface de classement du client Mastermind.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

def setup_ranking_ui(client):
    """Configure l'interface du classement."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Classement - {client.pseudo}")
    
    # Titre du classement
    title_label = tk.Label(
        client.current_frame, 
        text="Classement des joueurs", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(20, 10))
    
    # Informations sur le joueur actuel
    player_frame = tk.Frame(client.current_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    player_frame.pack(pady=10, padx=20, fill="x")
    
    # Récupérer les informations du joueur
    player_info = client.get_player_ranking()
    player_rank = client.get_player_rank()
    
    # Titre des informations du joueur
    tk.Label(
        player_frame, 
        text=f"Votre classement", 
        font=("Helvetica", 16, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=(10, 5))
    
    # Tableau des informations du joueur
    player_info_frame = tk.Frame(player_frame, bg=client.bg_color)
    player_info_frame.pack(pady=5, padx=10)
    
    # Rang
    tk.Label(
        player_info_frame, 
        text="Rang:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        anchor="e",
        width=15
    ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    
    tk.Label(
        player_info_frame, 
        text=f"#{player_rank}" if player_rank else "Non classé", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    # ELO
    tk.Label(
        player_info_frame, 
        text="Score ELO:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        anchor="e",
        width=15
    ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    
    tk.Label(
        player_info_frame, 
        text=str(player_info['elo_rating']), 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=1, column=1, padx=5, pady=5, sticky="w")
    
    # Parties jouées
    tk.Label(
        player_info_frame, 
        text="Parties jouées:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        anchor="e",
        width=15
    ).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    
    tk.Label(
        player_info_frame, 
        text=str(player_info['games_played']), 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    # Victoires/Défaites/Nuls
    tk.Label(
        player_info_frame, 
        text="V/D/N:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        anchor="e",
        width=15
    ).grid(row=3, column=0, padx=5, pady=5, sticky="e")
    
    tk.Label(
        player_info_frame, 
        text=f"{player_info['wins']}/{player_info['losses']}/{player_info['draws']}", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=3, column=1, padx=5, pady=5, sticky="w")
    
    # Taux de victoire
    win_rate = round(player_info['wins'] / player_info['games_played'] * 100, 1) if player_info['games_played'] > 0 else 0
    
    tk.Label(
        player_info_frame, 
        text="Taux de victoire:", 
        font=("Helvetica", 12, "bold"), 
        bg=client.bg_color, 
        fg=client.text_color,
        anchor="e",
        width=15
    ).grid(row=4, column=0, padx=5, pady=5, sticky="e")
    
    tk.Label(
        player_info_frame, 
        text=f"{win_rate}%", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    ).grid(row=4, column=1, padx=5, pady=5, sticky="w")
    
    # Classement des meilleurs joueurs
    ranking_frame = tk.Frame(client.current_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    ranking_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Titre du classement
    tk.Label(
        ranking_frame, 
        text="Top 10 des joueurs", 
        font=("Helvetica", 16, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=(10, 5))
    
    # Tableau du classement
    columns = ("rank", "pseudo", "elo", "games", "win_rate")
    tree = ttk.Treeview(ranking_frame, columns=columns, show="headings", height=10)
    
    # Définir les en-têtes
    tree.heading("rank", text="Rang")
    tree.heading("pseudo", text="Pseudo")
    tree.heading("elo", text="ELO")
    tree.heading("games", text="Parties")
    tree.heading("win_rate", text="% Victoires")
    
    # Définir les largeurs des colonnes
    tree.column("rank", width=50, anchor="center")
    tree.column("pseudo", width=150, anchor="w")
    tree.column("elo", width=80, anchor="center")
    tree.column("games", width=80, anchor="center")
    tree.column("win_rate", width=100, anchor="center")
    
    # Ajouter une barre de défilement
    scrollbar = ttk.Scrollbar(ranking_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(pady=5, padx=10, fill="both", expand=True)
    
    # Récupérer et afficher les données du classement
    top_players = client.get_top_players()
    for i, player in enumerate(top_players):
        tree.insert("", "end", values=(
            i + 1,
            player['pseudo'],
            player['elo_rating'],
            player['games_played'],
            f"{player['win_rate']}%"
        ))
    
    # Historique des parties du joueur
    history_frame = tk.Frame(client.current_frame, bg=client.bg_color, bd=2, relief=tk.GROOVE)
    history_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Titre de l'historique
    tk.Label(
        history_frame, 
        text="Votre historique récent", 
        font=("Helvetica", 16, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    ).pack(pady=(10, 5))
    
    # Tableau de l'historique
    history_columns = ("date", "opponent", "result", "old_elo", "new_elo", "change")
    history_tree = ttk.Treeview(history_frame, columns=history_columns, show="headings", height=5)
    
    # Définir les en-têtes
    history_tree.heading("date", text="Date")
    history_tree.heading("opponent", text="Adversaire")
    history_tree.heading("result", text="Résultat")
    history_tree.heading("old_elo", text="Ancien ELO")
    history_tree.heading("new_elo", text="Nouvel ELO")
    history_tree.heading("change", text="Variation")
    
    # Définir les largeurs des colonnes
    history_tree.column("date", width=150, anchor="w")
    history_tree.column("opponent", width=100, anchor="w")
    history_tree.column("result", width=80, anchor="center")
    history_tree.column("old_elo", width=80, anchor="center")
    history_tree.column("new_elo", width=80, anchor="center")
    history_tree.column("change", width=80, anchor="center")
    
    # Ajouter une barre de défilement
    history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
    history_tree.configure(yscrollcommand=history_scrollbar.set)
    history_scrollbar.pack(side="right", fill="y")
    history_tree.pack(pady=5, padx=10, fill="both", expand=True)
    
    # Récupérer et afficher l'historique du joueur
    player_history = client.get_player_history()
    for entry in player_history:
        # Formater la date
        try:
            date_obj = datetime.fromisoformat(entry['match_date'])
            formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            formatted_date = entry['match_date']
        
        # Formater la variation
        change = entry['rating_change']
        change_str = f"+{change}" if change > 0 else str(change)
        change_color = "green" if change > 0 else ("red" if change < 0 else "black")
        
        history_tree.insert("", "end", values=(
            formatted_date,
            entry['opponent'],
            entry['result'],
            entry['old_rating'],
            entry['new_rating'],
            change_str
        ))
        
    # Boutons pour les actions
    buttons_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    buttons_frame.pack(pady=15)
    
    # Bouton pour rafraîchir
    refresh_button = tk.Button(
        buttons_frame, 
        text="Rafraîchir", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=lambda: client.setup_ranking_ui(),
        activebackground=client.button_hover
    )
    refresh_button.grid(row=0, column=0, padx=10)
    
    # Bouton pour revenir au menu
    back_button = tk.Button(
        buttons_frame, 
        text="Retour au menu", 
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
    back_button.grid(row=0, column=1, padx=10)
