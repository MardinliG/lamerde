import tkinter as tk

def setup_waiting_ui(client):
    """Configure l'écran pour rejoindre ou quitter la file."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Morpion - File d'attente - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="File d'attente", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(50, 30))
    
    # Status
    client.status_label = tk.Label(
        client.current_frame, 
        text="Vous n'êtes pas dans la file d'attente.", 
        font=("Helvetica", 14), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    client.status_label.pack(pady=20)
    
    # Frame pour les boutons
    buttons_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    buttons_frame.pack(pady=20)
    
    # Bouton pour rejoindre la file
    client.join_button = tk.Button(
        buttons_frame, 
        text="Rejoindre la file d'attente", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.join_queue,
        activebackground=client.button_hover
    )
    client.join_button.grid(row=0, column=0, padx=10, pady=10)
    
    # Bouton pour quitter la file
    client.leave_button = tk.Button(
        buttons_frame, 
        text="Quitter la file d'attente", 
        font=("Helvetica", 12, "bold"), 
        bg="#d9534f", 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.leave_queue,
        state=tk.DISABLED,
        activebackground="#c9302c"
    )
    client.leave_button.grid(row=0, column=1, padx=10, pady=10)
    
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
