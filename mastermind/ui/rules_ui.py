"""
Module pour l'interface des règles du jeu du client Mastermind.
"""
import tkinter as tk

def setup_rules_ui(client):
    """Affiche les règles du jeu."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Règles - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="Règles du Mastermind 1v1", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(30, 20))
    
    # Frame pour les règles
    rules_frame = tk.Frame(client.current_frame, bg=client.bg_color)
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
        bg=client.bg_color, 
        fg=client.text_color,
        justify="left"
    )
    rules_label.pack(pady=10, fill="both")
    
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
