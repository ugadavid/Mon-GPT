"""Jeu MG-002 fictif, distinct du jeu MG-001 et des données utilisateur."""
import sys
from pathlib import Path
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store


def create(directory):
    store = Store(directory)
    store.acquire()
    try:
        if store.path.exists():
            raise ValueError("Catalogue existant : aucune donnée remplacée.")
        cat = Catalog()
        adapter = ChatGPT(cat)
        root = cat.add("Atelier des idées", "project")
        writing = cat.add("Écriture", "project", root.id)
        cat.add("Carnet de voyages imaginaires", "project", writing.id)
        lab = cat.add("Laboratoire", "project")
        cat.add("Projet sans enfant", "project")
        root.metadata = {"Équipe": "Imaginaire"}
        for n, title in enumerate(["Préparer une exploration imaginaire", "Travaux", "Un jardin sur la Lune — idées pour un récit", "Recette : une bibliothèque de rêves et de découvertes imaginaires", "À explorer plus tard"], 1):
            r, _ = adapter.ingest(title, f"https://chatgpt.com/c/00000000-0000-4000-8000-{n:012d}")
            r.description = "Des pistes et des idées pour une aventure entièrement fictive."
            r.notes = "Note fictive partagée : conserver cette même fiche dans tous ses emplacements."
            r.tags = ["Créativité", "Travaux"] if n < 3 else ["Été", "Lecture"]
            r.categories = ["Écriture", "Imaginaire"] if n != 2 else ["Technique"]
            r.metadata = {"État": "À explorer"}
            if n == 1:
                cat.attach(r.id, [writing.id, lab.id])
            elif n != 5:
                cat.attach(r.id, [writing.id if n == 3 else root.id])
        store.save(cat, adapter)
    finally:
        store.lock.close()


if __name__ == "__main__":
    create(Path(sys.argv[1]))
