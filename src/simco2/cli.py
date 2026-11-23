"""Commandes de gestion locale. Pas de compte administrateur par défaut."""
from __future__ import annotations
import argparse
import getpass
import os
from simco2.adapters.db import Database


def main():
    parser = argparse.ArgumentParser(description="SimCO2 prototype")
    parser.add_argument("command", choices=["init-db", "create-user"])
    parser.add_argument("--db", default=os.getenv("SIMCO2_DB_PATH", "./simco2.sqlite"))
    parser.add_argument("--username", help="Identifiant utilisateur pour create-user")
    args = parser.parse_args()
    db = Database(args.db)
    db.setup()
    if args.command == "init-db":
        print("Database initialized, FR energy codes only (no assumed national values).")
    elif args.command == "create-user":
        username = args.username or input("Login: ")
        password = getpass.getpass("Mot de passe (12 caractères min.): ")
        db.create_user(username, password)
        print("User created (password never displayed).")


if __name__ == "__main__":
    main()
