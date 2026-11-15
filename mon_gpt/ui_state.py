"""État de confort local, séparé du catalogue métier et de ses sauvegardes."""
import json
import re
from .storage import atomic_write

VIEWS = ("list", "detail")
MAX_BYTES = 256 * 1024
IDENTITY = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
WARNING = "Préférences d’affichage illisibles ; affichage par défaut, catalogue préservé."
FIELDS = {"version", "view", "inspector", "geometry", "query", "tag", "category", "scope", "selected", "expanded_projects"}


def validate(data):
    if not isinstance(data, dict) or set(data)-FIELDS or type(data.get("version")) is not int or data["version"] != 1 or data.get("view") not in VIEWS or type(data.get("inspector")) is not bool:
        raise ValueError("Préférences incompatibles")
    geometry=data.get("geometry")
    if not isinstance(geometry,str) or not re.fullmatch(r"\d{3,5}x\d{3,5}",geometry) or not all(100<=int(n)<=20000 for n in geometry.split("x")):
        raise ValueError("Taille de fenêtre invalide")
    for key,limit in (("query",4096),("tag",1024),("category",1024)):
        value=data.get(key,"")
        if not isinstance(value,str) or len(value)>limit or "\x00" in value:
            raise ValueError("Texte d’interface invalide")
    scope=data.get("scope","all")
    if not isinstance(scope,str) or (scope not in ("all","unfiled") and not IDENTITY.fullmatch(scope)):
        raise ValueError("Périmètre invalide")
    selected=data.get("selected")
    if selected is not None and (not isinstance(selected,str) or not IDENTITY.fullmatch(selected)):
        raise ValueError("Sélection invalide")
    if "expanded_projects" in data:
        expanded=data["expanded_projects"]
        if not isinstance(expanded,list) or len(expanded)>4096 or any(not isinstance(i,str) or not IDENTITY.fullmatch(i) for i in expanded) or len(set(expanded))!=len(expanded):
            raise ValueError("Branches invalides")
    return data


def load(path):
    if not path.exists(): return {}, ""
    try:
        with path.open("rb") as stream: raw=stream.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raise ValueError("Préférences trop volumineuses")
        return validate(json.loads(raw.decode("utf-8"))), ""
    except (OSError, ValueError, TypeError, RecursionError):
        return {}, WARNING


def save(path, inspector, geometry, view="list", *, query="", tag="", category="", scope="all", selected=None, expanded_projects=None):
    data={"version":1,"view":view,"inspector":inspector,"geometry":geometry,
          "query":query,"tag":tag,"category":category,"scope":scope,"selected":selected}
    if expanded_projects is not None: data["expanded_projects"]=expanded_projects
    atomic_write(path,validate(data))
