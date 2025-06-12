"""
Module pour l'interface des statistiques du client Morpion.
"""
import tkinter as tk

def setup_stats_ui(client):
    """Affiche les statistiques du joueur."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Morpion - Statistiques - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="Mes Statistiques", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(50, 30))
    
    # Frame pour les statistiques
    stats_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    stats_frame.pack(pady=20)
    
    # Afficher les statistiques
    stats_labels = [
        (f"Parties jouées: {client.stats['games_played']}", 0),
        (f"Victoires: {client.stats['wins']}", 1),
        (f"Défaites: {client.stats['losses']}", 2),
        (f"Matchs nuls: {client.stats['draws']}", 3)
    ]
    
    for text, row in stats_labels:
        label = tk.Label(
            stats_frame, 
            text=text, 
            font=("Helvetica", 14), 
            bg=client.bg_color, 
            fg=client.text_color
        )
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
    
    # Bouton pour revenir au menu
    back_button = tk.Button(
        client.current_frame, 
        text="Retour au Menu", 
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
    back_button.pack(pady=20)
