"""Préférences d'interface distinctes du catalogue métier schema: 1."""
import json
import re
from .storage import atomic_write


def load(path):
    if not path.exists():
        return {}, ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("version") != 1 or data.get("view") != "list" or type(data.get("inspector")) is not bool:
            raise ValueError("Préférences incompatibles")
        if not re.fullmatch(r"\d{3,5}x\d{3,5}", data.get("geometry", "")):
            raise ValueError("Taille de fenêtre invalide")
        return data, ""
    except (OSError, ValueError, TypeError):
        return {}, "Préférences d'affichage illisibles ; affichage par défaut, catalogue préservé."


def save(path, inspector, geometry):
    atomic_write(path, {"version": 1, "view": "list", "inspector": inspector, "geometry": geometry})
