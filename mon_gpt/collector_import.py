"""Contrat Collector v2 et plan d'import ChatGPT, sans Tk ni accès navigateur."""
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import json
import re
from urllib.parse import urlsplit
from uuid import UUID

from .chatgpt import PROJECT_KEY, parse_url
from .storage import encode, decode, catalog_bytes

MAX_EXPORT = 6 * 1024 * 1024
ENVELOPE = {"source", "schemaVersion", "exportedAt", "projects", "conversations"}
COMMON = {"firstSeenAt", "lastSeenAt", "seenCount"}
PROJECT_FIELDS = COMMON | {"projectKey", "observedName", "nameObservedAt", "evidence"}
THREAD_FIELDS = COMMON | {"conversationId", "url", "observedTitle", "observedUrls", "observedProjectKeys", "lastObservedActive"}
KINDS = {"direct-link", "direct-control", "project-page", "expanded-group", "key-only"}


class ImportProblem(ValueError):
    def __init__(self, issues):
        self.issues = issues
        super().__init__(f"Import refusé : {len(issues)} anomalie(s). " + issues[0])


@dataclass
class Observations:
    projects: list
    conversations: list


@dataclass(frozen=True)
class Decision:
    action: str = "create"
    target: str = ""
    title: str = ""


@dataclass
class Plan:
    before: dict
    data: dict
    counts: dict
    projects: list = field(default_factory=list)
    conversations: list = field(default_factory=list)

    @property
    def changed(self):
        return self.before != self.data

    def summary(self):
        n = self.counts
        return (f"{n['created_projects']} projets créés · {n['reused_projects']} réutilisés · "
                f"{n['associated_projects']} associés · {n['ignored_projects']} ignorés\n"
                f"{n['created_threads']} fils créés · {n['existing_threads']} déjà présents · "
                f"{n['unfiled_threads']} nouveaux à classer")


def _object(value, keys):
    if type(value) is not dict or set(value) != keys:
        raise ValueError("champs manquants ou supplémentaires")


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z", value):
        raise ValueError("date UTC attendue (millisecondes et Z)")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("date UTC impossible") from None


def _common(row):
    first, last = _date(row["firstSeenAt"]), _date(row["lastSeenAt"])
    if first > last:
        raise ValueError("première observation postérieure à la dernière")
    if type(row["seenCount"]) is not int or not 1 <= row["seenCount"] <= 9007199254740991:
        raise ValueError("compteur d’observations invalide")
    return first, last


def _text(value, limit, nullable=True):
    if value is None and nullable:
        return
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError(f"texte vide, caractères de contrôle ou longueur > {limit}")


def _key(value):
    if not isinstance(value, str) or not PROJECT_KEY.fullmatch(value):
        raise ValueError("clé de projet invalide")
    return value


def _url(value):
    _text(value, 2048, False)
    p = urlsplit(value)
    if p.scheme != "https" or p.netloc.lower() != "chatgpt.com" or p.fragment or value != value.strip():
        raise ValueError("URL observée non conforme (HTTPS chatgpt.com exact requis)")
    return p


def _project_url(value):
    p = _url(value)
    match = re.fullmatch(r"/g/(g-p-[A-Za-z0-9_-]{1,124})(?:/project|/c/[0-9a-fA-F-]{36})?/?", p.path)
    if not match:
        raise ValueError("URL de preuve de projet invalide")
    if "/c/" in p.path:
        parse_url(value)
    return match[1], "/c/" in p.path


def _thread_url(value, identity):
    p = _url(value)
    if parse_url(value)[0] != identity:
        raise ValueError("URL portant un autre UUID de conversation")
    match = re.fullmatch(r"/g/(g-p-[A-Za-z0-9_-]{1,124})/c/[^/]+/?", p.path)
    return match[1] if match else None


def _unique(values, limit, minimum=0):
    if type(values) is not list or not minimum <= len(values) <= limit or any(not isinstance(v, str) for v in values) or len(set(values)) != len(values):
        raise ValueError("liste invalide, trop longue ou dupliquée")


def validate_export(data):
    """Refus intégral si une ligne est invalide : aucune omission ni import partiel."""
    try:
        _object(data, ENVELOPE)
        if data["source"] != "mon-gpt-collector" or type(data["schemaVersion"]) is not int or data["schemaVersion"] != 2:
            raise ValueError("seul l’export Mon GPT Collector v2 est accepté")
        _date(data["exportedAt"])
        for name, limit in (("projects", 1000), ("conversations", 5000)):
            if type(data[name]) is not list or len(data[name]) > limit:
                raise ValueError(f"{name} : liste requise, maximum {limit}")
    except (ValueError, TypeError, KeyError) as exc:
        raise ImportProblem([f"Enveloppe : {exc}."]) from None
    issues, keys, identities = [], set(), set()
    for index, row in enumerate(data["projects"], 1):
        try:
            _object(row, PROJECT_FIELDS)
            key = _key(row["projectKey"])
            if key in keys:
                raise ValueError("clé dupliquée (même identique : corriger l’export)")
            keys.add(key)
            first, last = _common(row)
            _text(row["observedName"], 256)
            evidence = row["evidence"]
            _object(evidence, {"kind", "url"})
            kind, url = evidence["kind"], evidence["url"]
            if not isinstance(kind,str) or kind not in KINDS:
                raise ValueError("type de preuve inconnu")
            if row["observedName"] is None:
                if kind != "key-only" or row["nameObservedAt"] is not None:
                    raise ValueError("nom absent et preuve incohérents")
            elif kind == "key-only" or not first <= _date(row["nameObservedAt"]) <= last:
                raise ValueError("nom connu et preuve/date incohérents")
            if kind == "direct-control":
                if url is not None:
                    raise ValueError("preuve de contrôle : URL doit être null")
            elif url is None:
                if kind != "key-only":
                    raise ValueError("URL de preuve manquante")
            else:
                proof_key, thread = _project_url(url)
                if proof_key != key or (kind in ("direct-link", "project-page") and thread) or (kind == "expanded-group" and not thread):
                    raise ValueError("URL et preuve ne désignent pas ce projet")
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            issues.append(f"Projet ligne {index} : {exc}. Corriger le fichier avant import.")
    for index, row in enumerate(data["conversations"], 1):
        try:
            _object(row, THREAD_FIELDS)
            identity = row["conversationId"]
            if not isinstance(identity,str) or not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}",identity):
                raise ValueError("UUID de conversation invalide")
            identity = str(UUID(identity))
            if identity in identities:
                raise ValueError("UUID dupliqué (corriger l’export)")
            identities.add(identity)
            _common(row)
            _text(row["observedTitle"], 512)
            if type(row["lastObservedActive"]) is not bool:
                raise ValueError("indicateur d’activité invalide")
            urls, projects = row["observedUrls"], row["observedProjectKeys"]
            _unique(urls, 10, 1)
            _unique(projects, 10)
            for key in projects:
                _key(key)
                if key not in keys:
                    raise ValueError("référence à un projet absent de projects[]")
            _thread_url(row["url"], identity)
            if row["url"] not in urls:
                raise ValueError("URL représentative absente des URL observées")
            observed = {key for u in urls if (key := _thread_url(u, identity))}
            if observed != set(projects):
                raise ValueError("clés de projets discordantes avec les URL observées")
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            issues.append(f"Discussion ligne {index} : {exc}. Corriger le fichier avant import.")
    if issues:
        raise ImportProblem(issues)
    return Observations(data["projects"], data["conversations"])


def read_export(path):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("champ JSON dupliqué")
            result[key] = value
        return result
    try:
        with open(path, "rb") as stream:
            raw = stream.read(MAX_EXPORT + 1)
        if len(raw) > MAX_EXPORT:
            raise ValueError("export trop volumineux : 6 Mio maximum")
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nombre JSON non fini")))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ImportProblem([f"Fichier JSON : {exc}."]) from None
    return validate_export(data)


def initial_decisions(observations, catalog, adapter):
    choices = {}
    for row in observations.projects:
        key = row["projectKey"]
        target = adapter.project_links.get(key)
        if target in catalog.records and catalog.records[target].kind == "project":
            choices[key] = Decision("existing", target)
        elif target or row["observedName"] is None:
            choices[key] = Decision("resolve")
        else:
            choices[key] = Decision()
    return choices


def project_path(catalog, identity):
    parts, seen = [], set()
    while identity and identity not in seen:
        seen.add(identity)
        r = catalog.records[identity]
        parts.append(r.title)
        identity = r.parent
    return " / ".join(reversed(parts))


def build_plan(observations, decisions, catalog, adapter):
    """Candidat détaché. Les fiches déjà connues restent intégralement identiques."""
    before = encode(catalog, adapter)
    cat, source = decode(before)
    rows = {r["projectKey"]: r for r in observations.projects}
    if set(decisions) != set(rows):
        raise ValueError("Décisions incomplètes : chaque projet doit avoir une décision.")
    destinations, visiting = {}, set()
    counts = dict.fromkeys(("created_projects", "reused_projects", "associated_projects", "ignored_projects", "created_threads", "existing_threads", "unfiled_threads"), 0)

    def destination(key):
        if key in destinations:
            return destinations[key]
        if key in visiting or key not in rows:
            raise ValueError("Fusion circulaire ou source absente : choisir une destination valide.")
        visiting.add(key)
        decision = decisions[key]
        if decision.action == "ignore":
            result = None
            counts["ignored_projects"] += 1
        elif decision.action == "create":
            title = decision.title.strip() or rows[key]["observedName"]
            _text(title, 256, False)
            result = cat.add(title, "project").id
            counts["created_projects"] += 1
        elif decision.action == "existing":
            result = decision.target
            if result not in cat.records or cat.records[result].kind != "project":
                raise ValueError("Projet local disparu : choisir à nouveau une destination.")
            counts["reused_projects" if source.project_links.get(key) == result else "associated_projects"] += 1
        elif decision.action == "merge":
            result = destination(decision.target)
            if result is None:
                raise ValueError("Impossible de fusionner vers un projet ignoré.")
            counts["associated_projects"] += 1
        else:
            raise ValueError("Décision requise : nom absent ou ancien projet local supprimé.")
        if result is not None:
            source.project_links[key] = result
        destinations[key] = result
        visiting.remove(key)
        return result

    for key in rows:
        destination(key)
    thread_rows = []
    known = {c.conversation_id for c in source.conversations.values()}
    for row in observations.conversations:
        identity = str(UUID(row["conversationId"]))
        targets = list(dict.fromkeys(destinations[k] for k in row["observedProjectKeys"] if destinations[k]))
        existing = identity in known
        if existing:
            counts["existing_threads"] += 1
            old = next(c for c in source.conversations.values() if c.conversation_id == identity)
            targets = list(cat.records[old.record_id].projects)
        else:
            title = row["observedTitle"] or f"Discussion sans titre · {identity[:8]}"
            record, _ = source.ingest(title, row["url"])
            if targets:
                cat.attach(record.id, targets)
            known.add(identity)
            counts["created_threads"] += 1
            if not targets:
                counts["unfiled_threads"] += 1
        thread_rows.append({"identity": identity, "title": row["observedTitle"] or "Titre provisoire · " + identity[:8],
                            "sources": list(row["observedProjectKeys"]), "targets": targets,
                            "status": "Déjà présent · inchangé" if existing else ("Nouveau" if targets else "Nouveau · À classer"),
                            "provisional": row["observedTitle"] is None})
    data = encode(cat, source)
    decode(data)
    catalog_bytes(data)
    project_rows = [{"key": k, "name": r["observedName"] or "Nom non observé", "target": destinations[k],
                     "destination": project_path(cat, destinations[k]) if destinations[k] else "Ignoré · fils sans autre destination à classer"}
                    for k, r in rows.items()]
    return Plan(before, data, counts, project_rows, thread_rows)
