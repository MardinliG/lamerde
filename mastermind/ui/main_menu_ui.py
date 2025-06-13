"""
Module pour l'interface du menu principal du client Mastermind.
"""
import tkinter as tk

def setup_main_menu_ui(client):
    """Configure le menu principal."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Menu Principal - {client.pseudo}")
    
    # Titre du menu
    title_label = tk.Label(
        client.current_frame, 
        text=f"Bienvenue, {client.pseudo}!", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(50, 30))
    
    # Frame pour les boutons du menu
    menu_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    menu_frame.pack(pady=20)
    
    # Bouton pour jouer au Mastermind
    play_button = tk.Button(
        menu_frame, 
        text="Jouer au Mastermind", 
        font=("Helvetica", 14, "bold"), 
        bg=client.button_color, 
        fg="white", 
        width=20, 
        height=2, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_code_creation_ui,
        activebackground=client.button_hover
    )
    play_button.pack(pady=10)
    
    # Bouton pour les règles
    rules_button = tk.Button(
        menu_frame, 
        text="Règles du jeu", 
        font=("Helvetica", 14, "bold"), 
        bg=client.button_color, 
        fg="white", 
        width=20, 
        height=2, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.show_rules,
        activebackground=client.button_hover
    )
    rules_button.pack(pady=10)

    # Bouton pour le classement
    ranking_button = tk.Button(
        menu_frame, 
        text="Classement", 
        font=("Helvetica", 14, "bold"), 
        bg=client.button_color, 
        fg="white", 
        width=20, 
        height=2, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_ranking_ui,
        activebackground=client.button_hover
    )
    ranking_button.pack(pady=10)
    
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
        command=client.quit_game,
        activebackground="#c9302c"
    )
    quit_button.pack(pady=10)
