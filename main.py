"""
Point d'entrée principal pour l'application de jeux en réseau.
Lance le client principal qui permet de choisir entre Mastermind et Morpion.
"""
from app_client import AppClient

if __name__ == "__main__":
    client = AppClient()
    client.run()
