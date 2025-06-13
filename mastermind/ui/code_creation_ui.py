
import tkinter as tk

def setup_code_creation_ui(client):
    """Interface pour créer son code secret."""
    if client.current_frame:
        client.current_frame.destroy()
        
    client.current_frame = tk.Frame(client.root, bg=client.bg_color)
    client.current_frame.pack(fill="both", expand=True)
    
    client.root.title(f"Mastermind - Création du Code - {client.pseudo}")
    
    # Titre
    title_label = tk.Label(
        client.current_frame, 
        text="Créez votre code secret", 
        font=("Helvetica", 22, "bold"), 
        bg=client.bg_color, 
        fg=client.accent_color
    )
    title_label.pack(pady=(30, 20))
    
    # Instructions
    instructions_label = tk.Label(
        client.current_frame, 
        text="Sélectionnez 4 couleurs pour créer votre code secret", 
        font=("Helvetica", 14), 
        bg=client.bg_color, 
        fg=client.text_color
    )
    instructions_label.pack(pady=10)
    
    # Frame pour le code
    code_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    code_frame.pack(pady=20)
    
    # Emplacements pour le code
    client.code_slots = []
    for i in range(client.code_length):
        slot = tk.Canvas(code_frame, width=40, height=40, bg="white", highlightthickness=1, highlightbackground="black")
        slot.grid(row=0, column=i, padx=5)
        client.code_slots.append(slot)
    
    # Frame pour les couleurs disponibles
    colors_frame = tk.Frame(client.current_frame, bg=client.bg_color)
    colors_frame.pack(pady=20)
    
    # Boutons de couleurs
    for i, color in enumerate(client.colors):
        color_button = tk.Button(
            colors_frame, 
            bg=color, 
            width=3, 
            height=1, 
            bd=2, 
            relief=tk.RAISED, 
            command=lambda c=color: client.add_color_to_code(c)
        )
        color_button.grid(row=0, column=i, padx=5)
    
    # Bouton pour effacer
    clear_button = tk.Button(
        client.current_frame, 
        text="Effacer", 
        font=("Helvetica", 12), 
        bg="#f0ad4e", 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.clear_code,
        activebackground="#ec971f"
    )
    clear_button.pack(pady=10)
    
    # Bouton pour valider
    client.validate_code_button = tk.Button(
        client.current_frame, 
        text="Valider et chercher un adversaire", 
        font=("Helvetica", 12, "bold"), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.validate_code,
        state=tk.DISABLED,
        activebackground=client.button_hover
    )
    client.validate_code_button.pack(pady=10)
    
    # Bouton pour revenir au menu
    back_button = tk.Button(
        client.current_frame, 
        text="Retour au Menu", 
        font=("Helvetica", 12), 
        bg=client.button_color, 
        fg="white", 
        padx=20, 
        pady=5, 
        bd=0, 
        relief=tk.FLAT, 
        command=client.setup_main_menu,
        activebackground=client.button_hover
    )
    back_button.pack(pady=10)
