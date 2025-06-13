import tkinter as tk

def setup_result_ui(client, message, color):
    """Affiche le résultat du match."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    # Titre du résultat
    result_label = tk.Label(
        client.current_frame, 
        text="Fin de la partie", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    result_label.pack(pady=(50, 20))
    
    # Message du résultat
    message_label = tk.Label(
        client.current_frame, 
        text=message, 
        font=("Helvetica", 18, "bold"), 
        bg=client.bg_color, 
        fg=color
    )
    message_label.pack(pady=20)
    
    # Boutons pour les actions après la partie
    buttons_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    buttons_frame.pack(pady=30)
    
    # Bouton pour rejouer
    replay_button = tk.Button(
        buttons_frame, 
        text="Rejouer", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_waiting_ui,
        activebackground=client.button_hover
    )
    replay_button.grid(row=0, column=0, padx=10, pady=10)
    
    # Bouton pour revenir au menu
    menu_button = tk.Button(
        buttons_frame, 
        text="Menu Principal", 
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
    menu_button.grid(row=0, column=1, padx=10, pady=10)
