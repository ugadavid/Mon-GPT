"""Crée un catalogue fictif à un emplacement explicite, jamais par défaut."""
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
            raise ValueError("Un catalogue existe déjà ici ; exemple non écrit.")
        cat = Catalog()
        adapter = ChatGPT(cat)
        root = cat.add("Atelier des idées", "project")
        child = cat.add("Écriture", "project", root.id)
        cat.add("Carnet de voyages imaginaires", "project", child.id)
        other = cat.add("Laboratoire", "project")
        root.metadata = {"Équipe": "Imaginaire"}
        root.notes = "Exemples entièrement fictifs pour découvrir Mon GPT<3."
        for n, title in enumerate(["Un jardin sur la Lune — idées pour un récit", "Préparer une exposition imaginaire", "À explorer plus tard"], 1):
            r, _ = adapter.ingest(title, f"https://chatgpt.com/c/00000000-0000-4000-8000-{n:012d}")
            r.description = "Conversation fictive : aucun contenu distant n'est téléchargé."
            r.tags, r.categories = ["Créativité", "Été"], ["Idées", "Brouillon"]
            r.metadata = {"État": "À explorer", "Origine": "Démonstration fictive"}
            if n == 1:
                cat.attach(r.id, [child.id, other.id])
        store.save(cat, adapter)
    finally:
        store.lock.close()


if __name__ == "__main__":
    create(Path(sys.argv[1]))
