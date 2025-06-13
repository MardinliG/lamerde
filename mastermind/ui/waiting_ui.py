import tkinter as tk

def setup_waiting_ui(client):
    """Affiche l'écran d'attente d'un adversaire."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Recherche d'adversaire - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="Recherche d'un adversaire", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(100, 30))
    
    # Message d'attente
    waiting_label = tk.Label(
        client.current_frame, 
        text="Veuillez patienter pendant que nous cherchons un adversaire...", 
        font=("Helvetica", 14), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    waiting_label.pack(pady=20)
    
    # Animation d'attente (simple texte qui change)
    client.waiting_animation_label = tk.Label(
        client.current_frame, 
        text=".", 
        font=("Helvetica", 24, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    client.waiting_animation_label.pack(pady=20)
    client.animate_waiting_dots()
    
    # Bouton pour annuler
    cancel_button = tk.Button(
        client.current_frame, 
        text="Annuler", 
        font=("Helvetica", 12, "bold"), 
        bg="#d9534f", 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.cancel_matchmaking,
        activebackground="#c9302c"
    )
    cancel_button.pack(pady=30)
