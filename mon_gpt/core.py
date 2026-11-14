"""Organisation indépendante de toute source, interface et persistance."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from uuid import uuid4
import unicodedata


def now():
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def fold(value):
    return "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c)).replace("œ", "oe").replace("æ", "ae")


@dataclass
class Record:
    title: str
    kind: str = "item"
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    parent: str | None = None
    order: int = 0
    projects: list[str] = field(default_factory=list)
    created: str = field(default_factory=now)
    modified: str = field(default_factory=now)


class Catalog:
    def __init__(self, records=()):
        self.records = {r.id: r for r in records}

    def add(self, title, kind="item", parent=None):
        if not title.strip():
            raise ValueError("Le titre est obligatoire.")
        if kind not in ("project", "item") or (kind == "item" and parent is not None):
            raise ValueError("Type ou parent de fiche invalide.")
        if parent is not None and (parent not in self.records or self.records[parent].kind != "project"):
            raise ValueError("Projet parent introuvable.")
        r = Record(title.strip(), kind, parent=parent, order=max((x.order for x in self.children(parent)), default=-1) + 1)
        self.records[r.id] = r
        return r

    def children(self, parent=None, alphabetical=False):
        rows = [r for r in self.records.values() if r.kind == "project" and r.parent == parent]
        return sorted(rows, key=(lambda r: (fold(r.title), r.title, r.id)) if alphabetical else (lambda r: (r.order, r.id)))

    def descendants(self, project):
        result, pending = set(), [project]
        while pending:
            current = pending.pop()
            if current in result:
                continue
            result.add(current)
            pending.extend(r.id for r in self.children(current))
        return result

    def move(self, identity, parent):
        r = self.records[identity]
        if r.kind != "project":
            raise ValueError("Seul un projet peut avoir un parent.")
        if parent in self.descendants(identity):
            raise ValueError("Un projet ne peut pas être déplacé dans lui-même ou ses descendants.")
        if parent is not None and (parent not in self.records or self.records[parent].kind != "project"):
            raise ValueError("Projet parent introuvable.")
        r.parent, r.order, r.modified = parent, max((x.order for x in self.children(parent)), default=-1) + 1, now()

    def reorder(self, identity, step):
        r = self.records[identity]
        if r.kind != "project":
            raise ValueError("Seuls les projets ont un ordre manuel.")
        rows = self.children(r.parent)
        i = rows.index(r)
        j = i + step
        if 0 <= j < len(rows):
            rows[i], rows[j] = rows[j], rows[i]
            for n, row in enumerate(rows):
                row.order, row.modified = n, now()

    def attach(self, identity, projects):
        if any(p not in self.records or self.records[p].kind != "project" for p in projects):
            raise ValueError("Rattachement vers un projet absent.")
        r = self.records[identity]
        if r.kind != "item":
            raise ValueError("Seule une fiche peut avoir plusieurs emplacements.")
        r.projects, r.modified = list(dict.fromkeys(projects)), now()

    def delete(self, identity):
        r = self.records[identity]
        if r.kind == "project":
            for child in self.children(identity):
                self.move(child.id, r.parent)
            for item in self.records.values():
                if identity in item.projects:
                    self.attach(item.id, [p for p in item.projects if p != identity])
        del self.records[identity]

    def search(self, query="", project=None, tag="", category="", unfiled=False):
        scope = self.descendants(project) if project else None
        result = []
        for r in self.records.values():
            text = " ".join([r.title, r.description, r.notes, *r.tags, *r.categories, *r.metadata.keys(), *r.metadata.values()])
            if fold(query) not in fold(text):
                continue
            if tag and fold(tag) not in map(fold, r.tags):
                continue
            if category and fold(category) not in map(fold, r.categories):
                continue
            if unfiled and (r.kind != "item" or r.projects):
                continue
            if scope and not (r.id in scope or scope.intersection(r.projects)):
                continue
            result.append(r)
        return sorted(result, key=lambda r: (r.kind, fold(r.title), r.id))

    def to_list(self):
        return [asdict(r) for r in self.records.values()]
