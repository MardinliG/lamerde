import tkinter as tk

def setup_login_ui(client):
    """Configure l'interface de connexion."""
    if client.current_frame:
        client.current_frame.destroy()
    
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    # Logo ou titre
    title_label = tk.Label(
        client.current_frame, 
        text="JEUX EN RÉSEAU", 
        font=("Helvetica", 24, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(50, 30))
    
    # Sous-titre
    subtitle_label = tk.Label(
        client.current_frame, 
        text="Entrez votre pseudo pour commencer", 
        font=("Helvetica", 14), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    subtitle_label.pack(pady=(0, 20))
    
    # Frame pour le formulaire
    form_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    form_frame.pack(pady=20)
    
    # Label pour le pseudo
    pseudo_label = tk.Label(
        form_frame, 
        text="Pseudo:", 
        font=("Helvetica", 12), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    pseudo_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    
    # Entrée pour le pseudo
    client.pseudo_entry = tk.Entry(
        form_frame, 
        font=("Helvetica", 12), 
        width=20, 
        bd=2, 
        relief=tk.GROOVE
    )
    client.pseudo_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    client.pseudo_entry.focus_set()
    
    # Bouton de validation
    validate_button = tk.Button(
        client.current_frame, 
        text="Se Connecter", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.validate_pseudo,
        activebackground=client.button_hover
    )
    validate_button.pack(pady=20)
    
    # Lier la touche Entrée à la validation
    client.pseudo_entry.bind("<Return>", lambda event: client.validate_pseudo())
