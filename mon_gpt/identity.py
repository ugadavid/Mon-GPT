"""Repères visuels génériques et résolution pure, sans UI ni source distante."""
from dataclasses import dataclass
import re


COVERS = {
    "soleil": "Prairie au soleil",
    "ecriture": "Le jardin des mots", "voyage": "L’échappée belle",
    "montagne": "Les grands horizons", "laboratoire": "Le cabinet des curiosités",
    "creation": "La fabrique des idées", "technique": "L’atelier des inventions",
}
ICONS = {"folder":"Dossier", "book":"Carnet", "leaf":"Nature", "compass":"Exploration",
         "mountain":"Montagne", "flask":"Laboratoire", "palette":"Création", "circuit":"Technique",
         "pen":"Stylo", "feather":"Plume", "chat":"Bulle", "conversation":"Conversation",
         "lamp":"Lampe", "bulb":"Idée", "planet":"Planète", "star":"Étoile",
         "map":"Carte", "globe":"Globe", "tree":"Arbre", "flower":"Fleur",
         "sun":"Soleil", "moon":"Lune", "search":"Loupe", "code":"Code",
         "terminal":"Terminal", "database":"Données", "tools":"Outils", "gear":"Mécanique",
         "microscope":"Microscope", "music":"Musique", "camera":"Photo", "brush":"Pinceau",
         "calendar":"Calendrier", "clock":"Horloge", "home":"Maison", "heart":"Cœur"}
PALETTE = {
    "atelier": ("Atelier", "#315E4F"), "sauge": ("Sauge", "#8FA98B"),
    "mousse": ("Mousse", "#6D7C52"), "eucalyptus": ("Eucalyptus", "#6A9990"),
    "terracotta": ("Terracotta", "#BD7658"), "argile": ("Argile", "#D6A18B"),
    "rose": ("Rose poudré", "#C69B9F"), "prune": ("Prune", "#916A80"),
    "sable": ("Sable", "#D3BD92"), "ocre": ("Ocre", "#BE944C"),
    "miel": ("Miel", "#D9B75D"), "cacao": ("Cacao", "#92715E"),
    "brume": ("Bleu brume", "#91A8BD"), "petrole": ("Pétrole", "#447984"),
    "lavande": ("Lavande", "#AB9BBE"), "ardoise": ("Ardoise", "#6E7D94"),
}
DEFAULTS = {"image":"pack:soleil", "icon":"folder", "color":"atelier"}
ASSET = re.compile(r"asset:([0-9a-f]{64})\Z")


def validate_visual(value, kind="project"):
    if not isinstance(value, dict) or set(value)-set(DEFAULTS) or (kind!="project" and value):
        raise ValueError("Repères visuels de projet invalides.")
    if any(not isinstance(v,str) for v in value.values()):
        raise ValueError("Repères visuels : identifiants texte attendus.")
    image=value.get("image",DEFAULTS["image"])
    if image not in {"pack:"+key for key in COVERS} and not ASSET.fullmatch(image):
        raise ValueError("Référence d’image inconnue ou non sûre.")
    if value.get("icon",DEFAULTS["icon"]) not in ICONS or value.get("color",DEFAULTS["color"]) not in PALETTE:
        raise ValueError("Icône ou couleur inconnue.")


@dataclass(frozen=True)
class VisualIdentity:
    project: str | None = None
    image: str | None = None
    icon: str = "folder"
    color: str = "atelier"


def resolve_identity(catalog, identity=None, scope=None):
    """Projet choisi ; sinon contexte direct du fil, puis son premier lien."""
    record=catalog.records.get(identity)
    project=None
    if record and record.kind=="project": project=record
    elif record and record.projects:
        pid=scope if scope in record.projects else record.projects[0]
        project=catalog.records.get(pid)
    if project is None: return VisualIdentity()
    visual={**DEFAULTS,**project.visual}
    return VisualIdentity(project.id,visual["image"],visual["icon"],visual["color"])


def image_references(catalog):
    return {r.visual["image"] for r in catalog.records.values()
            if r.kind=="project" and ASSET.fullmatch(r.visual.get("image",""))}
