"""Stockage versionné, validation et remplacement atomique."""
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from uuid import UUID
from .core import Catalog, Record
from dataclasses import fields
from .chatgpt import ChatGPT, Conversation, parse_url


def encode(catalog, adapter):
    return {"schema": 1, "records": catalog.to_list(), "chatgpt": adapter.to_list()}


def decode(data):
    try:
        if type(data) is not dict or set(data) != {"schema", "records", "chatgpt"} or type(data["schema"]) is not int or data["schema"] != 1:
            raise ValueError("Version de sauvegarde non prise en charge.")
        if not isinstance(data["records"], list) or not isinstance(data["chatgpt"], list):
            raise ValueError("Listes attendues.")
        if any(not isinstance(r, dict) or set(r) != {f.name for f in fields(Record)} for r in data["records"]):
            raise ValueError("Champs de fiche manquants ou inconnus.")
        rows = [Record(**r) for r in data["records"]]
        cat = Catalog(rows)
        if len(rows) != len(cat.records):
            raise ValueError("Identifiants dupliqués.")
        for r in rows:
            UUID(r.id)
            if r.kind not in ("project", "item") or not isinstance(r.title, str) or not r.title.strip():
                raise ValueError("Fiche invalide.")
            if not all(isinstance(v, str) for v in (r.description, r.notes, r.created, r.modified)):
                raise ValueError("Champs texte invalides.")
            for stamp in (r.created, r.modified):
                if datetime.fromisoformat(stamp).tzinfo is None:
                    raise ValueError("Date sans fuseau.")
            for values in (r.tags, r.categories, r.projects):
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values) or len(values) != len(set(values)):
                    raise ValueError("Liste invalide ou dupliquée.")
            if not isinstance(r.metadata, dict) or not all(isinstance(k, str) and k.strip() and isinstance(v, str) for k, v in r.metadata.items()):
                raise ValueError("Métadonnées invalides.")
            if type(r.order) is not int or r.order < 0:
                raise ValueError("Ordre invalide.")
            if r.kind == "item" and r.parent is not None or r.kind == "project" and r.projects:
                raise ValueError("Relations invalides.")
            for p in ([r.parent] if r.parent is not None else []) + r.projects:
                if p not in cat.records or cat.records[p].kind != "project":
                    raise ValueError("Projet absent.")
            seen, cursor = {r.id}, r.parent
            while cursor is not None:
                if cursor in seen:
                    raise ValueError("Cycle de projets.")
                seen.add(cursor)
                cursor = cat.records[cursor].parent
        conversations = [Conversation(**c) for c in data["chatgpt"]]
        if len({c.record_id for c in conversations}) != len(conversations) or len({c.conversation_id for c in conversations}) != len(conversations):
            raise ValueError("Conversations dupliquées.")
        if {c.record_id for c in conversations} != {r.id for r in rows if r.kind == "item"}:
            raise ValueError("Adaptateur incomplet.")
        for c in conversations:
            if parse_url(c.url)[0] != c.conversation_id:
                raise ValueError("Identité de conversation incohérente.")
        return cat, ChatGPT(cat, conversations)
    except (TypeError, KeyError, AttributeError, ValueError) as exc:
        raise ValueError(f"Catalogue invalide : {exc}") from exc


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            name = stream.name
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.path = self.directory / "catalogue.json"
        self.lock = None

    def acquire(self):
        # Verrou OS libéré aussi en cas d'arrêt brutal ; aucun verrou périmé.
        import msvcrt
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = open(self.directory / "catalogue.lock", "a+b")
        try:
            if os.fstat(self.lock.fileno()).st_size == 0:
                self.lock.write(b"0")
                self.lock.flush()
            self.lock.seek(0)
            msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            self.lock.close()
            raise ValueError("Ce catalogue est déjà ouvert dans une autre instance.") from None

    def load(self):
        if not self.path.exists():
            cat = Catalog()
            return cat, ChatGPT(cat)
        return self.read(self.path)

    @staticmethod
    def read(path):
        with open(path, encoding="utf-8") as stream:
            return decode(json.load(stream))

    def save(self, cat, adapter):
        data = encode(cat, adapter)
        decode(data)
        atomic_write(self.path, data)

    def export(self, destination, cat, adapter):
        if Path(destination).resolve() == self.path:
            raise ValueError("Choisissez un autre fichier que le catalogue actif.")
        data = encode(cat, adapter)
        decode(data)
        atomic_write(destination, data)

    def restore(self, candidate, cat, adapter):
        # Revalidation avant toute écriture, même si l'interface a déjà validé.
        new_cat, new_adapter = decode(candidate)
        backup = self.directory / ("avant-restauration-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json")
        self.export(backup, cat, adapter)
        self.save(new_cat, new_adapter)
        return new_cat, new_adapter, backup
